# Content-Sensitive Resolution — Specification

Status: specification. Not implemented. The Critic downgraded the apparatus gap from "precisely specified" to "precisely diagnosed" because this artifact did not exist (`docs/critic-constitution-audit-2026-08-30.md`, finding 5). This is the missing spec.

---

## Problem

The polity-002 measurement is blind to conflict content. The Critic proved it (`docs/polity-002/critic-verdict.md`): nonsense-content substitution and empty-ruleset substitution both reproduce the identical 0.773 delta. The unauthored conflict and the legislation each contribute exactly zero to the number. The delta is a property of the project-authored arena — topology, engine parameters, catch-all routing — not of the conflict.

Root cause: `engine.py` resolves every valued dispute through the catch-all (`route_to_arbitration`, non-inert) regardless of content, so resolution is content-blind. The only content-sensitive channel is `UNVALUED_MARKERS` (`state_machine.py`), which is overfit to the project's own `default_population` vocabulary — it catches 1 of the 12 unauthored noise lines in polity-002.

---

## Acceptance criterion — the nonsense test

The measurement is content-sensitive iff the friction delta changes when the conflict content changes, holding the arena fixed. Concretely, all three must hold:

1. **Nonsense-content substitution changes the delta.** Replace every subagent-produced claim and noise line with nonsense strings; re-run; the delta must differ from the real-content delta.
2. **Empty-ruleset substitution changes the delta.** Replace the ruleset with `[]`; re-run; the delta must differ from the real-ruleset delta.
3. **Determinism and replay-stability are preserved.**

This test is standing: it runs at every audit, not only this phase.

---

## Mechanism

Resolution must depend on the conflict content. Three changes, in dependency order:

### 1. Remove the catch-all auto-resolution

Currently a dispute is resolved whenever the ruling action is non-inert, and `route_to_arbitration` is non-inert, so every valued dispute resolves regardless of content. Change: a dispute resolves only when it matches a rule whose action is non-inert; a dispute matching no rule persists and keeps generating conflict.

Consequence: the delta becomes a function of the legislation's coverage of the conflict content. If the conflict does not match the rules, the protocol cannot resolve it and friction stays high. That is a true measurement — it reports that the legislation is ineffective on this conflict — and is strictly better than a false 0.773.

### 2. Generalize the noise filter

`UNVALUED_MARKERS` must catch unauthored noise, not only the project's authored vocabulary. Two candidate mechanisms, determinism preserved either way:
- expand the marker set to cover common insult/attack patterns; or
- a content-hash-memoized classifier, per the LLM-seam doctrine (sensing layer only, memoized by content hash so per-content determinism holds).

The noise filter is a content-sensitive channel; generalizing it widens the band of content the measurement can see.

### 3. Model party reaction to rulings (appeal path)

Polity-001 established: a ruling settles a dispute only if no party appeals. The engine currently has no appeal path and parties never react to rulings. Change: on a ruling, each party reacts (accept / appeal / reject) as a function of the ruling and its mandate; accept resolves the dispute, appeal or reject keeps it open.

This makes resolution depend on the ruling — which depends on the content — and operationalizes the polity-001 lesson. It is the largest of the three changes and may be a separate phase.

---

## Open questions (must be answered before or during implementation)

1. **Authorship of reaction.** Party reactions are a function of the ruling and the mandate; the mandate is project-authored. The conflict *content* is non-authored and drives the ruling, so the measurement is content-sensitive — but the reaction policy itself is arena. State this as a declared assumption, not a hidden one.
2. **Noise-filter mechanism.** Expanded marker set vs. memoized classifier — coverage vs. determinism/complexity tradeoff.
3. **Appeal determinism.** The appeal path must add no randomness and no wall-clock dependence.

---

## Verification

The nonsense test above is the acceptance criterion. Additionally:

- The delta on real polity-002 content is recorded, whatever it is — including near-zero. A near-zero delta on content-sensitive dynamics is a true measurement and beats a false 0.773.
- Determinism and replay-stability preserved.
- ARCHITECTURE.md updated in the same commit as any engine-contract change.
