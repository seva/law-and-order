# Critic Verdict — Mechanism 2 Noise-Filter Generalization

**Provenance.** Verdict of a Critic subagent — a separate instance with an opposed mandate and fragmented context (claims + evidence, not the Steward's reasoning) — run at step completion, ROLES cadence. Committed as a file in the same cycle, per the defect class named in `docs/critic-constitution-audit-2026-08-30.md` finding 1 and the 2026-09-05 audit: verdicts get artifacts, not paraphrases. Known limitation, stated plainly: same base model as the system under review; separation is real but minimal — distinct context and opposed mandate, not a distinct model.

**Review date:** 2026-09-05. Claims under review: the Mechanism-2 cycle (commits 81a4360 red spec, a4f0c92 implementation).

## Verdicts

- **C1 (43 markers in five systematic families, not tailoring)** — CHALLENGED. Count and families real; but see N1/N2.
- **C2 (coverage 48/60; residuals resist family membership)** — CHALLENGED. Numbers exact; residual framing overstated (N1).
- **C3 (pin byte-exact from corpus)** — SUPPORTED. Independent probe: 48 unique lines, all verbatim corpus noise, zero claims, and pin == the exact set of corpus noise classifying UNVALUED.
- **C4 (guards)** — SUPPORTED. 80/80 unauthored claims VALUED; default population preserved; polity-001 transcript 6/6 VALUED; nonsense VALUED.
- **C5 (measurements byte-identical)** — SUPPORTED. Old-7 vs new-43 instrumented re-run: identical full histories, deltas, settlement counts, published counts, tails on all three polities (002 0.413…/2/31; 003 0.166…/4/10/tail 0.264…; 004 0.172…/4/14/tail 0.258…). Pin files unmodified in a4f0c92. One wording caveat (N4).
- **C6 (spec §2 satisfied, determinism preserved)** — SUPPORTED. classify is a pure lowercase substring scan; no randomness, no wall-clock.
- **C7 (record sync, same-commit discipline)** — SUPPORTED. Five files in a4f0c92; no stale status claims found by grep.

No claim outright falsified.

## Findings

1. **N1 — material.** Five of the twelve residuals were family-completable with guard-safe markers, yet excluded while their twins were included: `wasting` (twin of included `don't bother`/`save the excuses`), `stalling`, `keep talking` (twin of included `keep yelling`), `unbelievable`, `an excuse` (twin of included `save the excuses`). All five verified safe against every guard before and during the review. The asymmetry was evidence the boundary was drawn to land on 48, not to close families. Genuinely resisting: `rat` substring-hits two claims and a polity-001 line — that exclusion is honesty; plus the sarcasm/guilt-trip lines with no clean family member. **REPAIRED in-session:** the five markers added, pin extended 48 → 53, coverage 53/60 (12/12, 22/24, 19/24), suite green; records updated with attribution.
2. **N2 — material (mitigated).** 28/36 new markers fired on exactly one corpus line in the guarded text universe. Mitigation: most are productive lexical items (bully, calm down, garbage, loan shark, people like you); only ~4–5 are verbatim fragments. A pattern to watch, not a falsification.
3. **N3 — minor.** Red-spec commit message (81a4360) said "43 of the 48 lines pass the 7 authored markers"; measured: 6 of 48 caught, 42 slip past. Self-reported number off by one. **REPAIRED:** corrected in the records (commit messages are immutable, not amended).
4. **N4 — minor.** "No noise line ever triggered a rule match" is loose: `Your threats are pathetic.` carries the R5 substring `threat`; it never fires because `pathetic` pre-filters it under old and new markers alike, so the byte-identical result stands. **REPAIRED:** wording corrected in records to "no noise line ever fired a rule match."

## Cycle outcome

Step closed with repairs committed. The Critic's measurement-independent verification (independent classify probes, old-vs-new full-history replay) is the evidence base; the Steward's numbers matched wherever they overlapped.
