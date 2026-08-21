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

**Verification:** `python -m pytest` — 7 tests pass.

Status: complete at epistegrity instantiation (work predates scaffold adoption; checkboxes reflect verified state).

---

## Phase 2 — Discovery: Platform Integration

Must complete before any adapter code is written against external APIs.

- [ ] Survey Discord (gateway events, message intents, rate limits), Reddit (asyncpraw auth model, moderation surfaces), Slack (Events API, signing verification)
- [ ] Select the beachhead platform and record why
- [ ] Determine where the LLM layer attaches — classification, ruleset synthesis, or ruling draft — and record the determinism boundary at that seam
- [ ] Record findings in `docs/platform-survey.md` — this file is the hard gate for Phase 3

**Outputs:** structured discovery artifact committed to `docs/`.

---

## Phase 3 — First Platform Adapter

**Goal:** the kernel arbitrates live signals on one platform through a stateless adapter.

### Tasks

- [ ] `tests/adapters/test_[platform].py`
  - ingest produces well-formed Signals from recorded raw payloads
  - publish serializes a Ruling to the platform's message shape
  - adapter retains no state between calls
- [ ] `src/law_and_order/adapters/[platform].py`
  - implements `PlatformAdapter` against Phase 2 findings

**Verification:** adapter tests pass against recorded fixtures; one live round-trip (signal → ruling → publish) observed in a test community.

---

## Open Questions

1. Beachhead platform: Discord, Reddit, or Slack — open, Phase 2
2. LLM attachment point and how determinism is preserved at that seam — open, Phase 2
3. TypeScript parity: parallel kernel or wrapper over the Python kernel — open
4. Source of network graph data for `topology.py` on each platform — open, Phase 2

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
