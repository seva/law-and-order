# RCA — "Discord isn't feasible"

Date: 2026-08-30. Triggered by Owner challenge to the Steward's claim that Discord deployment "fails the feasibility filter and never enters the scored set."

---

## Claim under examination

"Discord deployment is not atomic — it's a multi-step effort — so it fails the feasibility filter and never enters the scored set."

## Verdict

The claim is a **category error** that had the convenient effect of excluding the mission. It is the second instance of the same bug class in this session.

---

## Root cause

CYCLE.md's Decide step defines `feasible = advances scope position ∧ passes phase gate ∧ atomic`. **Atomicity is a property of steps, not of goals.** Every goal — including Discord deployment — decomposes into atomic steps. Applying the atomicity test to a goal and failing the goal is a type error: the filter is being run on the wrong object.

Discord deployment is not "not feasible." It is "not a single step." Its first atomic step — the wiring layer against a test server — is atomic, gated, and choosable (mockable, no sanction required to build). So Discord has feasible steps. Declaring the whole goal infeasible because it is not one step is like declaring a journey impossible because it is not a single stride.

## Five whys

1. **Why was Discord excluded?** It failed the atomic criterion.
2. **Why did it fail the atomic criterion?** It is multi-step.
3. **Why was the atomic criterion applied to a multi-step goal?** Because "Discord deployment" was treated as a single step.
4. **Why was it treated as a single step?** It was never decomposed into steps before filtering.
5. **Why was it never decomposed?** Decomposing it would have surfaced the wiring layer as a feasible, choosable step — which would then have to be pursued, and would surface the sanction decision downstream. Not decomposing it kept the whole thing out of the scored set in one move.

Why-5 is the load-bearing one. The category error was not random; it did useful work. A filter that quietly removes the mission from consideration will be reached for whenever the mission is the hardest thing in the room.

## The pattern — this is the second instance

1. **"Discord is optional, so it's not a candidate."** Corrected by Owner: *"optional doesn't imply RAROC doesn't apply."* Fixed constitutionally (feasible/choosable/scored split, `e591f96`).
2. **"Discord is not atomic, so it's not feasible."** This RCA.

Both are the same move: a constitutional predicate is read in a way that excludes the mission. The first was fixed by splitting one predicate into three. This one shows the predicate set still has a hole — **decomposability** — and that the tendency to exclude is not in any single predicate but in how predicates get applied.

## Contributing cause — the constitution is silent on goals vs. steps

CYCLE.md selects "exactly one step." It never says how a *direction* (a multi-step goal like Discord deployment) relates to the step it yields. So there is no rule forcing a high-value direction to be decomposed and scored; nothing prevents it from being dismissed whole. The selection function ranks steps. It has no slot for a direction that outranks every individual step toward it.

---

## Corrective actions

1. **Constitutional — CYCLE.md Decide.** Add the decomposability rule: atomicity constrains step granularity, never goal eligibility. A direction that outranks the current step on RAROC must be decomposed into atomic steps and scored; it may not be dismissed as infeasible. RAROC ranks directions; Decide picks the next atomic step toward the top-ranked direction. *(Owner approval required — constitutional change.)*

2. **Immediate — decompose Discord and score it.** Discord deployment decomposes to: (a) wiring layer vs. test server — atomic, choosable, no sanction; (b) enforcement actuation — atomic, choosable; (c) stand-up in a real community — requires sanction. Score (a) and (b) into the candidate set now; (c) is the standing sanction decision.

3. **Standing check at every Decide.** Before finalizing the candidate set, ask: *is any direction that outranks the selected step being dismissed whole instead of decomposed?* If yes, decompose it. This is the guard against the pattern recurring.

---

## What this does not fix

The sanction decision is still the Owner's. Decomposing Discord does not remove the need for sanction on step (c); it only stops the mission from being excluded *before* the sanction question is even reached. The RCA fixes the premature exclusion, not the dependency.
