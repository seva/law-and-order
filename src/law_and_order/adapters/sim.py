from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from ..protocol import Ruling, Signal
from .base import render_ruling

OnRuling = Callable[[Ruling, str], Awaitable[None]]


@dataclass(frozen=True, slots=True)
class SimAdapter:
    on_ruling: OnRuling

    async def ingest(self, raw: str, source: str) -> Signal:
        event = json.loads(raw)
        dispute_key = event.get("dispute_key")
        text = event.get("text")
        if dispute_key is None or text is None:
            raise ValueError("sim event missing dispute_key or text")
        return Signal(source=f"sim:{dispute_key}", payload=text)

    async def publish(self, ruling: Ruling) -> None:
        await self.on_ruling(ruling, render_ruling(ruling))
