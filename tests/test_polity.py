import json
import os
import subprocess
import sys
from pathlib import Path

from law_and_order import RuleSet
from law_and_order.polity import adjudicate, analyze, load_transcript, settlement_signals

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
