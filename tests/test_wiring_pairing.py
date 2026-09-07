import asyncio
import hashlib
from pathlib import Path
from types import SimpleNamespace

from law_and_order import RuleSet
from law_and_order.adjudication import Observation, SettlementService
from law_and_order.pairing import PairingTracker
from law_and_order.protocol import Signal
from law_and_order.state_machine import StateMachine
from law_and_order.wiring.discord_live import (
    LIVE_SOURCE,
    Routing,
    adjudicate_message,
    pair_event_from,
    route_paired_event,
)

RULESET_PATH = Path(__file__).resolve().parents[1] / "rulesets" / "v1.json"


def load_ruleset() -> RuleSet:
    return RuleSet.from_json(RULESET_PATH.read_text(encoding="utf-8"))


def router() -> tuple[PairingTracker, SettlementService]:
    return PairingTracker(source_prefix="discord-live"), SettlementService(load_ruleset(), source="discord-live")


def adjudication_fakes():
    pronounced = []
    ingested = []

    async def ingest(msg):
        ingested.append(msg)
        return Signal(source=LIVE_SOURCE, payload=msg.content if isinstance(msg.content, str) else "")

    return pronounced, ingested, ingest


def message(content="message text", author_id=101, channel_id=7, reference=None):
    ref = None
    if reference is not None:
        if reference == "unresolved":
            ref = SimpleNamespace(resolved=None)
        elif reference == "deleted":
            ref = SimpleNamespace(resolved=SimpleNamespace())
        else:
            ref = SimpleNamespace(resolved=SimpleNamespace(author=SimpleNamespace(id=reference)))
    return SimpleNamespace(
        content=content,
        author=SimpleNamespace(id=author_id),
        channel=SimpleNamespace(id=channel_id),
        reference=ref,
    )


def test_pair_event_extracts_opaque_ids_and_content():
    event = pair_event_from(message(content="demand a refund", author_id=101, channel_id=7))
    assert event is not None
    assert event.channel == "7"
    assert event.speaker == "101"
    assert event.referenced_speaker is None
    assert event.text == "demand a refund"


def test_pair_event_resolves_reference_author():
    assert pair_event_from(message(author_id=101, reference=202)).referenced_speaker == "202"


def test_unresolved_and_deleted_references_degrade_to_adjacency():
    assert pair_event_from(message(reference="unresolved")).referenced_speaker is None
    assert pair_event_from(message(reference="deleted")).referenced_speaker is None


def test_degenerate_messages_yield_no_event():
    assert pair_event_from(SimpleNamespace(content="x", author=None, channel=SimpleNamespace(id=7), reference=None)) is None
    assert pair_event_from(SimpleNamespace(content="x", author=SimpleNamespace(id=None), channel=SimpleNamespace(id=7), reference=None)) is None
    assert pair_event_from(SimpleNamespace(content="x", author=SimpleNamespace(id=1), channel=None, reference=None)) is None


def test_unpaired_message_routes_to_nothing_for_continuity_fallback():
    tracker, service = router()
    event = pair_event_from(message(content="first words in channel", author_id=101))
    routing = route_paired_event(tracker, service, event)
    assert isinstance(routing, Routing)
    assert routing.counterpart is None
    assert routing.observation is None


def test_paired_unripe_message_returns_empty_observation():
    tracker, service = router()
    first = route_paired_event(tracker, service, pair_event_from(message(content="opening words", author_id=101)))
    assert first.counterpart is None
    assert first.observation is None
    second = route_paired_event(tracker, service, pair_event_from(message(content="reply words", author_id=202)))
    assert second.counterpart == "101"
    assert isinstance(second.observation, Observation)
    assert second.observation.rulings == ()
    assert not second.observation.settled


