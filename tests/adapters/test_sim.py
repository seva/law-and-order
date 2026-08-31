import asyncio
import json

import pytest

from law_and_order import Ruling
from law_and_order.adapters import PlatformAdapter
from law_and_order.adapters.base import render_ruling
from law_and_order.adapters.sim import SimAdapter


def make_adapter():
    published = []

    async def on_ruling(ruling: Ruling, text: str) -> None:
        published.append((ruling, text))

    return SimAdapter(on_ruling=on_ruling), published


def test_adapter_satisfies_platform_adapter_protocol():
    adapter, _ = make_adapter()
    assert isinstance(adapter, PlatformAdapter)


def test_ingest_produces_signal_from_sim_event():
    adapter, _ = make_adapter()
    raw = json.dumps({"dispute_key": "buyer|seller", "text": "demand a refund"})
    signal = asyncio.run(adapter.ingest(raw, source="hint"))
    assert signal.source == "sim:buyer|seller"
    assert signal.payload == "demand a refund"


def test_ingest_is_identity_free_by_construction():
    adapter, _ = make_adapter()
    raw = json.dumps({"dispute_key": "buyer|seller", "text": "demand a refund"})
    signal = asyncio.run(adapter.ingest(raw, source="hint"))
    assert "buyer" not in signal.payload
    assert "seller" not in signal.payload


def test_ingest_rejects_event_missing_fields():
    adapter, _ = make_adapter()
    with pytest.raises(ValueError):
        asyncio.run(adapter.ingest(json.dumps({"text": "no key"}), source="hint"))


def test_publish_emits_rendered_ruling():
    adapter, published = make_adapter()
    ruling = Ruling(digest="ef" * 32, action="order_refund", rule_id="R1")
    asyncio.run(adapter.publish(ruling))
    assert published == [(ruling, render_ruling(ruling))]


def test_adapter_is_immutable():
    import dataclasses

    adapter, _ = make_adapter()
    with pytest.raises(dataclasses.FrozenInstanceError):
        adapter.on_ruling = None
