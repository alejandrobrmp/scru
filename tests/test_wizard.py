from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from scru.config import Config, RecordConfig, SourceConfig, load_config, save_config
from scru.wizard import edit, new


@pytest.fixture
def mock_zones():
    return [
        {"id": "zone-1-id", "name": "example.com"},
        {"id": "zone-2-id", "name": "test.org"},
    ]


@pytest.fixture
def mock_records_example():
    return [
        {"id": "rec-1", "name": "www.example.com", "type": "A", "content": "1.2.3.4"},
        {"id": "rec-2", "name": "api.example.com", "type": "A", "content": "5.6.7.8"},
    ]


@pytest.fixture
def mock_records_empty():
    return []


def _make_client_mock(zones, records_map):
    client = MagicMock()
    client.list_all_zones.return_value = zones
    client.list_all_records.side_effect = lambda zone_id: records_map.get(zone_id, [])
    return client


def _input_sequence(responses):
    it = iter(responses)

    def _input(_prompt):
        try:
            return next(it)
        except StopIteration:
            return ""

    return _input


class TestNewWizard:
    def test_token_missing(self, monkeypatch, capsys):
        monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)
        new()
        captured = capsys.readouterr()
        assert "CLOUDFLARE_API_TOKEN is not set" in captured.out

    def test_new_one_fixed_record(
        self, tmp_path, monkeypatch, mock_zones, mock_records_example, capsys
    ):
        monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test-token")
        config_path = tmp_path / "config.yaml"

        client_mock = _make_client_mock(
            mock_zones, {"zone-1-id": mock_records_example}
        )

        responses = _input_sequence([
            "1",  # zone: example.com
            "1",  # record: www.example.com
            "1",  # source: fixed
            "10.0.0.1",  # fixed IP
            "n",  # proxied: no
            "",  # ttl: omit
            "n",  # add another: no
        ])

        with patch("scru.cloudflare.CloudflareClient", return_value=client_mock):
            new(config_path=config_path, input_func=responses)

        config = load_config(config_path)
        assert len(config.records) == 1
        r = config.records[0]
        assert r.zone_id == "zone-1-id"
        assert r.name == "www.example.com"
        assert r.source.type == "fixed"
        assert r.source.value == "10.0.0.1"
        assert r.proxied is False
        assert r.ttl is None

        captured = capsys.readouterr()
        assert "✔ Config saved to" in captured.out

    def test_new_two_records_public_custom(
        self, tmp_path, monkeypatch, mock_zones, mock_records_example, capsys
    ):
        monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test-token")
        config_path = tmp_path / "config.yaml"

        client_mock = _make_client_mock(
            mock_zones,
            {
                "zone-1-id": mock_records_example,
                "zone-2-id": [],
            },
        )

        responses = _input_sequence([
            "1",  # first record: zone example.com
            "2",  # record: api.example.com
            "2",  # source: public
            "n",  # proxied: no
            "",  # ttl: omit
            "y",  # add another
            "2",  # second record: zone test.org
            "my-record",  # type new name
            "3",  # source: custom
            "echo 1.1.1.1",  # command
            "y",  # proxied: yes
            "",  # ttl: omit
            "n",  # add another: no
        ])

        with patch("scru.cloudflare.CloudflareClient", return_value=client_mock):
            new(config_path=config_path, input_func=responses)

        config = load_config(config_path)
        assert len(config.records) == 2

        r1 = config.records[0]
        assert r1.zone_id == "zone-1-id"
        assert r1.name == "api.example.com"
        assert r1.source.type == "public"
        assert r1.proxied is False
        assert r1.ttl is None

        r2 = config.records[1]
        assert r2.zone_id == "zone-2-id"
        assert r2.name == "my-record"
        assert r2.source.type == "custom"
        assert r2.source.command == "echo 1.1.1.1"
        assert r2.proxied is True
        assert r2.ttl is None

        captured = capsys.readouterr()
        assert "✔ Config saved to" in captured.out

    def test_new_proxied_with_ttl_warning(
        self, tmp_path, monkeypatch, mock_zones, mock_records_example, capsys
    ):
        monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test-token")
        config_path = tmp_path / "config.yaml"

        client_mock = _make_client_mock(
            mock_zones, {"zone-1-id": mock_records_example}
        )

        responses = _input_sequence([
            "1",  # zone
            "1",  # record
            "2",  # source: public
            "y",  # proxied: yes
            "300",  # ttl: 300
            "n",  # add another
        ])

        with patch("scru.cloudflare.CloudflareClient", return_value=client_mock):
            new(config_path=config_path, input_func=responses)

        config = load_config(config_path)
        assert len(config.records) == 1
        r = config.records[0]
        assert r.proxied is True
        assert r.ttl == 300

        captured = capsys.readouterr()
        assert "warning: ttl is ignored for proxied records" in captured.out

    def test_new_no_zones(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test-token")
        config_path = tmp_path / "config.yaml"

        client_mock = _make_client_mock([], {})

        responses = _input_sequence([])

        with patch("scru.cloudflare.CloudflareClient", return_value=client_mock):
            new(config_path=config_path, input_func=responses)

        captured = capsys.readouterr()
        assert "No zones found" in captured.out
        assert not config_path.exists()


class TestEditWizard:
    def _write_config(self, path, records):
        save_config(path, Config(records=records))

    def test_edit_add_one_record(
        self, tmp_path, monkeypatch, mock_zones, mock_records_example, capsys
    ):
        monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test-token")
        config_path = tmp_path / "config.yaml"
        self._write_config(config_path, [])
        save_config(config_path, Config(records=[]))

        client_mock = _make_client_mock(
            mock_zones, {"zone-1-id": mock_records_example}
        )

        responses = _input_sequence([
            "a",  # add
            "1",  # zone
            "1",  # record
            "2",  # source: public
            "n",  # proxied
            "",  # ttl
            "q",  # save and quit
        ])

        with patch("scru.cloudflare.CloudflareClient", return_value=client_mock):
            edit(config_path=config_path, input_func=responses)

        config = load_config(config_path)
        assert len(config.records) == 1
        r = config.records[0]
        assert r.name == "www.example.com"
        assert r.source.type == "public"

        captured = capsys.readouterr()
        assert "✔ Config saved to" in captured.out

    def test_edit_update_record_blank_keep(
        self, tmp_path, monkeypatch, mock_zones, mock_records_example, capsys
    ):
        monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test-token")
        config_path = tmp_path / "config.yaml"

        existing = RecordConfig(
            zone_id="zone-1-id",
            name="www.example.com",
            source=SourceConfig(type="custom", command="echo 1.2.3.4"),
            proxied=False,
            ttl=120,
        )
        self._write_config(config_path, [existing])

        client_mock = _make_client_mock(
            mock_zones, {"zone-1-id": mock_records_example}
        )

        responses = _input_sequence([
            "u 1",  # update record 1
            "",  # source: keep custom (default)
            "",  # command: keep
            "",  # proxied: keep no
            "",  # ttl: keep 120
            "q",  # save and quit
        ])

        with patch("scru.cloudflare.CloudflareClient", return_value=client_mock):
            edit(config_path=config_path, input_func=responses)

        config = load_config(config_path)
        assert len(config.records) == 1
        r = config.records[0]
        assert r.zone_id == "zone-1-id"
        assert r.name == "www.example.com"
        assert r.source.type == "custom"
        assert r.source.command == "echo 1.2.3.4"
        assert r.proxied is False
        assert r.ttl == 120

        captured = capsys.readouterr()
        assert "✔ Config saved to" in captured.out

    def test_edit_update_record_change_fields(
        self, tmp_path, monkeypatch, mock_zones, mock_records_example, capsys
    ):
        monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test-token")
        config_path = tmp_path / "config.yaml"

        existing = RecordConfig(
            zone_id="zone-1-id",
            name="www.example.com",
            source=SourceConfig(type="public"),
            proxied=False,
            ttl=None,
        )
        self._write_config(config_path, [existing])

        client_mock = _make_client_mock(
            mock_zones, {"zone-1-id": mock_records_example}
        )

        responses = _input_sequence([
            "u 1",  # update record 1
            "1",  # source: fixed
            "10.0.0.99",  # IP
            "y",  # proxied: yes
            "",  # ttl: omit
            "q",  # save and quit
        ])

        with patch("scru.cloudflare.CloudflareClient", return_value=client_mock):
            edit(config_path=config_path, input_func=responses)

        config = load_config(config_path)
        assert len(config.records) == 1
        r = config.records[0]
        assert r.source.type == "fixed"
        assert r.source.value == "10.0.0.99"
        assert r.proxied is True
        assert r.ttl is None

        captured = capsys.readouterr()
        assert "✔ Config saved to" in captured.out

    def test_edit_delete_record(
        self, tmp_path, monkeypatch, mock_zones, capsys
    ):
        monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test-token")
        config_path = tmp_path / "config.yaml"

        records = [
            RecordConfig(
                zone_id="zone-1-id",
                name="www.example.com",
                source=SourceConfig(type="public"),
            ),
            RecordConfig(
                zone_id="zone-2-id",
                name="api.test.org",
                source=SourceConfig(type="fixed", value="10.0.0.1"),
            ),
        ]
        self._write_config(config_path, records)

        client_mock = _make_client_mock(mock_zones, {})

        responses = _input_sequence([
            "d 1",  # delete record 1
            "q",  # save and quit
        ])

        with patch("scru.cloudflare.CloudflareClient", return_value=client_mock):
            edit(config_path=config_path, input_func=responses)

        config = load_config(config_path)
        assert len(config.records) == 1
        assert config.records[0].name == "api.test.org"

        captured = capsys.readouterr()
        assert "✔ Config saved to" in captured.out

    def test_edit_delete_last_record_no_save(
        self, tmp_path, monkeypatch, mock_zones, capsys
    ):
        monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test-token")
        config_path = tmp_path / "config.yaml"

        records = [
            RecordConfig(
                zone_id="zone-1-id",
                name="www.example.com",
                source=SourceConfig(type="public"),
            ),
        ]
        self._write_config(config_path, records)

        client_mock = _make_client_mock(mock_zones, {})

        responses = _input_sequence([
            "d 1",  # delete the only record
            "q",  # save and quit
        ])

        with patch("scru.cloudflare.CloudflareClient", return_value=client_mock):
            edit(config_path=config_path, input_func=responses)

        captured = capsys.readouterr()
        assert "✔ Config saved (no records) to" in captured.out

        config = load_config(config_path)
        assert len(config.records) == 0

    def test_edit_token_missing(self, monkeypatch, capsys):
        monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)
        edit()
        captured = capsys.readouterr()
        assert "CLOUDFLARE_API_TOKEN is not set" in captured.out
