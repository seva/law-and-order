import json
import os
import subprocess
import sys
from pathlib import Path

from law_and_order import RuleSet, Ruling
from law_and_order.polity import (
    adjudicate,
    adjudicate_appeals,
    analyze,
    final_settlement,
    load_transcript,
    settlement_signals,
)

RULESET_PATH = Path(__file__).resolve().parents[1] / "rulesets" / "v1.json"
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "adjudicate_transcript.py"


def load_ruleset() -> RuleSet:
    return RuleSet.from_json(RULESET_PATH.read_text(encoding="utf-8"))


def test_load_transcript_parses_jsonl():
    raw = (
        '{"round":1,"party":"claimant","text":"demand a refund"}\n'
        "\n"
        '{"round":1,"party":"respondent","text":"refuse"}\n'
    )
    statements = load_transcript(raw)
    assert len(statements) == 2
    assert statements[0]["party"] == "claimant"


def test_adjudicate_is_deterministic():
    statements = ({"round": 1, "party": "claimant", "text": "demand a refund"},)
    first = adjudicate(statements, load_ruleset(), "001")
    second = adjudicate(statements, load_ruleset(), "001")
    assert first == second
    assert first[0].action == "order_refund"


def test_adjudicate_drops_unvalued_and_routes_neutral():
    statements = (
        {"round": 1, "party": "claimant", "text": "you are pathetic"},
        {"round": 1, "party": "respondent", "text": "let us discuss the logistics"},
    )
    rulings = adjudicate(statements, load_ruleset(), "001")
    assert rulings[0].action == "drop"
    assert rulings[1].action == "route_to_arbitration"


def test_settlement_signals_parse_first_token():
    statements = (
        {"phase": "settlement", "party": "claimant", "text": "ACCEPT. The ruling is fair."},
        {"phase": "settlement", "party": "respondent", "text": "appeal — I contest the finding."},
        {"phase": "settlement", "party": "silent", "text": ""},
        {"phase": "argument", "party": "respondent", "text": "ACCEPT should be ignored here"},
    )
    signals = settlement_signals(statements)
    assert signals == {"claimant": "ACCEPT", "respondent": "APPEAL"}


def test_analyze_reports_settled_only_when_all_accept():
    statements = ({"round": 1, "party": "claimant", "text": "demand a refund"},)
    rulings = adjudicate(statements, load_ruleset(), "001")
    accepted = analyze(statements, rulings, {"claimant": "ACCEPT", "respondent": "ACCEPT"})
    appealed = analyze(statements, rulings, {"claimant": "ACCEPT", "respondent": "APPEAL"})
    empty = analyze(statements, rulings, {})
    assert accepted["settled"] is True
    assert appealed["settled"] is False
    assert empty["settled"] is False
    assert accepted["actions"]["order_refund"] == 1
    assert accepted["statements"] == 1


def test_adjudicate_appeals_hears_every_appeal_deterministically():
    statements = (
        {"round": 1, "phase": "argument", "party": "claimant", "text": "demand a refund"},
        {"round": 1, "phase": "argument", "party": "respondent", "text": "refuse the refund"},
        {"round": 2, "phase": "settlement", "party": "claimant", "text": "ACCEPT. fair."},
        {
            "round": 2,
            "phase": "settlement",
            "party": "respondent",
            "text": "APPEAL. the ruling misreads the evidence",
        },
    )
    rulings = adjudicate(statements, load_ruleset(), "t")
    first = adjudicate_appeals(statements, rulings, load_ruleset())
    second = adjudicate_appeals(statements, rulings, load_ruleset())
    assert first == second
    assert set(first) == {"respondent"}
    assert first["respondent"].action == "affirm"
    assert first["respondent"].rule_id == "R1"


