from __future__ import annotations

from enum import Enum, auto

from .protocol import Ruling


class Enforcement(Enum):
    NONE = auto()
    DELETE = auto()


_DELETE_ACTIONS = frozenset({"drop", "reject_oversize"})


def enforcement_for(ruling: Ruling) -> Enforcement:
    if ruling.action in _DELETE_ACTIONS:
        return Enforcement.DELETE
    return Enforcement.NONE
