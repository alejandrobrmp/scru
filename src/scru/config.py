from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

TOKEN_ENV_VAR = "CLOUDFLARE_API_TOKEN"


class ConfigError(ValueError):
    pass


@dataclass(slots=True)
class SourceConfig:
    type: str
    value: str | None = None
    command: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SourceConfig":
        if not isinstance(data, dict):
            raise ConfigError("source must be a mapping")

        source_type = data.get("type")
        if not source_type:
            raise ConfigError("source.type is required")

        value = data.get("value")
        command = data.get("command")
        if source_type == "fixed":
            if not value:
                raise ConfigError("source.value is required for fixed source")
            return cls(type=source_type, value=str(value))
        if source_type == "custom":
            if not command:
                raise ConfigError("source.command is required for custom source")
            return cls(type=source_type, command=str(command))
        if source_type == "public":
            return cls(type=source_type)

        raise ConfigError(f"unsupported source type: {source_type}")

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"type": self.type}
        if self.value is not None:
            data["value"] = self.value
        if self.command is not None:
            data["command"] = self.command
        return data


@dataclass(slots=True)
class RecordConfig:
    zone_id: str
    name: str
    source: SourceConfig
    proxied: bool | None = None
    ttl: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecordConfig":
        if not isinstance(data, dict):
            raise ConfigError("record entries must be mappings")

        zone_id = data.get("zone_id")
        if not zone_id:
            raise ConfigError("records[].zone_id is required")

        name = data.get("name")
        if not name:
            raise ConfigError("records[].name is required")

        source = SourceConfig.from_dict(data.get("source") or {})
        proxied = data.get("proxied")
        ttl = data.get("ttl")
        return cls(
            zone_id=str(zone_id),
            name=str(name),
            source=source,
            proxied=None if proxied is None else bool(proxied),
            ttl=None if ttl is None else int(ttl),
        )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "zone_id": self.zone_id,
            "name": self.name,
            "source": self.source.to_dict(),
        }
        if self.proxied is not None:
            data["proxied"] = self.proxied
        if self.ttl is not None:
            data["ttl"] = self.ttl
        return data


@dataclass(slots=True)
class Config:
    records: list[RecordConfig] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        if not isinstance(data, dict):
            raise ConfigError("config must be a mapping")

        if "records" not in data:
            raise ConfigError("records is required")

        records = [RecordConfig.from_dict(record) for record in data["records"]]
        return cls(records=records)

    def to_dict(self) -> dict[str, Any]:
        return {"records": [record.to_dict() for record in self.records]}


def load_config(path: Path) -> Config:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return Config.from_dict(data)


def save_config(path: Path, config: Config) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(
            config.to_dict(),
            handle,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        )
