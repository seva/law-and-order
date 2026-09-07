from __future__ import annotations

from collections import deque
from dataclasses import dataclass

RECENCY_WINDOW = 8


@dataclass(frozen=True, slots=True)
class PairEvent:
    channel: str
    speaker: str
    referenced_speaker: str | None
    text: str


class PairingTracker:
    def __init__(self, source_prefix: str) -> None:
        self._source_prefix = source_prefix
        self._recency: dict[str, deque[str]] = {}

    def resolve(self, event: PairEvent) -> str | None:
        history = self._recency.setdefault(event.channel, deque(maxlen=RECENCY_WINDOW))
        counterpart: str | None = None
        if event.referenced_speaker is not None and event.referenced_speaker != event.speaker:
            counterpart = event.referenced_speaker
        else:
            for recent in reversed(history):
                if recent != event.speaker:
                    counterpart = recent
                    break
        history.append(event.speaker)
        return counterpart

    def dispute_key(self, speaker: str, counterpart: str) -> str:
        return f"{self._source_prefix}:{'|'.join(sorted((speaker, counterpart)))}"
