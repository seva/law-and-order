# Architecture

---

## Principles

**Separation of concerns** — auth, storage, transport, business logic, and interface layers are separate modules. No cross-cutting logic.

**Isolation of fragility** — unstable dependencies (external APIs, undocumented interfaces, third-party services) are contained in a single module. When they change, only that module updates. Nothing else knows about their internal shape.

**Security** — sensitive data never in plaintext on disk or in logs. Secrets never surfaced in tool or API output.

---

## Coding Hygiene

Guard clauses. Graceful degradation. No silent failures. Explicit error types.

Code as documentation — names and structure must be self-explanatory. Comments explain why, not what. Maximize semantic and cognitive ROI.

---

## Engineering Invariants

Enforced at audit (METHODOLOGY.md Post-Phase Audit, item 5). Deviations must be declared in `AGENTS.md` Conventions with rationale — undeclared violations are gaps.

**Boundary defense** — all untrusted input (HTTP parameters and bodies, queue messages, environment variables, files from other systems) passes a runtime schema parser at the ingestion boundary. Internal code trusts validated contracts and omits redundant defensive checks for guaranteed fields. Never pass unvalidated dynamic types into domain functions.

**Re-entrant mutations** — every state-altering operation (write endpoints, queue consumers, scheduled jobs) accepts an idempotency key or deterministic deduplication token, checked atomically before execution, with the result written back on completion. Financial and counter mutations never execute without an explicit transaction lock or idempotency guard.

**Non-destructive schema evolution** — migrations run Expand → dual-write → backfill → Contract, each in a distinct deployment; forward- and backward-compatible with N−1 running instances. Substrates that cannot contract (deployed smart contracts, append-only stores) substitute versioned parallel deployment; the substitution is recorded under Constraints.

**Vertical slice locality** — code grouped by domain feature, not technical layer. A feature slice co-locates its route, schema, domain rules, and queries. A single business-capability change touching more than three distinct folders is a design smell — reject or document the exception.

**Indirection cap** — at most three hops within a feature domain: handler → domain rule → persistence. Abstractions generalize only after the same logic occurs at ≥3 production call-sites (Rule of Three).

---

## Banned Patterns

| Pattern | Replacement |
|---|---|
| Generic repository abstraction over the ORM | Native ORM queries or type-safe compiled SQL directly in the slice |
| Premature microservices | Modular monolith with language-enforced visibility boundaries |
| Global DRY across bounded contexts | Context-local duplication; integrate through contracts, not shared models |
| Speculative OOP (AbstractFactory, Strategy/Visitor classes for one implementation) | Functions, guard clauses, native pattern matching |
| Unstructured logging | Structured logs with correlation/trace/tenant IDs propagated across async boundaries |
| Mock-testing internal boundaries; tautological tests asserting mock calls | Real ephemeral dependencies (Testcontainers or local instances); mocks only for external third-party APIs |

---

## Invariant Applicability (migration M6, 2026-09-07 — declarations per the deviation rule)

