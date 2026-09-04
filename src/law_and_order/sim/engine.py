from __future__ import annotations

import asyncio
import json
import random
from dataclasses import dataclass

from ..adapters.sim import SimAdapter
from ..appeals import Appeal, Appellate
from ..arbitration import Dispute
from ..protocol import Ruling
from ..reaction import Party, Reaction, react
from ..ruleset import RuleSet
from ..state_machine import DEFAULT_RULE_ID, StateMachine
from ..topology import Network
from .population import Persona

P_ESCALATE = 0.9
P_INITIATE = 0.1
P_CHAT = 0.4
NOISE_SHARE = 0.3
WINDOW = 10
CRITICAL_FRICTION = 0.25
INERT_ACTIONS = frozenset({"drop", "abstain", "reject_oversize"})


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
    machine = StateMachine(ruleset) if installed and ruleset is not None else None
    published: list[Ruling] = []
    adapter = None

    if machine is not None:

        async def on_ruling(ruling: Ruling, text: str) -> None:
            published.append(ruling)

        adapter = SimAdapter(on_ruling=on_ruling)
        appellate = Appellate(ruleset)

    open_disputes: set[frozenset[str]] = set()
    resolved: set[frozenset[str]] = set()
    window_exchanges: list[tuple[int, str, str, bool]] = []
    history: list[RoundRecord] = []
    resolved_count = 0
    last_said: dict[frozenset[str], dict[str, str]] = {}

    def adjudicate(pair: frozenset[str], speaker: str, text: str) -> bool:
        nonlocal resolved_count
        counterparty = next(iter(pair - {speaker}))
        counter_text = last_said.get(pair, {}).get(counterparty)
        if counter_text is None:
            return False
        raw = json.dumps({"dispute_key": "|".join(sorted(pair)), "text": text})
        signal = asyncio.run(adapter.ingest(raw, source="sim"))
        ruling = machine.step(signal)
        if ruling.action in INERT_ACTIONS or ruling.rule_id == DEFAULT_RULE_ID:
            return False
        asyncio.run(adapter.publish(ruling))
        author_reaction = react(ruling, text, Party.AUTHOR)
        counter_reaction = react(ruling, text, Party.COUNTERPARTY)
        if author_reaction is Reaction.ACCEPT and counter_reaction is Reaction.ACCEPT:
            settled = True
        elif author_reaction is Reaction.APPEAL or counter_reaction is Reaction.APPEAL:
            dispute = Dispute(claim=text, counterclaim=counter_text)
            ground = text if author_reaction is Reaction.APPEAL else counter_text
            appellate_ruling = appellate.resolve(
                Appeal(dispute=dispute, ruling=ruling, ground=ground)
            )
            asyncio.run(adapter.publish(appellate_ruling))
            settled = appellate_ruling.action == "affirm"
        else:
            settled = False
        if not settled:
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
            last_said.setdefault(pair, {})[speaker] = text
            if machine is not None and adjudicate(pair, speaker, text):
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
            last_said.setdefault(pair, {})[persona.name] = text
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
