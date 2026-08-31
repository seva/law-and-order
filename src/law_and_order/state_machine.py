from __future__ import annotations

from .protocol import BoundaryConstraints, Ruling, Signal, SignalKind
from .ruleset import RuleSet

UNVALUED_MARKERS = frozenset(
    {
        "worthless",
        "idiot",
        "stupid",
        "shut up",
        "loser",
        "pathetic",
        "hate you",
    }
)


def classify(signal: Signal) -> SignalKind:
    text = signal.payload.lower()
    if any(marker in text for marker in UNVALUED_MARKERS):
        return SignalKind.UNVALUED
    return SignalKind.VALUED


class StateMachine:
    def __init__(
        self,
        ruleset: RuleSet,
        boundaries: BoundaryConstraints = BoundaryConstraints(),
    ) -> None:
        self._ruleset = ruleset
        self._boundaries = boundaries

    def step(self, signal: Signal) -> Ruling:
        if len(signal.payload) > self._boundaries.max_payload:
            return Ruling(digest=signal.digest, action="reject_oversize", rule_id="R-boundary")
        if classify(signal) is SignalKind.UNVALUED:
            return Ruling(digest=signal.digest, action="drop", rule_id="R0")
        text = signal.payload.lower()
        for rule in self._ruleset.ordered():
            if rule.match in text:
                action = rule.action if self._boundaries.permits(rule.action) else "abstain"
                return Ruling(digest=signal.digest, action=action, rule_id=rule.rule_id)
        return Ruling(digest=signal.digest, action="route_to_arbitration", rule_id="R-default")
