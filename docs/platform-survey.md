# Platform Survey — Phase 2 Discovery

Date: 2026-08-21. Status: **hard gate for Phase 3 — satisfied pending owner beachhead selection.**
Sources: official documentation via web research (Discord Developer Docs, Reddit Data API Wiki / asyncpraw docs, Slack Developer Docs), current as of mid-2026.

Dimensions Phase 3 requires: ingest model, publish path, auth model, rate limits, moderation/enforcement surfaces, statelessness fit.

---

## Discord

- **Ingest:** Gateway push (websocket), `MESSAGE_CREATE` events; 120 gateway commands per 60s per connection. Stateless ingest maps directly: event in → `Signal` out.
- **Message content:** `MESSAGE_CONTENT` privileged intent required for arbitrary message text. Free toggle below **10,000 unique users** reach (threshold changed June 2026 from server count to user reach); review + annual reapplication above. **Exemptions that need no intent:** DMs to the bot, @mentions of the bot, replies to the bot's own messages.
- **Publish:** REST `POST /channels/{id}/messages`, ~5 messages / 5s per channel; global 50 req/s per token; parse `X-RateLimit-*` headers.
- **Auth:** bot token; intents enabled both in Developer Portal and client code.
- **Enforcement surfaces (complete):** timeout up to 28 days (`MODERATE_MEMBERS`), ban, kick, message delete / bulk delete (`MANAGE_MESSAGES`, bulk limited to messages <14 days), audit-log reasons. **AutoMod is fully API-manageable** (keyword/spam/mention-spam rules; block/alert/timeout actions) and runs server-side — it can carry crude pattern work while the kernel handles nuanced arbitration.
- **Constraints:** role hierarchy — the bot's highest role must exceed the target's; verification required near 100 servers.
- **SDK:** discord.py, mature async.

**Fit:** strongest. Push ingest, full enforcement toolkit, and the sub-10k-user intent exemption matches beachhead scale exactly. Highest conflict density of the three — the largest measurable friction delta, which is what proof (DoS condition 2) requires.

## Reddit

- **Ingest:** asyncpraw 8.x streams — `modqueue`, `reports`, `spam`, `unmoderated`, mod log; comment/submission trees give persistent, threaded disputes (good raw material for identity-free Dispute extraction).
- **Publish:** comments / distinguished comments; removal messages to authors.
- **Auth:** script-type OAuth app, password grant; tokens ~1h with automatic refresh; `client_credentials` is read-only (insufficient).
- **Rate limits:** 100 queries/min per OAuth client, averaged over 10 minutes; ~60 QPM the practical sustained rate; headers exposed (`X-Ratelimit-*`).
- **Enforcement surfaces:** approve, remove (with removal reasons), distinguish, lock/unlock, ignore reports, moderator notes. No user-level sanctions (no timeout/ban equivalent at subreddit level via these surfaces — user bans exist but are coarse).
- **Platform risk (decisive):** all API apps must be registered/confirmed by **30 September 2026**; Reddit is migrating mod automation toward Devvit (its own platform). Classic Data API access for registered mod bots persists "for now." Building the first production beachhead on a surface under active contraction violates isolation-of-fragility in the worst direction — the fragility is the platform's intent, not its instability.

**Fit:** strong dispute material, weak and shrinking foundation.

## Slack

- **Ingest:** Events API over HTTP (signed HMAC-SHA256, 3s ack — production path) or Socket Mode (websocket, no public endpoint — dev/firewalled; ~10 concurrent connections; barred from Marketplace).
- **Publish:** `chat.postMessage`, Special tier: ~1 message/s per channel plus a workspace-wide cap; 429 + `Retry-After`.
- **Auth:** bot token + signing secret; granular scopes; `conversations.history` dropped to Tier 1 (1 req/min) for non-Marketplace distributed apps since May 2025.
- **Enforcement surfaces (disqualifying):** a standard app can delete **only its own messages**. Arbitrating user content requires Enterprise org admin scopes or the partner-only Discovery API. Native moderation UI (pause replies, hide threads) is not exposed to ordinary apps.
- **Fit:** an arbitration agent whose rulings cannot be enforced is advisory, not judicial. Slack fails the enforcement requirement at standard-app tier; conflict density is also the lowest of the three.

---

## Comparison

| Dimension | Discord | Reddit | Slack |
|---|---|---|---|
| Ingest model | gateway push | asyncpraw streams (polling/pseudo-stream) | Events API / Socket Mode |
| Content access | intent-gated, free <10k users | open (auth) | scopes; history tiered down |
| Publish limits | ~1 msg/s per channel | 100 QPM shared budget | ~1 msg/s per channel |
| Enforcement | **complete** (timeout/ban/delete/AutoMod) | content-level only (remove/lock/distinguish) | **none for standard apps** |
| Stateless fit | natural (event → Signal) | natural (item → Signal) | natural (event → Signal) |
| Platform risk | intent policy drift (manageable) | **registration deadline 2026-09-30 + Devvit migration** | tier erosion |
| Conflict density | high (real-time chat) | medium (threads) | low (workplace) |

---

## Beachhead recommendation: Discord

RAROC reasoning:

- **V = 5** — complete enforcement surface means rulings can be self-enforcing (the scope.md Axis II requirement), and maximal conflict density maximizes the measurable friction delta — the exact quantity proof must demonstrate.
- **P = 0.8** — sub-10k-user intent exemption, mature async SDK, server-side AutoMod offloads crude pattern work; residual risk is intent-policy drift.
- **C = 2** — bot creation, test community, role setup, adapter + fixtures.
- **RAROC ≈ 2.0**, above Reddit (≈1.0: good surfaces × contracting platform) and Slack (≈0.3: no enforcement).

Mitigations adopted:

1. Design ingest to degrade without `MESSAGE_CONTENT`: mention/reply/DM paths and slash-command interactions remain functional if the intent is revoked; classify() receives whatever content arrives.
2. AutoMod carries marker-level filtering at the platform layer; the kernel adjudicates what AutoMod cannot — separation of crude and nuanced arbitration.
3. Deployment contract: bot requires a moderation role above ordinary members (role hierarchy is a configuration fact, recorded at install).

**Selection remains owner-gated** (IMPLEMENTATION.md Phase 2). This recommendation is the survey's output; the decision is the owner's.

---

## Open items for Phase 3 (Discord, if selected)

1. Bot account + application, `MESSAGE_CONTENT` toggle, moderation role in a test community
2. Recorded raw-payload fixtures for adapter tests (ingest/publish/statelessness)
3. Ruling publication shape: reply-with-ruling vs dedicated arbitration channel vs thread
4. AutoMod rule template as part of the installed protocol (compute subsidization at the platform layer)
5. Friction measurement hook: how conflict-edge density is sampled from channel activity (feeds topology.py)
