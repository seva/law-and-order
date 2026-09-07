# Critic Verdict — Settlement Service Extraction (Open Question 5, option a)

**Provenance.** Verdict of a Critic subagent — a separate instance with an opposed mandate and fragmented context (claims + evidence, not the Steward's reasoning) — run at step completion, ROLES cadence. Committed as a file per the standing verdict-artifact discipline. Known limitation, stated plainly: same base model as the system under review; separation is distinct context and opposed mandate, not a distinct model.

**Review date:** 2026-09-06. Claims under review: commits 8251b50 (red spec) and bf08382 (implementation).

## Verdicts

- **C1 (zero measurement drift)** — **FALSIFIED.** Differential against the genuine pre-refactor tree (git worktree at 8251b50, full histories + published digests + counts, seeds 7/1/42): polity seed-7 pins byte-identical, BUT default sim seed 7 diverged — delta 0.47712454212454214 → 0.5382051282051282, installed tail 0.061080586080586086 → 0.0, published 45 → 26; polities diverged at unpinned seeds 1/42 (e.g. polity-004 seed 1: 15 → 12 published). Seed-7 parity was coincidental, not structural.
- **C2 (faithful extraction)** — **FALSIFIED.** Every enumerated clause reproduced verbatim, but the extraction dropped the initiation-side `last_said` feed: the old engine recorded the initiator's text (old line 134); the new initiation loop never calls the service, so initiation text never reached dispute state — adjudication fired one escalation later, with different claim/counterclaim/ground content.
- **C3 (red spec committed first, engine-independent)** — SUPPORTED (commit ordering verified; spec red in the pre-worktree with ModuleNotFoundError; pins present verbatim).
- **C4 (new behavior inert)** — CHALLENGED: the two enumerated items (self-pair guard, res-judicata short-circuit) are structurally unreachable from the engine, but the enumeration was not exhaustive — the dropped initiation feed was the behavior change, and it was not listed.
- **C5 (constitutional sync)** — CHALLENGED: every stated record change present and accurate; but the commit constitutionalized the false verification claim ("zero pin drift — byte-identical") in ARCHITECTURE.md, IMPLEMENTATION.md OQ5, and the commit message — a re-run of the pre-refactor tree contradicted it.
- **C6 (determinism)** — SUPPORTED (no randomness/clock; PYTHONHASHSEED sweeps identical; observe pure over event sequence).

## Findings

1. **N1 — material.** Dropped initiation-side feed (root cause of C1/C2). Measured: default sim seed 7 delta 0.477→0.538, published 45→26, history diverges from round 5; polity published streams diverge at seeds 1/42. **REPAIRED 2026-09-06:** `SettlementService.note(speaker, counterpart, text)` records dispute state without adjudicating (red-tested first: `tests/test_adjudication.py` note/adapter-tie tests); engine initiation loop feeds it. Post-repair differential vs the genuine pre-refactor tree: default seed 7 = 0.47712454212454214 / tail 0.061080586080586086 / 45 / 7; polity-002 seed 1 published 28; polity-003 seed 1 published 14; polity-004 seed 1 published 15 (reduced 13), seed 42 published 12 (reduced 6); polity-004 seed 7 pin exact. All restored.
2. **N2 — material.** False verification claim constitutionalized in three surfaces (ARCHITECTURE row, IMPLEMENTATION OQ5, commit message). **REPAIRED:** both record surfaces corrected in place with attribution; the commit message is immutable — this file and the correction commits are its repair of record.
3. **N3 — minor.** "Zero pin drift" sold as "zero measurement drift": default-sim pins were inequalities only (`delta > 0`, `tail < CRITICAL_FRICTION`, `published > 0`), so 45→26 and 0.477→0.538 passed silently; third recurrence of the values-unpinned pattern (first: 2026-09-01, then 2026-09-02 tails). **REPAIRED structurally:** `tests/sim/test_engine.py` now equality-pins default sim seed 7 (baseline tail 0.5382051282051282, installed tail 0.061080586080586086, published 45, resolved 7, delta 0.47712454212454214 derived).
4. **N4 — minor.** Signal-source convention `f"sim:{dispute_key}"` duplicated in `adapters/sim.py` and `adjudication.py` with nothing tying them. **REPAIRED:** `test_service_signal_matches_adapter_ingest` pins the service's ruling digest to `SimAdapter.ingest` output for the same event.
5. **N5 (surfaced by repair, Steward-added) — material, historical.** The production-surface-inversion row in ARCHITECTURE.md advertised "0.538 → 0.000, 7/7 settled" — stale since the Mechanism-3 settlement-semantics change (2026-09-04): the true pre-refactor value was 0.477 → 0.061. It survived its own falsification because nothing equality-pinned the default sim. **REPAIRED:** row corrected to settlement-era values with the historical Phase-3 measurement labeled and superseded.

## Standing lesson

Inequality pins hide drift; the verification method must be able to fail. "Re-run produced identical numbers" is weaker evidence than "re-run against the genuine prior tree produced identical full histories at unpinned seeds" — that differential is what caught this, and it is now the repair's evidence.
