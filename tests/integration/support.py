from __future__ import annotations

import os
import re
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Mapping

import yaml

from scru.cloudflare import CloudflareClient

REQUIRED_ENV_KEYS = (
    "CLOUDFLARE_API_TOKEN",
    "SCRU_INTEGRATION_ZONE_NAME",
    "SCRU_INTEGRATION_RECORD_NAME",
    "SCRU_INTEGRATION_RECORD_NAME_1",
    "SCRU_INTEGRATION_RECORD_NAME_2",
    "SCRU_INTEGRATION_RECORD_NAME_3",
    "SCRU_INTEGRATION_MISSING_RECORD_NAME",
    "SCRU_INTEGRATION_SENTINEL_RECORD_NAME",
    "SCRU_INTEGRATION_INITIAL_IP",
    "SCRU_INTEGRATION_TARGET_IP",
)

PLACEHOLDER_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}|\$([A-Z0-9_]+)")


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()

        key, separator, value = line.partition("=")
        if not separator:
            continue

        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key] = value

    return values


def missing_required_keys(env: Mapping[str, str]) -> list[str]:
    return [key for key in REQUIRED_ENV_KEYS if not env.get(key)]


def expand_placeholders(value: Any, env: Mapping[str, str]) -> Any:
    if isinstance(value, str):
        def replace(match: re.Match[str]) -> str:
            key = match.group(1) or match.group(2)
            if key not in env:
                raise KeyError(key)
            return env[key]

        return PLACEHOLDER_PATTERN.sub(replace, value)

    if isinstance(value, list):
        return [expand_placeholders(item, env) for item in value]

    if isinstance(value, dict):
        return {key: expand_placeholders(item, env) for key, item in value.items()}

    return value


def load_case(path: Path, env: Mapping[str, str]) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    expanded = expand_placeholders(data, env)
    if not isinstance(expanded, dict):
        raise ValueError("case file must contain a mapping")
    return expanded


def normalize_zone_ids(value: Any, zone_name: str, zone_id: str) -> Any:
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if key == "zone_id" and isinstance(item, str) and item == zone_name:
                normalized[key] = zone_id
            else:
                normalized[key] = normalize_zone_ids(item, zone_name, zone_id)
        return normalized

    if isinstance(value, list):
        return [normalize_zone_ids(item, zone_name, zone_id) for item in value]

    return value


def render_config_yaml(config_yaml: str, zone_name: str, zone_id: str) -> str:
    data = yaml.safe_load(config_yaml) or {}
    normalized = normalize_zone_ids(data, zone_name, zone_id)
    return yaml.safe_dump(normalized, sort_keys=False, default_flow_style=False)


def config_path_for_home(home: Path) -> Path:
    return home / ".config" / "scru" / "config.yaml"


def zone_id_for_case(client: CloudflareClient, env: Mapping[str, str]) -> str:
    return client.get_zone_id(str(env["SCRU_INTEGRATION_ZONE_NAME"]))


def build_run_env(repo_root: Path, env: Mapping[str, str], home: Path) -> dict[str, str]:
    run_env = dict(os.environ)
    run_env.update(env)
    run_env["HOME"] = str(home)
    run_env["USERPROFILE"] = str(home)

    src_path = str(repo_root / "src")
    existing_pythonpath = run_env.get("PYTHONPATH")
    run_env["PYTHONPATH"] = src_path if not existing_pythonpath else os.pathsep.join((src_path, existing_pythonpath))
    return run_env


def run_scru(repo_root: Path, env: Mapping[str, str], home: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "scru"],
        cwd=repo_root,
        env=build_run_env(repo_root, env, home),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


@contextmanager
def managed_cloudflare_records(client: CloudflareClient, records: list[Mapping[str, Any]]):
    created_records: list[tuple[str, str]] = []
    try:
        for record in records:
            zone_id = str(record["zone_id"])
            name = str(record["name"])

            existing = client.get_record(zone_id, name)
            while existing is not None:
                client.delete_record(zone_id, str(existing["id"]))
                existing = client.get_record(zone_id, name)

            created = client.create_record(
                zone_id,
                name=name,
                content=str(record["content"]),
                proxied=None if record.get("proxied") is None else bool(record["proxied"]),
                ttl=None if record.get("ttl") is None else int(record["ttl"]),
            )
            created_records.append((zone_id, str(created["id"])))

        yield created_records
    finally:
        cleanup_error: Exception | None = None
        for zone_id, record_id in reversed(created_records):
            try:
                client.delete_record(zone_id, record_id)
            except Exception as exc:  # pragma: no cover - best-effort cleanup path
                cleanup_error = cleanup_error or exc

        if cleanup_error is not None and sys.exc_info()[0] is None:
            raise cleanup_error
