from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .measurement import LiveFrictionMonitor
from .protocol import Phase

READOUT_STRIDE = 10


@dataclass(frozen=True, slots=True)
class ChannelSummary:
    channel: str
    messages: int
    ruled: int
    settled: int
    edges: int
    conflict_edges: int
    friction: float
    phase: Phase
    peak_friction: float
    trajectory: tuple[tuple[int, float], ...]


def summarize(path: Path | str) -> tuple[ChannelSummary, ...]:
    ledger_path = Path(path)
    if not ledger_path.exists():
        return ()
    monitor = LiveFrictionMonitor()
    tallies: dict[str, dict[str, int]] = {}
    peaks: dict[str, float] = {}
    trajectories: dict[str, list[tuple[int, float]]] = {}
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        channel = record["channel"]
        rulings = tuple(tuple(ruling) for ruling in record["rulings"])
        tally = tallies.setdefault(channel, {"messages": 0, "ruled": 0, "settled": 0})
        peaks.setdefault(channel, 0.0)
        trajectory = trajectories.setdefault(channel, [])
        tally["messages"] += 1
        if rulings:
            tally["ruled"] += 1
        if record["settled"]:
            tally["settled"] += 1
        monitor.record_message(
            channel,
            record["speaker"],
            record["counterpart"],
            rulings,
            record["settled"],
        )
        friction = monitor.friction(channel)
        peaks[channel] = max(peaks[channel], friction)
        if tally["messages"] % READOUT_STRIDE == 0:
            trajectory.append((tally["messages"] - 1, friction))
    return tuple(
        ChannelSummary(
            channel=channel,
            messages=tally["messages"],
            ruled=tally["ruled"],
            settled=tally["settled"],
            edges=len(monitor.network(channel).edges),
            conflict_edges=len(monitor.network(channel).conflict_edges),
            friction=monitor.friction(channel),
            phase=monitor.phase(channel),
            peak_friction=peaks[channel],
            trajectory=tuple(trajectories[channel]),
        )
        for channel, tally in tallies.items()
    )