def test_paired_ripe_message_routes_through_settlement_and_settles():
    tracker, service = router()
    route_paired_event(tracker, service, pair_event_from(message(content="opening words", author_id=101)))
    route_paired_event(tracker, service, pair_event_from(message(content="I refuse to pay anything further", author_id=202)))
    routed = route_paired_event(tracker, service, pair_event_from(message(content="demand a refund for the goods", author_id=101)))
    assert routed.counterpart == "202"
    assert [ruling.action for ruling in routed.observation.rulings] == ["order_refund", "affirm"]
    assert routed.observation.settled


def test_settlement_clears_the_pair_for_a_new_dispute():
    tracker, service = router()
    route_paired_event(tracker, service, pair_event_from(message(content="opening words", author_id=101)))
    route_paired_event(tracker, service, pair_event_from(message(content="I refuse to pay anything further", author_id=202)))
    settled = route_paired_event(tracker, service, pair_event_from(message(content="demand a refund for the goods", author_id=101)))
    assert settled.observation.settled
    assert not service.is_settled("101", "202")
    renewed = route_paired_event(tracker, service, pair_event_from(message(content="demand a refund again", author_id=202)))
    assert renewed.counterpart == "101"
    assert renewed.observation.rulings == ()
    assert not renewed.observation.settled


def test_routing_digest_uses_the_live_source_prefix():
    tracker, service = router()
    route_paired_event(tracker, service, pair_event_from(message(content="opening words", author_id=101)))
    route_paired_event(tracker, service, pair_event_from(message(content="I refuse to pay anything further", author_id=202)))
    text = "demand a refund for the goods"
    routed = route_paired_event(tracker, service, pair_event_from(message(content=text, author_id=101)))
    expected = hashlib.sha256(f"discord-live:101|202:{text}".encode("utf-8")).hexdigest()
    assert routed.observation.rulings[0].digest == expected


def test_live_source_constant_is_pinned():
    assert LIVE_SOURCE == "discord-live"


def test_self_message_is_skipped_entirely():
    tracker, service = router()
    machine = StateMachine(load_ruleset())
    pronounced, ingested, ingest = adjudication_fakes()
    recorded = []

    async def pronounce(ruling):
        pronounced.append(ruling)
        return True

    def record(*facts):
        recorded.append(facts)

    msg = message(content="demand a refund", author_id=999)
    asyncio.run(
        adjudicate_message(
            msg, self_user=msg.author, tracker=tracker, service=service,
            machine=machine, ingest=ingest, pronounce=pronounce, record=record,
        )
    )
    assert pronounced == []
    assert ingested == []
    assert recorded == []


def test_service_rulings_suppress_the_legacy_path():
    tracker, service = router()
    machine = StateMachine(load_ruleset())
    pronounced, ingested, ingest = adjudication_fakes()

    async def pronounce(ruling):
        pronounced.append(ruling)
        return True

    def send(content, author_id):
        asyncio.run(
            adjudicate_message(
                message(content=content, author_id=author_id),
                self_user=SimpleNamespace(id=999), tracker=tracker, service=service,
                machine=machine, ingest=ingest, pronounce=pronounce,
            )
        )

    send("opening words", 101)
    assert len(ingested) == 1
    send("I refuse to pay anything further", 202)
    assert len(ingested) == 2
    pronounced.clear()
    send("demand a refund for the goods", 101)
    assert [ruling.action for ruling in pronounced] == ["order_refund", "affirm"]
    assert len(ingested) == 2


def test_pronouncement_failure_skips_remaining_service_rulings():
    tracker, service = router()
    machine = StateMachine(load_ruleset())
    ingested = []
    attempts = []

    async def ingest(msg):
        ingested.append(msg)
        return Signal(source=LIVE_SOURCE, payload=msg.content if isinstance(msg.content, str) else "")

    async def pronounce(ruling):
        attempts.append(ruling)
        return False

    def send(content, author_id):
        asyncio.run(
            adjudicate_message(
                message(content=content, author_id=author_id),
                self_user=SimpleNamespace(id=999), tracker=tracker, service=service,
                machine=machine, ingest=ingest, pronounce=pronounce,
            )
        )

    send("opening words", 101)
    send("I refuse to pay anything further", 202)
    attempts.clear()
    send("demand a refund for the goods", 101)
    assert len(attempts) == 1


