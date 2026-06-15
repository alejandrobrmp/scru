from __future__ import annotations

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from scru.cloudflare import CloudflareClient

from tests.integration.support import missing_required_keys


load_dotenv(Path(__file__).with_name(".env"), override=False)


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def integration_env() -> dict[str, str]:
    env = dict(os.environ)

    missing = missing_required_keys(env)
    if missing:
        pytest.skip("missing integration env vars: " + ", ".join(missing))

    return env


@pytest.fixture
def integration_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    return home


@pytest.fixture
def cloudflare_client(integration_env: dict[str, str]) -> CloudflareClient:
    return CloudflareClient(token=integration_env["CLOUDFLARE_API_TOKEN"])
