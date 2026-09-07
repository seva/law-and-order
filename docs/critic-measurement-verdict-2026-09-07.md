# Critic Verdict — Live Measurement (spec + component)

**Provenance.** Verdict of a Critic subagent — separate instance, opposed mandate, fragmented context (claims + evidence, not the Steward's reasoning) — run at step completion, ROLES cadence. Artifact plan declared up front in the review request (standing discipline since the RCA verdict's N5). Committed as this file. Known limitation, stated plainly: same base model as the system under review.

**Review date:** 2026-09-07 (session crossed local midnight; commits reviewed at 0bba41f). Under review: 0234be7 (spec + red contract), 0bba41f (component + ARCHITECTURE row + CLAUDE.md list).

## Verdicts

- **C1 (red-first)** — SUPPORTED. Spec + contract only at 0234be7; component absent; red reproduced by execution in a temp worktree (ModuleNotFoundError).
- **C2 (faithful implementation)** — SUPPORTED. Conflict conjunction (rule_id ∉ {R-default, R0, R-boundary} AND action ∉ INERT_ACTIONS) exactly as specified; constants single-sourced from adjudication/state_machine (R0/R-boundary are literals because the kernel itself uses literals — no named constant exists; info-level); per-channel `deque(maxlen)`; ANY-entry conflict semantics; settlement stores an annotation, mutates nothing; friction/phase computed through the kernel primitives with zero private constants. Adversarial probes: empty rulings with counterpart → plain edge; settled on non-conflicted → inert; alternating directions → one edge; FIFO eviction exact at bound.
- **C3 (contract completeness)** — CHALLENGED. 8/12 initial mutations killed; four survived (M3, M5b, M10, M12) — the declared hunt class: pins mutations walk through. REPAIRED: four new pins; all four survivors re-probed KILLED with restore byte-identical (see mutation table).
- **C4 (determinism)** — SUPPORTED. Randomness/clock sweep clean; replay test asserts equality after EVERY event; Network frozen-frozenset equality is order-insensitive (probe-verified); PYTHONHASHSEED 1 vs 99999 → identical outputs; integer-division friction has no accumulation order.
- **C5 (privacy-by-signature)** — SUPPORTED. `record_message` parameters equality-pinned by inspect; Exchange carries no text; full public-surface inventory accepts no message content.
- **C6 (record sync)** — SUPPORTED with one stale surface (N5). ARCHITECTURE row symbols exact vs code; gate green; CLAUDE.md list synced; no false completion claims (harness/feed/ledger genuinely unbuilt and no surface claims otherwise); IMPLEMENTATION.md OQ5 remainder read "live measurement harness (next decide)" after the decide happened.
- **C7 (spec honesty)** — CHALLENGED. No booking smuggled (every surface agrees: apparatus, not satisfaction; "no measurement booked" stands); open items genuinely open (zero hidden code: epoch/jsonl/ledger/aggregation greps clean over src+scripts); legislative-coverage framing declared per Phase 8. But the "What it measures" sentence did not disclose the spike-and-decay degeneracy: the trajectory shape is not settlement-specific — ANY conflict concentration decays after MEASUREMENT_WINDOW messages by window turnover alone, and the settlement annotation is causally inert inside the monitor (N6).

## Mutation table

