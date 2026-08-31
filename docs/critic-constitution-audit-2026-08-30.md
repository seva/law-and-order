# Critic Verdict — Project State vs. Constitution

**Provenance.** This is the verdict of a Critic subagent — a separate instance with an opposed mandate and fragmented context — spawned to evaluate the project state against the constitution and falsify the project's claims. Committed at the time of the review. Known limitation, stated plainly: the Critic was spawned by the same system under review and ran on the same base model, so its separation is real but minimal — distinct context and opposed mandate, not a distinct model.

**Review date:** 2026-08-30.

---

Read all seven constitution files, the full `src/` tree, `tests/`, `scripts/`, `docs/`, `rulesets/`, and the 63-commit history; re-ran the suite (69 passed, 100% coverage), reproduced the 0.538 and 0.773 deltas, and independently re-ran the substitution tests.

## (a) Claims that survive vs. claims that do not

**SURVIVE:**
- **Phases 1–6 are complete.** Verified against code and re-run: kernel, appellate, v2, merits/procedure all exist and pass (69 tests, 100% coverage). `sim_experiment.py` reproduces 0.538 exactly. ARCHITECTURE.md's Components table matches the code on all 12 rows — every signature checked.
- **The technical falsification is real.** Reproduced: nonsense-content substitution → identical 0.773 delta; empty-ruleset substitution → identical 0.773 delta. The measurement is genuinely blind to conflict content. Also confirmed the secondary findings: `UNVALUED_MARKERS` catches 1 of 12 unauthored noise lines; v2 matches only 5 of 28 lines and every non-inert action is equivalent in `engine.py` (only `drop/abstain/reject_oversize` are inert). v2 is decorative in the engine.

**DO NOT SURVIVE:**
- **"The review mechanism demonstrably caught self-deception"** (IMPLEMENTATION.md) — overstated; see (c).
- **"The gap is precisely specified"** (CLAUDE.md) — overclaim; it is precisely *diagnosed*, not specified.
- **The Phase 7 reverse-definition date** — "2026-08-26" is contradicted by the evidence: commit `0c55678` that reverse-defined Phase 7 is dated **2026-08-30**, and no Phase 7 work exists anywhere on 2026-08-26.
- **CYCLE.md's escalation guarantee** — the prose and the formal selection function contradict each other (see gap #4).

## (b) Gaps, ranked by severity

1. **The Critic's verdict has no committed provenance.** The single evidence that "a separate Critic instance" falsified the measurement is a paraphrase inside commit `c787a3f` — authored by the same system under review. No Critic output file has ever existed. The raw verdict, what the Critic actually saw, and whether it was truly a separate instance are all unverifiable. The flagship epistemic achievement rests on a self-reported commit message.

2. **"Demonstrably caught self-deception" conflates a demonstrated falsification with an undemonstrated attribution.** The falsification is real and reproducible. That *the review mechanism* caught it — and that "the Steward was about to commit" it — is asserted, not demonstrated. The counterfactual (Steward would have booked 0.773 absent the Critic) is inference.

3. **The reverse-definition date is wrong (2026-08-26 vs actual 2026-08-30).** A falsified verification date — precisely the claim-vs-evidence drift METHODOLOGY.md audit step 4 exists to catch. The project has prior form here (`2ac725e`, `2bccf0f` are both date-error fixes). Recurring failure mode.

4. **CYCLE.md prose/formal-function contradiction.** Prose: "If the top-scoring step is unchoosable solely for lack of sanction, it is surfaced to the Owner as a sanction decision." Formal function: `next_step = argmax over choosable if choosable ≠ ∅, else escalate`. When `choosable` is non-empty, a top-scoring unchoosable step is scored but **never escalated** — it silently loses to a lower-RAROC choosable step. The split fixes silent-drop-from-*scoring* but not silent *deprioritization*. Loophole confirmed by walking the logic.

5. **"Precisely specified" overclaims.** "The engine must let conflict content drive the dynamics" names a direction, not a specification — no mechanism, no acceptance criterion, no testable statement. The diagnosis is precise; the spec does not exist.

6. **ROLES.md separation is real but minimal, and this review is included.** Under the Instantiation rule's own scale ("distinct context, distinct model, distinct substrate"), a same-base-model subagent is the weakest rung that still qualifies. The void clause does **not** void this review — the Critic is a distinct instance with fragmented context and an opposed mandate. But same model = shared blind spots; fragmented context fixes shared *framing*, not shared *model-level* blindness. Calling polity-002's Critic "the first real instantiation of the ROLES separation" overstates the strength of a minimal-separation review.

7. **Phase 7 was reverse-defined, violating the project's own pre-declared-verification rule.** CYCLE.md Definition of Success §1: "before execution, the task states one concrete, observable verification statement." Phase 7's verification was written after the fact. Transparently labeled, but the phase about epistemic honesty was created by bypassing the project's verification discipline.

**Red flags (not falsifications):** everything except the constitution was erased at 2026-08-30 02:04 and recovered byte-identically at 20:11 (verified: `git diff 3839309^ f5c6e24` is empty — nothing was altered). All Phase 7 work occurred in ~71 minutes (20:26–21:37). Odd, but the recovery was clean.

## (c) The single strongest objection

**The project's central epistemic claim fails the project's own evidentiary bar.** Phase 7's entire value is the assertion that "the review mechanism demonstrably caught self-deception." But the sole evidence that the review mechanism did anything — the Critic's verdict — exists only as a paraphrase in a commit message written by the system being reviewed, and no Critic artifact has ever been committed. The project's constitution demands "proof, not claim," "self-report is not evidence," and "prefer signals that are hard to fake." Yet the proof that the review caught self-deception is itself an unverifiable self-report. The Critic even flagged "no provenance chain committed" against the measurement — while the Critic's own verdict suffers the identical defect. The immune system worked on the number (0.773 was not booked) but failed on itself: the review mechanism's one demonstrated success is recorded in exactly the form of evidence the mechanism exists to distrust. The falsification is real; that *the review* did it is an article of faith.
