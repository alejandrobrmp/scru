from pathlib import Path

from .constants import CONFIG_PATH


def config_exists(config_path: Path | None = None) -> bool:
    path = CONFIG_PATH if config_path is None else config_path
    return path.exists()
