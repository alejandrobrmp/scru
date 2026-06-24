from __future__ import annotations

import json
import os
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class CloudflareClientError(RuntimeError):
    pass


class CloudflareClient:
    def __init__(self, token: str | None = None, *, base_url: str = "https://api.cloudflare.com/client/v4", timeout: float = 30.0):
        self.token = token or os.environ.get("CLOUDFLARE_API_TOKEN")
        if not self.token:
            raise CloudflareClientError("CLOUDFLARE_API_TOKEN is required")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_record(self, zone_id: str, name: str) -> Mapping[str, Any] | None:
        records = self.list_records(zone_id, name=name, record_type="A")
        return records[0] if records else None

    def get_zone_id(self, zone_name: str) -> str:
        zones = self.list_zones(zone_name)
        if not zones:
            raise CloudflareClientError(f"zone not found: {zone_name}")

        zone = zones[0]
        zone_id = zone.get("id")
        if not zone_id:
            raise CloudflareClientError(f"zone id missing for: {zone_name}")

        return str(zone_id)

    def list_zones(self, name: str | None = None) -> list[Mapping[str, Any]]:
        query: dict[str, str] = {"per_page": "1"}
        if name is not None:
            query["name"] = name

        result = self._request_json("GET", f"/zones?{urlencode(query)}")
        if result is None:
            return []
        if isinstance(result, list):
            return [zone for zone in result if isinstance(zone, Mapping)]
        raise CloudflareClientError("cloudflare response result was not a list")

    def list_all_zones(self) -> list[Mapping[str, Any]]:
        query: dict[str, str] = {"per_page": "50"}
        result = self._request_json("GET", f"/zones?{urlencode(query)}")
        if result is None:
            return []
        if isinstance(result, list):
            return [zone for zone in result if isinstance(zone, Mapping)]
        raise CloudflareClientError("cloudflare response result was not a list")

    def list_records(self, zone_id: str, *, name: str | None = None, record_type: str | None = "A") -> list[Mapping[str, Any]]:
        query: dict[str, str] = {"per_page": "1"}
        if name is not None:
            query["name"] = name
        if record_type is not None:
            query["type"] = record_type

        result = self._request_json("GET", f"/zones/{zone_id}/dns_records?{urlencode(query)}")
        if result is None:
            return []
        if isinstance(result, list):
            return [record for record in result if isinstance(record, Mapping)]
        raise CloudflareClientError("cloudflare response result was not a list")

    def list_all_records(self, zone_id: str) -> list[Mapping[str, Any]]:
        query: dict[str, str] = {"per_page": "50", "type": "A"}
        result = self._request_json("GET", f"/zones/{zone_id}/dns_records?{urlencode(query)}")
        if result is None:
            return []
        if isinstance(result, list):
            return [record for record in result if isinstance(record, Mapping)]
        raise CloudflareClientError("cloudflare response result was not a list")

    def create_record(
        self,
        zone_id: str,
        *,
        name: str,
        content: str,
        proxied: bool | None = None,
        ttl: int | None = None,
    ) -> Mapping[str, Any]:
        payload: dict[str, Any] = {"type": "A", "name": name, "content": content}
        if proxied is not None:
            payload["proxied"] = proxied
        if ttl is not None:
            payload["ttl"] = ttl

        result = self._request_json("POST", f"/zones/{zone_id}/dns_records", payload)
        return {} if result is None else result

    def update_record(
        self,
        zone_id: str,
        record_id: str,
        content: str,
        *,
        proxied: bool | None = None,
        ttl: int | None = None,
    ) -> None:
        payload: dict[str, Any] = {"content": content}
        if proxied is not None:
            payload["proxied"] = proxied
        if ttl is not None:
            payload["ttl"] = ttl

        self._request_json("PATCH", f"/zones/{zone_id}/dns_records/{record_id}", payload)

    def delete_record(self, zone_id: str, record_id: str) -> None:
        self._request_json("DELETE", f"/zones/{zone_id}/dns_records/{record_id}")

    def _request_json(self, method: str, path: str, payload: Mapping[str, Any] | None = None) -> Any:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method=method,
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload_data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise CloudflareClientError(self._message_from_http_error(exc)) from exc
        except URLError as exc:
            raise CloudflareClientError(f"cloudflare request failed: {exc.reason}") from exc

        if not isinstance(payload_data, dict):
            raise CloudflareClientError("cloudflare response was not a JSON object")

        if not payload_data.get("success", False):
            raise CloudflareClientError(self._message_from_payload(payload_data))

        return payload_data.get("result")

    def _message_from_http_error(self, exc: HTTPError) -> str:
        try:
            payload = json.loads(exc.read().decode("utf-8"))
        except Exception:
            return f"cloudflare request failed: HTTP {exc.code}"

        return self._message_from_payload(payload)

    def _message_from_payload(self, payload: Mapping[str, Any]) -> str:
        errors = payload.get("errors") or []
        if isinstance(errors, list) and errors:
            messages = []
            for error in errors:
                if isinstance(error, Mapping):
                    message = error.get("message") or error.get("error")
                    if message:
                        messages.append(str(message))
                else:
                    messages.append(str(error))
            if messages:
                return "; ".join(messages)

        messages = payload.get("messages") or []
        if isinstance(messages, list) and messages:
            return "; ".join(str(message) for message in messages)

        return "cloudflare request failed"
