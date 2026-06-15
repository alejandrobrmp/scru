from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from .config import Config, ConfigError, RecordConfig, SourceConfig, load_config
from .constants import CONFIG_PATH


class CloudflareRecordClient(Protocol):
    def get_record(self, zone_id: str, name: str) -> Mapping[str, Any] | None:
        pass

    def update_record(
        self,
        zone_id: str,
        record_id: str,
        content: str,
        *,
        proxied: bool | None = None,
        ttl: int | None = None,
    ) -> None:
        pass


class SourceResolver(Protocol):
    def __call__(self, source: SourceConfig) -> str:
        pass


@dataclass(slots=True)
class _UnavailableCloudflareClient:
    def get_record(self, zone_id: str, name: str) -> Mapping[str, Any] | None:
        raise NotImplementedError("cloudflare client is not implemented yet")

    def update_record(
        self,
        zone_id: str,
        record_id: str,
        content: str,
        *,
        proxied: bool | None = None,
        ttl: int | None = None,
    ) -> None:
        raise NotImplementedError("cloudflare client is not implemented yet")


def resolve_source_ipv4(source: SourceConfig) -> str:
    raise NotImplementedError("source resolution is not implemented yet")


def process_record(
    record: RecordConfig,
    *,
    source_resolver: SourceResolver,
    client: CloudflareRecordClient,
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
    client: CloudflareRecordClient | None = None,
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
    record_client = client if client is not None else _UnavailableCloudflareClient()
    output(process_record(record, source_resolver=source_resolver, client=record_client))
