from __future__ import annotations

from scru.public_ip import fetch_public_ipv4


class FakeResponse:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body


def test_fetch_public_ipv4_returns_ipv4_text():
    def opener(url):
        assert url == "https://example.invalid/ip"
        return FakeResponse(b"198.51.100.7\n")

    assert fetch_public_ipv4(opener=opener, url="https://example.invalid/ip") == "198.51.100.7"


def test_fetch_public_ipv4_rejects_empty_response():
    def opener(url):
        return FakeResponse(b"   \n")

    try:
        fetch_public_ipv4(opener=opener, url="https://example.invalid/ip")
    except ValueError as exc:
        assert str(exc) == "public IP response is empty"
    else:
        raise AssertionError("expected ValueError")


def test_fetch_public_ipv4_rejects_non_ipv4_response():
    def opener(url):
        return FakeResponse(b"2001:db8::1")

    try:
        fetch_public_ipv4(opener=opener, url="https://example.invalid/ip")
    except ValueError as exc:
        assert str(exc) == "public IP response must be an IPv4 address"
    else:
        raise AssertionError("expected ValueError")
