from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass

from ..adapters.sim import SimAdapter
from ..adjudication import SettlementService
from ..protocol import Ruling
from ..ruleset import RuleSet
from ..topology import Network
from .population import Persona

P_ESCALATE = 0.9
P_INITIATE = 0.1
P_CHAT = 0.4
NOISE_SHARE = 0.3
WINDOW = 10
CRITICAL_FRICTION = 0.25


@dataclass(frozen=True, slots=True)
class RoundRecord:
    round: int
    exchanges: tuple[tuple[str, str, str, bool], ...]
    friction: float


def run(
    population: tuple[Persona, ...],
    rounds: int,
    seed: int,
    installed: bool = False,
    ruleset: RuleSet | None = None,
) -> tuple[tuple[RoundRecord, ...], tuple[Ruling, ...], int]:
    rng = random.Random(seed)
    names = [persona.name for persona in population]
    by_name = {persona.name: persona for persona in population}
    service = SettlementService(ruleset, source="sim") if installed and ruleset is not None else None
    published: list[Ruling] = []
    adapter = None

    if service is not None:

        async def on_ruling(ruling: Ruling, text: str) -> None:
            published.append(ruling)

        adapter = SimAdapter(on_ruling=on_ruling)

    open_disputes: set[frozenset[str]] = set()
    resolved: set[frozenset[str]] = set()
    window_exchanges: list[tuple[int, str, str, bool]] = []
    history: list[RoundRecord] = []
    resolved_count = 0

    def adjudicate(pair: frozenset[str], speaker: str, text: str) -> bool:
        nonlocal resolved_count
        counterparty = next(iter(pair - {speaker}))
        observation = service.observe(speaker, counterparty, text)
        for ruling in observation.rulings:
            asyncio.run(adapter.publish(ruling))
        if not observation.settled:
            return False
        resolved_count += 1
        return True

    for round_index in range(rounds):
        exchanges: list[tuple[str, str, str, bool]] = []

        for pair in sorted(open_disputes, key=sorted):
            if rng.random() >= P_ESCALATE:
                continue
            a, b = sorted(pair)
            speaker = rng.choice((a, b))
            persona = by_name[speaker]
            other = b if speaker == a else a
            if rng.random() < NOISE_SHARE:
                text = rng.choice(persona.noise)
            else:
                text = rng.choice(persona.claims)
            exchanges.append((speaker, other, text, True))
            window_exchanges.append((round_index, speaker, other, True))
            if service is not None and adjudicate(pair, speaker, text):
                open_disputes.discard(pair)
                resolved.add(pair)

        for persona in population:
            if rng.random() >= P_INITIATE:
                continue
            candidates = [
                name
                for name in persona.counterparts
                if frozenset((persona.name, name)) not in open_disputes
                and frozenset((persona.name, name)) not in resolved
            ]
            if not candidates:
                continue
            other = rng.choice(candidates)
            pair = frozenset((persona.name, other))
            if rng.random() < NOISE_SHARE:
                text = rng.choice(persona.noise)
            else:
                text = rng.choice(persona.claims)
            exchanges.append((persona.name, other, text, True))
            window_exchanges.append((round_index, persona.name, other, True))
            open_disputes.add(pair)

        for persona in population:
            if rng.random() >= P_CHAT:
                continue
            other = rng.choice([name for name in names if name != persona.name])
            exchanges.append((persona.name, other, "general discussion", False))
            window_exchanges.append((round_index, persona.name, other, False))

        cutoff = round_index - WINDOW
        window_exchanges = [entry for entry in window_exchanges if entry[0] > cutoff]
        edges: set[frozenset[str]] = set()
        conflict_edges: set[frozenset[str]] = set()
        for _, a, b, conflict in window_exchanges:
            pair = frozenset((a, b))
            edges.add(pair)
            if conflict:
                conflict_edges.add(pair)
        network = Network(
            nodes=frozenset(names),
            edges=frozenset(edges),
            conflict_edges=frozenset(conflict_edges),
        )
        history.append(
            RoundRecord(round=round_index, exchanges=tuple(exchanges), friction=network.friction())
        )

    return tuple(history), tuple(published), resolved_count
