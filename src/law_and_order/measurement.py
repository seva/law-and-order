from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass

from .adjudication import INERT_ACTIONS
from .protocol import Phase
from .state_machine import DEFAULT_RULE_ID
from .topology import Network
from .topology import phase as network_phase

MEASUREMENT_WINDOW = 100
NON_CONFLICT_RULE_IDS = frozenset({DEFAULT_RULE_ID, "R0", "R-boundary"})


@dataclass(frozen=True, slots=True)
class Exchange:
    speaker: str
    counterpart: str | None
    conflicted: bool
    settled: bool


class LiveFrictionMonitor:
    def __init__(self, window: int = MEASUREMENT_WINDOW) -> None:
        self._window = window
        self._channels: dict[str, deque[Exchange]] = {}

    def record_message(
        self,
        channel: str,
        speaker: str,
        counterpart: str | None,
        rulings: Iterable[tuple[str, str]],
        settled: bool,
    ) -> None:
        conflicted = any(
            rule_id not in NON_CONFLICT_RULE_IDS and action not in INERT_ACTIONS
            for action, rule_id in rulings
        )
        history = self._channels.setdefault(channel, deque(maxlen=self._window))
        history.append(
            Exchange(
                speaker=speaker,
                counterpart=counterpart,
                conflicted=conflicted,
                settled=settled,
            )
        )

    def network(self, channel: str) -> Network:
        history = self._channels.get(channel, ())
        nodes: set[str] = set()
        edges: set[frozenset[str]] = set()
        conflict_pairs: set[frozenset[str]] = set()
        for entry in history:
            nodes.add(entry.speaker)
            if entry.counterpart is None:
                continue
            nodes.add(entry.counterpart)
            edge = frozenset((entry.speaker, entry.counterpart))
            edges.add(edge)
            if entry.conflicted:
                conflict_pairs.add(edge)
        return Network(
            nodes=frozenset(nodes),
            edges=frozenset(edges),
            conflict_edges=frozenset(conflict_pairs),
        )

    def friction(self, channel: str) -> float:
        return self.network(channel).friction()

    def phase(self, channel: str) -> Phase:
        return network_phase(self.network(channel))
