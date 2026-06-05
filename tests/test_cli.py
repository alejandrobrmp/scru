from pathlib import Path

from scru.cli import main


def test_main_routes_to_run_mode_when_config_exists(tmp_path, capsys):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("token: example\n", encoding="utf-8")
    calls = []

    main(
        [],
        config_path=config_path,
        run_handler=lambda: calls.append("run"),
        new_wizard_handler=lambda: calls.append("new"),
        edit_wizard_handler=lambda: calls.append("edit"),
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
        new_wizard_handler=lambda: calls.append("new"),
        edit_wizard_handler=lambda: calls.append("edit"),
    )

    assert calls == ["new"]
    assert capsys.readouterr().out == "No config file found, create one first.\n"


def test_main_routes_config_command_to_edit_wizard(tmp_path):
    config_path = tmp_path / "config.yaml"
    calls = []

    main(
        ["config"],
        config_path=config_path,
        run_handler=lambda: calls.append("run"),
        new_wizard_handler=lambda: calls.append("new"),
        edit_wizard_handler=lambda: calls.append("edit"),
    )

    assert calls == ["edit"]