| Invariant / pattern | Status here | Basis |
|---|---|---|
| Boundary defense | PARTIAL — declared deviation | Adapter ingest validates envelope shape by guard clauses with explicit `ValueError`s (`adapters/discord.py`: event type, dict `d`, required `channel_id`/`content`); payload is opaque text to the pure kernel; env config is fail-fast validated (launcher, `parse_enforcement_channels`). A runtime schema parser is deferred until a second live input surface exists; deviation declared in AGENTS.md |
| Re-entrant mutations | ADOPTED by equivalent | Kernel is pure (no mutations to re-enter); the live surface's re-entrancy control is the launcher single-instance guard (demonstrated live 2026-09-06: duplicate startup refused); delete actuation is idempotent per message (second delete → logged HTTP failure); ledger seq is the dedup token, single-writer by the same guard |
| Non-destructive schema evolution | ADOPTED via substitution | No database; the JSONL ledger is append-only — a substrate that cannot contract. Substitution (per the invariant's own clause, recorded under Constraints): schema changes use versioned parallel files, never in-place migration |
| Vertical slice locality | DEVIATION — declared | The kernel is layered by constitutional design: the fractal primitive chain (Signal → classify → RuleSet → Dispute → Ruling → friction) IS the product (docs/scope.md — scale grows around the kernel, not inside it). Capability changes touch one layer's contract + records; the three-folder smell targets route/schema/query sprawl, which has no analogue here |
| Indirection cap | COMPLIANT under declared interpretation | Hops count to the actuation/persistence boundary; kernel-internal delegation (wiring → adjudicate → service → machine) is the domain-rule layer's interior, not added hops |
| Generic repo abstraction / premature microservices / global DRY / speculative OOP | N/A or compliant | No ORM, single process; single-source settlement semantics is contract-sharing (the prescribed replacement form); frozen dataclasses + functions throughout |
| Unstructured logging | GAP — declared, backlog filed | Wiring prints unstructured lines to `logs/discord_bot.log`; structured lines (ts/level/event/message-id correlation) are an independent atomic step (live-visible change, own verification) — issue #11 backlog; deviation declared until landed |
| Mock-testing internal boundaries | COMPLIANT under declared interpretation | Injected fakes sit at the Discord-gateway boundary (external third-party, untestable without a live gateway); mutation-probe verification is the anti-tautology evidence (AGENTS.md deviation, migration M5) |

---

## System Diagram

```
[LLM legislative layer]   (planned) offline: ruleset synthesis, conflict-edge sensing
        |  candidate Rules, frozen into versioned RuleSet
        v
     [RuleSet]
          \
Platform (Discord / Reddit / Slack / simulation)
        |  raw message
        v
[PlatformAdapter.ingest]   stateless, no session retained
        |  Signal(source, payload)
        v
[StateMachine.step]   ruleset + boundaries injected
        |  oversize          -> Ruling(reject_oversize, R-boundary)
        |  unvalued          -> Ruling(drop, R0)
        |  rule match        -> Ruling(rule action, boundary-checked)
        |  no match          -> Ruling(route_to_arbitration, R-default)
        v
[Arbitrator.resolve]       identity-free Dispute(claim, counterclaim)
        |  Ruling(action, rule_id)
        v
[Appellate.resolve]        Appeal(dispute, ruling, ground) — due process
         |  Ruling(affirm | overturn, merits rule)
         |
[SettlementService]      adjudication.py: stateful institutional memory above the
         |               stateless adapter contract — last-said per pair, res judicata;
         |               reaction.py: ACCEPT | APPEAL | REJECT per (ruling, stance, side)
         |  both ACCEPT or appellate affirm -> settled; overturn / REJECT -> persists
         v
[PlatformAdapter.publish]
        |
[wiring/discord_live.py]   live Discord surface: gateway connect, on_message loop;
                           sole discord.py importer; token from environment only

[Network / phase]          friction = conflict-edge density; DISORDERED -> ORDERED
```

_Last verified: 2026-09-07_

---

## Components

| Component | Responsibility | Key interface |
|---|---|---|
| `src/law_and_order/protocol.py` | Immutable core types and boundary enforcement | `Signal`, `Ruling`, `BoundaryConstraints.permits`, `SignalKind`, `Phase` |
| `src/law_and_order/ruleset.py` | Compute subsidization: canonical compressed rulesets | `Rule`, `RuleSet.ordered / canonical / compressed_size / from_json` |
| `src/law_and_order/state_machine.py` | Zero-emotional-latency transitions; classify and route signals | `StateMachine.step(Signal) -> Ruling`, `classify` |
| `src/law_and_order/arbitration.py` | Identity-free neutral arbitration | `Arbitrator.resolve(Dispute) -> Ruling` |
| `src/law_and_order/appeals.py` | Appellate instance: due-process review of contested rulings | `Appeal(dispute, ruling, ground)`, `Appellate.resolve(Appeal) -> Ruling` |
| `src/law_and_order/reaction.py` | Mechanism 3 reaction layer: stance extraction and party reaction to rulings — arena policy, not legislation | `stance_of(statement) -> Stance`, `react(ruling, statement, party) -> Reaction`, `Stance`, `Party`, `Reaction` |
| `src/law_and_order/adjudication.py` | Settlement semantics as a reusable stateful service above the stateless adapter contract (Open Question 5 option a): institutional memory — last-said text per speaker pair, res-judicata on settled pairs — delegating to StateMachine, reaction, and Appellate; single source, the sim engine consumes it | `SettlementService(ruleset, source, boundaries).observe(speaker, counterpart, text) -> Observation(rulings, settled)`, `note(speaker, counterpart, text)`, `is_settled(speaker, counterpart)`, `clear(speaker, counterpart)`, `Observation`, `INERT_ACTIONS` |
| `src/law_and_order/pairing.py` | Live pairing policy (live-wired 2026-09-06): maps platform message events to dispute pairs — reference-first, adjacency fallback over bounded per-channel recency; opaque speaker keys are routing state, never merits input | `PairEvent(channel, speaker, referenced_speaker, text)`, `PairingTracker(source_prefix).resolve(event) -> str \| None`, `dispute_key(speaker, counterpart)`, `RECENCY_WINDOW` |
| `src/law_and_order/measurement.py` | Live friction monitor — the measurement apparatus over the live surface (docs/live-measurement-spec.md): sliding per-channel window of recorded messages; conflict edge = legislative visibility (rule-match/appellate rulings; default/inert/boundary are plain edges); kernel `Network` supplies friction and phase; observe-only, message content inadmissible by signature | `LiveFrictionMonitor(window).record_message(channel, speaker, counterpart, rulings, settled)`, `network(channel)`, `friction(channel)`, `phase(channel)`, `Exchange`, `MEASUREMENT_WINDOW` |
| `src/law_and_order/ledger.py` | Live measurement persistence: append-only JSONL of processed messages (seq, channel, opaque keys, ruling action/rule-ids, settled — message text inadmissible by fields); `replay` reconstructs the identical friction series (docs/live-measurement-spec.md) | `JsonlLedger(path).append(channel, speaker, counterpart, rulings, settled)`, `JsonlLedger.touch()`, `replay(path) -> LiveFrictionMonitor` |
| `src/law_and_order/enforcement.py` | Enforcement policy: pure content-addressed mapping from rulings to enforcement acts — advisory to judicial (step 1: DELETE on `drop`/`reject_oversize`, pronounce-only otherwise) | `enforcement_for(ruling) -> Enforcement`, `Enforcement` |
| `src/law_and_order/topology.py` | Network friction metric and phase detection | `Network.friction()`, `phase(Network)` |
| `src/law_and_order/polity.py` | Transcript adjudication: offline rulings, appeal re-hearing, and settlement analysis for polity records | `load_transcript`, `adjudicate`, `adjudicate_appeals`, `settlement_signals`, `final_settlement`, `analyze` |
| `src/law_and_order/adapters/base.py` | Stateless platform adapter contract; shared ruling renderer | `PlatformAdapter` protocol: `ingest`, `publish`; `render_ruling` |
| `src/law_and_order/adapters/discord.py` | Discord adapter: MESSAGE_CREATE ingest, ruling publication to a dedicated arbitration channel | `DiscordAdapter(ruling_channel_id, send)` implements `PlatformAdapter` |
| `src/law_and_order/adapters/sim.py` | Simulation adapter: dispute-event ingest, ruling emission | `SimAdapter(on_ruling)` implements `PlatformAdapter` |
| `src/law_and_order/sim/population.py` | Deterministic conflict population | `Persona`, `default_population()` |
| `src/law_and_order/sim/engine.py` | Simulation production surface: round-based conflict dynamics, protocol installation, friction measurement; settlement semantics delegated to `adjudication.SettlementService` (single source) — matched non-inert rulings publish, settlement only via both-ACCEPT (dead letter under the initial table) or appellate affirm, overturn/REJECT persist, unripe disputes (counterpart never spoke) emit no ruling | `run(population, rounds, seed, installed, ruleset)` |
| `src/law_and_order/wiring/discord_live.py` | Adapter bound to a real gateway; sole discord.py importer; token env-only; scoped enforcement, default advisory; pairing + settlement: PairEvent → `Routing`, settle → clear, service-silent → first-instance continuity (docs/live-pairing-spec.md); measurement feed observe-only, isolated — ledger logs/measurement.jsonl (docs/live-measurement-spec.md) | `build_client(ruleset, ruling_channel_id, enforcement_channels)`, `main`, `pair_event_from`, `route_paired_event`, `adjudicate_message`, `make_recorder`, `build_ledger`, `Routing` |

_Last verified: 2026-09-07_

---

## Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| State immutability | `frozen=True, slots=True` dataclasses throughout | "Stateless protocol wrappers with immutable boundary constraints" — mutation is unrepresentable rather than policed |
| Bribe resistance | `Dispute` carries claim/counterclaim text only, no party identities | Rulings cannot depend on who disputes; neutrality by construction, not by intention |
| Tie-break | SHA-256 comparison of claim texts | Deterministic, symmetric, status-free; identical disputes always yield identical rulings |
| Unvalued text | Marker-based `classify()` routes to `drop` (R0) | Deterministic baseline; classifier is a pure function, replaceable without touching the state machine |
| Noise-filter generalization (Mechanism 2, 2026-09-05) | `UNVALUED_MARKERS` 7 → 48: 41 markers in five systematic families; families chosen over memoized classifier (spec Q2) | Catches 53/60 unauthored noise lines (12/12, 22/24, 19/24); 7 residuals disclosed not fitted (`rat` excluded — hits valued claims). Gates held: claims/transcript/nonsense stay valued; measurements byte-identical — no noise line fired a rule match. Live effect: noise drops at R0, actuation-capable. Detail + repairs: docs/content-sensitivity-spec.md §2, docs/critic-mechanism2-verdict-2026-09-05.md |
| Forbidden actions | `BoundaryConstraints` checked at every emission point | `retaliate`, `extract_credit`, `status_claim` become `abstain` regardless of ruleset content |
| Appellate instance | Merits re-adjudication: the dispute re-ruled under the ruleset in force; affirm iff merits match the contested action; ground is provenance, never merits input; one instance — affirm exhausts due process | Due process as a pure, identity-free, deterministic function of (dispute, contested ruling, ground): outcome depends on the law in force, not appeal rhetoric; ground-consuming merits were gameable (Phase 6 — docs/polity-001/record.md). Under stance-blind v1 the appeal affirmed: teeth require legislative evolution (v2 row) |
| Stance-aware matching (v2) | Ordered stance markers before general content match: refusal (`decline/refuse the refund`), contestation (`dispute the`) rule first; v1 frozen as legislative history | Stance as content markers — deterministic, no LLM at the ruling seam. Measured 2026-08-24: first-instance discrimination flips; appellate under v2 OVERTURNS the contested [R1] — teeth arrive with legislative evolution; v1 settlement stands res judicata (docs/polity-001/record.md) |
| Error handling | Total functions on the ruling path: every input yields a `Ruling`; rejection is an action (`drop`, `abstain`, `reject_oversize`), never an exception | Coding Hygiene's "explicit error types" is satisfied by explicit rejection actions; exceptions would add non-deterministic control flow and untracked failure states |
| Catch-all auto-resolution removed (Phase 8 Mechanism 1, 2026-09-01) | Sim engine: a dispute resolves only on a matched non-inert rule; unmatched disputes persist and keep generating conflict | The delta must be a function of conflict content and legislative coverage (docs/content-sensitivity-spec.md). Measured: polity-002 + v2 → 0.773; nonsense / empty-ruleset → 0.000 — the nonsense test flips and stands. Saturation caveat (4-pair topology, binary delta) resolved by polity-003 (next row) |
| Polity-003 arena (saturation break, 2026-09-02) | Eight minds under opposed mandates across four domains, generated by four separate subagent instances; 9-pair symmetric counterpart graph; v2-minus-R7 as legislative probe | Measurement must grade coverage — polity-002 saturated binary. Graded values: match-era 0.212 full / 0.110 probe / 0.000 nonsense; settlement-era 0.166 full (tail 0.264 DISORDERED) / 0.000 / 0.000; polity-002 0.413. Full numbers, provenance, limits: docs/polity-003/record.md |
| Polity-004 arena (provenance-first polity, 2026-09-05) | Mandates committed BEFORE generation (8c1a04b); outputs persisted with sha256 + ids; assembly machine-verified; corroboration persisted (corroboration.json) | Critic falsified booking: non-authorship was reported, not evidenced — now machine-checkable (docs/polity-004/protocol.md, docs/polity-004/record.md). Measured 0.000 under the initial reaction table (zero appeals), 0.172 after generalization (4/9 settled via appellate affirm); nonsense flips. Booking remains the Owner's act; provenance proves integrity, not strong unauthorship |
| Engine settlement semantics (Mechanism 3, 2026-09-04) | Adjudication fires on a matched non-inert ruling once both have spoken (unripe: none); first-instance publishes; parties react per `reaction.py`; settlement = both-ACCEPT (dead letter) or appellate affirm; overturn/REJECT/procedural persist; pins re-forge at changes | The delta grades what settles, not what matches — sensitive to ruling quality (a wrong-stance refund order can be overturned on a marker-carrying counterclaim). Settlement rate = affirm rate; order harder than coverage (docs/polity-003/record.md, tests/sim/) |
| Settlement service extraction (Open Question 5 option a, 2026-09-06) | Settlement semantics in `adjudication.SettlementService` — stateful memory above the stateless adapter contract; the engine delegates; `source="sim"` preserves digests | Adapters stay stateless; live gains measured semantics. Rejected: (b) adapter statefulness exception; (c) first-instance-only live tier (no advance). First cut dropped the initiation feed — falsified by differential vs the pre-refactor tree, repaired (`note()`); false parity claim corrected: docs/critic-adjudication-verdict-2026-09-06.md |
| Live pairing policy (spec + component, 2026-09-06) | `pairing.py` per `docs/live-pairing-spec.md`: reference-first, adjacency fallback (window 8), self-refs ignored, channels isolated, digest convention tied by test; wired live same day (11837ea) | The envelope drops identity at the seam by design; pairing supplies the opaque routing keys service memory needs, never merits input. Digest-provenance widening: Owner interpretation item (alias-map mitigation in spec). Res judicata: finality to the dispute, not the pair. Bounded memory degrades to continuity, never garbage |
| Reaction layer (Mechanism 3 step 2, 2026-09-02) | `reaction.py` — arena policy: `stance_of` extracts CLAIM/REFUSAL/NEUTRAL by markers (REFUSAL wins overlap; families generalized 2026-09-05); `react` total, REJECT-default; favorability = final favorable actions only (`order_refund`) | Pure-function semantics preceded engine integration; legislation and arena policy evolve independently — overlap creates no coupling. Settlement exists only where declared policy says so; both-ACCEPT measured unreachable — every settlement via appellate affirm. Detail: docs/mechanism3-reaction-spec.md |
| LLM seam | Legislative and sensing layers only: ruleset synthesis, conflict-edge sensing, optional content-hash-memoized classification. Never at ruling emission | The judicial layer must remain a pure function of (signal, ruleset, boundaries). Non-determinism is confined to producing frozen, versioned rulesets, which are auditable via canonical form; memoization restores per-content determinism for classification |
| Beachhead platform | Discord | Survey (`docs/platform-survey.md`): complete enforcement surface (timeout/ban/delete/API-manageable AutoMod) enables self-enforcing rulings — the proof requirement; MESSAGE_CONTENT free below 10k unique users; maximal conflict density maximizes the measurable friction delta. Slack cannot enforce rulings at standard-app tier; Reddit's surface is contracting (registration deadline 2026-09-30, Devvit migration) |
| Adapter dependency inversion | `DiscordAdapter` takes an async `send` callable and immutable config; discord.py is confined to the live wiring layer | Isolation of fragility: SDK churn touches only wiring; adapter tests run dependency-free against spec-accurate fixtures |
| Ruling publication | Dedicated arbitration channel, fixed at construction | Rulings are published to a dedicated channel (destination is immutable config, not session state). DECISION DEBT 2026-08-31: the ruling-channel input boundary was removed in the live wiring, so replies in the ruling channel are now ingested as disputes; the neutral-placement property ("rulings go out, disputes come in") is no longer enforced — see IMPLEMENTATION.md "Decision Debt" for the revisit question |
| Identity-free ingest | `Signal` carries channel origin and content only; author identity is dropped at the seam | The judicial layer never sees who spoke; neutrality begins at sensing |
| Inaugural ruleset | `rulesets/v1.json` — canonical JSON, versioned by filename and git, LF-guarded via `.gitattributes` for byte stability | The legislative layer's first frozen artifact: canonical form is the interchange format, round-trip integrity is testable, and the constitutional immune system (boundary compliance, unique ordered ids) is enforced by tests at load time |
| Production-surface inversion | Self-generated production surfaces, autonomously stood up; external platforms are optional expansions, never gates | Production is what the project generates; no step may require owner action or provisioning. Seed-7 measurement, equality-pinned (tests/sim/test_engine.py): delta 0.477 (baseline 0.538 → installed 0.061), 7/7 resolved, 45 published; the once-advertised 0.538 → 0.000 was match-era (2026-08-23), stale since 2026-09-04 — corrected via docs/critic-adjudication-verdict-2026-09-06.md. Falsification proceeds against real minds in controlled polities |
| Owner sanction | Autonomy is the default regime, not an absolute: the owner may sanction violations by prompt | The owner stands outside the cycle as its legislative layer; a sanctioned prompt is an auditable constitutional act and the only legitimate path by which external dependencies enter the cycle. Absent sanction, the cycle never stalls on external provisioning. Sanction is permission, not provision: prerequisites block the deployments they gate — honestly — but their resolution is autonomous stand-up by the cycle, never owner labor |
| Live enforcement (Discord step b, 2026-09-05) | Pure content-addressed mapping (`enforcement.py`); the act executes in wiring; pronounce-first; enforcement skips on failure; failures logged, never silent | Follows content-based rulings mechanically; requires MANAGE_MESSAGES. TIMEOUT/AutoMod unassigned. `reject_oversize` unreachable on Discord (4096 > 2000) — only `drop` actuates; publish-then-delete digests reference vanished messages. Owner ruling (issue #8): channel-scoped via `DISCORD_ENFORCEMENT_CHANNEL_IDS`, default empty = advisory everywhere; pronouncement/adjudication global |
| Language | Python 3.11+ first, TypeScript parity later | Listed platforms (Discord, Reddit, Slack) all have mature async Python SDKs; kernel is pure and portable |

_Last verified: 2026-09-07_

---

## Constraints

- Python 3.11+; async-first for all platform-facing code
- No randomness and no wall-clock dependence in any ruling path
- `BoundaryConstraints.forbidden_actions` are never emitted: `retaliate`, `extract_credit`, `status_claim`
- Adapters are stateless: every `ingest`/`publish` call is self-contained; no session state retained
- Platform SDKs are confined to adapter modules (isolation of fragility)
- LLM output never emits a ruling directly; it enters the kernel only as candidate `Rule`s frozen into a versioned `RuleSet`, or as classifications memoized by content hash
- Simulation assumptions, declared with falsification status: settlement is mediated by due process — a ruling settles the dispute **only if** no party appeals or the appellate affirms; REJECT unsettles (Phase 4; engine 2026-09-04); unvalued text starves without reaction (wild-experienced since 2026-09-05: docs/critic-mechanism2-verdict-2026-09-05.md); engine resolution by rule match + due process (catch-all falsified 2026-08-30: docs/critic-constitution-audit-2026-08-30.md); friction is pair-based over a sliding window. Live operation against real minds remains the falsification surface
- Autonomy: the cycle is self-sufficient. By default no step may require owner action or externally provisioned accounts; live surfaces are surfaces the project controls or autonomously stands up, and the first live polity is artificial minds under opposing mandates (S11 — substrate-blind design makes them legitimate parties). External platforms are optional expansions, never gates. The owner may sanction exceptions by prompt — a sanctioned prompt is the only legitimate path by which an external dependency enters the cycle, and every sanction is recorded on the relevant issue
- Sanction and blocking (interpretation constitutionalized 2026-08-24): external prerequisites are real — they block the deployments they gate, and gap analysis states them plainly. Sanction is permission, not owner labor: the owner legislates the exception, the provisioning work belongs to the cycle (autonomous stand-up). "Blocked on owner" is not a state the cycle may occupy; absent sanction the state is inversion, not waiting
- Append-only substrates (the JSONL measurement ledger) cannot contract: schema evolution uses versioned parallel files (measurement-v2.jsonl), never in-place migration — the Non-destructive-schema-evolution substitution, recorded here per the invariant (migration M6, 2026-09-07)

_Last verified: 2026-09-07_
