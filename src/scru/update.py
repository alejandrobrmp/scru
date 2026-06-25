from __future__ import annotations

import ipaddress
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib.request import urlopen

from .cloudflare import CloudflareClient
from .config import Config, ConfigError, RecordConfig, SourceConfig, load_config
from .constants import CONFIG_PATH

SourceResolver = Callable[[SourceConfig], str]
OutputFn = Callable[[str], None]
DEFAULT_PUBLIC_IP_URL = "https://api.ipify.org"
PUBLIC_IP_URL_ENV_VAR = "SCRU_PUBLIC_IP_URL"
CUSTOM_SOURCE_TIMEOUT_SECONDS = 10
PROXIED_AUTO_TTL = 1


def _no_output(_message: str) -> None:
    pass


def _is_unchanged(record: RecordConfig, current: Mapping[str, Any], source_ipv4: str) -> bool:
    if current.get("content") != source_ipv4:
        return False
    if current.get("proxied") != record.proxied:
        return False
    if record.proxied is True:
        # Cloudflare enforces auto TTL (1) for proxied records; SCRU never
        # sends a ttl for proxied records, so do not fight the provider value.
        return True
    current_ttl = current.get("ttl")
    if current_ttl == PROXIED_AUTO_TTL and record.ttl is None:
        return True
    return current_ttl == record.ttl


def resolve_fixed_ipv4(source: SourceConfig) -> str:
    if source.value is None:
        raise ValueError("source.value is required for fixed source")

    address = ipaddress.ip_address(source.value)
    if address.version != 4:
        raise ValueError("source.value must be an IPv4 address")

    return str(address)


def resolve_public_source_ipv4() -> str:
    target_url = os.environ.get(PUBLIC_IP_URL_ENV_VAR, DEFAULT_PUBLIC_IP_URL)

    with urlopen(target_url, timeout=10) as response:
        text = response.read().decode("utf-8").strip()

    if not text:
        raise ValueError("public IP response is empty")

    address = ipaddress.ip_address(text)
    if address.version != 4:
        raise ValueError("public IP response must be an IPv4 address")

    return str(address)


def resolve_custom_source_ipv4(source: SourceConfig) -> str:
    if source.command is None:
        raise ValueError("source.command is required for custom source")

    command = shlex.split(source.command)
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=CUSTOM_SOURCE_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ValueError(f"custom source command timed out after {CUSTOM_SOURCE_TIMEOUT_SECONDS} seconds") from exc

    if completed.returncode != 0:
        raise ValueError(f"custom source command failed with exit code {completed.returncode}")

    text = completed.stdout.strip()
    if not text:
        raise ValueError("custom source command produced no output")

    try:
        address = ipaddress.ip_address(text)
    except ValueError as exc:
        raise ValueError("custom source command must output exactly one IPv4 address") from exc

    if address.version != 4:
        raise ValueError("custom source command must output exactly one IPv4 address")

    return str(address)


def resolve_source_ipv4(source: SourceConfig) -> str:
    match source.type:
        case "fixed":
            return resolve_fixed_ipv4(source)
        case "public":
            return resolve_public_source_ipv4()
        case "custom":
            return resolve_custom_source_ipv4(source)
        case _:
            raise ValueError(f"unsupported source type: {source.type}")


def process_record(
    record: RecordConfig,
    *,
    source_resolver: SourceResolver,
    client: CloudflareClient,
    output: OutputFn = _no_output,
) -> str:
    try:
        source_ipv4 = source_resolver(record.source)
        current = client.get_record(record.zone_id, record.name)

        if current is None:
            return f"{record.name}: failed (record not found)"

        if _is_unchanged(record, current, source_ipv4):
            return f"{record.name}: skipped (unchanged)"

        record_id = current.get("id")
        if not record_id:
            return f"{record.name}: failed (record id missing)"

        ttl_for_patch = record.ttl
        if record.proxied is True and record.ttl is not None:
            output(f"{record.name}: warning (ttl ignored for proxied record)")
            ttl_for_patch = None

        client.update_record(
            record.zone_id,
            str(record_id),
            source_ipv4,
            proxied=record.proxied,
            ttl=ttl_for_patch,
        )
        return f"{record.name}: updated"
    except Exception as exc:
        return f"{record.name}: failed ({exc})"


def main(
    *,
    config_path: Path | None = None,
    config_loader: Callable[[Path], Config] = load_config,
    source_resolver: SourceResolver = resolve_source_ipv4,
    client: CloudflareClient | None = None,
    output: Callable[[str], None] = print,
) -> None:
    path = CONFIG_PATH if config_path is None else config_path

    try:
        config = config_loader(path)
    except (OSError, ConfigError) as exc:
        output(f"config: failed ({exc})")
        return

    record_client = client
    for record in config.records:
        if record_client is None:
            record_client = CloudflareClient()
        output(process_record(record, source_resolver=source_resolver, client=record_client, output=output))
