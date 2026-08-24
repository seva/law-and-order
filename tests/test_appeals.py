from dataclasses import fields

from law_and_order import BoundaryConstraints, Dispute, Rule, RuleSet, Ruling
from law_and_order.appeals import Appeal, Appellate


def make_ruleset() -> RuleSet:
    return RuleSet(rules=(Rule("R1", "refund", "order_refund"),))


def make_appeal(ground: str = "the ruling misreads the delivery evidence") -> Appeal:
    dispute = Dispute(claim="demand a refund", counterclaim="refuse the refund")
    ruling = Ruling(digest=dispute.digest, action="order_refund", rule_id="R1")
    return Appeal(dispute=dispute, ruling=ruling, ground=ground)


def test_appellate_ruling_is_deterministic():
    first = Appellate(make_ruleset()).resolve(make_appeal())
    second = Appellate(make_ruleset()).resolve(make_appeal())
    assert first == second


def test_appeal_digest_is_content_addressed():
    base = make_appeal()
    same = make_appeal()
    other = make_appeal(ground="different ground")
    assert base.digest == same.digest
    assert base.digest != other.digest


def test_affirm_when_merits_match_contested_action():
    appeal = make_appeal()
    ruling = Appellate(make_ruleset()).resolve(appeal)
    assert ruling.action == "affirm"
    assert ruling.rule_id == "R1"
    assert ruling.digest == appeal.digest


def test_overturn_when_merits_differ():
    dispute = Dispute(claim="demand a refund", counterclaim="refuse the refund")
    contested = Ruling(digest=dispute.digest, action="drop", rule_id="R0")
    appeal = Appeal(dispute=dispute, ruling=contested, ground="the text was valued all along")
    ruling = Appellate(make_ruleset()).resolve(appeal)
    assert ruling.action == "overturn"
    assert ruling.rule_id == "R1"
    assert ruling.digest == appeal.digest


def test_appeal_is_identity_free_by_construction():
    assert {field.name for field in fields(Appeal)} == {"dispute", "ruling", "ground"}


def test_forbidden_action_coerced_at_appellate_emission():
    boundaries = BoundaryConstraints(forbidden_actions=("affirm",))
    ruling = Appellate(make_ruleset(), boundaries).resolve(make_appeal())
    assert ruling.action == "abstain"
    assert ruling.rule_id == "R-boundary"
