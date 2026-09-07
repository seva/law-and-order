import inspect
import json

from law_and_order.ledger import JsonlLedger, replay
from law_and_order.measurement import LiveFrictionMonitor

EVENTS = (
    ("c1", "101", None, (), False),
    ("c1", "202", "101", (("order_refund", "R1"),), False),
    ("c1", "101", "202", (("order_refund", "R1"), ("affirm", "R1")), True),
    ("c2", "303", None, (), False),
)


def test_append_writes_one_record_per_message_with_closed_fields(tmp_path):
    path = tmp_path / "measurement.jsonl"
    ledger = JsonlLedger(path)
    for event in EVENTS:
        ledger.append(*event)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == len(EVENTS)
    for seq, (line, event) in enumerate(zip(lines, EVENTS)):
        record = json.loads(line)
        assert set(record) == {"seq", "channel", "speaker", "counterpart", "rulings", "settled"}
        assert record["seq"] == seq
        assert record["channel"] == event[0]
        assert record["speaker"] == event[1]
        assert record["counterpart"] == event[2]
        assert [tuple(ruling) for ruling in record["rulings"]] == [tuple(ruling) for ruling in event[3]]
        assert record["settled"] == event[4]


def test_append_signature_admits_no_text_parameter():
    parameters = list(inspect.signature(JsonlLedger.append).parameters)
    assert parameters == ["self", "channel", "speaker", "counterpart", "rulings", "settled"]


def test_seq_continues_across_ledger_instances(tmp_path):
    path = tmp_path / "measurement.jsonl"
    first = JsonlLedger(path)
    first.append(*EVENTS[0])
    first.append(*EVENTS[1])
    second = JsonlLedger(path)
    second.append(*EVENTS[2])
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert [record["seq"] for record in records] == [0, 1, 2]


def test_replay_reconstructs_the_identical_monitor(tmp_path):
    path = tmp_path / "measurement.jsonl"
    live = LiveFrictionMonitor()
    ledger = JsonlLedger(path)
    for event in EVENTS:
        live.record_message(*event)
        ledger.append(*event)
    rebuilt = replay(path)
    for channel in ("c1", "c2", "absent"):
        assert rebuilt.friction(channel) == live.friction(channel)
        assert rebuilt.phase(channel) == live.phase(channel)
        assert rebuilt.network(channel) == live.network(channel)


def test_replay_of_missing_file_is_an_empty_monitor(tmp_path):
    rebuilt = replay(tmp_path / "absent.jsonl")
    assert rebuilt.friction("any") == 0.0


def test_replay_skips_blank_lines(tmp_path):
    path = tmp_path / "measurement.jsonl"
    ledger = JsonlLedger(path)
    ledger.append(*EVENTS[1])
    with path.open("a", encoding="utf-8", newline="\n") as ledger_file:
        ledger_file.write("\n")
    rebuilt = replay(path)
    live = LiveFrictionMonitor()
    live.record_message(*EVENTS[1])
    assert rebuilt.network("c1") == live.network("c1")
    assert rebuilt.friction("c1") == live.friction("c1")


def test_replay_preserves_order_beyond_the_window(tmp_path):
    from law_and_order.measurement import MEASUREMENT_WINDOW

    path = tmp_path / "measurement.jsonl"
    live = LiveFrictionMonitor()
    ledger = JsonlLedger(path)
    total = MEASUREMENT_WINDOW + 50
    for index in range(total):
        event = (
            "c1",
            f"s{index}",
            f"s{index - 1}" if index > 0 else None,
            (("order_refund", "R1"),) if index % 7 == 0 else (),
            index % 11 == 0,
        )
        live.record_message(*event)
        ledger.append(*event)
    rebuilt = replay(path)
    assert rebuilt.network("c1") == live.network("c1")
    assert rebuilt.friction("c1") == live.friction("c1")
    assert rebuilt.phase("c1") == live.phase("c1")


def test_touch_creates_the_empty_ledger_file(tmp_path):
    path = tmp_path / "logs" / "measurement.jsonl"
    ledger = JsonlLedger(path)
    assert not path.exists()
    ledger.touch()
    assert path.exists()
    assert path.read_text(encoding="utf-8") == ""
    assert replay(path).friction("any") == 0.0