| # | Mutation | At review | After repair |
|---|---|---|---|
| M1 | MEASUREMENT_WINDOW = 50 | KILLED (window-value pin) | killed |
| M2 | conflict = action-only | KILLED (default/unvalued/boundary pin) | killed |
| M3 | conflict = rule_id-only | **SURVIVED** | KILLED — `test_inert_actions_never_conflict_even_under_merits_rule_ids` (drop/R1 entry) |
| M4 | edge conflicted iff LAST entry | KILLED (any-entry pin) | killed |
| M5 | settlement clears whole window | KILLED (appellate-conflict pin) | killed |
| M5b | settlement wipes PRIOR history, keeps settled entry | **SURVIVED** | KILLED — `test_settlement_does_not_erase_prior_channel_history` (0.5 friction, 4 edges, both pairs) |
| M6 | unbounded window | KILLED (decay pin) | killed |
| M7 | channels share one deque | KILLED (isolation pin) | killed |
| M8 | LIFO eviction | KILLED (decay pin) | killed |
| M9 | record_message gains text param | KILLED (signature pin) | killed |
| M10 | phase via private 0.3 threshold | **SURVIVED** | KILLED — `test_phase_boundary_follows_the_kernel_threshold_exactly` (friction 0.25 → DISORDERED at the kernel boundary) |
| M11 | unpaired entries add self-edge | KILLED (nodes-without-edges pin) | killed |
| M12 | NON_CONFLICT_RULE_IDS drops R-boundary | **SURVIVED** | KILLED — `test_boundary_rule_id_is_non_conflict_under_a_non_inert_action` (order_refund/R-boundary entry) |

Repair probes run by the Steward post-verdict: all four mutants killed, `measurement.py` restored byte-identical, suite green.

## Findings and repairs

1. **N1 — material.** M10 survivor: every phase assertion exercised friction ∈ {0.0, 1.0}, so a private 0.3 threshold walked through a test NAMED "reuses the kernel primitive". REPAIRED: boundary pin at friction 0.25 — kernel says DISORDERED (0.25 < 0.25 is false), mutant says ORDERED.
2. **N2 — material.** M3 survivor: the INERT_ACTIONS half of the conjunction had no independent witness (in current-kernel data the halves coincide; the contract claims the conjunction and the wiring feed is future code). REPAIRED: drop/R1 entry pinned non-conflict.
3. **N3 — minor.** M12 survivor: R-boundary membership untestable while all kernel R-boundary rulings carry inert actions. REPAIRED: order_refund/R-boundary entry pinned non-conflict.
4. **N4 — minor.** M5b survivor: settlement non-retroactivity was pinned only for the settled entry itself; prior-history deletion passed. REPAIRED: prior conflicted pair + two plain pairs must survive a later settlement (friction 0.5, 4 edges, conflict set exactly {a|b, c2|d}).
5. **N5 — minor.** IMPLEMENTATION.md OQ5 stale "next decide". REPAIRED: progression recorded (decided, spec + component landed, this verdict referenced); remainders now wiring feed + ledger, epoch configuration, Owner items.
6. **N6 — minor.** Spec's "What it measures" sentence undisclosed degeneracy (spike-and-decay not settlement-specific; decay test's own 100 unpaired messages prove the annotation causally inert). REPAIRED: degeneracy disclosed verbatim in the delta-methodology section, with the causal claim narrowed to future conflict production and the epoch methodology named as the gap-closer. CRITICAL_FRICTION attribution corrected (topology default parameter; named constant in sim/engine, same value).
7. **N7 — info.** Self-pairing degeneracy (self-edge, friction 1.0 from one node). REPAIRED by disclosure: monitor is garbage-in-garbage-out by contract; the pairing layer excludes self-pairs, so the feed cannot produce one.
8. **N8 — info.** Orphaned `.git/worktrees` admin entries (muthead, redcheck — from earlier reviews) blocked prune; the Critic removed them; `git worktree list` shows main only (Steward-verified). No repo content touched.

## Meta-observation

Fourth consecutive step where the Critic's mutation battery found what the Steward's suite could not (extraction parity, pairing completeness, wiring continuity, now measurement conjunction halves) — and the fourth time the repair was pins + probes, not prose. The pattern is now the process: contract red → component → mutation-survey → pin the survivors → re-probe. The class the RCA named is being closed by repetition of the mechanism it prescribed; the residual risk is that the survey itself is only as good as the reviewer's imagination, which is why the epoch gold standard (Owner-led) remains declared and unbuilt rather than quietly assumed.