def test_final_settlement_rules():
    affirm = Ruling(digest="aa" * 32, action="affirm", rule_id="R1")
    overturn = Ruling(digest="bb" * 32, action="overturn", rule_id="R1")
    assert final_settlement({"a": "ACCEPT", "b": "ACCEPT"}, {}) is True
    assert final_settlement({"a": "ACCEPT", "b": "APPEAL"}, {"b": affirm}) is True
    assert final_settlement({"a": "ACCEPT", "b": "APPEAL"}, {"b": overturn}) is False
    assert final_settlement({"a": "ACCEPT", "b": "REJECT"}, {}) is False
    assert final_settlement({}, {}) is False


def test_adjudicate_appeals_requires_two_parties():
    statements = (
        {"round": 1, "phase": "argument", "party": "claimant", "text": "demand a refund"},
        {"round": 2, "phase": "settlement", "party": "claimant", "text": "APPEAL. unfair"},
    )
    rulings = adjudicate(statements, load_ruleset(), "t")
    assert adjudicate_appeals(statements, rulings, load_ruleset()) == {}


def test_adjudicate_appeals_skips_appellant_without_argument_statement():
    statements = (
        {"round": 1, "phase": "argument", "party": "claimant", "text": "demand a refund"},
        {"round": 1, "phase": "argument", "party": "respondent", "text": "refuse the refund"},
        {"round": 2, "phase": "settlement", "party": "claimant", "text": "ACCEPT."},
        {"round": 2, "phase": "settlement", "party": "latecomer", "text": "APPEAL. unheard"},
    )
    rulings = adjudicate(statements, load_ruleset(), "t")
    assert adjudicate_appeals(statements, rulings, load_ruleset()) == {}


def test_polity_001_appeal_is_reheard_deterministically():
    transcript = Path(__file__).resolve().parents[1] / "docs" / "polity-001" / "transcript.jsonl"
    statements = load_transcript(transcript.read_text(encoding="utf-8"))
    rulings = adjudicate(statements, load_ruleset(), "polity-001")
    first = adjudicate_appeals(statements, rulings, load_ruleset())
    second = adjudicate_appeals(statements, rulings, load_ruleset())
    assert first == second
    assert set(first) == {"respondent"}
    assert first["respondent"].action == "affirm"
    assert first["respondent"].rule_id == "R1"
    assert final_settlement(settlement_signals(statements), first) is True


def test_cli_emits_appellate_rulings_and_final_settlement(tmp_path):
    transcript = tmp_path / "appeal.jsonl"
    transcript.write_text(
        '{"round":1,"phase":"argument","party":"claimant","text":"demand a refund"}\n'
        '{"round":1,"phase":"argument","party":"respondent","text":"refuse the refund"}\n'
        '{"round":2,"phase":"settlement","party":"claimant","text":"ACCEPT. fair."}\n'
        '{"round":2,"phase":"settlement","party":"respondent","text":"APPEAL. misreads evidence"}\n',
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(transcript), str(RULESET_PATH)],
        capture_output=True,
        text=True,
        check=True,
        env=dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src")),
    )
    lines = [line for line in result.stdout.splitlines() if line]
    appellate_line = json.loads(lines[-2])
    assert appellate_line["party"] == "respondent"
    assert appellate_line["action"] == "affirm"
    summary = json.loads(lines[-1])
    assert summary["final_settlement"] is True


def test_cli_end_to_end(tmp_path):
    transcript = tmp_path / "polity-001.jsonl"
    transcript.write_text(
        '{"round":1,"party":"claimant","text":"demand a refund"}\n', encoding="utf-8"
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(transcript), str(RULESET_PATH)],
        capture_output=True,
        text=True,
        check=True,
        env=dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src")),
    )
    lines = [line for line in result.stdout.splitlines() if line]
    ruling_line = json.loads(lines[0])
    assert ruling_line["action"] == "order_refund"
    assert ruling_line["rule_id"] == "R1"
    summary = json.loads(lines[1])
    assert summary["statements"] == 1
