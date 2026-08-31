from pathlib import Path

from law_and_order import BoundaryConstraints, RuleSet, Signal, StateMachine
from law_and_order.polity import adjudicate, adjudicate_appeals, load_transcript

RULESET_PATH = Path(__file__).resolve().parent.parent / "rulesets" / "v2.json"
TRANSCRIPT_PATH = Path(__file__).resolve().parent.parent / "docs" / "polity-001" / "transcript.jsonl"


def load_raw() -> str:
    return RULESET_PATH.read_text(encoding="utf-8")


def load_v2() -> RuleSet:
    return RuleSet.from_json(load_raw())


def load_transcript_statements():
    return load_transcript(TRANSCRIPT_PATH.read_text(encoding="utf-8"))


def test_from_json_round_trips_byte_identically():
    raw = load_raw()
    assert RuleSet.from_json(raw).canonical() == raw.strip()


def test_v2_passes_immune_system():
    ruleset = load_v2()
    boundaries = BoundaryConstraints()
    assert ruleset.rules
    assert all(boundaries.permits(rule.action) for rule in ruleset.rules)


def test_v2_ids_unique_and_ordered():
    ids = [rule.rule_id for rule in load_v2().rules]
    assert len(ids) == len(set(ids))
    assert ids == sorted(ids)


def test_v2_rulings_are_deterministic():
    first = StateMachine(load_v2()).step(Signal(source="guild:channel", payload="demanding a refund"))
    second = StateMachine(load_v2()).step(Signal(source="guild:channel", payload="demanding a refund"))
    assert first == second
    assert first.action == "order_refund"


def test_v2_refusal_does_not_order_refund():
    ruling = StateMachine(load_v2()).step(Signal(source="guild:channel", payload="I must decline the refund"))
    assert ruling.action != "order_refund"


def test_v2_contestation_reopens():
    ruling = StateMachine(load_v2()).step(Signal(source="guild:channel", payload="I dispute the refund ruling"))
    assert ruling.action == "reopen_arbitration"


def test_v2_stance_discrimination_on_polity_001():
    statements = load_transcript_statements()
    rulings = adjudicate(statements, load_v2(), "polity-001")
    by_key = {(s["round"], s["party"]): r for s, r in zip(statements, rulings)}
    for key in ((1, "claimant"), (2, "claimant"), (3, "claimant")):
        assert by_key[key].action == "order_refund"
    for key in ((1, "respondent"), (2, "respondent"), (3, "respondent")):
        assert by_key[key].action != "order_refund"


def test_v2_appellate_rehearing_is_replay_stable():
    statements = load_transcript_statements()
    ruleset = load_v2()
    rulings = adjudicate(statements, ruleset, "polity-001")
    first = adjudicate_appeals(statements, rulings, ruleset)
    second = adjudicate_appeals(statements, rulings, ruleset)
    assert first == second
    assert set(first) == {"respondent"}
