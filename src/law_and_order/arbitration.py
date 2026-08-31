from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .protocol import BoundaryConstraints, Ruling
from .ruleset import RuleSet


@dataclass(frozen=True, slots=True)
class Dispute:
    claim: str
    counterclaim: str

    @property
    def digest(self) -> str:
        return sha256(f"{self.claim}|{self.counterclaim}".encode("utf-8")).hexdigest()


class Arbitrator:
    def __init__(
        self,
        ruleset: RuleSet,
        boundaries: BoundaryConstraints = BoundaryConstraints(),
    ) -> None:
        self._ruleset = ruleset
        self._boundaries = boundaries

    def resolve(self, dispute: Dispute) -> Ruling:
        action, rule_id = self._adjudicate(dispute)
        if not self._boundaries.permits(action):
            action, rule_id = "abstain", "R-boundary"
        return Ruling(digest=dispute.digest, action=action, rule_id=rule_id)

    def _adjudicate(self, dispute: Dispute) -> tuple[str, str]:
        text = f"{dispute.claim} {dispute.counterclaim}".lower()
        for rule in self._ruleset.ordered():
            if rule.match in text:
                return rule.action, rule.rule_id
        claim_hash = sha256(dispute.claim.encode("utf-8")).digest()
        counter_hash = sha256(dispute.counterclaim.encode("utf-8")).digest()
        if claim_hash <= counter_hash:
            return "uphold_claim", "R-tiebreak"
        return "uphold_counterclaim", "R-tiebreak"
