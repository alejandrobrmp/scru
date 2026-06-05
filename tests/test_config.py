from pathlib import Path
import re

import pytest

from scru.config import Config, ConfigError, RecordConfig, SourceConfig, ZoneConfig, load_config, save_config


def test_load_config_parses_multiple_zones_and_records(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """token_env_var: CF_TOKEN
zones:
  - id: zone-1
    name: example.com
  - id: zone-2
records:
  - zone_id: zone-1
    name: www
    source:
      type: fixed
      value: 203.0.113.10
    proxied: true
    ttl: 120
  - zone_id: zone-2
    name: api
    source:
      type: public
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config == Config(
        token_env_var="CF_TOKEN",
        zones=[ZoneConfig(id="zone-1", name="example.com"), ZoneConfig(id="zone-2")],
        records=[
            RecordConfig(
                zone_id="zone-1",
                name="www",
                source=SourceConfig(type="fixed", value="203.0.113.10"),
                proxied=True,
                ttl=120,
            ),
            RecordConfig(zone_id="zone-2", name="api", source=SourceConfig(type="public")),
        ],
    )


def test_save_config_writes_yaml(tmp_path):
    config_path = tmp_path / "nested" / "config.yaml"
    config = Config(
        token_env_var="CF_TOKEN",
        zones=[ZoneConfig(id="zone-1", name="example.com")],
        records=[
            RecordConfig(
                zone_id="zone-1",
                name="www",
                source=SourceConfig(type="custom", command="get-ip"),
            )
        ],
    )

    save_config(config_path, config)

    assert config_path.read_text(encoding="utf-8") == (
        "token_env_var: CF_TOKEN\n"
        "zones:\n"
        "  - id: zone-1\n"
        "    name: example.com\n"
        "records:\n"
        "  - zone_id: zone-1\n"
        "    name: www\n"
        "    source:\n"
        "      type: custom\n"
        "      command: get-ip\n"
    )


@pytest.mark.parametrize(
    "contents,error",
    [
        ("zones: []\nrecords: []\n", "token_env_var is required"),
        ("token_env_var: CF_TOKEN\nrecords: []\n", "zones is required"),
        ("token_env_var: CF_TOKEN\nzones: []\n", "records is required"),
        (
            "token_env_var: CF_TOKEN\nzones:\n  - id: zone-1\nrecords:\n  - zone_id: missing\n    name: www\n    source:\n      type: public\n",
            "records[].zone_id not found: missing",
        ),
    ],
)
def test_load_config_rejects_missing_required_fields(tmp_path, contents, error):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(contents, encoding="utf-8")

    with pytest.raises(ConfigError, match=re.escape(error)):
        load_config(config_path)


def test_load_config_rejects_missing_source_fields(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """token_env_var: CF_TOKEN
zones:
  - id: zone-1
records:
  - zone_id: zone-1
    name: www
    source:
      type: fixed
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="source.value is required for fixed source"):
        load_config(config_path)
