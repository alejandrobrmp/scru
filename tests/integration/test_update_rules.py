from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import pytest

from scru.cloudflare import CloudflareClient

from tests.integration.support import (
    config_path_for_home,
    load_case,
    managed_cloudflare_records,
    render_config_yaml,
    run_scru,
    zone_id_for_case,
)

CASES_DIR = Path(__file__).with_name("cases")
PROXIED_TTL_WARNING_CASE_FILE = CASES_DIR / "06-proxied-ttl-warning.yaml"
PROXIED_NO_TTL_CASE_FILE = CASES_DIR / "07-proxied-no-ttl.yaml"
NON_PROXIED_TTL_SKIP_CASE_FILE = CASES_DIR / "08-non-proxied-ttl-skip.yaml"


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


def test_proxied_record_with_config_ttl_warns_and_skips_on_rerun(
    repo_root: Path,
    integration_env: dict[str, str],
    integration_home: Path,
    cloudflare_client: CloudflareClient,
):
    if not integration_env.get("SCRU_INTEGRATION_RECORD_NAME_3"):
        pytest.skip("SCRU_INTEGRATION_RECORD_NAME_3 is required for proxied integration tests")

    record_name = str(integration_env["SCRU_INTEGRATION_RECORD_NAME_3"])

    with integration_case_context(
        integration_env, integration_home, cloudflare_client, PROXIED_TTL_WARNING_CASE_FILE
    ) as (_, config_path, zone_id, _):
        first = run_scru(repo_root, integration_env, integration_home)

        assert first.returncode == 0
        assert first.stderr == ""
        assert first.stdout.splitlines() == [
            f"{record_name}: warning (ttl ignored for proxied record)",
            f"{record_name}: updated",
        ]

        record = cloudflare_client.get_record(zone_id, record_name)
        assert record is not None
        assert record["content"] == integration_env["SCRU_INTEGRATION_TARGET_IP"]
        assert record["proxied"] is True

        second = run_scru(repo_root, integration_env, integration_home)

        assert second.returncode == 0
        assert second.stderr == ""
        assert second.stdout.strip() == f"{record_name}: skipped (unchanged)"


def test_proxied_record_without_config_ttl_skips_on_rerun(
    repo_root: Path,
    integration_env: dict[str, str],
    integration_home: Path,
    cloudflare_client: CloudflareClient,
):
    if not integration_env.get("SCRU_INTEGRATION_RECORD_NAME_3"):
        pytest.skip("SCRU_INTEGRATION_RECORD_NAME_3 is required for proxied integration tests")

    record_name = str(integration_env["SCRU_INTEGRATION_RECORD_NAME_3"])

    with integration_case_context(
        integration_env, integration_home, cloudflare_client, PROXIED_NO_TTL_CASE_FILE
    ) as (_, config_path, zone_id, _):
        first = run_scru(repo_root, integration_env, integration_home)

        assert first.returncode == 0
        assert first.stderr == ""
        assert first.stdout.strip() == f"{record_name}: updated"

        record = cloudflare_client.get_record(zone_id, record_name)
        assert record is not None
        assert record["content"] == integration_env["SCRU_INTEGRATION_TARGET_IP"]
        assert record["proxied"] is True

        second = run_scru(repo_root, integration_env, integration_home)

        assert second.returncode == 0
        assert second.stderr == ""
        assert second.stdout.strip() == f"{record_name}: skipped (unchanged)"


def test_non_proxied_record_skips_when_content_proxied_and_ttl_all_match(
    repo_root: Path,
    integration_env: dict[str, str],
    integration_home: Path,
    cloudflare_client: CloudflareClient,
):
    if not integration_env.get("SCRU_INTEGRATION_RECORD_NAME_3"):
        pytest.skip("SCRU_INTEGRATION_RECORD_NAME_3 is required for proxied integration tests")

    record_name = str(integration_env["SCRU_INTEGRATION_RECORD_NAME_3"])

    with integration_case_context(
        integration_env, integration_home, cloudflare_client, NON_PROXIED_TTL_SKIP_CASE_FILE
    ) as (_, config_path, zone_id, _):
        result = run_scru(repo_root, integration_env, integration_home)

        assert result.returncode == 0
        assert result.stderr == ""
        assert result.stdout.strip() == f"{record_name}: skipped (unchanged)"

        record = cloudflare_client.get_record(zone_id, record_name)
        assert record is not None
        assert record["content"] == integration_env["SCRU_INTEGRATION_TARGET_IP"]
        assert record["proxied"] is False
        assert record["ttl"] == 300
