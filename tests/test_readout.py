import inspect
import json
from dataclasses import FrozenInstanceError

import pytest

from law_and_order.ledger import JsonlLedger
from law_and_order.protocol import Phase
from law_and_order.readout import READOUT_STRIDE, ChannelSummary, summarize


def build_ledger(tmp_path, events):
    path = tmp_path / "measurement.jsonl"
    ledger = JsonlLedger(path)
    for event in events:
        ledger.append(*event)
    return path


def trajectory_events():
    events = []
    for index in range(25):
        if index % 2 == 0:
            events.append(("c1", f"s{index}", None, (), False))
        else:
            rulings = (("order_refund", "R1"),) if index % 6 == 3 else ()
            events.append(("c1", f"s{index}", f"s{index - 1}", rulings, False))
    return tuple(events)


def test_readout_stride_value_is_legislated():
    assert READOUT_STRIDE == 10


def test_missing_file_summarizes_to_empty(tmp_path):
    assert summarize(tmp_path / "absent.jsonl") == ()


def test_empty_file_summarizes_to_empty(tmp_path):
    path = tmp_path / "measurement.jsonl"
    JsonlLedger(path).touch()
    assert summarize(path) == ()


def test_per_channel_aggregation_is_exact(tmp_path):
    events = (
        ("c1", "a", None, (), False),
        ("c1", "b", "a", (("order_refund", "R1"),), False),
        ("c1", "a", "b", (("order_refund", "R1"), ("affirm", "R1")), True),
        ("c2", "x", None, (), False),
    )
    summaries = summarize(build_ledger(tmp_path, events))
    assert [summary.channel for summary in summaries] == ["c1", "c2"]
    c1 = summaries[0]
    assert (c1.messages, c1.ruled, c1.settled) == (3, 2, 1)
    assert c1.edges == 1
    assert c1.conflict_edges == 1
    assert c1.friction == 1.0
    assert c1.phase is Phase.DISORDERED
    c2 = summaries[1]
    assert (c2.messages, c2.ruled, c2.settled) == (1, 0, 0)
    assert c2.edges == 0
    assert c2.conflict_edges == 0
    assert c2.friction == 0.0
    assert c2.phase is Phase.ORDERED


def test_trajectory_samples_at_stride_and_peak_catches_spikes_between_samples(tmp_path):
    summary = summarize(build_ledger(tmp_path, trajectory_events()))[0]
    assert summary.trajectory == ((9, 0.4), (19, 0.3))
    assert summary.peak_friction == 0.5
    assert summary.friction == 4 / 12
    assert summary.messages == 25
    assert summary.ruled == 4
    assert summary.settled == 0


def test_phase_boundary_follows_the_kernel_threshold(tmp_path):
    events = []
    for index in range(4):
        events.append(("c1", f"u{index}", None, (), False))
        rulings = (("order_refund", "R1"),) if index == 0 else ()
        events.append(("c1", f"v{index}", f"u{index}", rulings, False))
    summary = summarize(build_ledger(tmp_path, tuple(events)))[0]
    assert summary.friction == 0.25
    assert summary.phase is Phase.DISORDERED


def test_summarize_is_deterministic(tmp_path):
    path = build_ledger(tmp_path, trajectory_events())
    assert summarize(path) == summarize(path)


def test_summary_type_is_closed_and_frozen():
    fields = tuple(ChannelSummary.__dataclass_fields__)
    assert fields == (
        "channel",
        "messages",
        "ruled",
        "settled",
        "edges",
        "conflict_edges",
        "friction",
        "phase",
        "peak_friction",
        "trajectory",
    )
    summary = ChannelSummary(
        channel="c",
        messages=0,
        ruled=0,
        settled=0,
        edges=0,
        conflict_edges=0,
        friction=0.0,
        phase=Phase.ORDERED,
        peak_friction=0.0,
        trajectory=(),
    )
    with pytest.raises(FrozenInstanceError):
        summary.channel = "other"
    assert not hasattr(summary, "__dict__")


def test_summarize_signature_is_path_only():
    assert list(inspect.signature(summarize).parameters) == ["path"]


def test_channel_order_is_first_appearance_not_sorted(tmp_path):
    events = (
        ("zebra", "z", None, (), False),
        ("alpha", "a", None, (), False),
    )
    summaries = summarize(build_ledger(tmp_path, events))
    assert [summary.channel for summary in summaries] == ["zebra", "alpha"]


def test_topology_is_windowed_not_full_history(tmp_path):
    events = [
        ("c1", "a", None, (), False),
        ("c1", "b", "a", (("order_refund", "R1"),), False),
    ]
    for pair in range(52):
        events.append(("c1", f"p{pair}", None, (), False))
        events.append(("c1", f"q{pair}", f"p{pair}", (), False))
    summary = summarize(build_ledger(tmp_path, tuple(events)))[0]
    assert (summary.messages, summary.ruled, summary.settled) == (106, 1, 0)
    assert summary.peak_friction == 1.0
    assert summary.edges == 50
    assert summary.conflict_edges == 0
    assert summary.friction == 0.0
    assert summary.phase is Phase.ORDERED


def test_trajectory_stride_counts_per_channel(tmp_path):
    events = []
    for round_index in range(20):
        events.append(("c1", f"s{round_index}", None, (), False))
        events.append(("c2", f"t{round_index}", None, (), False))
    summaries = summarize(build_ledger(tmp_path, tuple(events)))
    c1, c2 = summaries
    assert c1.trajectory == ((9, 0.0), (19, 0.0))
    assert c2.trajectory == ((9, 0.0), (19, 0.0))


def test_malformed_line_fails_loudly(tmp_path):
    path = tmp_path / "measurement.jsonl"
    path.write_text(
        '{"seq":0,"channel":"c1","speaker":"a","counterpart":null,"rulings":[],"settled":false}\n'
        "NOT JSON\n",
        encoding="utf-8",
    )
    with pytest.raises(json.JSONDecodeError):
        summarize(path)
