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
[PlatformAdapter.publish]

[Network / phase]          friction = conflict-edge density; DISORDERED -> ORDERED
```

_Last verified: 2026-08-21_

---

## Components

| Component | Responsibility | Key interface |
|---|---|---|
| `src/law_and_order/protocol.py` | Immutable core types and boundary enforcement | `Signal`, `Ruling`, `BoundaryConstraints.permits`, `SignalKind`, `Phase` |
| `src/law_and_order/ruleset.py` | Compute subsidization: canonical compressed rulesets | `Rule`, `RuleSet.ordered / canonical / compressed_size / from_json` |
| `src/law_and_order/state_machine.py` | Zero-emotional-latency transitions; classify and route signals | `StateMachine.step(Signal) -> Ruling`, `classify` |
| `src/law_and_order/arbitration.py` | Identity-free neutral arbitration | `Arbitrator.resolve(Dispute) -> Ruling` |
| `src/law_and_order/topology.py` | Network friction metric and phase detection | `Network.friction()`, `phase(Network)` |
| `src/law_and_order/adapters/base.py` | Stateless platform adapter contract | `PlatformAdapter` protocol: `ingest`, `publish` |
| `src/law_and_order/adapters/discord.py` | Discord adapter: MESSAGE_CREATE ingest, ruling publication to a dedicated arbitration channel | `DiscordAdapter(ruling_channel_id, send)` implements `PlatformAdapter`; `render_ruling` |
| `src/law_and_order/adapters/sim.py` | Simulation adapter: dispute-event ingest, ruling emission | `SimAdapter(on_ruling)` implements `PlatformAdapter` |
| `src/law_and_order/sim/population.py` | Deterministic conflict population | `Persona`, `default_population()` |
| `src/law_and_order/sim/engine.py` | Simulation production surface: round-based conflict dynamics, protocol installation, friction measurement | `run(population, rounds, seed, installed, ruleset)` |

_Last verified: 2026-08-21_

---

## Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| State immutability | `frozen=True, slots=True` dataclasses throughout | "Stateless protocol wrappers with immutable boundary constraints" — mutation is unrepresentable rather than policed |
| Bribe resistance | `Dispute` carries claim/counterclaim text only, no party identities | Rulings cannot depend on who disputes; neutrality by construction, not by intention |
| Tie-break | SHA-256 comparison of claim texts | Deterministic, symmetric, status-free; identical disputes always yield identical rulings |
| Unvalued text | Marker-based `classify()` routes to `drop` (R0) | Deterministic baseline; classifier is a pure function, replaceable without touching the state machine |
| Forbidden actions | `BoundaryConstraints` checked at every emission point | `retaliate`, `extract_credit`, `status_claim` become `abstain` regardless of ruleset content |
| Error handling | Total functions on the ruling path: every input yields a `Ruling`; rejection is an action (`drop`, `abstain`, `reject_oversize`), never an exception | Coding Hygiene's "explicit error types" is satisfied by explicit rejection actions; exceptions would add non-deterministic control flow and untracked failure states |
| LLM seam | Legislative and sensing layers only: ruleset synthesis, conflict-edge sensing, optional content-hash-memoized classification. Never at ruling emission | The judicial layer must remain a pure function of (signal, ruleset, boundaries). Non-determinism is confined to producing frozen, versioned rulesets, which are auditable via canonical form; memoization restores per-content determinism for classification |
| Beachhead platform | Discord | Survey (`docs/platform-survey.md`): complete enforcement surface (timeout/ban/delete/API-manageable AutoMod) enables self-enforcing rulings — the proof requirement; MESSAGE_CONTENT free below 10k unique users; maximal conflict density maximizes the measurable friction delta. Slack cannot enforce rulings at standard-app tier; Reddit's surface is contracting (registration deadline 2026-09-30, Devvit migration) |
| Adapter dependency inversion | `DiscordAdapter` takes an async `send` callable and immutable config; discord.py is confined to the live wiring layer | Isolation of fragility: SDK churn touches only wiring; adapter tests run dependency-free against spec-accurate fixtures |
| Ruling publication | Dedicated arbitration channel, fixed at construction | Rulings appear in a status-free space, not inside the conflict — neutral arbitration by placement; destination is immutable config, not session state |
| Identity-free ingest | `Signal` carries channel origin and content only; author identity is dropped at the seam | The judicial layer never sees who spoke; neutrality begins at sensing |
| Inaugural ruleset | `rulesets/v1.json` — canonical JSON, versioned by filename and git, LF-guarded via `.gitattributes` for byte stability | The legislative layer's first frozen artifact: canonical form is the interchange format, round-trip integrity is testable, and the constitutional immune system (boundary compliance, unique ordered ids) is enforced by tests at load time |
| Production-surface inversion | Self-generated production surfaces, autonomously stood up; external platforms are optional expansions, never gates | No blocking accepted — the dependency is inverted: production is what the project generates, and no step may require owner action or externally provisioned accounts. Demonstrated at seed 7: friction 0.538 (disordered) → 0.000 (ordered), 7/7 grievances ruled and settled. Falsification proceeds against real minds in polities the project controls — first: artificial minds under opposing mandates (polity-001) |
| Owner sanction | Autonomy is the default regime, not an absolute: the owner may sanction violations by prompt | The owner stands outside the cycle as its legislative layer; a sanctioned prompt is an auditable constitutional act and the only legitimate path by which external dependencies enter the cycle. Absent sanction, the cycle never stalls on external provisioning |
| Language | Python 3.11+ first, TypeScript parity later | Listed platforms (Discord, Reddit, Slack) all have mature async Python SDKs; kernel is pure and portable |

_Last verified: 2026-08-21_

---

## Constraints

- Python 3.11+; async-first for all platform-facing code
- No randomness and no wall-clock dependence in any ruling path
- `BoundaryConstraints.forbidden_actions` are never emitted: `retaliate`, `extract_credit`, `status_claim`
- Adapters are stateless: every `ingest`/`publish` call is self-contained; no session state retained
- Platform SDKs are confined to adapter modules (isolation of fragility)
- LLM output never emits a ruling directly; it enters the kernel only as candidate `Rule`s frozen into a versioned `RuleSet`, or as classifications memoized by content hash
- Simulation assumptions, declared: a published ruling settles its dispute durably; unvalued text starves without reaction; friction is pair-based over a sliding window. Live operation against real minds is the falsification surface for these assumptions
- Autonomy: the cycle is self-sufficient. By default no step may require owner action or externally provisioned accounts; live surfaces are surfaces the project controls or autonomously stands up, and the first live polity is artificial minds under opposing mandates (S11 — substrate-blind design makes them legitimate parties). External platforms are optional expansions, never gates. The owner may sanction exceptions by prompt — a sanctioned prompt is the only legitimate path by which an external dependency enters the cycle, and every sanction is recorded on the relevant issue

_Last verified: 2026-08-21_
