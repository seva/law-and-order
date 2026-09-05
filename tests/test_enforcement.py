from law_and_order.enforcement import Enforcement, enforcement_for
from law_and_order.protocol import Ruling


def ruling(action: str, digest: str = "ab" * 32) -> Ruling:
    return Ruling(digest=digest, action=action, rule_id="R-test")


def test_unvalued_drop_is_enforced_by_deletion():
    assert enforcement_for(ruling("drop")) is Enforcement.DELETE


def test_oversize_rejection_is_enforced_by_deletion():
    assert enforcement_for(ruling("reject_oversize")) is Enforcement.DELETE


def test_final_rulings_pronounce_without_deletion():
    for action in ("order_refund", "escalate_to_arbitration", "reopen_arbitration", "escalate_to_human"):
        assert enforcement_for(ruling(action)) is Enforcement.NONE, action


def test_boundary_abstain_enforces_nothing():
    assert enforcement_for(ruling("abstain")) is Enforcement.NONE


def test_unmatched_routing_enforces_nothing():
    assert enforcement_for(ruling("route_to_arbitration")) is Enforcement.NONE


def test_unknown_action_enforces_nothing():
    assert enforcement_for(ruling("a brand new action")) is Enforcement.NONE


def test_enforcement_is_deterministic():
    assert enforcement_for(ruling("drop")) is enforcement_for(ruling("drop"))


def test_enforcement_is_identity_free():
    assert enforcement_for(ruling("drop", digest="ab" * 32)) is enforcement_for(
        ruling("drop", digest="cd" * 32)
    )
