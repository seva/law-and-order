import itertools

import pytest

from law_and_order.protocol import Ruling
from law_and_order.reaction import Party, Reaction, Stance, react, stance_of

CLAIM_STATEMENT = "I demand a refund of the full purchase amount immediately."
REFUSAL_STATEMENT = "I refuse to issue any refund for damage I did not cause."
OVERLAP_STATEMENT = "I refuse the full refund you are asking for."
NEUTRAL_STATEMENT = "alpha beta gamma delta."

KNOWN_ACTIONS = (
    "order_refund",
    "escalate_to_arbitration",
    "reopen_arbitration",
    "escalate_to_human",
    "drop",
    "abstain",
    "reject_oversize",
)
UNKNOWN_ACTION = "a brand new action"


def ruling(action: str, digest: str = "digest-a") -> Ruling:
    return Ruling(digest=digest, action=action, rule_id="R-test")


def test_stance_of_extracts_claim_refusal_and_neutral():
    assert stance_of(CLAIM_STATEMENT) is Stance.CLAIM
    assert stance_of(REFUSAL_STATEMENT) is Stance.REFUSAL
    assert stance_of(NEUTRAL_STATEMENT) is Stance.NEUTRAL


def test_stance_of_refusal_takes_precedence_on_overlap():
    assert stance_of(OVERLAP_STATEMENT) is Stance.REFUSAL


def test_stance_of_matching_is_case_insensitive_substring():
    assert stance_of("I DEMAND A REFUND OF THE FULL AMOUNT.") is Stance.CLAIM
    assert stance_of("the offer was declined yesterday") is Stance.REFUSAL
    assert stance_of("she refused the delivery outright") is Stance.REFUSAL
    assert stance_of("") is Stance.NEUTRAL


def test_stance_of_recognizes_natural_claim_phrasing():
    assert stance_of("I paid full price and I demand a complete refund.") is Stance.CLAIM
    assert stance_of("we expect an entire refund for the damaged item") is Stance.CLAIM
    assert stance_of("I want a refund for the broken item.") is Stance.CLAIM
    assert stance_of("I want my money back now.") is Stance.CLAIM
    assert stance_of("I expect a refund of the charges.") is Stance.CLAIM
    assert stance_of("we are owed a refund under the warranty") is Stance.CLAIM


def test_stance_of_recognizes_natural_refusal_phrasing():
    assert stance_of("We will not issue a refund for that.") is Stance.REFUSAL
    assert stance_of("we won't issue any refund at all") is Stance.REFUSAL
    assert stance_of("we will not pay for that.") is Stance.REFUSAL
    assert stance_of("you won't get a refund from us") is Stance.REFUSAL


def test_stance_of_refusal_precedes_claim_on_new_markers():
    assert stance_of("we refuse to give a complete refund") is Stance.REFUSAL
    assert stance_of("I want my money back but will not pay your fee") is Stance.REFUSAL


def test_reaction_is_total():
    for action, party in itertools.product((*KNOWN_ACTIONS, UNKNOWN_ACTION), Party):
        for statement in (CLAIM_STATEMENT, REFUSAL_STATEMENT, NEUTRAL_STATEMENT):
            assert react(ruling(action), statement, party) in Reaction


def test_reaction_is_deterministic():
    for party in Party:
        first = react(ruling("order_refund"), CLAIM_STATEMENT, party)
        second = react(ruling("order_refund"), CLAIM_STATEMENT, party)
        assert first is second


def test_favorable_final_ruling_settles_author_and_provokes_counterparty():
    assert react(ruling("order_refund"), CLAIM_STATEMENT, Party.AUTHOR) is Reaction.ACCEPT
    assert react(ruling("order_refund"), CLAIM_STATEMENT, Party.COUNTERPARTY) is Reaction.APPEAL


def test_unfavorable_final_ruling_appeals_author_and_settles_counterparty():
    assert react(ruling("order_refund"), REFUSAL_STATEMENT, Party.AUTHOR) is Reaction.APPEAL
    assert react(ruling("order_refund"), REFUSAL_STATEMENT, Party.COUNTERPARTY) is Reaction.ACCEPT


def test_neutral_stance_rejects_final_rulings():
    assert react(ruling("order_refund"), NEUTRAL_STATEMENT, Party.AUTHOR) is Reaction.REJECT
    assert react(ruling("order_refund"), NEUTRAL_STATEMENT, Party.COUNTERPARTY) is Reaction.REJECT


@pytest.mark.parametrize(
    "action",
    [
        "escalate_to_arbitration",
        "reopen_arbitration",
        "escalate_to_human",
        "drop",
        "abstain",
        "reject_oversize",
    ],
)
def test_procedural_and_inert_rulings_settle_nothing(action):
    for statement in (CLAIM_STATEMENT, REFUSAL_STATEMENT, NEUTRAL_STATEMENT):
        for party in Party:
            assert react(ruling(action), statement, party) is Reaction.REJECT


def test_unknown_action_rejects_by_default():
    for party in Party:
        for statement in (CLAIM_STATEMENT, REFUSAL_STATEMENT, NEUTRAL_STATEMENT):
            assert react(ruling(UNKNOWN_ACTION), statement, party) is Reaction.REJECT


def test_reaction_is_identity_free():
    assert react(
        ruling("order_refund", digest="digest-a"), CLAIM_STATEMENT, Party.AUTHOR
    ) is react(ruling("order_refund", digest="digest-b"), CLAIM_STATEMENT, Party.AUTHOR)
    assert react(
        Ruling(digest="digest-a", action="order_refund", rule_id="R1"),
        CLAIM_STATEMENT,
        Party.AUTHOR,
    ) is react(
        Ruling(digest="digest-a", action="order_refund", rule_id="R9"),
        CLAIM_STATEMENT,
        Party.AUTHOR,
    )
