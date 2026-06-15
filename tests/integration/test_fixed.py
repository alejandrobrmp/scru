from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

from scru.cloudflare import CloudflareClient

from tests.integration.support import (
    config_path_for_home,
    load_case,
    managed_cloudflare_records,
    render_config_yaml,
    zone_id_for_case,
    run_scru,
)

CASES_DIR = Path(__file__).with_name("cases")
UPDATE_CASE_FILE = CASES_DIR / "01-update-existing-record.yaml"
MISSING_CASE_FILE = CASES_DIR / "02-missing-record.yaml"


@contextmanager
def integration_case_context(
    integration_env: dict[str, str],
    integration_home: Path,
    cloudflare_client: CloudflareClient,
    case_file: Path,
):
    case = load_case(case_file, integration_env)
    config_path = config_path_for_home(integration_home)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    zone_id = zone_id_for_case(cloudflare_client, integration_env)
    zone_name = str(integration_env["SCRU_INTEGRATION_ZONE_NAME"])

    try:
        setup = case.get("setup") or {}
        create_records = [
            {**record, "zone_id": zone_id if str(record.get("zone_id")) == zone_name else str(record.get("zone_id"))}
            for record in (setup.get("create_records") or [])
        ]
        config_yaml = render_config_yaml(str(case["config_yaml"]), zone_name, zone_id)

        with managed_cloudflare_records(cloudflare_client, create_records):
            config_path.write_text(config_yaml, encoding="utf-8")
            yield case, config_path, zone_id, zone_name
    finally:
        if config_path.exists():
            config_path.unlink()


def test_update_existing_record(repo_root: Path, integration_env: dict[str, str], integration_home: Path, cloudflare_client: CloudflareClient):
    with integration_case_context(integration_env, integration_home, cloudflare_client, UPDATE_CASE_FILE) as (_, config_path, zone_id, _):
        result = run_scru(repo_root, integration_env, integration_home)

        assert result.returncode == 0
        assert result.stderr == ""
        assert result.stdout.strip() == f"{integration_env['SCRU_INTEGRATION_RECORD_NAME']}: updated"

        assert config_path.exists()

        record = cloudflare_client.get_record(zone_id, str(integration_env["SCRU_INTEGRATION_RECORD_NAME"]))
        assert record is not None
        assert record["content"] == integration_env["SCRU_INTEGRATION_TARGET_IP"]


def test_missing_record_fails(repo_root: Path, integration_env: dict[str, str], integration_home: Path, cloudflare_client: CloudflareClient):
    with integration_case_context(integration_env, integration_home, cloudflare_client, MISSING_CASE_FILE) as (_, config_path, zone_id, _):
        result = run_scru(repo_root, integration_env, integration_home)

        assert result.returncode == 0
        assert result.stderr == ""
        assert result.stdout.strip() == f"{integration_env['SCRU_INTEGRATION_MISSING_RECORD_NAME']}: failed (record not found)"

        assert config_path.exists()

        assert cloudflare_client.get_record(zone_id, str(integration_env["SCRU_INTEGRATION_MISSING_RECORD_NAME"])) is None
        sentinel_record = cloudflare_client.get_record(zone_id, str(integration_env["SCRU_INTEGRATION_SENTINEL_RECORD_NAME"]))
        assert sentinel_record is not None
        assert sentinel_record["content"] == integration_env["SCRU_INTEGRATION_INITIAL_IP"]
