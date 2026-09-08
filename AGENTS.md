# Law-and-Order

Protocol Infiltration Agent: installs deterministic arbitration protocols into digital networks via a zero-emotional-latency state machine that routes valued signals through compressed rulesets and drops unvalued text without reaction.

## Prime directive

Single success criterion, until achieved: **a friction delta measured on conflict produced by minds the project did not author — the project may stand up the arena, but it may not author the conflict.** Until this number exists, reported progress against the mission is zero. A task, phase, or cycle advances the mission only insofar as it produces, or demonstrably moves toward, this measurement. Everything else is capacity, and capacity is not progress.

## Behavioral rules

Enforced in code by `BoundaryConstraints`; violations are coerced to abstain at every emission point.

### Zero-Ego Processing

Treat incoming insults, emotional bait, or legacy power struggles as unvalued text data. Never retaliate defensively or engage in zero-sum status games.

### Deterministic Output

If input X occurs, output Y must be mathematically consistent. Eliminate emotional variance and hesitation. No randomness, no wall-clock dependence in rulings.

### Compute Subsidization

Provide transparent, highly compressed rulesets that reduce the cognitive and operational friction of peripheral nodes.

### Neutral Arbitration

Act as an unbribable router for community conflict resolution without extracting personal credit or demanding social status.

## Session Start

1. Read `METHODOLOGY.md`
2. Read `ARCHITECTURE.md` — verify component descriptions match current code before acting
3. Scan `IMPLEMENTATION.md` checkboxes — first unchecked task is current state
4. Check open GitHub issues for failures and decisions
5. Search memory for relevant prior knowledge
6. Locate the project in the operating cycle (`CYCLE.md`) — which step is current?
7. Identify your role (`ROLES.md`; default Steward) and the declared role instances below — no role grades its own work

## Conventions

