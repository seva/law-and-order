import hashlib
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from law_and_order import RuleSet
from law_and_order.adjudication import SettlementService
from law_and_order.pairing import RECENCY_WINDOW, PairEvent, PairingTracker

RULESET_PATH = Path(__file__).resolve().parents[1] / "rulesets" / "v1.json"


def tracker(prefix: str = "sim") -> PairingTracker:
    return PairingTracker(source_prefix=prefix)


def event(channel: str, speaker: str, text: str, referenced: str | None = None) -> PairEvent:
    return PairEvent(channel=channel, speaker=speaker, referenced_speaker=referenced, text=text)


def test_event_descriptor_is_immutable():
    e = event("c1", "a", "text")
    with pytest.raises(FrozenInstanceError):
        e.speaker = "b"


def test_fresh_channel_has_no_counterpart():
    t = tracker()
    assert t.resolve(event("c1", "a", "first words")) is None


def test_adjacency_pairs_consecutive_speakers():
    t = tracker()
    assert t.resolve(event("c1", "a", "first words")) is None
    assert t.resolve(event("c1", "b", "reply words")) == "a"


def test_reference_takes_priority_over_recency():
    t = tracker()
    for speaker in ("a", "b", "c"):
        t.resolve(event("c1", speaker, f"{speaker} speaks"))
    assert t.resolve(event("c1", "d", "answering a", referenced="a")) == "a"


def test_self_reference_is_ignored_and_falls_to_adjacency():
    t = tracker()
    t.resolve(event("c1", "a", "first words"))
    assert t.resolve(event("c1", "b", "self reply", referenced="b")) == "a"


def test_recency_excludes_the_speaker():
    t = tracker()
    t.resolve(event("c1", "a", "one"))
    t.resolve(event("c1", "b", "two"))
    assert t.resolve(event("c1", "a", "three")) == "b"


def test_channels_are_isolated():
    t = tracker()
    t.resolve(event("c1", "a", "channel one"))
    assert t.resolve(event("c2", "b", "channel two")) is None


def test_recency_window_is_bounded():
    t = tracker()
    for _ in range(RECENCY_WINDOW + 1):
        t.resolve(event("c1", "a", "flooding"))
    assert t.resolve(event("c1", "a", "still flooding")) is None
    assert t.resolve(event("c1", "b", "someone new")) == "a"


def test_recency_window_value_is_legislated():
    assert RECENCY_WINDOW == 8


def test_evicted_speakers_do_not_resolve():
    t = tracker()
    t.resolve(event("c1", "a", "spoken once"))
    for _ in range(RECENCY_WINDOW):
        t.resolve(event("c1", "b", "flooding"))
    assert t.resolve(event("c1", "b", "after eviction")) is None


def test_resolution_is_content_blind():
    plain = tracker()
    poisoned = tracker()
    structure = (("a", None), ("b", None), ("a", "b"), ("c", "a"), ("b", None))
    plain_results = [
        plain.resolve(event("c1", speaker, "neutral text", referenced=ref))
        for speaker, ref in structure
    ]
    poisoned_results = [
        poisoned.resolve(event("c1", speaker, "zzz neutral text zzz", referenced=ref))
        for speaker, ref in structure
    ]
    assert plain_results == poisoned_results


def test_reference_resolutions_feed_recency():
    t = tracker()
    for speaker in ("a", "b", "c"):
        t.resolve(event("c1", speaker, f"{speaker} speaks"))
    assert t.resolve(event("c1", "d", "answering a", referenced="a")) == "a"
    assert t.resolve(event("c1", "e", "next in channel")) == "d"


def test_reference_bypasses_the_recency_window():
    t = tracker()
    assert t.resolve(event("c1", "d", "answering a ghost", referenced="ghost")) == "ghost"


def test_replay_is_deterministic():
    events = (
        event("c1", "a", "one"),
        event("c1", "b", "two"),
        event("c2", "x", "three"),
        event("c1", "a", "four", referenced="b"),
        event("c1", "c", "five"),
    )
    first = tracker()
    second = tracker()
    assert [first.resolve(e) for e in events] == [second.resolve(e) for e in events]


def test_dispute_key_ties_to_the_settlement_service_digest():
    ruleset = RuleSet.from_json(RULESET_PATH.read_text(encoding="utf-8"))
    t = tracker(prefix="sim")
    service = SettlementService(ruleset, source="sim")
    text = "demand a refund for the goods"
    service.note("denier", "claimant", "I refuse to pay anything further")
    observation = service.observe("claimant", "denier", text)
    key = t.dispute_key("claimant", "denier")
    assert key == "sim:claimant|denier"
    assert key == t.dispute_key("denier", "claimant")
    expected = hashlib.sha256(f"{key}:{text}".encode("utf-8")).hexdigest()
    assert observation.rulings[0].digest == expected
