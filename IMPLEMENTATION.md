# Implementation Plan

---

## Phase 1 — Core Arbitration Kernel

**Goal:** deterministic, platform-independent kernel exists: signal classification, rule matching, identity-free arbitration, boundary enforcement, friction/phase metrics.

No Phase 0 gate applies: the kernel depends on no external interfaces, APIs, or contracts.

### Tasks

- [x] `tests/test_determinism.py`
  - identical input yields identical ruling across independent Arbitrator instances
  - unvalued text dropped (R0) without retaliation
  - valued signal matches its rule
  - forbidden action coerced to abstain
  - arbitration identity-free and hash-symmetric
  - ruleset canonical form order-independent
  - phase transition on friction drop
- [x] `src/law_and_order/protocol.py`, `ruleset.py`, `state_machine.py`, `arbitration.py`, `topology.py`, `adapters/base.py`
  - frozen/slotted dataclasses; pure transition functions; hash tie-break
- [x] `tests/test_determinism.py` — coverage-gap closure (post-phase audit 2026-08-21)
  - arbitrator coerces forbidden action to abstain
  - tie-break exercises both branches via swapped pair
  - oversize payload rejected at boundary
  - unmatched valued signal routes to arbitration
  - compressed_size consistent with canonical bytes
  - empty network: zero friction, ordered phase

**Verification:** `python -m pytest` — 13 tests pass; kernel coverage 100%, adapters uncovered (Acceptable: contract-only until Phase 3).

Status: complete — seeded 2026-08-21; audit coverage gaps closed 2026-08-21.

---

## Phase 2 — Discovery: Platform Integration

Must complete before any adapter code is written against external APIs.

- [x] Survey Discord (gateway events, message intents, rate limits), Reddit (asyncpraw auth model, moderation surfaces), Slack (Events API, signing verification) — findings in `docs/platform-survey.md` (2026-08-21)
- [x] Select the beachhead platform and record why — **Discord**, 2026-08-21: survey RAROC ≈ 2.0 vs Reddit 1.0 / Slack 0.3 — enforcement completeness (self-enforcing rulings), sub-10k-user intent exemption, maximal conflict density (`docs/platform-survey.md`, ARCHITECTURE.md Design Decisions)
- [x] Determine where the LLM layer attaches — resolved 2026-08-21: legislative/sensing layers only, never ruling emission (ARCHITECTURE.md Design Decisions); determinism boundary = frozen versioned RuleSet + content-hash-memoized classification
- [x] Record findings in `docs/platform-survey.md` — this file is the hard gate for Phase 3 (recorded 2026-08-21; gate satisfied; beachhead Discord)

**Outputs:** structured discovery artifact committed to `docs/`.

---

## Phase 3 — First Platform Adapter (Discord)

**Goal:** the kernel arbitrates live signals on Discord through a stateless adapter.

### Tasks

- [x] `tests/adapters/test_discord.py`
  - ingest produces well-formed Signals from recorded raw payloads
  - publish serializes a Ruling to the platform's message shape
  - adapter retains no state between calls
  - spec-accurate synthetic fixtures; live-recorded fixtures pending bot account
- [x] `src/law_and_order/adapters/discord.py`
  - implements `PlatformAdapter` against Phase 2 findings
  - dependency-inverted `send` callable; discord.py confined to live wiring
- [x] `rulesets/v1.json` — inaugural ruleset (legislative layer)
  - frozen canonical artifact; `RuleSet.from_json` round-trips byte-identically
  - immune-system tested: boundary compliance, unique ordered ids; LF-guarded for cross-platform byte stability

**Verification:** adapter tests pass against recorded fixtures; one live round-trip (signal → ruling → publish) observed in a test community.

---

## Open Questions

1. Beachhead platform: Discord, Reddit, or Slack — resolved 2026-08-21: Discord, see ARCHITECTURE.md Design Decisions
2. LLM attachment point and how determinism is preserved at that seam — resolved 2026-08-21, see ARCHITECTURE.md Design Decisions
3. TypeScript parity: parallel kernel or wrapper over the Python kernel — open
4. Source of network graph data for `topology.py` — open, Phase 3 (Discord channel activity sampling; survey open item 5)

---

## Dependencies

```toml
[project]
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
discord = ["discord.py>=2.3"]
reddit = ["asyncpraw>=7.7"]
slack = ["slack-bolt>=1.18"]
dev = ["pytest>=8", "pytest-cov>=5"]
```
