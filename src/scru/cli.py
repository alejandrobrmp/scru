from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

from .constants import CONFIG_PATH, MISSING_CONFIG_MESSAGE
from .helpers import config_exists
from .run_mode import main as run_mode_main
from .wizard import main as wizard_main

def main(
    argv: list[str] | None = None,
    *,
    config_path: Path | None = None,
    run_handler: Callable[[], None] = run_mode_main,
    wizard_handler: Callable[..., None] = wizard_main,
    output: Callable[[str], None] = print,
) -> None:
    args = sys.argv[1:] if argv is None else argv
    path = CONFIG_PATH if config_path is None else config_path

    if args == ["config"]:
        wizard_handler(config_path=path)
        return

    if args:
        raise SystemExit("usage: scru [config]")

    if config_exists(path):
        run_handler()
        return

    output(MISSING_CONFIG_MESSAGE)
    wizard_handler(config_path=path)
