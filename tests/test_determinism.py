from law_and_order import (
    Arbitrator,
    BoundaryConstraints,
    Dispute,
    Network,
    Phase,
    Rule,
    RuleSet,
    Signal,
    StateMachine,
    phase,
)


def test_same_input_same_output():
    ruleset = RuleSet(rules=(Rule("R1", "refund", "order_refund"),))
    dispute = Dispute(claim="demand a refund", counterclaim="refuse the refund")
    first = Arbitrator(ruleset).resolve(dispute)
    second = Arbitrator(ruleset).resolve(dispute)
    assert first == second


def test_unvalued_text_is_dropped_without_retaliation():
    machine = StateMachine(RuleSet(rules=()))
    ruling = machine.step(Signal(source="node-7", payload="you are worthless and stupid"))
    assert ruling.action == "drop"
    assert ruling.rule_id == "R0"


def test_valued_signal_matches_rule():
    machine = StateMachine(RuleSet(rules=(Rule("R1", "refund", "order_refund"),)))
    ruling = machine.step(Signal(source="node-1", payload="requesting refund for order 42"))
    assert ruling.action == "order_refund"
    assert ruling.rule_id == "R1"


def test_forbidden_actions_never_emerge():
    boundaries = BoundaryConstraints()
    machine = StateMachine(
        RuleSet(rules=(Rule("R1", "attack", "retaliate"),)),
        boundaries,
    )
    ruling = machine.step(Signal(source="node-2", payload="node-3 did attack the channel"))
    assert ruling.action == "abstain"


def test_arbitration_is_identity_free():
    arbitrator = Arbitrator(RuleSet(rules=()))
    first = arbitrator.resolve(Dispute(claim="alpha", counterclaim="beta"))
    second = arbitrator.resolve(Dispute(claim="alpha", counterclaim="beta"))
    assert first == second
    assert first.rule_id == "R-tiebreak"


def test_ruleset_canonical_form_is_order_independent():
    r1 = Rule("R1", "refund", "order_refund")
    r2 = Rule("R2", "breach", "enforce")
    assert RuleSet((r1, r2)).canonical() == RuleSet((r2, r1)).canonical()


def test_phase_transition_on_friction_drop():
    edges = frozenset(
        {
            frozenset(("a", "b")),
            frozenset(("b", "c")),
            frozenset(("c", "d")),
            frozenset(("a", "d")),
        }
    )
    disordered = Network(nodes=frozenset("abcd"), edges=edges, conflict_edges=edges)
    ordered = Network(nodes=frozenset("abcd"), edges=edges, conflict_edges=frozenset())
    assert phase(disordered) is Phase.DISORDERED
    assert phase(ordered) is Phase.ORDERED


def test_arbitrator_coerces_forbidden_action_to_abstain():
    ruleset = RuleSet(rules=(Rule("R1", "breach", "retaliate"),))
    arbitrator = Arbitrator(ruleset)
    ruling = arbitrator.resolve(Dispute(claim="breach occurred", counterclaim="no breach"))
    assert ruling.action == "abstain"
    assert ruling.rule_id == "R-boundary"


def test_tiebreak_exercises_both_branches():
    arbitrator = Arbitrator(RuleSet(rules=()))
    forward = arbitrator.resolve(Dispute(claim="alpha", counterclaim="beta"))
    swapped = arbitrator.resolve(Dispute(claim="beta", counterclaim="alpha"))
    assert {forward.action, swapped.action} == {"uphold_claim", "uphold_counterclaim"}
    assert forward.rule_id == swapped.rule_id == "R-tiebreak"


def test_oversize_payload_rejected_at_boundary():
    machine = StateMachine(RuleSet(rules=()))
    ruling = machine.step(Signal(source="node-9", payload="x" * 4097))
    assert ruling.action == "reject_oversize"
    assert ruling.rule_id == "R-boundary"


def test_unmatched_valued_signal_routes_to_arbitration():
    machine = StateMachine(RuleSet(rules=(Rule("R1", "refund", "order_refund"),)))
    ruling = machine.step(Signal(source="node-1", payload="unrelated query about nothing"))
    assert ruling.action == "route_to_arbitration"
    assert ruling.rule_id == "R-default"


def test_compressed_size_matches_canonical_bytes():
    ruleset = RuleSet(rules=(Rule("R1", "refund", "order_refund"),))
    assert ruleset.compressed_size() == len(ruleset.canonical().encode("utf-8"))


def test_empty_network_has_zero_friction_and_orders():
    empty = Network(nodes=frozenset(), edges=frozenset(), conflict_edges=frozenset())
    assert empty.friction() == 0.0
    assert phase(empty) is Phase.ORDERED
