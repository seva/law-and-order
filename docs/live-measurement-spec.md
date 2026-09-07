# Live Measurement — Specification

Status: specification + component contract. Committed before the component and ahead of the wiring feed it gates. Decide and RAROC forecast: issue #9, 2026-09-07 (session clock; local 2026-09-06 late). UPDATE 2026-09-07: wiring feed + JSONL ledger landed (red d39ae1a, green 94d60bf, Critic repairs per docs/critic-feed-verdict-2026-09-07.md) — the live bot records to logs/measurement.jsonl; replay determinism pinned beyond the window; recorder facts pinned via extracted `build_ledger`/`make_recorder`. Readout tooling remains a separate step.

---

## Why this exists

The live surface has settlement semantics (wiring integration, 2026-09-06): paired messages adjudicate through due process, settlements clear at dispute scope, continuity preserves first-instance behavior everywhere else. What it does not have is measurement. The prime directive's number requires a friction delta measured on conflict produced by minds the project did not author — live human conflict is that surface, and the candidate number (polity-004, 0.172) awaits supersession or confirmation here. This spec pins the apparatus.

## Fractal reuse — the kernel's metric, not a new one

Friction is `topology.Network.friction()` — conflict-edge density over the window's exchange graph; phase is `topology.phase()` at the kernel threshold 0.25 (topology's default parameter; the named constant `CRITICAL_FRICTION` lives in `sim/engine.py` at the same value — single value, two homes, attribution recorded per Critic N6). The monitor builds `Network(nodes, edges, conflict_edges)` per channel from recorded messages and computes nothing novel. Scope.md's kernel pre-adaptation: extensions reuse primitives; scale grows around the kernel, not inside it.

## Event model — what the wiring can honestly report

One recorded message = one window entry. Wiring calls, per processed message:

`record_message(channel, speaker, counterpart, rulings, settled)`

