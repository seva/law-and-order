# Critic Verdict — Measurement Feed (observe-only wiring integration + JSONL ledger)

**Provenance.** Verdict of a Critic subagent — separate instance, opposed mandate, fragmented context (claims + evidence, not the Steward's reasoning) — run at step completion, ROLES cadence. This review was CANCELLED mid-run on 2026-09-07 (first launch) and RELAUNCHED after the epistegrity migration landed; it judges the step's commits (d39ae1a, 94d60bf) against current HEAD (dd4f5f0 — migration touched no src/). Artifact plan declared up front. Known limitation, stated plainly: same base model as the system under review.

**Review date:** 2026-09-07. Suite at review: 215 passed (pre-repair; 219 post-repair).

## Verdicts

- **C1 (red-first)** — SUPPORTED. d39ae1a is tests-only; red reproduced by execution in a temp worktree (ModuleNotFoundError ledger; Routing ImportError; no record param at that commit).
- **C2 (feed isolation — load-bearing)** — SUPPORTED. feed_measurement invoked only after pronounce calls on both paths (call-site grep); exceptions caught and logged (pinned); record=None flow equivalent to pre-feed 11837ea semantics (line-by-line comparison); degenerate events pronounce legacy without feed; import graph confirms measurement/ledger cannot reach ruling paths (ledger→measurement is the only edge, for replay).
- **C3 (feed facts exact)** — SUPPORTED. One call per message (exact 3-record list equality); pronounced-prefix tuples; settled-even-on-pronouncement-failure; self-messages silent; paired-unripe records the tracker-resolved counterpart. Gap: partial prefix (success-then-failure) bracketed but not directly pinned (N8 — repaired).
- **C4 (ledger contract)** — SUPPORTED with one material detection gap. Closed field set + signature pins; seq continuation file-derived; append-only (only "a" and touch exist in the module); replay identity vs live-fed monitor; blank-line skip; touch() pinned. Gap: order fidelity beyond the window unpinned — M8 survived (N3 — repaired).
- **C5 (mutation battery)** — 9 KILLED / 3 SURVIVED at review (M8 replay-reverse, M9 startup-touch invocation, M11 recorder-closure settled falsification). All three repaired and re-probed KILLED (below). M9 answered as demanded: no test caught startup-touch removal; the claim rested on the live artifact (0-byte file, mtime 8 s after process start) + the touch() unit pin.
- **C6 (record sync)** — CHALLENGED. Step-commit rows exact vs code; current wiring row still matches. Two surfaces stale at review: IMPLEMENTATION.md OQ5 still listed the feed as "next step" (N1), and live-measurement-spec.md status carried no feed-landed UPDATE (N2). Both repaired. AGENTS.md scope-position ("ledger recording, awaiting organic traffic") verified accurate against live state.
- **C7 (constitution)** — SUPPORTED. No randomness/wall-clock (seq is a counter; grep clean); replay determinism across PYTHONHASHSEED 0/1/42/12345 on a 156-record ledger; privacy end-to-end traced: message content flows to tracker/service/state-machine only — the feed passes opaque keys, (action, rule_id) tuples, and the settled bool; ruling digests never recorded; logs/ gitignored and never committed (git log --all -- logs/ empty).

## Mutation table

| # | Mutation | At review | After repair |
|---|---|---|---|
| M1 | feed before pronounce loop | KILLED | killed |
| M2 | remove try/except (exception propagates) | KILLED | killed |
| M3 | smuggle text field into ledger record | KILLED | killed |
| M4 | settled hardwired False (service path) | KILLED | killed |
| M5 | feed degenerate messages, fabricated speaker | KILLED | killed |
| M6 | record returned rulings, not pronounced prefix | KILLED | killed |
| M7 | seq resets per instance | KILLED | killed |
| M8 | replay feeds records in reverse | **SURVIVED** | KILLED — `test_replay_preserves_order_beyond_the_window` (150-event ledger; window eviction makes order observable) |
| M9 | remove ledger.touch() from build | **SURVIVED** | KILLED — `build_ledger` extracted gateway-free; `test_build_ledger_creates_the_startup_file` |
| M10 | duplicate feed | KILLED | killed |
| M11 | monitor fed settled=False in record closure | **SURVIVED** | KILLED — `make_recorder` extracted; `test_make_recorder_feeds_monitor_and_ledger_identical_facts` |
| M12 | counterpart hardwired None in feed | KILLED | killed |

Repair probes run by the Steward post-verdict: M8/M9/M11 each KILLED, files restored byte-identical, suite 219 green.

## Findings and repairs

1. **N3 — material.** M8 survivor: replay order fidelity unpinned beyond the measurement window — live traffic will exceed 100 records per channel, where order corruption becomes undetectable-by-old-suite. REPAIRED: 150-event replay-vs-live identity pin (window eviction makes forward/reverse feeds diverge in node sets — probe-verified).
2. **N4 — material (bounded).** M11 survivor: the live monitor's settled facts could be falsified inside the uncovered record closure (the ledger stayed correct — durable record safe, in-memory readout divergent). REPAIRED: `make_recorder(monitor, ledger)` extracted module-level; pin asserts monitor window entry AND ledger line carry identical facts including settled.
3. **N5 — minor.** M9 survivor: startup-touch invocation uncovered; the empty-file-at-boot claim rested on the live artifact + unit pin. REPAIRED: `build_ledger(path)` extracted (construct + touch), pinned; build_client consumes it. Disclosed nuance: append() also touches, so absence self-heals at first traffic — the pin protects the pre-traffic observable.
4. **N1 — minor.** IMPLEMENTATION.md OQ5 stale ("feed next step" after landing). REPAIRED: progression recorded with commits and this verdict referenced; remainders now readout tooling, epoch configuration, interpretation item, settlement persistence.
5. **N2 — minor.** Spec status lacked the feed-landed UPDATE (pairing-spec precedent). REPAIRED.
6. **N6 — info.** 94d60bf's "uncovered remainder is real gateway I/O only" was overgenerous — the record closure and touch invocation were gateway-free logic embedded in glue (exactly where M9/M11 survived). Corrected of record here; the extractions remove the ambiguity going forward.
7. **N7 — info.** Wiring row elides the `=frozenset()` default annotation — parameter names exact; accepted (row budget).
8. **N8 — info → repaired.** Partial pronounce prefix (success-then-failure) now directly pinned (`test_record_captures_a_partial_pronounced_prefix`: first ruling pronounced, appellate skipped, record carries the 1-tuple prefix with settled=True).
9. **N9 — info.** Seq continuation counts file lines: external blank lines make seq skip (monotonic, never duplicated); concurrent writers would duplicate seqs — deployment carries the launcher single-instance guard. Declared, no repair.
10. **N10 — info.** Worktree admin cleanup: OneDrive resisted admin-dir deletion; checkouts removed, worktrees deregistered, residual shells force-deleted — `git worktree list` shows main only.

## Summary

No claim falsified; the step's isolation and privacy architecture held under line-by-line and import-graph review. The three survivors were all of one kind: gateway-free logic hiding in uncovered glue, or persistence semantics beyond the pinned window. The repair shape was uniform — extract to a testable surface, pin, kill-probe. Suite 219 green; the live bot records to logs/measurement.jsonl (empty until organic traffic; the trajectory readout is the next step).
