from pathlib import Path


CONFIG_PATH = Path.home() / ".config" / "scru" / "config.yaml"
MISSING_CONFIG_MESSAGE = "No config file found, create one first."
CLOUDFLARE_API_TOKEN_ENV_VAR = "CLOUDFLARE_API_TOKEN"
