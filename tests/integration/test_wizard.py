from __future__ import annotations

import os
from pathlib import Path

import pytest

from scru.config import Config, RecordConfig, SourceConfig, load_config, save_config
from scru.wizard import edit, new


def _require_token() -> None:
    if not os.environ.get("CLOUDFLARE_API_TOKEN"):
        pytest.skip("CLOUDFLARE_API_TOKEN is not set")


def _input_sequence(responses):
    it = iter(responses)

    def _input(_prompt):
        try:
            return next(it)
        except StopIteration:
            return ""

    return _input


def test_wizard_new_creates_config(tmp_path):
    _require_token()

    config_path = tmp_path / "config.yaml"
    responses = _input_sequence([
        "1",  # select first zone
        "scru-wizard-it-new",  # type a new record name
        "2",  # source: public
        "n",  # proxied: no
        "",  # ttl: omit
        "n",  # add another: no
    ])

    new(config_path=config_path, input_func=responses)

    assert config_path.exists()
    config = load_config(config_path)
    assert len(config.records) == 1
    r = config.records[0]
    assert r.name == "scru-wizard-it-new"
    assert r.zone_id
    assert r.source.type == "public"
    assert r.proxied is False
    assert r.ttl is None


def test_wizard_new_creates_config_with_two_records(tmp_path):
    _require_token()

    config_path = tmp_path / "config.yaml"
    responses = _input_sequence([
        "1",  # select first zone
        "scru-wizard-it-a",  # type new record name
        "2",  # source: public
        "y",  # proxied: yes
        "",  # ttl: omit
        "y",  # add another
        "1",  # select first zone again
        "scru-wizard-it-b",  # type another record name
        "1",  # source: fixed
        "10.0.0.99",  # fixed IP
        "n",  # proxied: no
        "120",  # ttl
        "n",  # add another: no
    ])

    new(config_path=config_path, input_func=responses)

    assert config_path.exists()
    config = load_config(config_path)
    assert len(config.records) == 2

    r1 = config.records[0]
    assert r1.name == "scru-wizard-it-a"
    assert r1.source.type == "public"
    assert r1.proxied is True
    assert r1.ttl is None

    r2 = config.records[1]
    assert r2.name == "scru-wizard-it-b"
    assert r2.source.type == "fixed"
    assert r2.source.value == "10.0.0.99"
    assert r2.proxied is False
    assert r2.ttl == 120


def test_wizard_new_token_missing(monkeypatch, capsys):
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)
    new()
    captured = capsys.readouterr()
    assert "CLOUDFLARE_API_TOKEN is not set" in captured.out


def test_wizard_edit_save_and_quit(tmp_path):
    _require_token()

    config_path = tmp_path / "config.yaml"
    save_config(config_path, Config(records=[
        RecordConfig(
            zone_id="dummy-zone",
            name="dummy.example.com",
            source=SourceConfig(type="public"),
        ),
    ]))

    responses = _input_sequence([
        "q",  # save and quit immediately
    ])

    edit(config_path=config_path, input_func=responses)

    assert config_path.exists()
    config = load_config(config_path)
    assert len(config.records) == 1
    assert config.records[0].name == "dummy.example.com"


def test_wizard_edit_token_missing(monkeypatch, capsys):
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)
    edit()
    captured = capsys.readouterr()
    assert "CLOUDFLARE_API_TOKEN is not set" in captured.out