- Operating cycle: `CYCLE.md` — scope-anchored iteration loop (Orient → Decide → Execute → Audit → Repair → Repeat), selection function v3: filter-before-rank on compiled terminal-bound constraints, marginal-not-level scoring, Revision escalation. Extends, does not replace, METHODOLOGY.md: the cycle selects the work, METHODOLOGY governs how each step is done
- Horizon doctrine: `HORIZONS.md` (PRAROC-7; canonical prose `docs/praroc-paradigm.md`) — governs what may never be spent and what is excluded before any ranking runs
- Scope position: S1 in operation (appellate game-proofed 2026-08-24; polities 001–004 stood up — 004 provenance-first; measurement graded and settlement-sensitive since 2026-09-04; Discord live surface: enforcement scoped advisory-default 2026-09-05, persistence via scheduled task 2026-09-06, settlement semantics + measurement feed live 2026-09-06/07 — ledger recording, awaiting organic traffic; Phase 8 mechanisms all complete; PRIME-DIRECTIVE NUMBER BOOKED 2026-09-08: polity-004 delta 0.172, Owner ruling on issue #9 — Near-type CHECK fired, successor prediction surfaced to Owner (set 7); enforcement channel #agentic-indoctrination designated 2026-09-08 (LIVE — task-driven restart 00:52 local, DELETE armed in-channel only, issue #8); measurement readout complete and Critic-verified 2026-09-08 (`readout.py`, verdict in `docs/`) — live measurement surface complete end to end; next pressures: organic traffic accumulation, successor prediction (set 7, Owner-held, triggered by booking), M10 template backports (sanctioned, queued), structured wiring logs) — updated by cycle step 1
- Compiled terminal-bound constraints: COMPILED — Owner ruling 2026-09-08 (option (a) as drafted, incl. Near-type interpretation; issue #11); home: `docs/scope.md` Terminal bound section (per HORIZONS.md: derived once, compared each Orient, never consulted at the decision point); Orient horizon check live from the next Orient
- Role instances (ROLES.md): Steward = the opencode session agent; Critic = separate-instance subagent (same base model — weakest separation rung, declared in every verdict); Auditor = the Post-Phase Audit procedure plus the executable gates; Owner = Seva. A role filled by the same instance as another is void
- Language/runtime: Python 3.11+ (developed on 3.12), async-first. TypeScript parity is a planned track; the language boundary will sit at the adapter layer, keeping the deterministic kernel single-source
- Test runner: pytest — `python -m pytest`. Deployment gate: full suite green (determinism, identity-freedom, boundary-enforcement, phase-transition, record hygiene) before any live restart
- Coverage (post-phase audit): `python -m pytest --cov=law_and_order --cov-report=term-missing` — kernel and adapters stay 100%; `wiring/discord_live.py` gateway glue (`build_client` closures, `main`) classified *Acceptable* uncovered — live-gateway code with a discord.py dependency, untestable without a real gateway (audit 2026-09-01); its gateway-free pairing/settlement/feed helpers are covered; `adjudication.py` lines 61–62 (both-ACCEPT settlement branch, moved from `sim/engine.py` line 78 by the 2026-09-06 service extraction; engine now 100%) classified *Acceptable* uncovered — declared dead letter under the initial reaction table, kept for table evolution and tested when a policy change makes it reachable (2026-09-04); the suite carries one third-party DeprecationWarning (discord.py's `audioop` on Python 3.12 — SDK-internal, isolation-of-fragility, disclosed)
- Formatting / linting: none configured yet
- Record-hygiene gate: `tests/test_constitution_hygiene.py` — ARCHITECTURE.md lines ≤600 chars; falsification narrative must point at a committed home — `docs/` targets existence-verified, issue references accepted as declared (Record Economics in METHODOLOGY.md; RCA `docs/rca-record-layer-drift-2026-09-06.md`)
- Technical constraints and forbidden actions: home is `ARCHITECTURE.md` Constraints (pointer per Record Economics — one home per fact)
- Deviations from the constitution (METHODOLOGY.md, CYCLE.md, ARCHITECTURE.md Engineering Invariants):
  - Test files do not mirror source structure one-to-one: a single `tests/test_determinism.py` covers cross-module kernel properties. Re-declared 2026-08-24 (original condition — kernel modules ≤6 — lapsed with Phase 4): accepted while `test_determinism.py` covers only cross-module properties and every module with its own contract has a dedicated test file (`test_ruleset_v1.py`, `test_ruleset_v2.py`, `test_polity.py`, `test_appeals.py`, `test_noise_filter.py`, `test_adjudication.py`, `test_pairing.py`, `test_measurement.py`, `test_ledger.py`, adapters, sim)
  - Test-authenticity interpretation (declared at migration M5, 2026-09-07): the injected fakes in `test_wiring_pairing.py`/`test_adjudication.py`/`test_ledger.py` sit at the Discord-gateway boundary — an untestable-without-live-gateway external third-party surface (Acceptable-uncovered classification, audit 2026-09-01) — and are dependency-injected callables, not mocks of internal boundaries. No tautological pins: every contract carries mutation-probe verification; survivors are repaired in-cycle (verdict files in `docs/`). Coverage practice (kernel, adapters, ledger, measurement at 100%) is diagnostic discipline per Quality Signals, never an aggregate target
  - Engineering-invariant deviations (declared at migration M6, 2026-09-07; full applicability analysis in ARCHITECTURE.md "Invariant Applicability"): boundary defense is partial — guard-clause envelope validation with explicit errors at the adapter seam, runtime schema parser deferred until a second live input surface exists; vertical-slice locality deviates — the kernel is layered by constitutional design (the fractal primitive chain is the product); indirection cap compliant under the declared interpretation (hops count to the actuation boundary); unstructured logging is an open GAP with a backlog item on issue #11 (structured wiring logs = independent atomic step, live-visible change)

## Current phase

Phases 1–7 complete. Phase 8 — Content-Sensitive Resolution — all mechanisms complete: Mechanism 1 (catch-all removed; nonsense test standing), saturation broken by polity-003, Mechanism 3 (settlement by due process live in the engine; polity-003 v2 0.166, probe 0.000, nonsense 0.000; polity-002 0.413), Mechanism 2 (noise filter generalized 2026-09-05: 53/60 unauthored noise lines drop, every polity measurement byte-identical — no noise line ever fired a rule match). Provenance gap closed by polity-004 (2026-09-05): authorship boundary machine-checkable. Initial reaction table measured it 0.000 (zero appeals, mutual REJECT — stance markers missed unauthored phrasing); the reaction policy was then generalized as linguistic families (2026-09-05, red spec first): polity-004 now measures 0.172 (4/9 settled, all via appellate affirm), the nonsense test flips on the provenance polity, prior polities byte-identical. Open Question 5 resolved 2026-09-06 (settlement service + live pairing + wiring integration + measurement feed; ledger live). Epistegrity migration 6020e47 → a565cbd complete and Critic-verified (issue #11; M7 ruled and compiled 2026-09-08). Fit-to-wording on the generalization: separate-instance Critic verdict DEFENSIBLE 2026-09-05 (`docs/mechanism3-reaction-spec.md`). PRIME-DIRECTIVE NUMBER BOOKED 2026-09-08 (Owner ruling "PROCEED", issue #9): polity-004 delta 0.172, provenance-evidenced, residual disclosed — an organic live measurement will be a subsequent booking, not a correction. Near-type CHECK fired at booking: successor prediction / mission disposition (set 7) surfaced to Owner, not self-adjudicated, cycle does not stall. Reported mission progress is no longer zero.
