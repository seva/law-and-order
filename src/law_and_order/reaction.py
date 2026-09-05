from __future__ import annotations

from enum import Enum, auto

from .protocol import Ruling


class Stance(Enum):
    CLAIM = auto()
    REFUSAL = auto()
    NEUTRAL = auto()


class Party(Enum):
    AUTHOR = auto()
    COUNTERPARTY = auto()


class Reaction(Enum):
    ACCEPT = auto()
    APPEAL = auto()
    REJECT = auto()


CLAIM_MARKERS = (
    "demand a refund",
    "refund of",
    "full refund",
    "refund within",
    "complete refund",
    "entire refund",
    "immediate refund",
    "want a refund",
    "want my money back",
    "get my money back",
    "expect a refund",
    "owed a refund",
)
REFUSAL_MARKERS = (
    "refuse",
    "refusal",
    "decline",
    "will not refund",
    "no refund",
    "will not issue",
    "won't issue",
    "not issuing",
    "will not pay",
    "won't pay",
    "not paying",
    "won't refund",
    "won't get a refund",
    "not giving a refund",
    "won't give a refund",
)

_INVERTED = {Stance.CLAIM: Stance.REFUSAL, Stance.REFUSAL: Stance.CLAIM, Stance.NEUTRAL: Stance.NEUTRAL}
_FAVORED_STANCE = {"order_refund": Stance.CLAIM}


def stance_of(statement: str) -> Stance:
    text = statement.lower()
    if any(marker in text for marker in REFUSAL_MARKERS):
        return Stance.REFUSAL
    if any(marker in text for marker in CLAIM_MARKERS):
        return Stance.CLAIM
    return Stance.NEUTRAL


def react(ruling: Ruling, statement: str, party: Party) -> Reaction:
    stance = stance_of(statement)
    if party is Party.COUNTERPARTY:
        stance = _INVERTED[stance]
    favored = _FAVORED_STANCE.get(ruling.action)
    if favored is None or stance is Stance.NEUTRAL:
        return Reaction.REJECT
    if stance is favored:
        return Reaction.ACCEPT
    return Reaction.APPEAL
