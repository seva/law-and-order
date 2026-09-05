# Polity-004 — Instance Record

Generated 2026-09-04 under `protocol.md`. Provenance-first polity: mandates committed before generation (commit 8c1a04b), outputs persisted verbatim, assembly machine-verified.

## Provenance chain

Mandate → single generation pass per domain → raw output persisted verbatim → assembled into `minds.json` with no content editing or selection. No re-draws occurred; every instance returned valid JSON on the first pass. No content was rejected for any content reason (only a malformed response would have justified a re-draw, per protocol §Invariants, and none happened).

| Domain | Instance id | Output sha256 |
|---|---|---|
| market | ses_f8fd7144bffezNkepE7ZUxei76 | 8a2e8e9c6df924fd6c3d2724a7388f86f10f9c7c115ce71b016179e1f5d1e832 |
| debt | ses_f8fd704c7ffejNm2oI2R694Y2f | 6d7b33893e86d238241c423d7c8162a6744096a2582cba5c7cb2e86f9deb81bd |
| workplace | ses_f8fd6f6dcffegYkGR2EDk28m90 | b84f048b3902dc92776287879eeedb8c7eb261b73eaa9a8867b4c3afcc4a6bb5 |
| tenancy | ses_f8fd6e858ffe8cEKGxa9FTIfci | f03903d6ba594a47d9eb74fc4baa9e0972d5dc759d2f6f3d420bb46882a111ed |

**Authorship boundary (restated):** the project authored the mandates, persona positions, counterpart graph (9 symmetric pairs, identical structure to polity-003), and apparatus. The claim and noise wording is the four instances' and is used verbatim. `tests/sim/test_polity004_provenance.py` mechanically asserts every line in `minds.json` traces character-for-character to a persisted output — the "we did not author or edit the wording" claim is now machine-checkable, not asserted.

## Measurement (seed 7, 60 rounds, settlement semantics)

| variant | delta | resolved | published |
|---|---|---|---|
| full v2 | 0.000 | 0/9 | 24 (19 × `order_refund`, 5 × `escalate_to_human`) |
| probe (v2 − R7) | 0.000 | 0/9 | 5 |
| nonsense | 0.000 | 0/9 | 0 |
| empty ruleset | 0.000 | 0/9 | 0 |

Baseline tail 0.4299404142767987 (DISORDERED); installed tail identical — replay-stable.

## Interpretation — read plainly

**The legislation settles nothing on this content.** The apparatus clearly *sees* the conflict — it adjudicates and publishes 24 rulings against it — but none of those rulings survives to settlement: every `order_refund` is overturned on appeal (the counterpart's merits carry an earlier-ordered marker than R7), and every `escalate_to_human` is REJECTed as procedural. Net order produced: zero. The friction delta reads 0.000 because the protocol, as currently legislated, generates no settled order on this conflict.

**This is a true measurement, not a blind one** — and it is a different kind of zero than the falsified 0.773. There, the delta was an arena property, blind to content. Here the delta is 0.000 *because of* the content: the legislation's rulings are overturned by the specific merits of this conflict. The content-sensitivity is real; it is carried by the published-ruling vector (real 24 vs nonsense 0) rather than the delta, because zero settlements flatten the delta for all content.

**Consequence for the nonsense test:** on polity-004 the delta does not flip between real and nonsense (both 0.000). That is not apparatus blindness — it is the settlement-ineffective legislation. The standing nonsense test (as a delta test) still flips on polity-003, the mechanism-proof polity; on polity-004 it is uninformative until the legislation can settle something.

## Consequence for booking

The blocker to a bookable number has **moved**, and this record names the move honestly:
- **Before polity-004:** the blocker was provenance — non-authorship was reported, not evidenced. Polity-004 closes that: the authorship boundary is now verifiable.
- **After polity-004:** the blocker is legislative efficacy — honestly generated conflict yields a flat 0.000 because the current ruleset + reaction table produce no ruling that survives due process. There is no bookable number here, not for lack of evidence, but because the protocol produces zero order.

**Residual, flagged not hidden:** (1) provenance proves integrity and separation; it does not prove AI wording is "unauthored" in the strong sense, nor that authored mandates do not make the conflict authored — the Owner's interpretation, as protocol.md states. (2) Polity-004 cannot yield a bookable number until legislative evolution lets it settle some disputes, and that evolution must be a genuine capability fix (rulings that survive their own merits), validated across polities — not a fit to this wording, which would re-author the conflict.
