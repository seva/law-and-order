from __future__ import annotations

import json

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
