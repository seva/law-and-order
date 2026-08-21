from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from ..protocol import Ruling, Signal

Send = Callable[[int, str], Awaitable[None]]


@dataclass(frozen=True, slots=True)
class DiscordAdapter:
    ruling_channel_id: int
    send: Send

    async def ingest(self, raw: str, source: str) -> Signal:
        envelope = json.loads(raw)
        if envelope.get("t") != "MESSAGE_CREATE":
            raise ValueError(f"unexpected gateway event: {envelope.get('t')!r}")
        event = envelope.get("d")
        if not isinstance(event, dict):
            raise ValueError("MESSAGE_CREATE envelope missing event data")
        channel_id = event.get("channel_id")
        content = event.get("content")
        if channel_id is None or content is None:
            raise ValueError("MESSAGE_CREATE event missing channel_id or content")
        guild_id = event.get("guild_id")
        origin = f"{guild_id}:{channel_id}" if guild_id else f"dm:{channel_id}"
        return Signal(source=origin, payload=content)

    async def publish(self, ruling: Ruling) -> None:
        await self.send(self.ruling_channel_id, render_ruling(ruling))


def render_ruling(ruling: Ruling) -> str:
    return f"[{ruling.rule_id}] {ruling.action} — case {ruling.digest[:16]}"
