import pytest

from scru.config import Config, ConfigError, RecordConfig, SourceConfig, load_config, save_config


def test_load_config_parses_records(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """records:
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

    assert load_config(config_path) == Config(
        records=[
            RecordConfig(
                zone_id="zone-1",
                name="www",
                source=SourceConfig(type="fixed", value="203.0.113.10"),
                proxied=True,
                ttl=120,
            ),
            RecordConfig(zone_id="zone-2", name="api", source=SourceConfig(type="public")),
        ]
    )


def test_save_config_writes_yaml(tmp_path):
    config_path = tmp_path / "nested" / "config.yaml"
    config = Config(
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
        "records:\n"
        "  - zone_id: zone-1\n"
        "    name: www\n"
        "    source:\n"
        "      type: custom\n"
        "      command: get-ip\n"
    )


def test_load_config_accepts_empty_records(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("records: []\n", encoding="utf-8")

    assert load_config(config_path) == Config(records=[])


def test_load_config_rejects_missing_record_zone_id(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """records:
  - name: www
    source:
      type: public
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match=r"records\[\]\.zone_id is required"):
        load_config(config_path)


def test_load_config_rejects_missing_source_fields(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """records:
  - zone_id: zone-1
    name: www
    source:
      type: fixed
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="source.value is required for fixed source"):
        load_config(config_path)
