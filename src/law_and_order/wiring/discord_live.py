"""Live Discord wiring layer.

This is the only module that imports discord.py (isolation of fragility).
It connects the dependency-inverted DiscordAdapter to a real gateway.
The bot token is read from the environment only — never from a file,
the repo, or any artifact.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import discord

from ..adapters.discord import DiscordAdapter
from ..ruleset import RuleSet
from ..state_machine import StateMachine

DEFAULT_RULESET = Path(__file__).resolve().parents[3] / "rulesets" / "v2.json"


def build_client(ruleset: RuleSet, ruling_channel_id: int) -> discord.Client:
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    async def send(channel_id: int, text: str) -> None:
        channel = client.get_channel(channel_id)
        if channel is not None:
            await channel.send(text)

    adapter = DiscordAdapter(ruling_channel_id=ruling_channel_id, send=send)
    machine = StateMachine(ruleset)

    @client.event
    async def on_message(message: discord.Message) -> None:
        if message.author == client.user:
            return
        # DECISION DEBT 2026-08-31: ruling-channel boundary removed; see
        # IMPLEMENTATION.md "Decision Debt". Revisit whether neutral placement
        # is load-bearing for the mission.
        envelope = {
            "t": "MESSAGE_CREATE",
            "d": {
                "channel_id": str(message.channel.id),
                "guild_id": str(message.guild.id) if message.guild else None,
                "content": message.content,
            },
        }
        signal = await adapter.ingest(json.dumps(envelope), source="discord-live")
        ruling = machine.step(signal)
        await adapter.publish(ruling)

    return client


def main() -> None:
    token = os.environ["DISCORD_BOT_TOKEN"]
    ruling_channel_id = int(os.environ["DISCORD_RULING_CHANNEL_ID"])
    ruleset_path = Path(os.environ.get("DISCORD_RULESET_PATH", str(DEFAULT_RULESET)))
    ruleset = RuleSet.from_json(ruleset_path.read_text(encoding="utf-8"))
    client = build_client(ruleset, ruling_channel_id)
    client.run(token)


if __name__ == "__main__":
    main()
