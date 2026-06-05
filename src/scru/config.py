from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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
        data = _parse_yaml(handle.read())
    return Config.from_dict(data)


def save_config(path: Path, config: Config) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(_dump_yaml(config.to_dict()))


def _parse_yaml(text: str) -> dict[str, Any]:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if not lines:
        return {}

    result: dict[str, Any] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if line == "zones: []":
            result["zones"] = []
            index += 1
            continue
        if line == "records: []":
            result["records"] = []
            index += 1
            continue
        if line == "zones:":
            zones, index = _parse_list(lines, index + 1, "zones")
            result["zones"] = zones
            continue
        if line == "records:":
            records, index = _parse_list(lines, index + 1, "records")
            result["records"] = records
            continue
        key, value = _parse_key_value(line)
        result[key] = value
        index += 1
    return result


def _parse_list(lines: list[str], index: int, field_name: str) -> tuple[list[dict[str, Any]], int]:
    items: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    while index < len(lines):
        line = lines[index]
        if not line.startswith("  "):
            break
        stripped = line.strip()
        if stripped.startswith("-"):
            if current is not None:
                items.append(current)
            current = {}
            remainder = stripped[1:].strip()
            if remainder:
                key, value = _parse_key_value(remainder)
                current[key] = value
        else:
            if current is None:
                raise ConfigError(f"{field_name} entries must start with '-'")
            if stripped == "source:":
                source, index = _parse_nested_mapping(lines, index + 1)
                current["source"] = source
                continue
            key, value = _parse_key_value(stripped)
            current[key] = value
        index += 1
    if current is not None:
        items.append(current)
    return items, index


def _parse_nested_mapping(lines: list[str], index: int) -> tuple[dict[str, Any], int]:
    mapping: dict[str, Any] = {}
    while index < len(lines):
        line = lines[index]
        if not line.startswith("      "):
            break
        if line.strip() == "":
            index += 1
            continue
        key, value = _parse_key_value(line.strip())
        mapping[key] = value
        index += 1
    return mapping, index


def _parse_key_value(line: str) -> tuple[str, Any]:
    if ":" not in line:
        raise ConfigError(f"invalid line: {line}")
    key, raw_value = line.split(":", 1)
    value = raw_value.strip()
    return key.strip(), _parse_scalar(value)


def _parse_scalar(value: str) -> Any:
    if value == "":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if value.isdigit():
        return int(value)
    return value


def _dump_yaml(data: dict[str, Any]) -> str:
    lines: list[str] = []
    if data["records"]:
        lines.append("records:")
        for record in data["records"]:
            lines.append(f"  - zone_id: {record['zone_id']}")
            lines.append(f"    name: {record['name']}")
            lines.append("    source:")
            lines.append(f"      type: {record['source']['type']}")
            if record['source'].get("value") is not None:
                lines.append(f"      value: {record['source']['value']}")
            if record['source'].get("command") is not None:
                lines.append(f"      command: {record['source']['command']}")
            if record.get("proxied") is not None:
                lines.append(f"    proxied: {'true' if record['proxied'] else 'false'}")
            if record.get("ttl") is not None:
                lines.append(f"    ttl: {record['ttl']}")
    else:
        lines.append("records: []")
    return "\n".join(lines) + "\n"
