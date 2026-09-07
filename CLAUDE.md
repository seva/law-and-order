# Law-and-Order

Protocol Infiltration Agent: installs deterministic arbitration protocols into digital networks via a zero-emotional-latency state machine that routes valued signals through compressed rulesets and drops unvalued text without reaction.

## Prime directive

Single success criterion, until achieved: **a friction delta measured on conflict produced by minds the project did not author — the project may stand up the arena, but it may not author the conflict.** Until this number exists, reported progress against the mission is zero. A task, phase, or cycle advances the mission only insofar as it produces, or demonstrably moves toward, this measurement. Everything else is capacity, and capacity is not progress.

## Session Start

1. Read `METHODOLOGY.md`
2. Read `ARCHITECTURE.md` — verify component descriptions match current code before acting
3. Scan `IMPLEMENTATION.md` checkboxes — first unchecked task is current state
4. Check open GitHub issues for failures and decisions
5. Search memory for relevant prior knowledge
6. Locate the project in the operating cycle (`CYCLE.md`) — which step is current?

## Conventions

- Operating cycle: `CYCLE.md` — scope-anchored iteration loop (Orient → Decide → Execute → Audit → Repair → Repeat). Extends, does not replace, METHODOLOGY.md: the cycle selects the work, METHODOLOGY governs how each step is done
- Scope position: S1 in operation (appellate game-proofed 2026-08-24; polities 001–004 stood up — 004 provenance-first; measurement graded and settlement-sensitive since 2026-09-04; Discord enforcement live 2026-09-05, audit-repaired, channel-scoped with advisory default; bot-persistence hygiene closed 2026-09-05 — temp launchers deleted, switch-over awaits Owner checkpoint; Phase 8 mechanisms all complete — noise filter generalized 2026-09-05; next pressures: switch-over checkpoint, live measurement harness, staged stand-up) — updated by cycle step 1

- Language/runtime: Python 3.11+ (developed on 3.12), async-first. TypeScript parity is a planned track; the language boundary will sit at the adapter layer, keeping the deterministic kernel single-source
- Test runner: pytest — `python -m pytest`
- Coverage (post-phase audit): `python -m pytest --cov=law_and_order --cov-report=term-missing` — kernel and adapters stay 100%; `wiring/discord_live.py` classified *Acceptable* at 0% (live-gateway glue with a discord.py dependency — untestable without a real gateway, same class as stdio/subprocess-only paths per METHODOLOGY Quality Signals; audit 2026-09-01); `adjudication.py` lines 61–62 (both-ACCEPT settlement branch, moved from `sim/engine.py` line 78 by the 2026-09-06 service extraction; engine now 100%) classified *Acceptable* uncovered — declared dead letter under the initial reaction table, kept for table evolution and tested when a policy change makes it reachable (2026-09-04)
- Formatting / linting: none configured yet
- Behavioral rules (zero-ego, deterministic output, compute subsidization, neutral arbitration) live in `AGENTS.md` and are enforced in code by `BoundaryConstraints`
- Review roles (Steward, Critic, Auditor, Owner) and their separation live in `ROLES.md`; no role grades its own work
- Deviations from METHODOLOGY.md:
  - Test files do not mirror source structure one-to-one: a single `tests/test_determinism.py` covers cross-module kernel properties. Re-declared 2026-08-24 (original condition — kernel modules ≤6 — lapsed with Phase 4): accepted while `test_determinism.py` covers only cross-module properties and every module with its own contract has a dedicated test file (`test_ruleset_v1.py`, `test_ruleset_v2.py`, `test_polity.py`, `test_appeals.py`, `test_noise_filter.py`, `test_adjudication.py`, `test_pairing.py`, adapters, sim)

## Current phase

Phases 1–7 complete. Phase 8 — Content-Sensitive Resolution — all mechanisms complete: Mechanism 1 (catch-all removed; nonsense test standing), saturation broken by polity-003, Mechanism 3 (settlement by due process live in the engine; polity-003 v2 0.166, probe 0.000, nonsense 0.000; polity-002 0.413), Mechanism 2 (noise filter generalized 2026-09-05: 53/60 unauthored noise lines drop, every polity measurement byte-identical — no noise line ever fired a rule match). Provenance gap closed by polity-004 (2026-09-05): authorship boundary machine-checkable. Initial reaction table measured it 0.000 (zero appeals, mutual REJECT — stance markers missed unauthored phrasing); the reaction policy was then generalized as linguistic families (2026-09-05, red spec first): polity-004 now measures 0.172 (4/9 settled, all via appellate affirm), the nonsense test flips on the provenance polity, prior polities byte-identical. First booking candidate exists — and two questions sit with the Owner: whether the generalization's polity-004 motivation is a fit (surfaced for Critic audit, not self-adjudicated), and the booking act itself. Prime directive unmet: no measurement booked.
