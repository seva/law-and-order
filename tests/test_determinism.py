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
