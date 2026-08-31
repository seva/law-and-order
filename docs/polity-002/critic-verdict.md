# Critic Verdict — Polity-002 Measurement Falsified

**Provenance.** This is the verdict of a Critic subagent — a separate instance with an opposed mandate and fragmented context (given the claim and the evidence, not the Steward's reasoning), spawned to falsify the polity-002 measurement claim. It is committed here to give the verdict provenance; previously it existed only as a paraphrase inside commit `c787a3f`. Known limitation, stated plainly: the Critic was spawned by the same system under review and ran on the same base model, so its separation is real but minimal — distinct context and opposed mandate, not a distinct model. This file is the best available record of that review.

**Review date:** 2026-08-30 (committed post-hoc to close the provenance gap).

---

## VERDICT

**(a) The claim does NOT survive falsification.** The number exists and reproduces (I ran `scripts/polity002.py`: baseline 0.773, installed 0.000, delta 0.773, 4/4). But the delta is provably a property of the project-authored arena, not of the unauthored conflict. The claim inverts what was measured.

**(b) Weaknesses, ranked:**

1. **The measurement is blind to the conflict content.** I replaced every subagent-generated claim and noise line with nonsense strings: identical delta 0.773. I replaced `rulesets/v2.json` with an empty ruleset `[]`: identical delta 0.773. The unauthored content and the legislation both contribute exactly zero to the number. The only channel through which content *can* affect the result is `UNVALUED_MARKERS` (state_machine.py:6-16) — and that list is literally the noise vocabulary of the project's own `default_population` (population.py:14-71). The sole content-sensitivity is tuned to authored conflict.

2. **Installed tail = 0.000 is pool exhaustion, not order.** The hardcoded `COUNTERPARTS` graph (polity002.py:20-25) permits exactly 4 distinct dispute pairs. The catch-all `route_to_arbitration` (state_machine.py:45) resolves each pair on first escalation (engine.py:58-67 — any non-inert action resolves). Once all 4 pairs are consumed, `candidates` is empty forever (engine.py:92-97). Order is achieved by running out of possible disputes, not by changing behavior. Same 4/4 across every seed I tested.

3. **Authorship sits with the project.** The project authored the mandates, the two opposed dyads, the claims/noise schema, and — decisively — the counterparts graph, which lives in polity002.py, not in minds.json. The subagents chose neither their opponents nor the structure of their conflict. And there is no provenance chain: `docs/polity-002/` contains only minds.json — no prompts, no raw outputs, no hashes. "Verbatim" is asserted, not evidenced.

4. **The noise filter fails on the unauthored content it exists to handle.** Of the 12 subagent noise lines, the filter catches 1 ("worthless"). "Scammer," "garbage," "parasite," "coward," "disgust" all classify as VALUED and route to rules. The flagship mechanism ("drop unvalued text without reaction") is overfit to self-authored conflict — precisely the failure mode the prime directive exists to prevent.

5. **The legislation is decorative.** Of 28 content lines, 5 match real rules (R4 "breach" ×3, R7 "refund" ×2); R1, R2, R3, R5, R6 never fire. All non-inert actions are equivalent in the engine, so the 5 that do match behave identically to the catch-all. v2 ≡ empty.

6. **Seed selection.** Delta ranges 0.667–0.773 across seeds; the reported seed 7 is the maximum in my sample. "Replay-stable" is trivial for any seeded deterministic sim and conflates reproducibility with robustness.

7. **The engine ignores the project's own prior lesson.** Polity-001's record (record.md:19) established "a ruling settles a dispute only if no party appeals." The engine has no appeal path and parties never react to rulings. "Resolved" means "the catch-all fired."

**(c) Single strongest objection:**

The nonsense-content experiment. Replacing every word the subagents produced with "alpha beta gamma / delta epsilon zeta" reproduces the identical 0.773 delta. Therefore the friction delta was not "measured on conflict produced by minds the project did not author" — it was measured on the arena *while* unauthored conflict sat as inert payload. The part of the conflict the project did not author is exactly the part the measurement cannot see; the part it did author (topology, engine parameters, catch-all) is 100% of what the number registers. The project did not clear the bar. It built an arena in which the bar cannot exist, then reported the arena's saturation level as if it were the conflict's resolution.
