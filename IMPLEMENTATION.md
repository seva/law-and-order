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
- [x] `src/law_and_order/adapters/sim.py` + `src/law_and_order/sim/` — simulation production surface (dependency inversion)
  - deterministic conflict population; protocol installation; friction measurement via `topology.py`
  - `scripts/sim_experiment.py`, seed 7, 60 rounds: baseline 0.538 (disordered) → installed 0.000 (ordered); delta 0.538; 7/7 grievances ruled and settled
- [x] polity-001 — first live adjudication against real (artificial) minds (`docs/polity-001/`)
  - unscripted subagent disputants under opposing mandates; kernel adjudicated all 6 statements, replay-stable
  - settlement: claimant ACCEPT, respondent APPEAL — due process exercised live; durable-settlement assumption revised
  - legislative gaps exposed: stance-blind matching, no evidence surface, no appellate instance

**Verification:** adapter tests pass against recorded fixtures; live round-trip (signal → ruling → publish) demonstrated in the simulation production surface with measured friction delta 0.538 (disordered → ordered, seed 7). Discord live community remains the external falsification surface — owner-gated, non-blocking.

Status: complete — verification re-run 2026-08-23 (48 tests, package coverage 100%, friction delta 0.538 reproduced); post-phase audit executed and repaired 2026-08-23.

---

## Phase 4 — Appellate Instance

**Goal:** due process is institutionally closed: every appeal is heard by a deterministic appellate instance; settlement is mediated by due process, per the corrected settlement assumption.

No Phase 0 gate applies: the appellate is a pure kernel institution with no external interfaces.

### Tasks

- [x] `tests/test_appeals.py` + `tests/test_polity.py` appeal extensions — spec first
  - appellate ruling deterministic and replay-stable; identity-free (depends on dispute, contested ruling, and ground content only)
  - affirm when merits re-adjudication matches the contested action; overturn when it differs — both branches exercised
  - forbidden action coerced to abstain at the appellate emission point
  - appeal construction from transcript: dispute from first-argument statements, contested ruling from the appellant's last argument statement, ground from the settlement text
  - final settlement under the corrected assumption: ACCEPT settles; APPEAL settles only if affirmed; REJECT unsettles
- [x] `src/law_and_order/appeals.py` + polity harness + ARCHITECTURE.md in the same commit (public contract)
  - `Appeal(dispute, ruling, ground)` frozen/slotted, content-addressed digest
  - `Appellate(ruleset, boundaries).resolve(Appeal) -> Ruling` — merits re-adjudicated via `Arbitrator` over (claim + ground, counterclaim); affirm/overturn; boundary-checked at emission
  - polity: `adjudicate_appeals`, final-settlement recompute, CLI emits appellate rulings
- [x] polity-001 appeal re-heard from the committed transcript; outcome recorded on the issue

**Verification:** the appellate instance adjudicates polity-001's pending appeal from the committed transcript — deterministic, replay-stable; final settlement recomputed under the corrected settlement assumption; suite green; package coverage 100%; CI green.

Status: complete — verification satisfied 2026-08-24: polity-001's appeal re-heard, AFFIRMED under v1 [R1], replay-stable (byte-identical across runs); final_settlement true — the dispute open since 2026-08-21 is durably settled through due process; 60 tests, package coverage 100%.

---

## Phase 5 — Legislative Evolution: Stance-Aware Ruleset v2

**Goal:** the law distinguishes claim from refusal and content from contestation — the stance-blindness exposed by polity-001 and demonstrated by the cycle-7 appellate affirm is corrected at the legislative layer.

No Phase 0 gate applies: a pure legislative artifact over the existing kernel.

### Tasks

- [x] `tests/test_ruleset_v2.py` + polity stance extensions — spec first
  - canonical form, byte-stable round-trip, immune system (every action permitted, ids unique and ordered)
  - stance discrimination on the polity-001 transcript: claim statements → `order_refund`; refusal/contestation statements → non-`order_refund` actions
  - determinism through the state machine; appellate re-hearing under v2 replay-stable
- [x] `rulesets/v2.json` + ARCHITECTURE.md in the same commit (legislative design decision)
  - ordered stance markers before general content match; v1 frozen, unmodified
- [x] polity-001 re-adjudicated under v2; appellate re-hearing outcome recorded with the res-judicata status of the v1 settlement

**Verification:** `rulesets/v2.json` committed in canonical form, LF-guarded, immune-system-passing; stance discrimination proven on the polity-001 committed transcript; appellate re-hearing under v2 deterministic and replay-stable with its outcome recorded alongside the res-judicata status of the v1 settlement; suite green; package coverage 100%; CI green.

Status: complete — verification satisfied 2026-08-24: stance discrimination proven (claimant order_refund [R7]; refusal escalate_to_arbitration [R1]; contestation reopen_arbitration [R3]); appellate re-hearing under v2 OVERTURNS the contested ruling [R1] — first overturn, replay-stable; v1 settlement stands as res judicata; 68 tests, package coverage 100%.

---

## Phase 6 — Merits/Procedure Separation

**Goal:** appellate merits are game-proof: the merits re-adjudicate the original dispute under the law in force; the appeal ground is provenance, not merits input.

No Phase 0 gate applies: a pure kernel correction.

### Tasks

- [x] `tests/test_appeals.py` gaming-resistance spec — red
  - a crafted appeal whose ground contains markers absent from the dispute cannot shift the merits outcome
  - existing appellate behavior preserved (affirm/overturn branches, boundary coercion, identity-freedom, digest)
- [x] `src/law_and_order/appeals.py` correction + ARCHITECTURE.md in the same commit
  - merits = `Arbitrator.resolve(appeal.dispute)` under the ruleset in force — no ground expansion
  - ground remains content-addressed in the appeal digest (provenance)
