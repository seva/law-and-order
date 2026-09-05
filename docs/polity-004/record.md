# Polity-004 — Instance Record

Generated 2026-09-05 (generation sessions 02:02:05–02:02:16 −0400; mandate commit 8c1a04b at 02:01:54 — an 11-second margin, disclosed: mandate authorship and generation were one continuous act). Provenance-first polity under `protocol.md`.

Dates in this record's first revision said 2026-09-04; that was antedating — the second recurrence of this failure mode, corrected by Critic audit 2026-09-05.

## Provenance chain

Mandate → single generation pass per domain → raw output persisted **byte-for-byte** (trailing-newline drift in the first revision corrected 2026-09-05) → assembled into `minds.json` with no content editing or selection. No re-draws: the opencode session store corroborates exactly four generation sessions, each one request/response.

| Domain | Instance id | Output sha256 |
|---|---|---|
| market | ses_f8fd7144bffezNkepE7ZUxei76 | 3610c612aaaebe2f8af9948df7b5f2d109cd03fc1021d8dd05618c649707d2f2 |
| debt | ses_f8fd704c7ffejNm2oI2R694Y2f | f4cb3fb88f0d8552cb290643e361bb880d59130604c019f1e739c3059c6d136c |
| workplace | ses_f8fd6f6dcffegYkGR2EDk28m90 | 095c21460489ce8414f71cfcfcfcb623aabf85a715bc1092a1138808111dd81e |
| tenancy | ses_f8fd6e858ffe8cEKGxa9FTIfci | 05fe3455fd16028f62e658a3914d2d6cd8e6ecaf519850132ae1ca66ec4568ce |

Generator model: qwen3.8-max (alibaba) via opencode `general` agent. External corroboration lives at `~/.local/share/opencode/opencode.db` (session rows); if that store is pruned, the instance ids above become dangling pointers — the repo cannot alone re-establish non-authorship. **Evidence honesty:** `test_polity004_provenance.py` proves internal consistency (minds.json wording == persisted outputs, all eight personas, claims and noise) — it cannot catch a coordinated rewrite of both, and the non-authorship claim rests on commit ordering plus the external session store, stated here, not hidden.

**Authorship boundary (restated):** the project authored the mandates, persona positions, counterpart graph (9 symmetric pairs, identical structure to polity-003), and apparatus. The claim and noise wording is the four instances' and is used verbatim.

## Measurement (seed 7, 60 rounds, settlement semantics)

| variant | delta | resolved | published |
|---|---|---|---|
| full v2 | 0.000 | 0/9 | 24 (19 × `order_refund`, 5 × `escalate_to_human`) |
| probe (v2 − R7) | 0.000 | 0/9 | 5 |
| nonsense | 0.000 | 0/9 | 0 |
| empty ruleset | 0.000 | 0/9 | 0 |

Baseline tail 0.4299404142767987 (DISORDERED); installed tail identical — replay-stable (full-history identity).

## Mechanism — instrumented 2026-09-05, not inferred

Correction: this record's first revision claimed the 19 `order_refund` rulings were "overturned on appeal." Instrumentation falsified that: **zero appeals occurred in the entire run.** Every `order_refund` died by mutual REJECT at the reaction layer. The two refund-triggering texts — "I paid full price… I demand a complete refund" and "We will not issue a refund for damage we did not cause…" — are stance-NEUTRAL under the current reaction markers (they match no CLAIM or REFUSAL marker), and NEUTRAL yields REJECT for both perspectives; the ruling never reaches either party's acceptance or the appellate instance. All 5 `escalate_to_human` rulings REJECT the same way (no favorability entry for that action). The appellate overturn machinery is real and tested elsewhere (test_engine.py overturn fixture; polity-003's v2 run has 4 appeals, all affirm, zero overturns) — it was never engaged here.

## Interpretation — read plainly

**The legislation fired; the reaction layer killed everything before due process could weigh it.** 24 rulings is more than polity-003 produced (10) — the ruleset is not the binding constraint. The binding constraint is reaction-marker coverage of unauthored phrasing: stance the project didn't choose isn't recognized, so rulings meet NEUTRAL, both sides REJECT, nothing settles. Net order produced: zero; the delta reads 0.000.

**True zero, not blind zero:** the apparatus sees the content (24 rulings vs nonsense 0); content-sensitivity is carried by the published vector because zero settlements flatten the delta for all content. The nonsense test (as a delta test) does not flip on polity-004 — it still flips on polity-003, the mechanism-proof polity.

**Consequence for booking:** the blocker is not provenance (closed here — authorship boundary machine-checkable within the repo, externally corroborated) and is not primarily the ruleset. It is the arena's reaction-policy coverage of unauthored phrasing — the same gap polity-003 disclosed ("stance-awareness does not survive vocabulary the project did not choose"), now shown to be binding. No bookable number exists while honest content settles nothing.

**Guardrail, extended:** any evolution of the reaction table or the ruleset must be a genuine capability fix validated across polities, never a fit to polity-004's wording — fitting would re-author the conflict this record exists to evidence.

## Residuals, flagged not hidden

1. Provenance proves integrity and separation; it does not prove AI wording is "unauthored" in the strong sense, nor that authored mandates do not make the conflict authored — the Owner's interpretation, as protocol.md states.
2. The market mandate embeds "refund" (a rule-match string) in the buyer's persona position. The dispute is about a refund, so the word is situation-natural, but invariant 3 as worded ("mandates never prescribe vocabulary") is strained; protocol.md amended 2026-09-05 to distinguish natural vocabulary from prescribed coverage.
