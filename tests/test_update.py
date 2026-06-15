from scru.config import Config, RecordConfig, SourceConfig
from scru.update import main, process_record, resolve_source_ipv4


class RecordingClient:
    def __init__(self, current_record=None):
        self.current_record = current_record
        self.calls = []

    def get_record(self, zone_id, name):
        self.calls.append(("get_record", zone_id, name))
        return self.current_record

    def update_record(self, zone_id, record_id, content, *, proxied=None, ttl=None):
        self.calls.append(("update_record", zone_id, record_id, content, proxied, ttl))


def test_process_record_skips_unchanged_record():
    record = RecordConfig(
        zone_id="zone-1",
        name="www",
        source=SourceConfig(type="fixed", value="203.0.113.10"),
    )
    client = RecordingClient(current_record={"id": "record-1", "content": "203.0.113.10"})
    order = []

    result = process_record(
        record,
        source_resolver=lambda source: order.append(("source", source.type)) or "203.0.113.10",
        client=client,
    )

    assert result == "www: skipped (unchanged)"
    assert order == [("source", "fixed")]
    assert client.calls == [("get_record", "zone-1", "www")]


def test_process_record_updates_changed_record_after_resolving_source():
    record = RecordConfig(
        zone_id="zone-1",
        name="www",
        source=SourceConfig(type="fixed", value="203.0.113.10"),
        proxied=True,
        ttl=120,
    )
    client = RecordingClient(current_record={"id": "record-1", "content": "203.0.113.1"})
    order = []

    result = process_record(
        record,
        source_resolver=lambda source: order.append(("source", source.type)) or "203.0.113.10",
        client=client,
    )

    assert result == "www: updated"
    assert order == [("source", "fixed")]
    assert client.calls == [
        ("get_record", "zone-1", "www"),
        ("update_record", "zone-1", "record-1", "203.0.113.10", True, 120),
    ]


def test_process_record_failure_returns_single_clear_result():
    record = RecordConfig(
        zone_id="zone-1",
        name="www",
        source=SourceConfig(type="fixed", value="203.0.113.10"),
    )

    class BrokenClient:
        def get_record(self, zone_id, name):
            raise RuntimeError("boom")

        def update_record(self, zone_id, record_id, content, *, proxied=None, ttl=None):
            raise AssertionError("should not update")

    result = process_record(record, source_resolver=lambda source: "203.0.113.10", client=BrokenClient())

    assert result == "www: failed (boom)"


def test_process_record_rejects_invalid_fixed_source_before_cloudflare_calls():
    record = RecordConfig(
        zone_id="zone-1",
        name="www",
        source=SourceConfig(type="fixed", value="not-an-ip"),
    )

    class RecordingClient:
        def __init__(self):
            self.calls = []

        def get_record(self, zone_id, name):
            self.calls.append(("get_record", zone_id, name))
            raise AssertionError("should not reach Cloudflare")

        def update_record(self, zone_id, record_id, content, *, proxied=None, ttl=None):
            self.calls.append(("update_record", zone_id, record_id, content, proxied, ttl))
            raise AssertionError("should not reach Cloudflare")

    client = RecordingClient()

    result = process_record(record, source_resolver=resolve_source_ipv4, client=client)

    assert result == "www: failed ('not-an-ip' does not appear to be an IPv4 or IPv6 address)"
    assert client.calls == []


def test_resolve_source_ipv4_returns_fixed_ipv4():
    source = SourceConfig(type="fixed", value="203.0.113.10")

    assert resolve_source_ipv4(source) == "203.0.113.10"


def test_resolve_source_ipv4_rejects_invalid_fixed_ipv4():
    source = SourceConfig(type="fixed", value="not-an-ip")

    try:
        resolve_source_ipv4(source)
    except ValueError as exc:
        assert str(exc) == "'not-an-ip' does not appear to be an IPv4 or IPv6 address"
    else:
        raise AssertionError("expected ValueError")


def test_resolve_source_ipv4_rejects_unsupported_source_types():
    source = SourceConfig(type="public")

    try:
        resolve_source_ipv4(source)
    except ValueError as exc:
        assert str(exc) == "unsupported source type: public"
    else:
        raise AssertionError("expected ValueError")


def test_main_processes_single_record_and_prints_result():
    record = RecordConfig(
        zone_id="zone-1",
        name="www",
        source=SourceConfig(type="fixed", value="203.0.113.10"),
    )
    config = Config(records=[record])
    lines = []
    client = RecordingClient(current_record={"id": "record-1", "content": "203.0.113.1"})

    main(
        config_loader=lambda path: config,
        source_resolver=lambda source: "203.0.113.10",
        client=client,
        output=lines.append,
    )

    assert lines == ["www: updated"]


def test_main_rejects_multiple_records():
    config = Config(
        records=[
            RecordConfig(
                zone_id="zone-1",
                name="www",
                source=SourceConfig(type="fixed", value="203.0.113.10"),
            ),
            RecordConfig(
                zone_id="zone-2",
                name="api",
                source=SourceConfig(type="fixed", value="203.0.113.11"),
            ),
        ]
    )
    lines = []

    main(
        config_loader=lambda path: config,
        source_resolver=lambda source: "203.0.113.10",
        client=RecordingClient(),
        output=lines.append,
    )

    assert lines == ["config: failed (expected exactly one record)"]
