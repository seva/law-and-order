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

_Last verified: 2026-09-06_

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
| `src/law_and_order/adjudication.py` | Settlement semantics as a reusable stateful service above the stateless adapter contract (Open Question 5 option a): institutional memory — last-said text per speaker pair, res-judicata on settled pairs — delegating to StateMachine, reaction, and Appellate; single source, the sim engine consumes it | `SettlementService(ruleset, source, boundaries).observe(speaker, counterpart, text) -> Observation(rulings, settled)`, `note(speaker, counterpart, text)`, `is_settled(speaker, counterpart)`, `Observation`, `INERT_ACTIONS` |
| `src/law_and_order/enforcement.py` | Enforcement policy: pure content-addressed mapping from rulings to enforcement acts — advisory to judicial (step 1: DELETE on `drop`/`reject_oversize`, pronounce-only otherwise) | `enforcement_for(ruling) -> Enforcement`, `Enforcement` |
| `src/law_and_order/topology.py` | Network friction metric and phase detection | `Network.friction()`, `phase(Network)` |
| `src/law_and_order/polity.py` | Transcript adjudication: offline rulings, appeal re-hearing, and settlement analysis for polity records | `load_transcript`, `adjudicate`, `adjudicate_appeals`, `settlement_signals`, `final_settlement`, `analyze` |
| `src/law_and_order/adapters/base.py` | Stateless platform adapter contract; shared ruling renderer | `PlatformAdapter` protocol: `ingest`, `publish`; `render_ruling` |
| `src/law_and_order/adapters/discord.py` | Discord adapter: MESSAGE_CREATE ingest, ruling publication to a dedicated arbitration channel | `DiscordAdapter(ruling_channel_id, send)` implements `PlatformAdapter` |
| `src/law_and_order/adapters/sim.py` | Simulation adapter: dispute-event ingest, ruling emission | `SimAdapter(on_ruling)` implements `PlatformAdapter` |
| `src/law_and_order/sim/population.py` | Deterministic conflict population | `Persona`, `default_population()` |
| `src/law_and_order/sim/engine.py` | Simulation production surface: round-based conflict dynamics, protocol installation, friction measurement; settlement semantics delegated to `adjudication.SettlementService` (single source) — matched non-inert rulings publish, settlement only via both-ACCEPT (dead letter under the initial table) or appellate affirm, overturn/REJECT persist, unripe disputes (counterpart never spoke) emit no ruling | `run(population, rounds, seed, installed, ruleset)` |
| `src/law_and_order/wiring/discord_live.py` | Live Discord wiring layer: binds the dependency-inverted adapter to a real gateway; sole discord.py importer (isolation of fragility); token environment-only; enforcement scope applied here (channel-membership gate, default empty = advisory everywhere) | `build_client(ruleset, ruling_channel_id, enforcement_channels=frozenset()) -> discord.Client`, `main()` |

_Last verified: 2026-09-06_

---

## Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| State immutability | `frozen=True, slots=True` dataclasses throughout | "Stateless protocol wrappers with immutable boundary constraints" — mutation is unrepresentable rather than policed |
| Bribe resistance | `Dispute` carries claim/counterclaim text only, no party identities | Rulings cannot depend on who disputes; neutrality by construction, not by intention |
| Tie-break | SHA-256 comparison of claim texts | Deterministic, symmetric, status-free; identical disputes always yield identical rulings |
| Unvalued text | Marker-based `classify()` routes to `drop` (R0) | Deterministic baseline; classifier is a pure function, replaceable without touching the state machine |
| Noise-filter generalization (Mechanism 2, 2026-09-05) | `UNVALUED_MARKERS` expanded from the 7 authored markers to 48 — 41 added across five systematic families (insult nouns, contempt assessments, dismissals, credibility denials, intimidation); expanded markers chosen over a content-hash-memoized classifier (spec open question 2 resolved by choice: family precedent proven at the reaction seam, pure determinism, no LLM-seam infrastructure) | Catches 53 of the 60 unauthored noise lines across polities 002–004 (per-polity before: 1/12, 3/24, 2/24; after: 12/12, 22/24, 19/24). The 7 residual lines resist family membership without tailoring and are disclosed, not fitted — the filter grades coverage, the spec's own framing (one excluded candidate, `rat`, substring-hits valued claims — exclusion is honesty, not omission). Separate-instance Critic challenged the first cut: five residuals were family-completable, not tailoring-dependent (wasting/stalling/keep talking/unbelievable/an excuse) — repaired by completing the families (`docs/critic-mechanism2-verdict-2026-09-05.md` N1); a self-reported off-by-one (N3) and loose wording (N4) corrected in the records. Gate held: every unauthored claim stays valued, default-population and polity-001 classifications unchanged, nonsense substitutions stay valued, and every polity measurement re-ran byte-identical (139 green) — no noise line ever fired a rule match (one line carries an R5 substring but is pre-filtered UNVALUED under old and new markers alike), so noise dropping changed no settlement dynamics. The live effect is real: under first-instance semantics noise now drops at R0, the actuation-capable act, instead of routing to arbitration |
| Forbidden actions | `BoundaryConstraints` checked at every emission point | `retaliate`, `extract_credit`, `status_claim` become `abstain` regardless of ruleset content |
| Appellate instance | Merits re-adjudication: the original dispute is re-ruled under the ruleset in force; affirm if the merits action matches the contested action, overturn otherwise; the appeal ground is provenance — content-addressed in the digest — not merits input; one instance — affirm exhausts due process and settles durably | Due process as a pure function: the appellate ruling is content-addressed over (dispute, contested ruling, ground), identity-free, deterministic. The institution hears every appeal; the outcome depends on the dispute and the law in force, not on the rhetoric of the appeal — merits that consumed the ground were gameable (corrected Phase 6, 2026-08-24; polity-001 outcomes preserved under v1 and v2). Under stance-blind v1, polity-001's appeal affirms, exposing that appellate teeth require legislative evolution. One instance: no infinite regress |
| Stance-aware matching (v2) | Ordered stance markers before general content match: refusal markers (`decline/refuse the refund`) and contestation (`dispute the`) rule before the general refund match; v1 frozen as legislative history | Stance expressed as content markers — deterministic, no LLM at the ruling seam; the cycle-7 appellate affirm under v1 proved the need. Measured 2026-08-24: first-instance discrimination flips (refusal/contestation no longer `order_refund`), and the appellate re-hearing under v2 OVERTURNS the contested ruling [R1] — appellate teeth arrive with legislative evolution; the v1 settlement stands as res judicata |
| Error handling | Total functions on the ruling path: every input yields a `Ruling`; rejection is an action (`drop`, `abstain`, `reject_oversize`), never an exception | Coding Hygiene's "explicit error types" is satisfied by explicit rejection actions; exceptions would add non-deterministic control flow and untracked failure states |
| Catch-all auto-resolution removed (Phase 8 Mechanism 1, 2026-09-01) | In the sim engine, a dispute resolves only on a matched non-inert rule; unmatched disputes persist, keep generating conflict, and produce no ruling | The friction delta must be a function of the conflict content and the legislation's coverage of it, per `docs/content-sensitivity-spec.md`. Measured under Mechanism-1 semantics (superseded by the settlement-semantics row below): real polity-002 content + v2 → delta 0.773 (4/4 pairs resolved); nonsense-content substitution → 0.000; empty-ruleset substitution → 0.000 — the nonsense test flips. Caveat recorded: polity-002's topology admits only 4 dispute pairs, so the delta saturates (binary resolution, not graded coverage) — resolved 2026-09-02 by the polity-003 arena (next row) |
| Polity-003 arena (saturation break, 2026-09-02) | Eight minds under opposed mandates across four domains (marketplace, debt, workplace, tenancy); content generated by four separate subagent instances; 9-pair symmetric counterpart graph in the `minds.json` schema; v2-minus-R7 derived subset as the legislative probe; provenance and limitations in `docs/polity-003/record.md` | Measurement must grade legislative coverage — polity-002's 4-pair topology saturated the delta to binary. Measured under match-resolution semantics (Mechanism-1 era): full v2 delta 0.212 (5/9 pairs resolved; installed tail 0.218), probe 0.110 (2/9), nonsense 0.000. Re-measured under settlement semantics (Mechanism 3, 2026-09-04): full v2 0.166 (4/9 settled; installed tail 0.264 — DISORDERED), probe 0.000 (breach-only legislation escalates but settles nothing), nonsense 0.000; polity-002 0.413 (2/4 settled, 31 rulings). Order is a matter of degree under partial coverage, and settlement now requires due process. One matched line can settle both of its author's pairs; the counterclaim's content can overturn on appeal (marker interference — an earlier-ordered marker in the counterpart's last word changes the merits) |
| Polity-004 arena (provenance-first polity, 2026-09-05) | `docs/polity-004/protocol.md` — mandates committed BEFORE generation (commit 8c1a04b), raw outputs persisted byte-for-byte with sha256 + instance ids, assembly machine-verified by `test_polity004_provenance.py` (internal consistency; non-authorship additionally rests on commit ordering + external session store); no content selection, single pass | The Critic falsified the booking claim because non-authorship was reported, not evidenced. The authorship boundary is now machine-checkable within the repo. Measured under settlement semantics with the initial reaction table: full v2 delta 0.000, 0/9 settled, 24 rulings published — zero appeals, all rulings mutual-REJECTed at the reaction layer (stance markers missed unauthored phrasing). Re-measured 2026-09-05 under the generalized reaction policy: full v2 delta 0.172 (4/9 settled — every settlement via order_refund → appeal → appellate affirm; 14 rulings), probe 0.000/5, nonsense 0.000/0, empty 0.000/0; the nonsense test flips on this polity. Guardrail validation: nonsense stayed resolved-zero on all polities, prior polities measured byte-identical, generalization disclosed to Critic/Owner for the fit-to-wording question. Booking: a candidate number now exists (0.172, provenance-evidenced); the act remains the Owner's. Residual: provenance proves integrity, not strong unauthorship (Owner) |
| Engine settlement semantics (Mechanism 3, 2026-09-04) | Adjudication fires on a matched non-inert ruling once both sides have spoken (unripe disputes emit no ruling); the first-instance ruling publishes; parties react per `reaction.py`; settlement = both-ACCEPT (dead letter under the initial table) or appellate affirm; overturn, REJECT, and procedural rulings keep the dispute open; all pins re-forged at the semantics change | Due process operationalizes the polity-001 lesson: the delta now grades what actually settles, not what merely matches — it is sensitive to ruling quality (a wrong-stance refund order can be overturned by a counterclaim carrying an earlier-ordered marker). Consequence declared and now measured: settlement rate is governed by the appellate affirm rate; order requires actual settlement, which is harder than match coverage (polity-003 tail 0.264 DISORDERED where coverage alone had reached 0.218 ORDERED; polity-004 settles nothing — 0.000: its 24 rulings met mutual REJECT at the reaction layer before due process could weigh them) |
| Settlement service extraction (Open Question 5 option a, 2026-09-06) | Settlement semantics live in `adjudication.SettlementService` — a stateful component ABOVE the adapter contract: institutional memory (last-said per pair via `note`/`observe`, res judicata) is service state, not adapter state; the sim engine delegates to it (`source="sim"` preserves signal digests byte-identically; `note` feeds initiation texts into dispute state without adjudicating, `observe` adjudicates). The first cut DROPPED the initiation-side feed and was falsified by separate-instance Critic (`docs/critic-adjudication-verdict-2026-09-06.md` N1): default sim diverged (delta 0.477→0.538, published 45→26) and polities diverged at unpinned seeds while seed-7 pins passed coincidentally; repaired by `note()` (N1), equality-pinning the default-sim measurement (N3 structural repair), tying the duplicated signal-source convention to the adapter contract by test (N4). Post-repair parity verified by full-history differential against the genuine pre-refactor tree: default and all three polities, seeds 7/1/42, identical histories, published streams, and counts. The original "zero pin drift — byte-identical" verification claim was false as recorded and is corrected here (N2) | Adapters stay stateless by construction (constitutional constraint intact); the live surface gains what the sim measures without a statefulness exception. Rejected: option (b) narrowed adapter statefulness (constitutional cost for convenience); option (c) first-instance-only live tier (live adjudication permanently divorced from measured semantics — no scope advance). Open remainder, next decide: the live pairing policy — how Discord messages map to (speaker, counterpart) events, since the live envelope drops author identity at the ingest seam by design |
| Reaction layer (Mechanism 3 step 2, 2026-09-02) | `reaction.py` — arena policy standing apart from any ruleset: `stance_of` extracts CLAIM/REFUSAL/NEUTRAL by markers (REFUSAL takes precedence on overlap; markers generalized to natural-language families 2026-09-05 after polity-004 disclosure, under the standing validation gate — nonsense resolved-zero on all polities, prior dynamics undisturbed); `react` is total and deterministic with REJECT the default; the favorability table covers final favorable actions only (`order_refund`); case-insensitive substring matching, no word boundaries | Settlement semantics must exist as a pure function before engine integration; legislation and arena policy evolve independently — marker overlap creates no coupling. REJECT-default: settlement exists only where the declared policy says it exists. Declared consequence, confirmed by measurement: both-ACCEPT unreachable under the table — every settlement flows through appellate affirm (measured 2026-09-05: 4/9 on polity-004, 4/4 affirms) |
| LLM seam | Legislative and sensing layers only: ruleset synthesis, conflict-edge sensing, optional content-hash-memoized classification. Never at ruling emission | The judicial layer must remain a pure function of (signal, ruleset, boundaries). Non-determinism is confined to producing frozen, versioned rulesets, which are auditable via canonical form; memoization restores per-content determinism for classification |
| Beachhead platform | Discord | Survey (`docs/platform-survey.md`): complete enforcement surface (timeout/ban/delete/API-manageable AutoMod) enables self-enforcing rulings — the proof requirement; MESSAGE_CONTENT free below 10k unique users; maximal conflict density maximizes the measurable friction delta. Slack cannot enforce rulings at standard-app tier; Reddit's surface is contracting (registration deadline 2026-09-30, Devvit migration) |
| Adapter dependency inversion | `DiscordAdapter` takes an async `send` callable and immutable config; discord.py is confined to the live wiring layer | Isolation of fragility: SDK churn touches only wiring; adapter tests run dependency-free against spec-accurate fixtures |
| Ruling publication | Dedicated arbitration channel, fixed at construction | Rulings are published to a dedicated channel (destination is immutable config, not session state). DECISION DEBT 2026-08-31: the ruling-channel input boundary was removed in the live wiring, so replies in the ruling channel are now ingested as disputes; the neutral-placement property ("rulings go out, disputes come in") is no longer enforced — see IMPLEMENTATION.md "Decision Debt" for the revisit question |
| Identity-free ingest | `Signal` carries channel origin and content only; author identity is dropped at the seam | The judicial layer never sees who spoke; neutrality begins at sensing |
| Inaugural ruleset | `rulesets/v1.json` — canonical JSON, versioned by filename and git, LF-guarded via `.gitattributes` for byte stability | The legislative layer's first frozen artifact: canonical form is the interchange format, round-trip integrity is testable, and the constitutional immune system (boundary compliance, unique ordered ids) is enforced by tests at load time |
| Production-surface inversion | Self-generated production surfaces, autonomously stood up; external platforms are optional expansions, never gates | No blocking accepted — the dependency is inverted: production is what the project generates, and no step may require owner action or externally provisioned accounts. Demonstrated at seed 7 under settlement semantics (post-Mechanism-3 values, equality-pinned 2026-09-06 — the Critic's extraction audit caught this row stale since the 2026-09-04 semantics change, hidden by inequality-only pins): baseline tail 0.538 → installed tail 0.061, delta 0.477, 7/7 resolved, 45 rulings published; the earlier 0.538 → 0.000 is the Phase-3 match-semantics-era measurement (2026-08-23), superseded. Falsification proceeds against real minds in polities the project controls — first: artificial minds under opposing mandates (polity-001) |
| Owner sanction | Autonomy is the default regime, not an absolute: the owner may sanction violations by prompt | The owner stands outside the cycle as its legislative layer; a sanctioned prompt is an auditable constitutional act and the only legitimate path by which external dependencies enter the cycle. Absent sanction, the cycle never stalls on external provisioning. Sanction is permission, not provision: prerequisites block the deployments they gate — honestly — but their resolution is autonomous stand-up by the cycle, never owner labor |
| Live enforcement (Discord step b, 2026-09-05) | Enforcement policy is a pure content-addressed mapping (`enforcement.py`); the act executes in the wiring layer — the only discord.py importer — which holds message identity; pronouncement publishes first and enforcement is additive and skips if the pronouncement fails (visible over silent: no unpronounced deletion); channel-miss and HTTP failures are logged, never silent | The judicial layer stays identity-free — rulings depend on content only; enforcement mechanically follows content-based rulings on the message that triggered them. Isolation of fragility: SDK side-effects confined to wiring. Requires MANAGE_MESSAGES on the live server. TIMEOUT/AutoMod are future policy, deliberately unassigned rather than arbitrary. Declared facts: `reject_oversize` is mapped but unreachable on Discord (kernel bound 4096 > platform limit 2000) — only `drop` actuates there; publish-then-delete leaves the pronouncement's digest referencing a vanished message, accepted as the enforcement audit trail. Blast radius resolved 2026-09-05 (Owner ruling): enforcement is CHANNEL-SCOPED — coercive acts execute only in channels designated by `DISCORD_ENFORCEMENT_CHANNEL_IDS` (default empty = advisory everywhere); pronouncement is unaffected, adjudication stays global. Guild-wide enforcement is not reachable in the default configuration |
| Language | Python 3.11+ first, TypeScript parity later | Listed platforms (Discord, Reddit, Slack) all have mature async Python SDKs; kernel is pure and portable |

_Last verified: 2026-09-06_

---

## Constraints

- Python 3.11+; async-first for all platform-facing code
- No randomness and no wall-clock dependence in any ruling path
- `BoundaryConstraints.forbidden_actions` are never emitted: `retaliate`, `extract_credit`, `status_claim`
- Adapters are stateless: every `ingest`/`publish` call is self-contained; no session state retained
- Platform SDKs are confined to adapter modules (isolation of fragility)
- LLM output never emits a ruling directly; it enters the kernel only as candidate `Rule`s frozen into a versioned `RuleSet`, or as classifications memoized by content hash
- Simulation assumptions, declared with falsification status: settlement is mediated by due process — a ruling settles its dispute **only if** no party appeals, or if the appellate instance affirms on appeal; a REJECT unsettles (executable law, Phase 4; the Constraints line reconciled 2026-09-02 to match the corpus — audit finding N1; operationalized in the sim engine 2026-09-04: settlement = both-ACCEPT — dead letter under the initial table — or appellate affirm; unripe disputes emit no ruling); unvalued text starves without reaction (experienced in the wild since the Mechanism-2 generalization of 2026-09-05: polity-001 no insults, noise-line drops under the generalized filter 12/12 polity-002, 22/24 polity-003, 19/24 polity-004, 7 residual lines disclosed; no measurement disturbed — no noise line ever fired a rule match); engine resolution is mediated by rule match and settled by due process (Phase 8 Mechanisms 1 + 3; the prior catch-all auto-resolution was falsified by the Critic as content-blind, 2026-08-30); friction is pair-based over a sliding window. Live operation against real minds is the falsification surface for these assumptions
- Autonomy: the cycle is self-sufficient. By default no step may require owner action or externally provisioned accounts; live surfaces are surfaces the project controls or autonomously stands up, and the first live polity is artificial minds under opposing mandates (S11 — substrate-blind design makes them legitimate parties). External platforms are optional expansions, never gates. The owner may sanction exceptions by prompt — a sanctioned prompt is the only legitimate path by which an external dependency enters the cycle, and every sanction is recorded on the relevant issue
- Sanction and blocking (interpretation constitutionalized 2026-08-24): external prerequisites are real — they block the deployments they gate, and gap analysis states them plainly. Sanction is permission, not owner labor: the owner legislates the exception, the provisioning work belongs to the cycle (autonomous stand-up). "Blocked on owner" is not a state the cycle may occupy; absent sanction the state is inversion, not waiting

_Last verified: 2026-09-06_
