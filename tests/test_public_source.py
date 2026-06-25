from __future__ import annotations

from scru.update import resolve_public_source_ipv4


class FakeResponse:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body


def test_resolve_public_source_ipv4_returns_ipv4_text(monkeypatch):
    def opener(url, **kwargs):
        assert url == "https://api.ipify.org"
        return FakeResponse(b"198.51.100.7\n")

    monkeypatch.setattr("scru.update.urlopen", opener)

    assert resolve_public_source_ipv4() == "198.51.100.7"


def test_resolve_public_source_ipv4_rejects_empty_response(monkeypatch):
    def opener(url, **kwargs):
        return FakeResponse(b"   \n")

    monkeypatch.setattr("scru.update.urlopen", opener)

    try:
        resolve_public_source_ipv4()
    except ValueError as exc:
        assert str(exc) == "public IP response is empty"
    else:
        raise AssertionError("expected ValueError")


def test_resolve_public_source_ipv4_rejects_non_ipv4_response(monkeypatch):
    def opener(url, **kwargs):
        return FakeResponse(b"2001:db8::1")

    monkeypatch.setattr("scru.update.urlopen", opener)

    try:
        resolve_public_source_ipv4()
    except ValueError as exc:
        assert str(exc) == "public IP response must be an IPv4 address"
    else:
        raise AssertionError("expected ValueError")
