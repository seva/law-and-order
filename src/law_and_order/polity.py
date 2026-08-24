from __future__ import annotations

import json

from .appeals import Appeal, Appellate
from .arbitration import Dispute
from .protocol import Ruling, Signal
from .ruleset import RuleSet
from .state_machine import StateMachine

SETTLEMENT_SIGNALS = frozenset({"ACCEPT", "REJECT", "APPEAL"})


def load_transcript(raw: str) -> tuple[dict, ...]:
    statements = []
    for line in raw.splitlines():
        line = line.strip()
        if line:
            statements.append(json.loads(line))
    return tuple(statements)


def adjudicate(
    statements: tuple[dict, ...], ruleset: RuleSet, dispute_id: str
) -> tuple[Ruling, ...]:
    machine = StateMachine(ruleset)
    return tuple(
        machine.step(Signal(source=f"polity:{dispute_id}", payload=statement["text"]))
        for statement in statements
    )


def settlement_signals(statements: tuple[dict, ...]) -> dict[str, str]:
    signals = {}
    for statement in statements:
        if statement.get("phase") != "settlement":
            continue
        tokens = statement["text"].split()
        if not tokens:
            continue
        first = tokens[0].upper().strip(".,!?;:")
        if first in SETTLEMENT_SIGNALS:
            signals[statement["party"]] = first
    return signals


def adjudicate_appeals(
    statements: tuple[dict, ...],
    rulings: tuple[Ruling, ...],
    ruleset: RuleSet,
) -> dict[str, Ruling]:
    argument = [
        (index, statement)
        for index, statement in enumerate(statements)
        if statement.get("phase", "argument") != "settlement"
    ]
    parties: list[str] = []
    for _, statement in argument:
        if statement["party"] not in parties:
            parties.append(statement["party"])
    if len(parties) < 2:
        return {}
    claim = next(s for _, s in argument if s["party"] == parties[0])["text"]
    counterclaim = next(s for _, s in argument if s["party"] == parties[1])["text"]
    dispute = Dispute(claim=claim, counterclaim=counterclaim)
    appellate = Appellate(ruleset)
    outcomes: dict[str, Ruling] = {}
    for index, statement in enumerate(statements):
        if statement.get("phase") != "settlement":
            continue
        tokens = statement["text"].split()
        if not tokens or tokens[0].upper().strip(".,!?;:") != "APPEAL":
            continue
        party = statement["party"]
        appellant_indices = [i for i, s in argument if s["party"] == party]
        if not appellant_indices:
            continue
        appeal = Appeal(
            dispute=dispute,
            ruling=rulings[max(appellant_indices)],
            ground=statement["text"],
        )
        outcomes[party] = appellate.resolve(appeal)
    return outcomes


def final_settlement(settlements: dict[str, str], appellate: dict[str, Ruling]) -> bool:
    if not settlements:
        return False
    for party, signal in settlements.items():
        if signal == "ACCEPT":
            continue
        ruling = appellate.get(party)
        if signal == "APPEAL" and ruling is not None and ruling.action == "affirm":
            continue
        return False
    return True


def analyze(
    statements: tuple[dict, ...],
    rulings: tuple[Ruling, ...],
    settlements: dict[str, str],
) -> dict:
    actions: dict[str, int] = {}
    for ruling in rulings:
        actions[ruling.action] = actions.get(ruling.action, 0) + 1
    settled = bool(settlements) and all(signal == "ACCEPT" for signal in settlements.values())
    return {
        "statements": len(statements),
        "actions": actions,
        "settlement_signals": settlements,
        "settled": settled,
    }
