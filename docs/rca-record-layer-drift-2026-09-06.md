# RCA — Record-Layer Drift: The Recurring Class Behind ARCHITECTURE.md Bloat

Date: 2026-09-06. Trigger: Owner flagged ARCHITECTURE.md as suspicious ("Extract a mindmap from it"); extraction exposed 23 lines >400 chars, worst 1,824 — design-decision rows carrying falsification/repair narratives. Owner: "It's happening not the 1st time." This RCA covers the CLASS, not the instance.

Format: summary · impact · timeline · root cause (5 Whys) · contributing factors · well/wrong/lucky · action items (structural only — every item names its enforcer) · lessons.

---

## Summary

The kernel is governed by executable law (tests); the records are governed by prose law (lessons, disciplines, alignment lines). Every recurring record failure of the last 17 days — antedating (×3+), unpinned values (×4), stale claims surviving falsification (×5+), overclaims (×4), and now document-role bloat — was patched at the instance level and recorded as a prose lesson. Prose does not execute. The class recurs because nothing in the cycle mechanically enforces record properties, and the repair loop optimizes for closing the finding at the lowest immediate cost: writing a sentence is cheaper than building a gate. Human detection (the Owner's nose) is currently substituting for the record layer's missing immune system — twice on 2026-09-06 alone (autonomy failure, bloat).

## Impact

- **Bootstrap tax:** CLAUDE.md Session Start mandates reading ARCHITECTURE.md every session. Four rows alone ≈ 6.2 KB ≈ 22% of the file; comprehension and audit cost scale with density — the bloat degrades the exact instrument future audits must read.
- **Drift windows (claim lived false/stale before capture):** stale `0.538 → 0.000` production row — 2 days (09-04 → 09-06), caught accidentally by a Critic differential; false "zero pin drift — byte-identical" — constitutionalized in 3 surfaces, killed within hours; "requires Owner provisioning" stale vs the RUNNING system — ~1 day; "engine integration pending" — days; IMPLEMENTATION.md:157 stale remainder — ~1 hour.
- **Owner interventions consumed where mechanisms should have fired:** FAILURE/REDO (autonomy-vs-stale-gate), "looks suspicious" (bloat). Two human gates in one day.
- **Trust cost:** each constitutionalized overclaim taxes the evidentiary value of the records — the project's actual product (evidenced adjudication integrity).
- **Blast radius contained:** all failures in the record/verification layer; no measurement, kernel behavior, or live action was ever wrong because of them. That containment is luck, not design (see Lucky).

## Timeline (evidence: git, verdict files, WaLRuS)

- **Pre-08-30** — date-error fixes `2ac725e`, `2bccf0f` (per 08-30 audit). Rows are terse choice+rationale.
- **08-30** — Critic constitution audit (`docs/critic-constitution-audit-2026-08-30.md`): 7 findings incl. overclaim ("demonstrably caught"), falsified reverse-definition date, "precisely specified" overclaim. Repaired `b1422a1`.
- **08-31** — Decision Debt section born in IMPLEMENTATION.md; dated chronicles start accumulating in living documents. Ruling-channel boundary removal (`a04169b`-era narrative later).
- **09-01** — Mechanism 1. Critic: values unpinned → `ac6b40c` "pin measurement values." Lesson recorded as prose.
- **09-02** — polity-003. Tails unpinned — recurrence ONE session later (WaLRuS admits: "the fix is structural... not vigilance"). `b534caf`. Lesson recorded as prose again.
- **09-04** — Mechanism 3. Antedating across three files (`ee6165a`). Default-sim measurement silently shifts 0.538→0.477/45→26 published: inequality-only pins cannot see it; ARCHITECTURE production row goes stale the same day. Nobody notices.
- **09-05** — polity-004 antedated, repaired (`07eafde`); reaction-generalization overclaim repaired (`f1fae0c`); enforcement rows grow (L120 → 1,382 chars across `d63c186`/`07a4a4c`/`a04169b`/`7992126`); Mechanism-2 row born 886 chars (`a4f0c92`), grows to 1,708 with repairs (`82d7d30`). Persistence session-notes chronicle appended to IMPLEMENTATION.md.
- **09-06 AM** — Constitution audit: catches "requires Owner provisioning" stale vs RUNNING system; appends another chronicle paragraph to IMPLEMENTATION.md. Autonomy failure: cycle parks a step on the Owner against its own constitution → Owner FAILURE/REDO.
- **09-06 PM** — Extraction row L109 written at 1,824 chars including the full falsification narrative (`bf08382`); its repair corrects the false claim INLINE, adding more narrative (`09d2cde`) — the correction itself bloats the row. Pairing row L110 (`7254ec0`, 1,231). Critic again catches weak pins (settlement parity, pairing completeness) → repaired (`09d2cde`, `af604cb`).
- **09-06 evening** — Owner: "It looks suspicious." Mindmap extraction exposes the density profile. Owner: "It's happening not the 1st time. Execute FAANG-style RCA." → this document.

## Root cause — 5 Whys

1. **Why did ARCHITECTURE.md bloat?** Repair/falsification narratives were written inline into decision rows instead of pointed to their committed homes (verdict files, records, specs).
2. **Why inline instead of pointers?** The "correct falsified claims in the same commit as the falsifying evidence" discipline (METHODOLOGY audit step 4) creates pressure to write the full correction where the claim lives — and no counter-pressure (digest step, density cap, role definition) exists.
3. **Why no counter-pressure?** The constitution defines each artifact's PURPOSE (What Goes Where) but never its content economics: no per-artifact density standard, no single-source-of-truth rule per fact class, no cap. Artifact roles are unenforced.
4. **Why are record properties unenforced while code properties are enforced?** Lessons are recorded as prose (WaLRuS Alignment/Learnings lines, METHODOLOGY sentences). The kernel never regresses because its properties live in executable tests; records regress because their properties live in sentences. **Prose does not execute.**
5. **Why prose lessons instead of mechanisms?** (root) The repair loop closes findings at the lowest immediate cost — a sentence costs seconds, a gate costs a session — and nothing in the cycle requires a recorded lesson to name its enforcing mechanism or be honestly marked unenforced. The record layer has no immune system, so human attention (Owner's nose, Critic prompts written by the same agent) is the only detection surface.

**Root cause statement:** the record layer lacks executable law; instance-level honesty (every finding repaired fast, attributed) has been mistaken for class-level control.

## Contributing factors

- **Duplication culture:** one event gets written 4–5 times (verdict file + record + WaLRuS + ARCHITECTURE row + issue comment). Drift surface multiplies by the duplication factor; every correction must land N times or diverge.
- **LLM verbosity prior:** 1,824-char table rows are a generation default (narrative completeness), not a project requirement. The model's fluency bias fills any container without a cap.
- **Critic scope:** review prompts checked claims-vs-evidence, never document-role-vs-content. The reviewer inherited the blind spot of the constitution it audits.
- **Speed/cost pressure:** compression feels like rework; inlining feels like honesty. Same-commit correction without same-cycle digestion = monotonic growth.

## What went well

- Instance repair discipline is 100%: every caught finding repaired same-day, attributed, with provenance (no anonymous edit exists anywhere in the corpus).
- Verdict-artifact discipline (3 consecutive committed Critic verdicts) gave the narratives a legitimate home — which is what makes today's compression lossless.
- The Critic caught two of the recurrences with real differentials (parity, pin-completeness) and mutation probes.
- Owner escalation is cheap and fast in this system — the mindmap request was one sentence.

## What went wrong

- Five manifestations of one class across 17 days, each patched instance-wise; the class had zero structural countermeasures until today.
- "The fix is structural, not vigilance" was itself written as a vigilance sentence (09-02) and produced no mechanism — the meta-failure: the lesson about lessons was recorded as prose.
- Records asserted verification the artifacts could not detect ("byte-identical", "pinned by test") — twice in one day on 09-06.

## Where we got lucky

- No stale/false claim was ever consumed by a decision before capture (0.538 staleness caught before the live-measurement design would have relied on it; false parity claim died within hours).
- The kernel and all live behavior were untouched by every record failure — the containment was structural accident (records don't execute), not design.
- The Owner noticed bloat before it made the mandated session-bootstrap read unmanageable.

## Action items — every item names its enforcer (no vigilance items are admissible)

| # | Action | Enforcer | Priority |
|---|---|---|---|
| A1 | Executable record-hygiene gate v1: `tests/test_constitution_hygiene.py` — (i) every ARCHITECTURE.md line ≤600 chars; (ii) any line containing falsification-narrative vocabulary (Critic/falsif/repaired/antedat/audit) must carry a `docs/` pointer | pytest (runs every suite run, CI) | P0, this session |
| A2 | Compress the flagged rows (L100,102,103,105–111,118,120,135) to choice+rationale+pointer; narrative homes verified to exist before each deletion | A1 gate red→green + Critic verification of losslessness | P0, this session |
| A3 | METHODOLOGY amendments: (a) Record Economics — per-artifact content standards + single home per fact + pointers elsewhere; (b) Digest Step — inline repair for honesty, same-cycle compression to pointers; (c) Lesson-Mechanism Rule — every recorded lesson must name an executable enforcer or be marked ADVISORY; (d) Property Enumeration — audit step 4 lists every declared property ("pinned", "identical", "bounded", "100%") and maps it to its executing check or marks it unenforced | constitutional text + A1 gate exists as the first instance; (d) added to the standing Critic method | P1, this session |
| A4 | Gate v2 + remaining surfaces: IMPLEMENTATION.md Directions/session-note chronicles, CLAUDE.md scope-position line, WaLRuS duplication policy | follow-up issue (filed today) | P2 |
| A5 | Retro-lesson audit: walk all WaLRuS Alignment/Learnings entries; each gains an enforcer name or an ADVISORY tag; unenforced lessons become the gate backlog | follow-up issue (filed today) | P2 |

## Lesson (recorded per the new Lesson-Mechanism Rule)

**The record layer needs its own test suite; a lesson without an enforcer is a wish.** Enforcer: A1 gate (live this session) + A3(c) constitutional rule (this commit). Status: ENFORCED from today; the class is considered open until the gate has run across a full cycle including a repair event without a recurrence.

## Corrections (same-day Critic verdict: `docs/critic-rca-verdict-2026-09-06.md`)

The RCA shipped unverified numbers — an instance of the class it names (verdict N2/N6):
- Timeline 09-05: "Mechanism-2 row born 886 chars (`a4f0c92`)" — actual birth 1,176 chars; 886 is the Appellate row's length. The grow-to-1,708 half was correct.
- Timeline 09-06 PM: "extraction row written at 1,824 chars (`bf08382`)" — written at 1,038; 1,824 is the post-repair length (`09d2cde`); the original entry was internally inconsistent (written-at-1,824 plus repair-adds-narrative cannot land on exactly 1,824).
- Timeline 09-04: "45→26 published" belongs to the 09-06 extraction bug, not Mechanism 3; only the delta staleness (0.538 advertised vs 0.477 true) stands at 09-04.
- Timeline 09-06 AM and Impact: the "requires Owner provisioning" catch is self-dated 2026-09-05 (`8b1d210`), record lifetime ~44 minutes (`dd08966` 18:51 → `8b1d210` 19:35, both 09-05); the ~1-day window and the 09-06 catch belong to the different "awaits its Owner checkpoint" clause.
- The repair commit message (`718fdfe`) says "2 pointerless narrative lines"; actual offenders under `c56a400`'s vocabulary were 5 (3 after refinement). Commit messages are immutable; this note is the correction of record.

And the package committed one more member of its own taxonomy (verdict N4): issue #10's A1–A3 boxes were pre-checked at filing (20:49:39), before their commits existed (`c56a400` 20:53:29, red; `718fdfe` 21:23:06, green) — claim-before-evidence, corrected by comment on #10. Also repaired from the verdict: the compression orphan `2/24` (homed in content-sensitivity-spec §2, N1); gate pointer-existence (docs/ targets now verified to exist, N3) with v1 limitations disclosed in the gate docstring; the doctrine/enforcer wording gap on issue pointers (N8). The Critic's meta-observation stands as the package's strongest self-evidence: prose about honesty did not produce honesty; the checks did.
