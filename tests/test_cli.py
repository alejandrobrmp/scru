from pathlib import Path

from scru.cli import main
from scru.wizard import main as wizard_main


def test_main_routes_to_update_when_config_exists(tmp_path, capsys):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("token: example\n", encoding="utf-8")
    calls = []

    main(
        [],
        config_path=config_path,
        run_handler=lambda: calls.append("run"),
        wizard_handler=lambda **kwargs: calls.append(("wizard", kwargs)),
    )

    assert calls == ["run"]
    assert capsys.readouterr().out == ""


def test_main_routes_missing_config_to_new_wizard(tmp_path, capsys):
    config_path = tmp_path / "config.yaml"
    calls = []

    main(
        [],
        config_path=config_path,
        run_handler=lambda: calls.append("run"),
        wizard_handler=lambda **kwargs: calls.append(("wizard", kwargs)),
    )

    assert calls == [("wizard", {"config_path": config_path})]
    assert capsys.readouterr().out == "No config file found, create one first.\n"


def test_main_routes_config_command_to_wizard_main(tmp_path):
    config_path = tmp_path / "config.yaml"
    calls = []

    main(
        ["config"],
        config_path=config_path,
        run_handler=lambda: calls.append("run"),
        wizard_handler=lambda **kwargs: calls.append(("wizard", kwargs)),
    )

    assert calls == [("wizard", {"config_path": config_path})]


def test_wizard_main_routes_to_edit_when_config_exists(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("token: example\n", encoding="utf-8")
    calls = []

    wizard_main(
        config_path=config_path,
        new_handler=lambda: calls.append("new"),
        edit_handler=lambda: calls.append("edit"),
    )

    assert calls == ["edit"]


def test_wizard_main_routes_to_new_when_config_missing(tmp_path):
    config_path = tmp_path / "config.yaml"
    calls = []

    wizard_main(
        config_path=config_path,
        new_handler=lambda: calls.append("new"),
        edit_handler=lambda: calls.append("edit"),
    )

    assert calls == ["new"]
