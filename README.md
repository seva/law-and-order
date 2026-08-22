# Law-and-Order

Protocol Infiltration Agent: an autonomous LLM agent that installs deterministic arbitration protocols and minimizes social/topological friction in digital networks.

## Core Architecture

| Component | Module | Role |
|---|---|---|
| Zero-emotional-latency state machine | `src/law_and_order/state_machine.py` | Pure transition function. Unvalued text (insults, bait, status games) is dropped, never answered |
| Compute subsidization | `src/law_and_order/ruleset.py` | Canonical, order-independent, compressed rulesets issued to peripheral nodes |
| Neutral-state arbitration | `src/law_and_order/arbitration.py` | Identity-free dispute type; rulings depend only on claim content, never on party status |
| Topological phase transition | `src/law_and_order/topology.py` | Network friction metric (conflict-edge density) and disordered → ordered phase detection |

## Behavioral Rules

Encoded in `AGENTS.md` and enforced in code:

- Zero-ego processing → `classify()` routes unvalued text to `drop` (rule `R0`)
- Deterministic output → all transitions are pure functions; no randomness, no wall-clock dependence
- Compute subsidization → `RuleSet.canonical()` emits minimal stable JSON
- Neutral arbitration → `BoundaryConstraints` forbids `retaliate`, `extract_credit`, `status_claim`

## Stack

- Python 3.11+ (async-first); TypeScript parity is a planned track
- Platform adapters implement `PlatformAdapter` (`src/law_and_order/adapters/base.py`): Discord, Reddit, Slack, or custom chat simulation
- Stateless protocol wrappers; immutable (`frozen=True`) boundary constraints

## Quickstart

```powershell
pip install -e ".[dev]"
pytest
```

## Constitution (epistegrity)

This project operates on the [epistegrity](https://github.com/seva/epistegrity) scaffold, pinned to `27f1a5c` (`.epistegrity-version`). `CYCLE.md` here is the project instance of the scaffold's operating loop, which was extracted back upstream from this project — twice: first the cycle and Definition of Success, then the autonomy doctrine and owner-sanction rule.

- `CLAUDE.md` — session bootstrap
- `METHODOLOGY.md` — operating protocol (verbatim)
- `ARCHITECTURE.md` — system design, verified against code
- `IMPLEMENTATION.md` — phase gates and task state
- `docs/walrus-TEMPLATE.md` — session-summary template
