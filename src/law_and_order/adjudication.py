from __future__ import annotations

from dataclasses import dataclass

from .appeals import Appeal, Appellate
from .arbitration import Dispute
from .protocol import BoundaryConstraints, Ruling, Signal
from .reaction import Party, Reaction, react
from .ruleset import RuleSet
from .state_machine import DEFAULT_RULE_ID, StateMachine

INERT_ACTIONS = frozenset({"drop", "abstain", "reject_oversize"})


@dataclass(frozen=True, slots=True)
class Observation:
    rulings: tuple[Ruling, ...]
    settled: bool


class SettlementService:
    def __init__(
        self,
        ruleset: RuleSet,
        source: str,
        boundaries: BoundaryConstraints = BoundaryConstraints(),
    ) -> None:
        self._machine = StateMachine(ruleset, boundaries)
        self._appellate = Appellate(ruleset, boundaries)
        self._source = source
        self._last_said: dict[frozenset[str], dict[str, str]] = {}
        self._settled: set[frozenset[str]] = set()

    @staticmethod
    def _pair(speaker: str, counterpart: str) -> frozenset[str]:
        pair = frozenset((speaker, counterpart))
        if len(pair) != 2:
            raise ValueError("speaker and counterpart must differ")
        return pair

    def note(self, speaker: str, counterpart: str, text: str) -> None:
        pair = self._pair(speaker, counterpart)
        self._last_said.setdefault(pair, {})[speaker] = text

    def observe(self, speaker: str, counterpart: str, text: str) -> Observation:
        pair = self._pair(speaker, counterpart)
        if pair in self._settled:
            return Observation(rulings=(), settled=True)
        self._last_said.setdefault(pair, {})[speaker] = text
        counter_text = self._last_said[pair].get(counterpart)
        if counter_text is None:
            return Observation(rulings=(), settled=False)
        dispute_key = "|".join(sorted(pair))
        signal = Signal(source=f"{self._source}:{dispute_key}", payload=text)
        ruling = self._machine.step(signal)
        if ruling.action in INERT_ACTIONS or ruling.rule_id == DEFAULT_RULE_ID:
            return Observation(rulings=(), settled=False)
        author_reaction = react(ruling, text, Party.AUTHOR)
        counter_reaction = react(ruling, text, Party.COUNTERPARTY)
        if author_reaction is Reaction.ACCEPT and counter_reaction is Reaction.ACCEPT:
            self._settled.add(pair)
            return Observation(rulings=(ruling,), settled=True)
        if author_reaction is Reaction.APPEAL or counter_reaction is Reaction.APPEAL:
            dispute = Dispute(claim=text, counterclaim=counter_text)
            ground = text if author_reaction is Reaction.APPEAL else counter_text
            appellate_ruling = self._appellate.resolve(
                Appeal(dispute=dispute, ruling=ruling, ground=ground)
            )
            if appellate_ruling.action == "affirm":
                self._settled.add(pair)
                return Observation(rulings=(ruling, appellate_ruling), settled=True)
            return Observation(rulings=(ruling, appellate_ruling), settled=False)
        return Observation(rulings=(ruling,), settled=False)

    def is_settled(self, speaker: str, counterpart: str) -> bool:
        return frozenset((speaker, counterpart)) in self._settled
