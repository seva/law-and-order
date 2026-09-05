from __future__ import annotations

from enum import Enum, auto

from .protocol import Ruling


class Enforcement(Enum):
    NONE = auto()
    DELETE = auto()


_DELETE_ACTIONS = frozenset({"drop", "reject_oversize"})


def enforcement_for(ruling: Ruling) -> Enforcement:
    # reject_oversize stays mapped though unreachable on Discord (kernel
    # bound 4096 exceeds the platform's 2000-char message limit): the
    # policy is platform-independent, and the branch is live on any
    # surface whose payload bound exceeds max_payload.
    if ruling.action in _DELETE_ACTIONS:
        return Enforcement.DELETE
    return Enforcement.NONE
