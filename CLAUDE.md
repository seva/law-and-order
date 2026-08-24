# Law-and-Order

Protocol Infiltration Agent: installs deterministic arbitration protocols into digital networks via a zero-emotional-latency state machine that routes valued signals through compressed rulesets and drops unvalued text without reaction.

## Session Start

1. Read `METHODOLOGY.md`
2. Read `ARCHITECTURE.md` — verify component descriptions match current code before acting
3. Scan `IMPLEMENTATION.md` checkboxes — first unchecked task is current state
4. Check open GitHub issues for failures and decisions
5. Search memory for relevant prior knowledge
6. Locate the project in the operating cycle (`CYCLE.md`) — which step is current?

## Conventions

- Operating cycle: `CYCLE.md` — scope-anchored iteration loop (Orient → Decide → Execute → Audit → Repair → Repeat). Extends, does not replace, METHODOLOGY.md: the cycle selects the work, METHODOLOGY governs how each step is done
- Scope position: S1 (single community, pre-beachhead) — updated by cycle step 1

- Language/runtime: Python 3.11+ (developed on 3.12), async-first. TypeScript parity is a planned track; the language boundary will sit at the adapter layer, keeping the deterministic kernel single-source
- Test runner: pytest — `python -m pytest`
- Coverage (post-phase audit): `python -m pytest --cov=law_and_order --cov-report=term-missing` — package stays 100% (kernel and adapters)
- Formatting / linting: none configured yet
- Behavioral rules (zero-ego, deterministic output, compute subsidization, neutral arbitration) live in `AGENTS.md` and are enforced in code by `BoundaryConstraints`
- Deviations from METHODOLOGY.md:
  - Test files do not mirror source structure one-to-one: a single `tests/test_determinism.py` covers the kernel. Accepted while kernel modules number ≤6 and the tested properties (determinism, boundary enforcement) are cross-module. Phase 3 adapter tests will mirror `src/law_and_order/adapters/`

## Current phase

Phases 1–3 complete (2026-08-23). No phase defined: next step selected by `CYCLE.md` Orient/Decide — legislative agenda sourced from polity-001 (`docs/polity-001/record.md`): stance-aware matching, evidence surface, appellate instance.
