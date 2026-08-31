from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256


class SignalKind(Enum):
    VALUED = "valued"
    UNVALUED = "unvalued"


class Phase(Enum):
    DISORDERED = "disordered"
    ORDERED = "ordered"


@dataclass(frozen=True, slots=True)
class Signal:
    source: str
    payload: str

    @property
    def digest(self) -> str:
        return sha256(f"{self.source}:{self.payload}".encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class Ruling:
    digest: str
    action: str
    rule_id: str


@dataclass(frozen=True, slots=True)
class BoundaryConstraints:
    max_payload: int = 4096
    forbidden_actions: tuple[str, ...] = ("retaliate", "extract_credit", "status_claim")

    def permits(self, action: str) -> bool:
        return action not in self.forbidden_actions
