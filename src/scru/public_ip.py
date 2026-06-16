from __future__ import annotations

import ipaddress
import os
from typing import Any, Callable
from urllib.request import urlopen

DEFAULT_PUBLIC_IP_URL = "https://api.ipify.org"
PUBLIC_IP_URL_ENV_VAR = "SCRU_PUBLIC_IP_URL"


def fetch_public_ipv4(
    *,
    opener: Callable[[str], Any] = urlopen,
    url: str | None = None,
) -> str:
    target_url = url or os.environ.get(PUBLIC_IP_URL_ENV_VAR, DEFAULT_PUBLIC_IP_URL)

    with opener(target_url) as response:
        text = response.read().decode("utf-8").strip()

    if not text:
        raise ValueError("public IP response is empty")

    address = ipaddress.ip_address(text)
    if address.version != 4:
        raise ValueError("public IP response must be an IPv4 address")

    return str(address)
