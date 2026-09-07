import hashlib
from pathlib import Path

import pytest

from law_and_order import RuleSet
from law_and_order.adjudication import Observation, SettlementService

RULESET_PATH = Path(__file__).resolve().parents[1] / "rulesets" / "v1.json"


def load_ruleset() -> RuleSet:
    return RuleSet.from_json(RULESET_PATH.read_text(encoding="utf-8"))


def service() -> SettlementService:
    return SettlementService(load_ruleset(), source="sim")


def test_unripe_observation_emits_nothing():
    s = service()
    observation = s.observe("claimant", "denier", "demand a refund for the goods")
    assert observation == Observation(rulings=(), settled=False)
    assert not s.is_settled("claimant", "denier")
    assert not s.is_settled("denier", "claimant")


def test_matched_claim_settles_through_appellate_affirm():
    s = service()
    assert s.observe("denier", "claimant", "I refuse to pay anything further").rulings == ()
    observation = s.observe("claimant", "denier", "demand a refund for the goods")
    assert [ruling.action for ruling in observation.rulings] == ["order_refund", "affirm"]
    assert [ruling.rule_id for ruling in observation.rulings] == ["R1", "R1"]
    assert observation.settled
    assert s.is_settled("claimant", "denier")


def test_settlement_is_res_judicata():
    s = service()
    s.observe("denier", "claimant", "I refuse to pay anything further")
    s.observe("claimant", "denier", "demand a refund for the goods")
    later = s.observe("denier", "claimant", "demand a refund again")
    assert later == Observation(rulings=(), settled=True)


def test_unfavored_ruling_rejects_and_persists():
    s = service()
    s.observe("alpha", "beta", "gamma delta epsilon")
    observation = s.observe("beta", "alpha", "this is a breach of nothing we signed")
    assert [ruling.action for ruling in observation.rulings] == ["escalate_to_arbitration"]
    assert not observation.settled
    assert not s.is_settled("alpha", "beta")


def test_unmatched_and_inert_observations_emit_nothing():
    s = service()
    assert s.observe("alpha", "beta", "gamma delta epsilon") == Observation((), False)
    assert s.observe("beta", "alpha", "you are pathetic") == Observation((), False)
    assert s.observe("alpha", "beta", "zeta eta theta") == Observation((), False)


def test_replay_is_deterministic():
    events = (
        ("denier", "claimant", "I refuse to pay anything further"),
        ("claimant", "denier", "demand a refund for the goods"),
    )
    first = service()
    second = service()
    first_observations = [first.observe(*event) for event in events]
    second_observations = [second.observe(*event) for event in events]
    assert first_observations == second_observations
    assert first_observations[-1].settled


def test_ruling_digest_follows_the_adapter_source_convention():
    s = service()
    s.observe("denier", "claimant", "I refuse to pay anything further")
    text = "demand a refund for the goods"
    observation = s.observe("claimant", "denier", text)
    expected = hashlib.sha256(f"sim:claimant|denier:{text}".encode("utf-8")).hexdigest()
    assert observation.rulings[0].digest == expected


def test_self_pair_is_rejected():
    s = service()
    with pytest.raises(ValueError):
        s.observe("alpha", "alpha", "demand a refund for the goods")


def test_note_feeds_dispute_state_without_adjudicating():
    s = service()
    assert s.note("denier", "claimant", "I refuse to pay anything further") is None
    assert s.note("claimant", "denier", "demand a refund for the goods") is None
    assert not s.is_settled("claimant", "denier")
    observation = s.observe("denier", "claimant", "demand a refund for the goods")
    assert [ruling.action for ruling in observation.rulings] == ["order_refund", "affirm"]
    assert observation.settled


def test_note_rejects_self_pairs():
    s = service()
    with pytest.raises(ValueError):
        s.note("alpha", "alpha", "demand a refund for the goods")


def test_service_signal_matches_adapter_ingest():
    import asyncio
    import json

    from law_and_order.adapters.sim import SimAdapter

    captured = []

    async def on_ruling(ruling, text):
        captured.append(ruling)

    adapter = SimAdapter(on_ruling=on_ruling)
    raw = json.dumps({"dispute_key": "claimant|denier", "text": "demand a refund for the goods"})
    signal = asyncio.run(adapter.ingest(raw, source="sim"))

    s = service()
    s.note("denier", "claimant", "I refuse to pay anything further")
    observation = s.observe("claimant", "denier", "demand a refund for the goods")
    assert observation.rulings[0].digest == signal.digest