- `channel`, `speaker`, `counterpart` — opaque platform keys (the pairing layer's tokens; `counterpart is None` for unpaired messages).
- `rulings` — the (action, rule_id) pairs pronounced on that message, service-governed or legacy continuity path; empty when nothing pronounced.
- `settled` — whether the service observation settled the dispute on that message.

No text parameter exists. Privacy (Security principle): live humans, not personas — the ledger and the monitor persist keys, counts, actions, rule ids, digests; never message content. The API makes content-capture unrepresentable, not merely avoided; the red contract pins the signature.

Self-pairing degeneracy (disclosed per Critic N7): `record_message` with speaker == counterpart produces a degenerate self-edge counting toward friction — the monitor is garbage-in-garbage-out by contract; the pairing layer excludes self-pairs (`resolve` returns either a distinct counterpart or None), so the wiring feed cannot produce one.

## Conflict edge — the live definition

An exchange is **conflicted** iff at least one pronounced ruling on it is legislative-visibility: `rule_id` not in {R-default, R0, R-boundary} AND `action` not in `INERT_ACTIONS`. Rule-match or appellate rulings are conflict; `route_to_arbitration`, `drop`, `reject_oversize`, and silence are not. Rationale: the measurement must stay content-sensitive (Phase 8's lesson — a metric blind to content is a property of the arena, not the conflict), and legislative visibility is exactly "the law saw this exchange." Degeneracy avoided: the legacy continuity path pronounces on every message, but only matched pronouncements mark conflict, so chat-heavy channels measure low-friction instead of saturated 1.0.

## Graph construction per window

- **Nodes:** every speaker, plus every resolved counterpart.
- **Edges:** one per entry with `counterpart ≠ None` — the pair {speaker, counterpart}; unpaired entries contribute nodes only.
- **Conflict edges:** the subset of edges whose entry was conflicted.
- Repeated pairs within the window are one edge (`frozenset` semantics, as in the sim engine); an edge is conflicted if ANY of its entries in the window was conflicted.

## Window semantics

Sliding, per channel, bounded by `MEASUREMENT_WINDOW = 100` recorded messages (declared initial legislative value, pinned by test — the Lesson-Mechanism bar: constants get equality pins, not parametric coverage). Rationale for count over wall-clock: replay determinism from the event sequence alone; no clock enters the measurement, mirroring the no-wall-clock constraint. Eviction is FIFO per channel; channels never share windows (pairing isolation carried through).

## Settlement decay — the delta's live mechanism

A settled message is itself conflicted (its rulings were pronounced — historical fact). Decay is what follows: the pair's memory clears, fresh disputes start unripe, and unripe/continuity exchanges are non-conflict edges. As the window advances past the settlement, the pair's edges fall out of the conflict set — friction decays without any baseline epoch. Pinned: (a) settlement annotation does not retroactively un-conflict recorded entries; (b) post-settlement silent exchanges are non-conflict; (c) after a full window of silent exchanges, friction returns below CRITICAL_FRICTION.

## Delta methodology, declared honestly

- **Immediate apparatus (this component):** the friction trajectory per channel under the installed protocol, with settlement decay as the order-producing mechanism. What it measures: whether legislation + due process produce declining conflict density on live, non-authored conflict — with a disclosed degeneracy (Critic N6): the spike-and-decay shape is not settlement-specific. Any conflict concentration decays after `MEASUREMENT_WINDOW` messages by window turnover alone; the settlement annotation is not a causal force inside the monitor. What settlement causally changes is FUTURE conflict production (a cleared pair adjudicates unripe instead of rematching), which trajectories across many windows distinguish from phrase exhaustion only statistically. The epoch methodology exists precisely to close this gap; until it runs, trajectory claims must name this degeneracy.
- **Gold standard (dependency, declared not faked):** baseline-vs-installed epochs per channel require the staged stand-up and a pronunciation-scope configuration (observe-only epochs) — Owner-led surfaces. The ledger format is designed so epoch boundaries are annotations, not migrations.
- **Candidate relation:** polity-004's 0.172 is a sim-semantics measurement on provenance-evidenced non-authored content. A live trajectory that settles real human disputes at declining friction supersedes it as the prime-directive evidence; the booking remains the Owner's act either way.

## Observe-only isolation

The monitor cannot influence adjudication: wiring feeds it AFTER routing and pronouncement decisions; feed failures are logged and never propagate into the ruling path (no silent failures — logged; no blocking — isolated). The measurement apparatus is downstream of the law, never upstream.

## Ledger (wiring-feed step, declared here)

Append-only JSONL under `logs/` (gitignored): one record per message with the same fields as `record_message`, plus per-record sequence index. Replay = feeding the ledger into a fresh monitor reproduces the identical friction series (determinism pin extends to the ledger). Rotation: unbounded growth is the disclosed live-daemon risk (walrus 2026-09-06); rotation policy is an ops follow-up, not silently deferred.

## Open items (declared, not hidden)

1. `MEASUREMENT_WINDOW` value (100) has no empirical base — legislative, pinned, changeable with a re-pin.
2. Cross-channel aggregation: deferred; per-channel series first, aggregation is a reporting question for the harness step.
3. Ledger rotation policy — ops follow-up, disclosed risk until decided.
4. Epoch configuration (observe-only pronunciation scope) — gold-standard dependency, Owner-led, named not built.

## Verification — red contract (`tests/test_measurement.py`)

1. Empty channel: friction 0.0, phase ORDERED (kernel constant reused).
2. Unpaired messages: nodes without edges; friction 0.0.
3. Matched rulings create conflict edges; friction and phase follow kernel semantics.
4. Default (`route_to_arbitration`/R-default), unvalued (`drop`/R0), boundary (`reject_oversize`/R-boundary), and inert-action pronouncements are edges WITHOUT conflict.
5. Appellate rulings (affirm/overturn with merits rule ids) are conflicted.
6. Settlement: annotation non-retroactive; post-settlement silent exchanges non-conflict; after a full window of silence, friction < CRITICAL_FRICTION.
7. Window bound: `MEASUREMENT_WINDOW == 100` equality-pinned; eviction FIFO per channel; channels isolated.
8. Replay: identical event sequences into independent monitors produce identical friction and phase at every step.
9. Content-privacy: `record_message`'s signature admits no text-like parameter (pinned via inspect); records are frozen slots.
10. Phase reuse: monitor phase == `topology.phase(monitor network)` — no private constant.

Component step gates: ARCHITECTURE.md component row same-commit; suite green; module coverage 100% or classified; gate (`tests/test_constitution_hygiene.py`) green after any record edit.
