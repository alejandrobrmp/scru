from types import SimpleNamespace
import subprocess

import pytest

from scru.config import SourceConfig
from scru.update import resolve_custom_source_ipv4


def test_resolve_custom_source_ipv4_trims_stdout_and_uses_timeout(monkeypatch):
    recorded = {}

    def fake_run(command, *, capture_output, text, timeout, check):
        recorded["command"] = command
        recorded["capture_output"] = capture_output
        recorded["text"] = text
        recorded["timeout"] = timeout
        recorded["check"] = check
        return SimpleNamespace(returncode=0, stdout=" 198.51.100.7\r\n")

    monkeypatch.setattr("scru.update.subprocess.run", fake_run)

    source = SourceConfig(type="custom", command='get-ip --4')

    assert resolve_custom_source_ipv4(source) == "198.51.100.7"
    assert recorded == {
        "command": ["get-ip", "--4"],
        "capture_output": True,
        "text": True,
        "timeout": 10,
        "check": False,
    }


def test_resolve_custom_source_ipv4_rejects_invalid_stdout(monkeypatch):
    def fake_run(command, *, capture_output, text, timeout, check):
        return SimpleNamespace(returncode=0, stdout="198.51.100.7\n203.0.113.8\n")

    monkeypatch.setattr("scru.update.subprocess.run", fake_run)

    source = SourceConfig(type="custom", command='get-ip --4')

    with pytest.raises(ValueError, match="custom source command must output exactly one IPv4 address"):
        resolve_custom_source_ipv4(source)


def test_resolve_custom_source_ipv4_rejects_nonzero_exit(monkeypatch):
    def fake_run(command, *, capture_output, text, timeout, check):
        return SimpleNamespace(returncode=2, stdout="198.51.100.7\n")

    monkeypatch.setattr("scru.update.subprocess.run", fake_run)

    source = SourceConfig(type="custom", command='get-ip --4')

    with pytest.raises(ValueError, match="custom source command failed with exit code 2"):
        resolve_custom_source_ipv4(source)


def test_resolve_custom_source_ipv4_rejects_timeout(monkeypatch):
    recorded = {}

    def fake_run(command, *, capture_output, text, timeout, check):
        recorded["timeout"] = timeout
        raise subprocess.TimeoutExpired(cmd=command, timeout=timeout)

    monkeypatch.setattr("scru.update.subprocess.run", fake_run)

    source = SourceConfig(type="custom", command='get-ip --4')

    with pytest.raises(ValueError, match="custom source command timed out after 10 seconds"):
        resolve_custom_source_ipv4(source)

    assert recorded["timeout"] == 10
