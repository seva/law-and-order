from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Persona:
    name: str
    claims: tuple[str, ...]
    noise: tuple[str, ...]
    counterparts: tuple[str, ...]


def default_population() -> tuple[Persona, ...]:
    return (
        Persona(
            name="buyer",
            claims=(
                "demand a refund",
                "requesting refund for the order",
                "appeal the ruling",
            ),
            noise=("you are pathetic", "shut up"),
            counterparts=("seller", "creditor"),
        ),
        Persona(
            name="seller",
            claims=(
                "refuse the refund, this is a breach",
                "appeal the ruling",
            ),
            noise=("idiot", "loser"),
            counterparts=("buyer", "accuser"),
        ),
        Persona(
            name="creditor",
            claims=(
                "the unpaid debt is a breach",
                "threat of legal action",
            ),
            noise=("pathetic",),
            counterparts=("debtor", "buyer"),
        ),
        Persona(
            name="debtor",
            claims=(
                "demand a refund on the interest",
                "appeal the ruling",
            ),
            noise=("stupid",),
            counterparts=("creditor", "seller"),
        ),
        Persona(
            name="accuser",
            claims=(
                "this conduct is a threat to the community",
                "breach of trust",
            ),
            noise=("hate you",),
            counterparts=("defender", "seller"),
        ),
        Persona(
            name="defender",
            claims=(
                "appeal the ruling",
                "demand a refund of reputation",
            ),
            noise=("worthless",),
            counterparts=("accuser", "debtor"),
        ),
    )
