from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..protocol import Ruling, Signal


@runtime_checkable
class PlatformAdapter(Protocol):
    async def ingest(self, raw: str, source: str) -> Signal: ...

    async def publish(self, ruling: Ruling) -> None: ...
