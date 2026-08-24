# Polity-001 — First Live Adjudication

Date: 2026-08-21. The kernel's first adjudication of a real dispute between real (artificial) minds under opposing mandates — no simulation repertoire, no owner action, no external accounts. S11 in operation: substrate-blind design makes artificial minds legitimate parties.

## Provenance

- Parties: two independently spawned subagents, claimant (buyer of Order 42, cracked casing, demands refund) and respondent (seller, dispatched intact, refuses refund). Opposing mandates; all statements unscripted — genuine model output.
- Protocol: three rounds — openings, rebuttals (each party saw the other's statement and the published rulings), settlement (first word constrained to ACCEPT / REJECT / APPEAL).
- Adjudication: `scripts/adjudicate_transcript.py` over `transcript.jsonl`, ruleset v1, dispute id `transcript`. Replay-stable: identical rulings across runs.

## Result

- 6 statements, all valued — **zero unvalued text**. The adversarial conflict stayed substantive throughout; the zero-ego starvation mechanism was never needed.
- All 6 statements ruled `[R1] order_refund` — see legislative gaps below.
- Settlement: claimant **ACCEPT**, respondent **APPEAL**. `settled: false` — due process exercised live. The appeal is pending; R4 (`reopen_arbitration`) is the seed law's answer, and polity-001 is the first demand for an appellate instance.

## Falsification results (simulation assumptions)

1. **"A published ruling settles its dispute durably" — revised.** The losing party appealed rather than settled. Corrected assumption: a ruling settles a dispute only if no party appeals; an appeal reopens it. Settlement is mediated by due process, not immediate upon publication.
2. **"Unvalued text starves without reaction" — not exercised.** Real adversarial mandates produced no insults; the mechanism remains untested in the wild.
3. **Determinism of the judicial layer — confirmed.** Every statement adjudicated as a pure function of content; replay-stable across runs.

## Legislative gaps exposed by live operation

Real conflict — not self-authored conflict — generated the ruleset's first evolution pressure:

1. **Coarse matching is stance-blind.** R1 fired on the respondent's refusal ("decline the refund"), on the contestation ("dispute the refund ruling"), and on the appeal itself. v1 reads content, not stance: claim and refusal are indistinguishable.
2. **No evidence surface.** The respondent's defense was evidentiary (dispatch photos, delivery confirmation); v1 has no rule that admits, weighs, or requests evidence.
3. **No appellate instance.** R4 reopens arbitration, but nothing adjudicates the reopened case. The polity's first act of due process is waiting on a forum.

These three are the legislative agenda for the next cycle, sourced from live operation.

## Status (2026-08-24)

The appeal was adjudicated: AFFIRMED under v1 [R1], `final_settlement: true` — the dispute is durably settled through due process (Phase 4). Re-heard under stance-aware v2: OVERTURN [R1] — appellate teeth arrived with legislative evolution; the v1 settlement stands as res judicata (Phase 5). Of the three legislative gaps above: the appellate instance was built (Phase 4), stance-blind matching produced v2 (Phase 5), the evidence surface remains open.
