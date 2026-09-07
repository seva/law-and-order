import inspect
from dataclasses import FrozenInstanceError

import pytest

from law_and_order.measurement import MEASUREMENT_WINDOW, Exchange, LiveFrictionMonitor
from law_and_order.protocol import Phase
from law_and_order.topology import phase as kernel_phase


def monitor(window: int = MEASUREMENT_WINDOW) -> LiveFrictionMonitor:
    return LiveFrictionMonitor(window=window)


def matched_ruling(action: str = "order_refund", rule_id: str = "R1"):
    return ((action, rule_id),)


def test_measurement_window_value_is_legislated():
    assert MEASUREMENT_WINDOW == 100


def test_empty_channel_is_zero_and_ordered():
    m = monitor()
    assert m.friction("empty") == 0.0
    assert m.phase("empty") is Phase.ORDERED


def test_unpaired_messages_add_nodes_without_edges():
    m = monitor()
    m.record_message("c", "101", None, (), False)
    m.record_message("c", "202", None, (), False)
    network = m.network("c")
    assert network.nodes == frozenset({"101", "202"})
    assert network.edges == frozenset()
    assert m.friction("c") == 0.0


def test_matched_rulings_create_conflict_edges():
    m = monitor()
    m.record_message("c", "101", None, (), False)
    m.record_message("c", "202", "101", matched_ruling(), False)
    network = m.network("c")
    assert network.edges == frozenset({frozenset({"101", "202"})})
    assert network.conflict_edges == network.edges
    assert m.friction("c") == 1.0
    assert m.phase("c") is Phase.DISORDERED


def test_default_unvalued_and_boundary_rulings_are_edges_without_conflict():
    m = monitor()
    m.record_message("c", "a", None, (), False)
    m.record_message("c", "b", "a", matched_ruling("route_to_arbitration", "R-default"), False)
    m.record_message("c", "d", "b", matched_ruling("drop", "R0"), False)
    m.record_message("c", "e", "d", matched_ruling("reject_oversize", "R-boundary"), False)
    network = m.network("c")
    assert len(network.edges) == 3
    assert network.conflict_edges == frozenset()
    assert m.friction("c") == 0.0


def test_appellate_rulings_are_conflicted():
    m = monitor()
    m.record_message("c", "a", None, (), False)
    m.record_message("c", "b", "a", (("order_refund", "R1"), ("affirm", "R1")), True)
    assert m.network("c").conflict_edges == m.network("c").edges
    assert m.friction("c") == 1.0


def test_edge_is_conflicted_if_any_window_entry_was():
    m = monitor()
    m.record_message("c", "a", None, (), False)
    m.record_message("c", "b", "a", matched_ruling(), False)
    m.record_message("c", "a", "b", (), False)
    network = m.network("c")
    assert len(network.edges) == 1
    assert len(network.conflict_edges) == 1


def test_settlement_is_non_retroactive_and_friction_decays_with_the_window():
    m = monitor()
    m.record_message("c", "a", None, (), False)
    m.record_message("c", "b", "a", (("order_refund", "R1"), ("affirm", "R1")), True)
    assert m.friction("c") == 1.0
    for index in range(MEASUREMENT_WINDOW):
        m.record_message("c", f"s{index}", None, (), False)
    assert m.friction("c") == 0.0
    assert m.phase("c") is Phase.ORDERED


def test_post_settlement_paired_exchanges_are_plain_edges():
    m = monitor()
    m.record_message("c", "a", None, (), False)
    m.record_message("c", "b", "a", (("order_refund", "R1"), ("affirm", "R1")), True)
    for index in range(MEASUREMENT_WINDOW):
        m.record_message("c", f"s{index}", None, (), False)
    m.record_message("c", "x", None, (), False)
    m.record_message("c", "y", "x", (), False)
    network = m.network("c")
    assert network.edges == frozenset({frozenset({"x", "y"})})
    assert network.conflict_edges == frozenset()
    assert m.friction("c") == 0.0


def test_window_is_bounded_evicts_fifo_and_isolates_channels():
    m = monitor(window=3)
    m.record_message("c1", "a", None, (), False)
    m.record_message("c1", "b", "a", matched_ruling(), False)
    m.record_message("c2", "z", None, (), False)
    assert m.friction("c2") == 0.0
    assert m.network("c2").nodes == frozenset({"z"})
    for index in range(3):
        m.record_message("c1", f"s{index}", None, (), False)
    assert m.friction("c1") == 0.0
    assert m.network("c1").nodes == frozenset({"s0", "s1", "s2"})


def test_replay_is_deterministic():
    events = (
        ("a", None, (), False),
        ("b", "a", matched_ruling(), False),
        ("a", "b", (("escalate_to_human", "R5"),), False),
        ("b", "a", (("order_refund", "R1"), ("affirm", "R1")), True),
        ("c", None, (), False),
        ("c", "a", (), False),
    )
    first = monitor()
    second = monitor()
    for event in events:
        first.record_message("ch", *event)
        second.record_message("ch", *event)
        assert first.friction("ch") == second.friction("ch")
        assert first.phase("ch") is second.phase("ch")
    assert first.network("ch") == second.network("ch")


def test_record_message_admits_no_text_parameter():
    parameters = list(inspect.signature(LiveFrictionMonitor.record_message).parameters)
    assert parameters == ["self", "channel", "speaker", "counterpart", "rulings", "settled"]


def test_exchange_records_are_frozen_and_slotted():
    entry = Exchange(speaker="a", counterpart="b", conflicted=True, settled=False)
    with pytest.raises(FrozenInstanceError):
        entry.speaker = "b"
    assert not hasattr(entry, "__dict__")


def test_phase_reuses_the_kernel_primitive():
    m = monitor()
    m.record_message("c", "a", None, (), False)
    m.record_message("c", "b", "a", matched_ruling(), False)
    assert m.phase("c") is kernel_phase(m.network("c"))
