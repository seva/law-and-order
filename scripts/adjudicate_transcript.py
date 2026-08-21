import json
import sys
from pathlib import Path

from law_and_order import RuleSet
from law_and_order.polity import adjudicate, analyze, load_transcript, settlement_signals


def main() -> None:
    transcript_path = Path(sys.argv[1])
    ruleset_path = (
        Path(sys.argv[2])
        if len(sys.argv) > 2
        else Path(__file__).resolve().parent.parent / "rulesets" / "v1.json"
    )
    ruleset = RuleSet.from_json(ruleset_path.read_text(encoding="utf-8"))
    statements = load_transcript(transcript_path.read_text(encoding="utf-8"))
    dispute_id = transcript_path.stem
    rulings = adjudicate(statements, ruleset, dispute_id)
    settlements = settlement_signals(statements)
    for statement, ruling in zip(statements, rulings):
        print(
            json.dumps(
                {
                    "round": statement.get("round"),
                    "phase": statement.get("phase", "argument"),
                    "party": statement["party"],
                    "action": ruling.action,
                    "rule_id": ruling.rule_id,
                }
            )
        )
    print(json.dumps(analyze(statements, rulings, settlements)))


if __name__ == "__main__":
    main()
