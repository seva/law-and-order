from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .arbitration import Arbitrator
from .protocol import BoundaryConstraints, Ruling
from .ruleset import RuleSet


@dataclass(frozen=True, slots=True)
class Appeal:
    dispute: Dispute
    ruling: Ruling
    ground: str

    @property
    def digest(self) -> str:
        return sha256(
            f"{self.dispute.digest}|{self.ruling.digest}|{self.ground}".encode("utf-8")
        ).hexdigest()


class Appellate:
    def __init__(
        self,
        ruleset: RuleSet,
        boundaries: BoundaryConstraints = BoundaryConstraints(),
    ) -> None:
        self._ruleset = ruleset
        self._boundaries = boundaries

    def resolve(self, appeal: Appeal) -> Ruling:
        merits = Arbitrator(self._ruleset, self._boundaries).resolve(appeal.dispute)
        action = "affirm" if merits.action == appeal.ruling.action else "overturn"
        if not self._boundaries.permits(action):
            return Ruling(digest=appeal.digest, action="abstain", rule_id="R-boundary")
        return Ruling(digest=appeal.digest, action=action, rule_id=merits.rule_id)
