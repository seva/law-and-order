# CYCLE.md — Operating Methodology

A simple, iterative, scope-anchored loop. Deterministic: identical state yields identical next action. WIP limit = 1. Runs until the terminal form (see `docs/scope.md`).

---

## The Cycle

### 1. Orient — status quo against maximal scope

Inputs: `docs/scope.md` (S1–S15), `IMPLEMENTATION.md`, open issues, latest WaLRuS.
Output: current scope position and the gap to the next rung.
Question answered: *where is the project on the ladder, and what is missing to reach the next level?*

### 2. Decide — the next required atomic step

Select exactly one step satisfying all three:

- **Atomic** — completable in one session, one commit unit, verifiable
- **Gated** — depends on no undiscovered interface (METHODOLOGY.md Phase Gate)
- **Maximal** — highest RAROC = (V×P)/C among steps that advance scope position

Output: the step, recorded as a GitHub issue or an `IMPLEMENTATION.md` task.
Never queue a second step; the next is chosen only after the current one completes.

### 3. Execute

TDD per METHODOLOGY.md — tests first; done means the verification statement is true, not that code was written. Commit discipline applies; public-contract changes update `ARCHITECTURE.md` in the same commit.

### 4. Audit — evaluate against the constitution

Post-Phase Audit procedure (METHODOLOGY.md), generalized:

1. `ARCHITECTURE.md` interfaces versus current code
2. Coverage run; uncovered lines classified *Acceptable* or *Gap*
3. Cross-cutting: placeholders, `.gitignore`, record sync (issues ↔ `IMPLEMENTATION.md`), session-protocol compliance

Output: classified gap list. Zero gaps is the only passing state.

### 5. Repair

Gaps ranked by RAROC, executed in order. Each gap is an atomic step of a repair sub-cycle: return to step 4 after repairs until the audit passes clean.

### 6. Repeat

Loop invariant at cycle exit: constitution clean, scope position non-decreasing.
Session end within a cycle: checkboxes updated, comment on the open issue, WaLRuS if the session had meaningful scope.

---

## Selection function (compressed)

```
next_step = argmax  RAROC(s)   over   s ∈ feasible
feasible  = { s : advances scope position ∧ passes phase gate ∧ atomic }
```

---

## Termination

Asymptotic. The cycle runs until the terminal form — protocol ambient, agent idle. There is no completion, only convergence.
