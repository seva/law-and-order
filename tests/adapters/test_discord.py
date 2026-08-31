import asyncio
import dataclasses
import json

import pytest

from law_and_order import Ruling
from law_and_order.adapters import PlatformAdapter
from law_and_order.adapters.discord import DiscordAdapter, render_ruling

MESSAGE_CREATE = {
    "op": 0,
    "t": "MESSAGE_CREATE",
    "s": 42,
    "d": {
        "id": "1211768591494418512",
        "channel_id": "1211768590999494707",
        "guild_id": "1211768590499494706",
        "author": {"id": "1211768591000000001", "username": "node-7"},
        "content": "demand a refund for order 42",
    },
}

DM_MESSAGE_CREATE = {
    "op": 0,
    "t": "MESSAGE_CREATE",
    "s": 43,
    "d": {
        "id": "1211768591494418513",
        "channel_id": "1211768590999494708",
        "guild_id": None,
        "author": {"id": "1211768591000000002", "username": "node-8"},
        "content": "requesting refund",
    },
}


def make_adapter():
    sent = []

    async def send(channel_id: int, text: str) -> None:
        sent.append((channel_id, text))

    return DiscordAdapter(ruling_channel_id=999, send=send), sent


def test_adapter_satisfies_platform_adapter_protocol():
    adapter, _ = make_adapter()
    assert isinstance(adapter, PlatformAdapter)


def test_ingest_message_create_produces_signal():
    adapter, _ = make_adapter()
    signal = asyncio.run(adapter.ingest(json.dumps(MESSAGE_CREATE), source="hint"))
    assert signal.source == "1211768590499494706:1211768590999494707"
    assert signal.payload == "demand a refund for order 42"


def test_ingest_dm_uses_dm_source_prefix():
    adapter, _ = make_adapter()
    signal = asyncio.run(adapter.ingest(json.dumps(DM_MESSAGE_CREATE), source="hint"))
    assert signal.source == "dm:1211768590999494708"


def test_ingest_is_identity_free():
    adapter, _ = make_adapter()
    signal = asyncio.run(adapter.ingest(json.dumps(MESSAGE_CREATE), source="hint"))
    author_id = MESSAGE_CREATE["d"]["author"]["id"]
    assert author_id not in signal.source
    assert author_id not in signal.payload


def test_ingest_is_deterministic():
    adapter, _ = make_adapter()
    raw = json.dumps(MESSAGE_CREATE)
    first = asyncio.run(adapter.ingest(raw, source="hint"))
    second = asyncio.run(adapter.ingest(raw, source="hint"))
    assert first == second


def test_ingest_rejects_non_message_create():
    adapter, _ = make_adapter()
    raw = json.dumps({"op": 0, "t": "MESSAGE_DELETE", "d": {"id": "1"}})
    with pytest.raises(ValueError):
        asyncio.run(adapter.ingest(raw, source="hint"))


def test_ingest_rejects_event_missing_required_fields():
    adapter, _ = make_adapter()
    raw = json.dumps({"op": 0, "t": "MESSAGE_CREATE", "d": {"id": "1"}})
    with pytest.raises(ValueError):
        asyncio.run(adapter.ingest(raw, source="hint"))


def test_ingest_rejects_envelope_without_event_data():
    adapter, _ = make_adapter()
    raw = json.dumps({"op": 0, "t": "MESSAGE_CREATE", "d": "garbage"})
    with pytest.raises(ValueError):
        asyncio.run(adapter.ingest(raw, source="hint"))


def test_publish_renders_ruling_to_arbitration_channel():
    adapter, sent = make_adapter()
    ruling = Ruling(digest="ab" * 32, action="order_refund", rule_id="R1")
    asyncio.run(adapter.publish(ruling))
    assert sent == [(999, render_ruling(ruling))]
    assert "[R1]" in sent[0][1]
    assert "order_refund" in sent[0][1]
    assert "ab" * 8 in sent[0][1]


def test_publish_is_deterministic():
    ruling = Ruling(digest="cd" * 32, action="drop", rule_id="R0")
    assert render_ruling(ruling) == render_ruling(ruling)


def test_adapter_is_immutable():
    adapter, _ = make_adapter()
    with pytest.raises(dataclasses.FrozenInstanceError):
        adapter.ruling_channel_id = 1
