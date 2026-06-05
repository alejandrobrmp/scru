from __future__ import annotations

from pathlib import Path
from typing import Callable

from .helpers import config_exists


def new() -> None:
    pass


def edit() -> None:
    pass


def main(
    *,
    config_path: Path | None = None,
    new_handler: Callable[[], None] = new,
    edit_handler: Callable[[], None] = edit,
) -> None:
    if config_exists(config_path):
        edit_handler()
        return

    new_handler()
