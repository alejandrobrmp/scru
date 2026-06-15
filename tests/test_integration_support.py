from pathlib import Path

from tests.integration.support import build_run_env, expand_placeholders, load_case, load_env_file


def test_load_env_file_parses_comments_and_quotes(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        """# comment
KEY=value
QUOTED=\"hello world\"
SINGLE='ok'
export EXPORTED=done
""",
        encoding="utf-8",
    )

    assert load_env_file(env_file) == {
        "KEY": "value",
        "QUOTED": "hello world",
        "SINGLE": "ok",
        "EXPORTED": "done",
    }


def test_expand_placeholders_recurses_through_nested_values():
    env = {"ZONE": "zone-1", "NAME": "www", "IP": "203.0.113.10"}
    data = {
        "config_yaml": "records:\n  - zone_id: ${ZONE}\n    name: $NAME\n    source:\n      type: fixed\n      value: ${IP}\n",
        "items": ["${ZONE}", {"record": "$NAME"}],
    }

    assert expand_placeholders(data, env) == {
        "config_yaml": "records:\n  - zone_id: zone-1\n    name: www\n    source:\n      type: fixed\n      value: 203.0.113.10\n",
        "items": ["zone-1", {"record": "www"}],
    }


def test_load_case_expands_yaml_fields(tmp_path):
    case_file = tmp_path / "case.yaml"
    case_file.write_text(
        """setup:
  create_records:
    - zone_id: ${ZONE}
      name: ${NAME}
      content: ${IP}
config_yaml: |
  records:
    - zone_id: ${ZONE}
      name: ${NAME}
      source:
        type: fixed
        value: ${IP}
""",
        encoding="utf-8",
    )

    case = load_case(case_file, {"ZONE": "zone-1", "NAME": "www", "IP": "203.0.113.10"})

    assert case["setup"]["create_records"][0]["name"] == "www"
    assert case["config_yaml"].startswith("records:\n  - zone_id: zone-1")


def test_build_run_env_prepends_src_to_pythonpath(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    home = tmp_path / "home"

    env = build_run_env(repo_root, {"EXTRA": "1"}, home)

    assert env["HOME"] == str(home)
    assert env["USERPROFILE"] == str(home)
    assert env["PYTHONPATH"].startswith(str(repo_root / "src"))
