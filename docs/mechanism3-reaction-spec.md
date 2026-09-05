# Mechanism 3 — Party Reaction to Rulings: Specification

Status: steps 1–2 complete (2026-09-02); engine integration complete 2026-09-04 (commit f35e090 — settlement by due process live in `sim/engine.py`). Appeal determinism (open question 3) held: the appellate path added no randomness, replay byte-stable.

---

## Problem

The engine's "resolution" means a rule fired. The polity-001 lesson, constitutionalized in ARCHITECTURE Constraints, is that a ruling settles a dispute only if no party appeals, or if the appellate instance affirms on appeal. The engine currently skips both parties and the appellate institution: the graded delta measures legislative processing, not settlement. Until parties react, the delta cannot see ruling quality — a wrong-stance `order_refund` and a correct one are identical to it.

---

## Declared assumptions (spec open question 1, settled here)

1. **The reaction policy is arena, not conflict.** Parties react as a function of (ruling, the stance expressed by the adjudicated statement, which side of the statement they are on). The policy table and the stance markers are authored by the project; the conflict content that feeds them is not. Declared, not hidden, per the spec.
2. **Stance is extracted from content by markers** — deterministic, no LLM at the ruling seam, v2-doctrine applied at the reaction layer. Reaction markers live in the reaction module, not in any ruleset: legislation (what the law does with content) and arena policy (how parties receive rulings) are separate layers and evolve independently, even where their marker vocabulary overlaps.
3. **Settlement requires both parties.** A dispute settles only when both perspectives ACCEPT; one APPEAL routes to the appellate instance; affirm settles durably, overturn leaves it unsettled (ARCHITECTURE Constraints, settlement assumption).
4. **Appeal determinism** (spec open question 3): the appeal path adds no randomness and no wall-clock dependence — it reuses `Appellate.resolve`, a pure function (Phases 4/6).

---

## Contract

```
Stance   = CLAIM | REFUSAL | NEUTRAL          # stance_of(statement) — marker-based, total
Party    = AUTHOR | COUNTERPARTY              # which side of the statement reacts
Reaction = ACCEPT | APPEAL | REJECT           # total over all inputs

stance_of(statement: str) -> Stance
react(ruling: Ruling, statement: str, party: Party) -> Reaction
```

**Stance markers (arena policy; generalized 2026-09-05 after polity-004 proved the initial set missed unauthored phrasing):**
- CLAIM: `demand a refund`, `refund of`, `full refund`, `refund within`, `complete refund`, `entire refund`, `immediate refund`, `want a refund`, `want my money back`, `get my money back`, `expect a refund`, `owed a refund`
- REFUSAL: `refuse`, `refusal`, `decline`, `will not refund`, `no refund`, `will not issue`, `won't issue`, `not issuing`, `will not pay`, `won't pay`, `not paying`, `won't refund`, `won't get a refund`, `not giving a refund`, `won't give a refund`
- Generalization discipline (2026-09-05): markers expanded as linguistic families (demand/want/expect/owed claim families; will-not/won't refusal families), motivated by the diagnosed gap on polity-004 — the two workhorse markers (`complete refund`, `will not issue`) are verbatim substrings of polity-004 lines, because that is what diagnosis means; the generality claim rests on the paradigm, not on those two strings: 15 of the 18 added markers fire on no persisted polity, and the Critic (2026-09-05) confirmed the families catch novel unauthored English. Known limits, disclosed: `not paying`/`not issuing` are broader than the refund family (false-positive surface on unrelated sentences; the standing byte-identity gate protects existing polities); contraction markers (`won't …`) die on typographic apostrophes — all persisted polities use straight quotes. Validation gate, standing: nonsense substitutions stay resolved-zero on every polity, empty rulesets stay zero, and prior polities' measured histories must stay identical — verified 2026-09-05 by independent Critic replay (polity-002/003 full-60-round-history identical pre/post generalization).
- a statement carrying both classes: REFUSAL takes precedence (v2 doctrine — negation governs; refusal markers rule before general claim matches)
- matching is case-insensitive substring, no word-boundary enforcement (v2 matching convention): "declined" carries `decline`, "I DEMAND A REFUND" carries `demand a refund`
- no marker → NEUTRAL

**Reaction table (arena policy, initial set):**

| ruling action | AUTHOR stance CLAIM | AUTHOR stance REFUSAL | AUTHOR stance NEUTRAL |
|---|---|---|---|
| `order_refund` | ACCEPT | APPEAL | REJECT |
| `escalate_to_arbitration`, `reopen_arbitration` | REJECT | REJECT | REJECT |
| `escalate_to_human` | REJECT | REJECT | REJECT |
| inert (`drop`, `abstain`, `reject_oversize`) | REJECT | REJECT | REJECT |
| unknown action | REJECT | REJECT | REJECT |

COUNTERPARTY receives the inverted stance (CLAIM ↔ REFUSAL; NEUTRAL stays NEUTRAL) and the same table.

Semantics: ACCEPT — this ruling settles my side. APPEAL — unfavorable final ruling; the dispute goes to the appellate instance and stays open until affirm. REJECT — the ruling does not settle my side and is not appealed (procedural, inert, or unrecognized); the dispute persists exactly as under Mechanism 1. REJECT as default is deliberate: settlement exists only where the policy says it exists.

**Design decisions:**
- Procedural actions never settle: escalation and reopening are continuation, not resolution — both perspectives REJECT.
- Unknown actions REJECT by default: totality without invented settlement.
- Identity-freedom: `react` consumes (ruling, statement, party) only. Who spoke never enters the function.
- Consequence, stated before engine integration (audit finding N2): under the initial table, both-ACCEPT is unreachable — every final ruling yields (ACCEPT, APPEAL), everything else (REJECT, REJECT), so all first-instance settlement flows through appellate affirm. Consistent with polity-001's history (its settlement came through appeal affirm); known consequence for step 3: the engine's settlement rate will be governed by the appellate affirm rate. A richer table (mutually settleable rulings) is arena evolution, gated on measurement evidence.

---

## Engine integration (next step, out of scope here)

On adjudication of (pair, statement): both perspectives react. Both ACCEPT → dispute settles (removed, settled-set recorded). Any APPEAL → `Appellate.resolve(Appeal(dispute, ruling, ground))` with ground from the appellant's statement; affirm → settles durably; overturn → persists. Otherwise → persists. Friction is measured over the resulting dynamics. The nonsense test stays standing at every audit.

---

## Verification (this step)

`tests/test_reaction.py` red against the contract: totality, determinism across independent calls, stance extraction, the reaction table row by row, stance inversion for the counterparty, identity-freedom, and REJECT-default for unknown actions and procedural rulings. Existing suite green; red isolated to the new file.