def test_non_str_content_extracts_empty_text():
    assert pair_event_from(message(content=None)).text == ""


def test_record_receives_one_call_per_processed_message():
    tracker, service = router()
    machine = StateMachine(load_ruleset())
    pronounced, ingested, ingest = adjudication_fakes()
    recorded = []

    async def pronounce(ruling):
        pronounced.append(ruling)
        return True

    def record(*facts):
        recorded.append(facts)

    def send(content, author_id):
        asyncio.run(
            adjudicate_message(
                message(content=content, author_id=author_id),
                self_user=SimpleNamespace(id=999), tracker=tracker, service=service,
                machine=machine, ingest=ingest, pronounce=pronounce, record=record,
            )
        )

    send("opening words", 101)
    send("I refuse to pay anything further", 202)
    send("demand a refund for the goods", 101)
    assert recorded == [
        ("7", "101", None, (("route_to_arbitration", "R-default"),), False),
        ("7", "202", "101", (("route_to_arbitration", "R-default"),), False),
        ("7", "101", "202", (("order_refund", "R1"), ("affirm", "R1")), True),
    ]


def test_record_is_skipped_for_degenerate_messages_but_continuity_holds():
    tracker, service = router()
    machine = StateMachine(load_ruleset())
    pronounced, ingested, ingest = adjudication_fakes()
    recorded = []

    async def pronounce(ruling):
        pronounced.append(ruling)
        return True

    def record(*facts):
        recorded.append(facts)

    degenerate = SimpleNamespace(content="demand a refund", author=None, channel=SimpleNamespace(id=7), reference=None)
    asyncio.run(
        adjudicate_message(
            degenerate, self_user=SimpleNamespace(id=999), tracker=tracker, service=service,
            machine=machine, ingest=ingest, pronounce=pronounce, record=record,
        )
    )
    assert recorded == []
    assert len(pronounced) == 1
    assert len(ingested) == 1


def test_record_failure_is_isolated_from_adjudication(capsys):
    tracker, service = router()
    machine = StateMachine(load_ruleset())
    pronounced, ingested, ingest = adjudication_fakes()

    async def pronounce(ruling):
        pronounced.append(ruling)
        return True

    def exploding_record(*facts):
        raise RuntimeError("ledger disk on fire")

    def send(content, author_id):
        asyncio.run(
            adjudicate_message(
                message(content=content, author_id=author_id),
                self_user=SimpleNamespace(id=999), tracker=tracker, service=service,
                machine=machine, ingest=ingest, pronounce=pronounce, record=exploding_record,
            )
        )

    send("opening words", 101)
    send("I refuse to pay anything further", 202)
    pronounced.clear()
    send("demand a refund for the goods", 101)
    assert [ruling.action for ruling in pronounced] == ["order_refund", "affirm"]
    captured = capsys.readouterr()
    assert "measurement feed failed" in captured.out


def test_record_reflects_the_pronounced_prefix_on_failure():
    tracker, service = router()
    machine = StateMachine(load_ruleset())
    ingested = []
    recorded = []

    async def ingest(msg):
        ingested.append(msg)
        return Signal(source=LIVE_SOURCE, payload=msg.content if isinstance(msg.content, str) else "")

    async def pronounce(ruling):
        return False

    def record(*facts):
        recorded.append(facts)

    def send(content, author_id):
        asyncio.run(
            adjudicate_message(
                message(content=content, author_id=author_id),
                self_user=SimpleNamespace(id=999), tracker=tracker, service=service,
                machine=machine, ingest=ingest, pronounce=pronounce, record=record,
            )
        )

    send("opening words", 101)
    send("I refuse to pay anything further", 202)
    send("demand a refund for the goods", 101)
    assert recorded[0] == ("7", "101", None, (), False)
    assert recorded[1] == ("7", "202", "101", (), False)
    assert recorded[2] == ("7", "101", "202", (), True)
