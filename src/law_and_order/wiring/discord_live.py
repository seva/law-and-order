"""Live Discord wiring layer.

This is the only module that imports discord.py (isolation of fragility).
It connects the dependency-inverted DiscordAdapter to a real gateway.
The bot token is read from the environment only — never from a file,
the repo, or any artifact.
"""

from __future__ import annotations

import json
import os
from collections.abc import Awaitable, Callable
from pathlib import Path

import discord

from ..adapters.discord import DiscordAdapter
from ..adjudication import Observation, SettlementService
from ..enforcement import Enforcement, enforcement_for, parse_enforcement_channels
from ..pairing import PairEvent, PairingTracker
from ..protocol import Ruling, Signal
from ..ruleset import RuleSet
from ..state_machine import StateMachine

DEFAULT_RULESET = Path(__file__).resolve().parents[3] / "rulesets" / "v2.json"
LIVE_SOURCE = "discord-live"


def pair_event_from(message: discord.Message) -> PairEvent | None:
    author_id = getattr(getattr(message, "author", None), "id", None)
    channel_id = getattr(getattr(message, "channel", None), "id", None)
    if author_id is None or channel_id is None:
        return None
    resolved = getattr(getattr(message, "reference", None), "resolved", None)
    referenced_id = getattr(getattr(resolved, "author", None), "id", None)
    content = message.content
    return PairEvent(
        channel=str(channel_id),
        speaker=str(author_id),
        referenced_speaker=str(referenced_id) if referenced_id is not None else None,
        text=content if isinstance(content, str) else "",
    )


def route_paired_event(
    tracker: PairingTracker, service: SettlementService, event: PairEvent
) -> Observation | None:
    counterpart = tracker.resolve(event)
    if counterpart is None:
        return None
    observation = service.observe(event.speaker, counterpart, event.text)
    if observation.settled:
        service.clear(event.speaker, counterpart)
    return observation


async def adjudicate_message(
    message,
    *,
    self_user,
    tracker: PairingTracker,
    service: SettlementService,
    machine: StateMachine,
    ingest: Callable[[object], Awaitable[Signal]],
    pronounce: Callable[[Ruling], Awaitable[bool]],
) -> None:
    if message.author == self_user:
        return
    event = pair_event_from(message)
    observation = route_paired_event(tracker, service, event) if event is not None else None
    rulings = observation.rulings if observation is not None else ()
    for ruling in rulings:
        if not await pronounce(ruling):
            break
    if rulings:
        return
    await pronounce(machine.step(await ingest(message)))


def build_client(
    ruleset: RuleSet,
    ruling_channel_id: int,
    enforcement_channels: frozenset[int] = frozenset(),
) -> discord.Client:
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    async def send(channel_id: int, text: str) -> None:
        channel = client.get_channel(channel_id)
        if channel is not None:
            await channel.send(text)
        else:
            print(f"pronouncement lost: channel {channel_id} not in cache")

    adapter = DiscordAdapter(ruling_channel_id=ruling_channel_id, send=send)
    machine = StateMachine(ruleset)
    tracker = PairingTracker(source_prefix=LIVE_SOURCE)
    service = SettlementService(ruleset, source=LIVE_SOURCE)

    @client.event
    async def on_ready() -> None:
        print(f"gateway ready: logged in as {client.user} (id={client.user.id})")

    @client.event
    async def on_message(message: discord.Message) -> None:
        # DECISION DEBT 2026-08-31: ruling-channel boundary removed; see
        # IMPLEMENTATION.md "Decision Debt". Revisit whether neutral placement
        # is load-bearing for the mission.

        async def ingest(msg: discord.Message) -> Signal:
            envelope = {
                "t": "MESSAGE_CREATE",
                "d": {
                    "channel_id": str(msg.channel.id),
                    "guild_id": str(msg.guild.id) if msg.guild else None,
                    "content": msg.content,
                },
            }
            return await adapter.ingest(json.dumps(envelope), source=LIVE_SOURCE)

        async def pronounce(ruling: Ruling) -> bool:
            try:
                await adapter.publish(ruling)
            except discord.HTTPException as exc:
                print(f"pronouncement failed; enforcement skipped — visible over silent: {exc}")
                return False
            enforcement = enforcement_for(ruling)
            # Scoping decision 2026-09-05 (Owner ruling on issue #8): coercive
            # acts only in designated channels; empty config = advisory
            # everywhere. Pronouncement is unaffected — adjudication stays global.
            if enforcement is Enforcement.DELETE and message.channel.id in enforcement_channels:
                try:
                    await message.delete()
                except discord.HTTPException as exc:
                    print(f"enforcement failed (needs MANAGE_MESSAGES?): {exc}")
            return True

        await adjudicate_message(
            message,
            self_user=client.user,
            tracker=tracker,
            service=service,
            machine=machine,
            ingest=ingest,
            pronounce=pronounce,
        )

    return client


def main() -> None:
    token = os.environ["DISCORD_BOT_TOKEN"]
    ruling_channel_id = int(os.environ["DISCORD_RULING_CHANNEL_ID"])
    enforcement_channels = parse_enforcement_channels(
        os.environ.get("DISCORD_ENFORCEMENT_CHANNEL_IDS", "")
    )
    if enforcement_channels:
        print(f"enforcement scope: {sorted(enforcement_channels)}")
    else:
        print("enforcement scope: advisory everywhere (no channels designated)")
    ruleset_path = Path(os.environ.get("DISCORD_RULESET_PATH", str(DEFAULT_RULESET)))
    ruleset = RuleSet.from_json(ruleset_path.read_text(encoding="utf-8"))
    client = build_client(ruleset, ruling_channel_id, enforcement_channels)
    client.run(token)


if __name__ == "__main__":
    main()