- [x] polity-001 replay verified under v1 (AFFIRM [R1]) and v2 (OVERTURN [R1]); outcomes recorded

**Verification:** appellate merits exclude the appeal ground; crafted-appeal gaming test passes; polity-001 replay preserved under both rulesets, byte-identical across runs; suite green; package coverage 100%; CI green.

Status: complete — verification satisfied 2026-08-24: gaming-resistance proven (ground markers absent from the dispute cannot shift the merits; ground remains provenance via the digest); polity-001 replay preserved — v1 AFFIRM [R1] with final_settlement true, v2 OVERTURN [R1], both byte-identical across runs; 69 tests, package coverage 100%.

---

## Open Questions

1. Beachhead platform: Discord, Reddit, or Slack — resolved 2026-08-21: Discord, see ARCHITECTURE.md Design Decisions
2. LLM attachment point and how determinism is preserved at that seam — resolved 2026-08-21, see ARCHITECTURE.md Design Decisions
3. TypeScript parity: parallel kernel or wrapper over the Python kernel — open
4. Source of network graph data for `topology.py` — open, Phase 3 (Discord channel activity sampling; survey open item 5)

---

## Directions (decomposed) — added per decomposability rule, RCA 2026-08-30

Directions are multi-step goals. RAROC ranks directions; Decide picks the next atomic step toward the top-ranked direction. A direction is never dismissed whole as infeasible.

### Discord deployment — the beachhead, decomposed

| Step | Atomic? | Choosable? | V | P | C | RAROC |
|---|---|---|---|---|---|---|
| (a) Wiring layer vs. test server (discord.py client; adapter exists, live wiring does not) | yes | yes — mockable, no sanction to build | 4 | 0.8 | 2 | 1.6 |
| (b) Enforcement actuation (rulings that timeout/delete/AutoMod; advisory→judicial) | yes | yes — buildable against the adapter contract | 4 | 0.7 | 2 | 1.4 |
| (c) Stand-up in a real community (bot account, server, MESSAGE_CONTENT intent, moderation role) | yes | **no — requires Owner sanction** | 5 | 0.5 | 3 | 0.83 |

Step (c) is the standing sanction decision. Steps (a) and (b) are choosable and scored into the candidate set. Note: Discord's measurement also depends on Phase 8 (content-sensitive resolution) — without it a Discord measurement would be content-blind too — so Phase 8 Mechanism 1 is a prerequisite for any Discord measurement and currently outranks (a) as the bottleneck.

---

## Phase 8 — Content-Sensitive Resolution

**Goal:** the friction delta becomes a function of the conflict content, not the arena — the nonsense test fails, and a valid prime-directive measurement becomes possible.

No Phase 0 gate applies: pure kernel/engine work over existing interfaces.

### Tasks

- [x] `docs/content-sensitivity-spec.md` — the spec the Critic found missing (downgraded "precisely specified" → "precisely diagnosed"). Mechanism in dependency order: remove catch-all auto-resolution; generalize the noise filter; model party reaction to rulings (appeal path). Acceptance criterion: the nonsense test, standing at every audit.
- [ ] Mechanism 1 — remove catch-all auto-resolution: a dispute resolves only on a matched non-inert rule; unmatched disputes persist. TDD: nonsense test flips.
- [ ] Mechanism 2 — generalize the noise filter beyond the authored vocabulary (expanded markers or content-hash-memoized classifier).
- [ ] Mechanism 3 — party reaction to rulings / appeal path (largest; may split to its own phase).

**Verification:** the nonsense test (nonsense-content and empty-ruleset substitutions both change the delta; determinism and replay-stability preserved). Real-content delta recorded whatever it is, including near-zero.

Status: spec complete 2026-08-30; implementation not started.

---

## Phase 7 — Review Separation, Sharpened Criterion, First Falsified Measurement

**Goal:** the review mechanism exists and is exercised against self-deception; the prime directive is sharpened to close the arena/conflict loophole; the first measurement attempt is executed and honestly recorded as falsified.

Reverse-defined from achieved progress (2026-08-30): the work below is what was actually done, recorded after the fact at the Owner's direction.

### Tasks

- [x] `ROLES.md` — separated review roles (Steward / Critic / Auditor / Owner); five load-bearing rules; no role grades itself; void clause for same-instance role-filling; extraction note for epistegrity
- [x] Prime directive sharpened (CLAUDE.md, owner-approved b′): "the project may stand up the arena, but it may not author the conflict" — closes the "network the project does not fully control" loophole identified by the Critic verdict
- [x] `docs/polity-002/minds.json` — conflict content generated by four separate subagent minds under opposed mandates (buyer/seller, creditor/debtor); project-authored arena, non-authored conflict
- [x] `scripts/polity002.py` — measurement harness: baseline vs installed, 60 rounds, seed 7, v2 ruleset
- [x] Critic review as a separate subagent instance (fragmented context: claim + evidence, not reasoning) — the first real instantiation of the ROLES separation

**Verification:** the Critic falsified the measurement claim. Nonsense-content substitution reproduces the identical delta (0.773); empty-ruleset substitution reproduces it too. The measurement is blind to the conflict content; the number is a property of the project-authored arena. The number is not booked; the prime directive remains unmet. The falsification is recorded in commit c787a3f.

Status: complete — a separate Critic instance falsified the measurement claim before it was booked as the prime-directive number (that the Steward would have booked it absent the Critic is inference, not demonstrated — see `docs/critic-constitution-audit-2026-08-30.md`). The mission's number still does not exist; the gap is now precisely diagnosed (engine must let conflict content drive the dynamics; noise filter must generalize; legislation must be non-decorative).

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
