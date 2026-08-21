from __future__ import annotations

from dataclasses import dataclass

from .protocol import Phase


@dataclass(frozen=True, slots=True)
class Network:
    nodes: frozenset[str]
    edges: frozenset[frozenset[str]]
    conflict_edges: frozenset[frozenset[str]]

    def friction(self) -> float:
        if not self.edges:
            return 0.0
        return len(self.conflict_edges) / len(self.edges)


def phase(network: Network, critical_friction: float = 0.25) -> Phase:
    if network.friction() < critical_friction:
        return Phase.ORDERED
    return Phase.DISORDERED
