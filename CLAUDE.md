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
- Scope position: S1 in operation (appellate game-proofed 2026-08-24; polities 001–003 stood up, measurement graded since 2026-09-02; next pressures: enforcement actuation, party reaction (Mechanism 3), evidence surface) — updated by cycle step 1

- Language/runtime: Python 3.11+ (developed on 3.12), async-first. TypeScript parity is a planned track; the language boundary will sit at the adapter layer, keeping the deterministic kernel single-source
- Test runner: pytest — `python -m pytest`
- Coverage (post-phase audit): `python -m pytest --cov=law_and_order --cov-report=term-missing` — kernel and adapters stay 100%; `wiring/discord_live.py` classified *Acceptable* at 0% (live-gateway glue with a discord.py dependency — untestable without a real gateway, same class as stdio/subprocess-only paths per METHODOLOGY Quality Signals; audit 2026-09-01)
- Formatting / linting: none configured yet
- Behavioral rules (zero-ego, deterministic output, compute subsidization, neutral arbitration) live in `AGENTS.md` and are enforced in code by `BoundaryConstraints`
- Review roles (Steward, Critic, Auditor, Owner) and their separation live in `ROLES.md`; no role grades its own work
- Deviations from METHODOLOGY.md:
  - Test files do not mirror source structure one-to-one: a single `tests/test_determinism.py` covers cross-module kernel properties. Re-declared 2026-08-24 (original condition — kernel modules ≤6 — lapsed with Phase 4): accepted while `test_determinism.py` covers only cross-module properties and every module with its own contract has a dedicated test file (`test_ruleset_v1.py`, `test_ruleset_v2.py`, `test_polity.py`, `test_appeals.py`, adapters, sim)

## Current phase

Phases 1–7 complete. Phase 8 — Content-Sensitive Resolution — in progress: Mechanism 1 complete 2026-09-01 (catch-all auto-resolution removed; the nonsense test flips and is executable and standing — `tests/sim/test_content_sensitivity.py`); saturation broken 2026-09-02 by polity-003 (9-pair graph; graded deltas 0.212 v2 / 0.110 probe / 0.000 nonsense; provenance and limits in `docs/polity-003/record.md`); Mechanism 3 step 1 complete (reaction spec `docs/mechanism3-reaction-spec.md` + red contract); Mechanism 2 not started, Mechanism 3 engine integration pending. Prime directive unmet: no measurement booked.
