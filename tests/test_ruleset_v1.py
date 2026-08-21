from pathlib import Path

import pytest

from law_and_order import BoundaryConstraints, RuleSet, Signal, StateMachine

RULESET_PATH = Path(__file__).resolve().parent.parent / "rulesets" / "v1.json"


def load_raw() -> str:
    return RULESET_PATH.read_text(encoding="utf-8")


def test_from_json_rejects_non_array_artifact():
    with pytest.raises(ValueError):
        RuleSet.from_json('{"rule_id": "R1"}')


def test_ruleset_file_is_canonical():
    raw = load_raw()
    ruleset = RuleSet.from_json(raw)
    assert ruleset.canonical() == raw.strip()


def test_ruleset_passes_immune_system():
    ruleset = RuleSet.from_json(load_raw())
    boundaries = BoundaryConstraints()
    assert ruleset.rules
    assert all(boundaries.permits(rule.action) for rule in ruleset.rules)


def test_ruleset_ids_unique_and_ordered():
    ruleset = RuleSet.from_json(load_raw())
    ids = [rule.rule_id for rule in ruleset.rules]
    assert len(ids) == len(set(ids))
    assert ids == sorted(ids)


def test_v1_rulings_are_deterministic():
    ruleset = RuleSet.from_json(load_raw())
    first = StateMachine(ruleset).step(Signal(source="guild:channel", payload="demanding refund"))
    second = StateMachine(ruleset).step(Signal(source="guild:channel", payload="demanding refund"))
    assert first == second
    assert first.action == "order_refund"


def test_v1_breach_routes_to_arbitration():
    ruleset = RuleSet.from_json(load_raw())
    ruling = StateMachine(ruleset).step(Signal(source="guild:channel", payload="this is a breach of the agreement"))
    assert ruling.action == "escalate_to_arbitration"


def test_v1_threat_escalates_to_human():
    ruleset = RuleSet.from_json(load_raw())
    ruling = StateMachine(ruleset).step(Signal(source="guild:channel", payload="threat against the moderator"))
    assert ruling.action == "escalate_to_human"


def test_v1_appeal_reopens_arbitration():
    ruleset = RuleSet.from_json(load_raw())
    ruling = StateMachine(ruleset).step(Signal(source="guild:channel", payload="appeal the ruling"))
    assert ruling.action == "reopen_arbitration"
