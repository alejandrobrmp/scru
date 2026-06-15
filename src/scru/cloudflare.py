from __future__ import annotations

from typing import Any, Mapping


class CloudflareClient:
    def get_record(self, zone_id: str, name: str) -> Mapping[str, Any] | None:
        raise NotImplementedError("cloudflare client is not implemented yet")

    def update_record(
        self,
        zone_id: str,
        record_id: str,
        content: str,
        *,
        proxied: bool | None = None,
        ttl: int | None = None,
    ) -> None:
        raise NotImplementedError("cloudflare client is not implemented yet")
