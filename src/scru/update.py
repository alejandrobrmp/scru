from __future__ import annotations

import ipaddress
from pathlib import Path
from typing import Callable

from .cloudflare import CloudflareClient
from .config import Config, ConfigError, RecordConfig, SourceConfig, load_config
from .constants import CONFIG_PATH

SourceResolver = Callable[[SourceConfig], str]


def resolve_source_ipv4(source: SourceConfig) -> str:
    if source.type != "fixed":
        raise ValueError(f"unsupported source type: {source.type}")

    if source.value is None:
        raise ValueError("source.value is required for fixed source")

    address = ipaddress.ip_address(source.value)
    if address.version != 4:
        raise ValueError("source.value must be an IPv4 address")

    return str(address)


def process_record(
    record: RecordConfig,
    *,
    source_resolver: SourceResolver,
    client: CloudflareClient,
) -> str:
    try:
        source_ipv4 = source_resolver(record.source)
        current = client.get_record(record.zone_id, record.name)

        if current is None:
            return f"{record.name}: failed (record not found)"

        if current.get("content") == source_ipv4:
            return f"{record.name}: skipped (unchanged)"

        record_id = current.get("id")
        if not record_id:
            return f"{record.name}: failed (record id missing)"

        client.update_record(
            record.zone_id,
            str(record_id),
            source_ipv4,
            proxied=record.proxied,
            ttl=record.ttl,
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

    if len(config.records) != 1:
        output("config: failed (expected exactly one record)")
        return

    record = config.records[0]
    record_client = client if client is not None else CloudflareClient()
    output(process_record(record, source_resolver=source_resolver, client=record_client))
