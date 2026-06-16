from __future__ import annotations

import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

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
PUBLIC_CASE_FILE = CASES_DIR / "03-public-source.yaml"


class _PublicIPHandler(BaseHTTPRequestHandler):
    response_text = ""

    def do_GET(self):
        body = self.response_text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


@contextmanager
def public_ip_server(response_text: str):
    handler = type("PublicIPHandler", (_PublicIPHandler,), {"response_text": response_text})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/ip"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


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


def test_public_source_updates_record(
    repo_root: Path,
    integration_env: dict[str, str],
    integration_home: Path,
    cloudflare_client: CloudflareClient,
):
    with public_ip_server(integration_env["SCRU_INTEGRATION_TARGET_IP"]) as public_ip_url:
        run_env = dict(integration_env)
        run_env["SCRU_PUBLIC_IP_URL"] = public_ip_url

        with integration_case_context(run_env, integration_home, cloudflare_client, PUBLIC_CASE_FILE) as (
            _,
            config_path,
            zone_id,
            _,
        ):
            result = run_scru(repo_root, run_env, integration_home)

            assert result.returncode == 0
            assert result.stderr == ""
            assert result.stdout.strip() == f"{integration_env['SCRU_INTEGRATION_RECORD_NAME']}: updated"

            assert config_path.exists()

            record = cloudflare_client.get_record(zone_id, str(integration_env["SCRU_INTEGRATION_RECORD_NAME"]))
            assert record is not None
            assert record["content"] == integration_env["SCRU_INTEGRATION_TARGET_IP"]
