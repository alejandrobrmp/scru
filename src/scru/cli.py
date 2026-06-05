from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

from .constants import CONFIG_PATH, MISSING_CONFIG_MESSAGE
from .run_mode import main as run_mode_main
from .wizard import edit as wizard_edit
from .wizard import new as wizard_new

def main(
    argv: list[str] | None = None,
    *,
    config_path: Path | None = None,
    run_handler: Callable[[], None] = run_mode_main,
    new_wizard_handler: Callable[[], None] = wizard_new,
    edit_wizard_handler: Callable[[], None] = wizard_edit,
    output: Callable[[str], None] = print,
) -> None:
    args = sys.argv[1:] if argv is None else argv
    path = CONFIG_PATH if config_path is None else config_path

    if args == ["config"]:
        edit_wizard_handler()
        return

    if args:
        raise SystemExit("usage: scru [config]")

    if path.exists():
        run_handler()
        return

    output(MISSING_CONFIG_MESSAGE)
    new_wizard_handler()
