# Operating Cycle

A simple, iterative, scope-anchored loop. Deterministic: identical state yields identical next action. WIP limit = 1. Runs until the terminal form declared in the project's scope document (`docs/scope.md`).

---

## The Cycle

### 1. Orient — status quo against maximal scope

Inputs: `docs/scope.md`, `IMPLEMENTATION.md`, open issues, latest WaLRuS, and realized RAROC of completed tasks.
Output: current scope position and the gap to the next rung.
Question answered: *where is the project on its ladder, and what is missing to reach the next level?*

### 2. Decide — the next required atomic step

Select exactly one step satisfying all three:

- **Atomic** — completable in one session, one commit unit, verifiable
- **Gated** — depends on no undiscovered interface (METHODOLOGY.md Phase Gate)
- **Maximal** — highest RAROC among steps that advance scope position

RAROC = (V × P) / C — V: value protected or unlocked (1–5), P: probability it materializes (0–1), C: cost to remediate or execute (1–5).

**Capacity value-cap.** Work that builds capacity — kernel features, institutions, legislation, adapters, harnesses — is capped at V≤2 until that capacity is exercised in a live installation that produces or moves toward the prime-directive measurement (CLAUDE.md). Capacity has derivative value and is not priced as intrinsic; only work on the measurement itself may score V≥3.

Output: the step, recorded as a GitHub issue or an `IMPLEMENTATION.md` task, together with its expected-RAROC forecast (V, P, C) — the value that success must demonstrate.
Never queue a second step; the next is chosen only after the current one completes.

### 3. Execute

TDD per METHODOLOGY.md — tests first. Done means the Definition of Success holds (below), not that code was written. Commit discipline applies; public-contract changes update `ARCHITECTURE.md` in the same commit.

### 4. Audit — evaluate against the constitution

Post-Phase Audit procedure (METHODOLOGY.md), generalized:

1. `ARCHITECTURE.md` interfaces versus current code
2. Coverage run; uncovered lines classified *Acceptable* or *Gap*
3. Cross-cutting: placeholders, `.gitignore`, record sync (issues ↔ `IMPLEMENTATION.md`), session-protocol compliance
4. Declared claims versus evidence: constitutional statements about the world (assumptions, measured numbers, verification dates) checked against `docs/` and issue evidence; stale or falsified claims corrected or marked open

Output: classified gap list. Zero gaps is the only passing state.

### 5. Repair

Gaps ranked by RAROC, executed in order. Each gap is an atomic step of a repair sub-cycle — the same Definition of Success applies: return to step 4 after repairs until the audit passes clean.

### 6. Repeat

Loop invariant at cycle exit: constitution clean, scope position non-decreasing.
Session end within a cycle: checkboxes updated, comment on the open issue, WaLRuS if the session had meaningful scope.

---

## Definition of Success

An atomic task succeeds iff all five hold. Success is a decidable conjunction, not a judgment:

1. **Pre-declared verification** — before execution, the task states one concrete, observable verification statement. Success is that statement being true. A task without a verification statement is not started.
2. **Proof, not claim** — proof is a working solution in production, actively demonstrating the expected RAROC. Tests, CI, and remote confirmations are correctness checks, not proof of value. Self-report is not evidence. Until a production surface exists, verification statements grant provisional success only — convertible to proof when the solution demonstrates its forecast value live.
3. **No constitutional regression** — `ARCHITECTURE.md` matches code; records in sync (issues ↔ `IMPLEMENTATION.md`); commit discipline observed; coverage has not regressed, and any new gap is closed or classified.
4. **Scope delta ≥ 0** — after completion, scope position is non-decreasing, and the task's contribution toward the next rung is nameable. Repair tasks satisfy this at delta = 0 by restoring the loop invariant.
5. **Legible** — completion leaves a trace: commit references its issue, checkbox flipped in the same commit, comment on the open issue.

**Corollary (atomicity test):** if any condition is undecidable within one session, the task is not atomic — split it until success becomes decidable. Atomicity and decidability of success define each other.

**Feedback:** realized RAROC of completed tasks is recorded at success and consumed by Orient to calibrate future forecasts. The selection loop is closed — estimates that do not materialize correct themselves.

---

## Autonomy

The cycle is self-sufficient by default: no step may require owner action or externally provisioned resources. When a step appears blocked on an external dependency, the dependency is inverted — the production surface is generated or reused by the project itself — before the step may be declared blocked.

The owner stands outside the cycle as its legislative layer and may sanction exceptions by prompt. A sanctioned prompt is an auditable constitutional act and the only legitimate path by which an external dependency enters the cycle. Every sanction is recorded on the relevant issue. Absent sanction, the cycle never stalls on external provisioning.

External prerequisites are real: they block the deployments they gate, and gap analysis states them plainly. Sanction is permission, not provision — the owner legislates the exception; the provisioning work belongs to the cycle (autonomous stand-up). "Blocked on owner" is not a state the cycle may occupy; absent sanction, the state is inversion, not waiting.

---

## Selection function (compressed)

```
next_step = argmax  RAROC(s)   over   s ∈ feasible
feasible  = { s : advances scope position ∧ passes phase gate ∧ atomic
                ∧ requires no unsanctioned external dependency }
proof     = working in production ∧ expected RAROC actively demonstrated
```

---

## Termination

Asymptotic. The cycle runs until the terminal form declared in `docs/scope.md`. There is no completion, only convergence.
