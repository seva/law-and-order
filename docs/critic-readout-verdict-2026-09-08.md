# Critic Verdict — Measurement-Readout Step

- **Review date:** 2026-09-08
- **Role:** Critic (ROLES.md). Separate instance from the Steward that authored the work; same base model — **weakest separation rung, declared**. All evidence below was reproduced by this Critic; no Steward claim was trusted.
- **Commits under review:** red spec `bf228b5` (tests/test_readout.py only), component `a0f63a9` (src/law_and_order/readout.py + ARCHITECTURE.md row)
- **Claims reviewed:** C1 red-first, C2 contract green + coverage, C3 kernel primitives only, C4 privacy by signature, C5 determinism, C6 records hygiene
- **Mutation battery:** 12 mutants (M1–M8 as specified, M9–M12 Critic-designed)

## Per-claim verdicts

### C1 (red-first) — SUPPORTED

```
$ git show bf228b5 --stat
 tests/test_readout.py | 125 ++++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 125 insertions(+)

$ git show bf228b5:src/law_and_order/readout.py
fatal: path 'src/law_and_order/readout.py' exists on disk, but not in 'bf228b5'
(exit 128)
```

The red commit contains only the spec; the module is absent at that commit. Red-first discipline holds.

### C2 (contract green + coverage) — SUPPORTED

```
$ python -m pytest tests/test_readout.py -q
......... [100%]
9 passed in 0.13s

$ python -m pytest -q --cov=law_and_order.readout --cov-branch --cov-report=term-missing tests/test_readout.py
Name                           Stmts   Miss Branch BrPart  Cover   Missing
src\law_and_order\readout.py      45      0     10      0   100%
9 passed
```

9/9 green; 100% statements AND branches (0 miss, 0 partial out of 45 stmts / 10 branches).

### C3 (kernel primitives, no reimplemented thresholds) — SUPPORTED

Full read of readout.py (72 lines) plus regex scan for numeric literals / comparison operators against friction:

- No `0.25` anywhere in readout.py. The only numeric literals are `READOUT_STRIDE = 10` (legislated sampling constant, equality-pinned by `test_readout_stride_value_is_legislated`, not a kernel threshold) and `0.0` as the peak-seed identity element for `max`.
- No friction formula: friction arrives exclusively via `monitor.friction(channel)` (readout.py:54, 66) and phase via `monitor.phase(channel)` (readout.py:67); `LiveFrictionMonitor` delegates to `Network.friction()` / `topology.phase()` (measurement.py:72–76), where the `< 0.25` threshold lives (topology.py:20–21).
- Edges/conflict_edges come from `monitor.network(channel)` (readout.py:64–65), not from a reimplemented tally.

Corroborated by M6: when the threshold WAS reimplemented inline, the boundary test killed it immediately — the spec actively defends C3.

### C4 (privacy by signature) — SUPPORTED

- `summarize(path)` signature pinned by `test_summarize_signature_is_path_only` (parameters == `["path"]`).
- `ChannelSummary` frozen+slots+closed: `test_summary_type_is_closed_and_frozen` pins the exact ten-field tuple, raises `FrozenInstanceError` on assignment, and asserts `not hasattr(summary, "__dict__")` (slots).
- Field types: `str` (channel identifier), ints, floats, `Phase`, and `tuple[tuple[int, float], ...]` (trajectory). No field can carry message text; speaker/counterpart strings enter the monitor but never surface in the summary. One honest nuance: `channel: str` is an identifier and, like any str, could in principle hold arbitrary bytes — but it is the channel key already public in the ledger record, not message content. The claim as stated ("no field or parameter can carry message text") holds.

### C5 (determinism) — SUPPORTED, with one disclosure

- No clock, no randomness: imports are `json`, `dataclasses`, `pathlib`, `.measurement`, `.protocol` only. No `time`, no `random`, no wall-clock or hash-dependent values.
- Reproduction: built a 30-message, 3-channel ledger via the real `JsonlLedger`, ran `summarize` under `PYTHONHASHSEED=0` and `PYTHONHASHSEED=1` in separate processes — byte-identical output; `summarize(path) == summarize(path)` → `True`. (First attempt produced a vacuous "identical" from twin tracebacks — caught and re-run with `PYTHONPATH=src`; the evidence above is from the valid run.)
- **Disclosure:** determinism of channel order is guaranteed by dict insertion order, but the *specific choice* "first appearance" is not pinned by any test — see M7 (SURVIVED). First-appearance and sorted order are both deterministic; the tests cannot tell them apart.

### C6 (records) — SUPPORTED

```
$ git show a0f63a9 --stat
 ARCHITECTURE.md              |  3 +-
 src/law_and_order/readout.py | 72 +++++++++++++++++++++++
```

Row and module land in the same commit. Row length measured: **551 chars** (≤ 600). `python -m pytest tests/test_constitution_hygiene.py -q` → 3 passed.

## Mutation battery

Method: each mutant applied to `src/law_and_order/readout.py` in the working tree, `python -m pytest tests/test_readout.py -q` run, result recorded, restored via `git checkout -- src/law_and_order/readout.py`, `git status --short` verified clean before the next mutant. Tree verified clean after every restore and at the end.

| # | Mutant | Intent | Result | Killed by |
|---|--------|--------|--------|-----------|
| M1 | `% READOUT_STRIDE == 0` → `> 0` | trajectory sampling off-stride | KILLED | test_trajectory_samples_at_stride_and_peak_catches_spikes_between_samples |
| M2 | trajectory label `messages - 1` → `messages` | label off-by-one | KILLED | test_trajectory_samples_at_stride_and_peak_catches_spikes_between_samples |
| M3 | running `max(peaks[c], friction)` → friction at stride samples only (peak = last sample) | peak misses between-sample spikes | KILLED | test_trajectory_samples_at_stride_and_peak_catches_spikes_between_samples (peak 0.3 ≠ 0.5) |
| M4 | `if rulings: ruled += 1` → `+= len(rulings)` | ruled counts tuples not messages | KILLED | test_per_channel_aggregation_is_exact (ruled 3 ≠ 2 on the two-ruling message) |
| M5 | drop `if record["settled"]` increment | settled pinned | KILLED | test_per_channel_aggregation_is_exact (settled 0 ≠ 1) |
| M6 | `monitor.phase(channel)` → inline `<= 0.25` | threshold reimplementation (C3 probe) | KILLED | test_phase_boundary_follows_the_kernel_threshold (ORDERED at exactly 0.25 ≠ DISORDERED) |
| M7 | `tallies.items()` → `sorted(tallies.items())` | first-appearance vs sorted channel order | **SURVIVED** | — |
| M8 | remove missing-file guard | missing ledger must not raise | KILLED | test_missing_file_summarizes_to_empty (FileNotFoundError) |
| M9 | `LiveFrictionMonitor()` → `LiveFrictionMonitor(window=10**9)` | full-history aggregation instead of monitor window | **SURVIVED** | — |
| M10 | `if record["settled"]` → `if record["settled"] or rulings` | settled/ruled semantic conflation | KILLED | test_per_channel_aggregation_is_exact AND test_trajectory_samples... (settled 2≠1, 4≠0) |
| M11 | compute friction BEFORE `monitor.record_message` | sampling-order off-by-one (pre-record vs post-record friction) | KILLED | test_trajectory_samples_at_stride_and_peak_catches_spikes_between_samples |
| M12 | stride counter global across channels instead of per-channel `tally["messages"]` | per-channel trajectory semantics on interleaved multi-channel ledgers | **SURVIVED** | — |

**Kill rate: 9/12.**

## Survivor analysis

- **M7 (sorted vs first-appearance channel order) — immaterial to correctness, material to the declared claim.** Both orders are deterministic (C5 unaffected). But the contract narrative says "channel order = first appearance" and no test pins it: every multi-channel fixture uses `c1`, `c2` where the two orders coincide. **Pin that would kill it:** a fixture with channels appearing as `("c2", ...), ("c1", ...)` asserting output order `["c2", "c1"]`. One-line test; recommend adding.
- **M9 (window vs full history) — structural test-reach limit, as the battery brief anticipated.** All fixtures are ≤ 25 messages per channel; `MEASUREMENT_WINDOW = 100` never engages. A window-agnostic mutant is invisible. **Pin that would kill it:** a fixture with > 100 messages in one channel where an early conflict edge falls out of the window, asserting windowed friction/edges differ from full-history values (e.g., 101+ messages where message 1 creates the only conflict edge; windowed friction must exclude it). Note this is a readout-vs-spec gap, not a spec-vs-intent gap: the *windowed* semantics is arguably the intended contract for a live readout, so the pin belongs in tests/test_readout.py.
- **M12 (global vs per-channel stride) — same class as M9: reach limit.** The trajectory fixture is single-channel (`c1` × 25); the multi-channel fixture never asserts trajectories. A global counter produces identical output on every fixture. **Pin that would kill it:** a two-channel interleaved fixture with ≥ 10 messages per channel asserting each channel's trajectory labels are `(9, ...)` and `(19, ...)` per-channel — a global counter would sample at the wrong per-channel moments.

None of the survivors is a live-bug indicator in the current implementation (the committed code is correct on all three axes by inspection); each is an unpinned *declared property*. Under the project's standing bar (every declared property gets a pin), M7 and M9 correspond directly to claims in the spec's own commit message ("first appearance" ordering is in the contract; "monitor-windowed topology" is in the ARCHITECTURE row) and should get pins. M12's per-channel-ness is implied by "trajectory sampled every READOUT_STRIDE" per channel and rides along with the M9/M7 fixture work.

## What the battery CANNOT distinguish (honest limits)

1. **Windowed vs full-history aggregation** (M9): no fixture exceeds 25 messages per channel; window is 100. Any mutation confined to window semantics survives. The battery proves the *code path* is exercised, not that the *window bound* is.
2. **First-appearance vs any coincident ordering** (M7): fixtures use lexicographically increasing channel names in appearance order. Only orders that coincide are tested.
3. **Per-channel vs global stride counting** (M12): single-channel trajectory fixture cannot separate them.
4. **Malformed-input behavior**: the spec pins missing-file and empty-file, but not malformed JSON lines (a `json.loads` raise) or missing keys (`record["channel"]` KeyError). The contract says "never raising" only for missing/empty ledgers; whether malformed lines should raise or skip is unlegislated and untested — the battery did not probe it because no claim covers it. Flagging as an open contract question, not a defect.
5. **Coverage is per-file**: 100% of readout.py, but the battery cannot certify that `LiveFrictionMonitor` integration is correct beyond what test_measurement.py already pins — cross-module seam correctness rests on the monitor's own contract tests, which this review did not re-litigate.

## Overall verdict

**VERDICT: ACCEPT WITH REPAIRS.** All six claims SUPPORTED on independently reproduced evidence (C5 with the M7 disclosure). Mutation battery: 9/12 killed; 3 survivors (M7, M9, M12), none indicating a live bug, all indicating unpinned declared properties. Repairs required by the standing bar (every declared property gets a pin): (1) multi-channel ordering fixture killing M7; (2) >window fixture killing M9; (3) interleaved multi-channel trajectory fixture killing M12. Working tree left clean (verified `git status --short` after every restore and at end; only this verdict file added). Full suite sanity: 229 passed, 1 third-party DeprecationWarning (disclosed, SDK-internal).

---

## Steward repair record (post-verdict, same session)

All three survivors killed by new pins in tests/test_readout.py (13 tests, module still 100% statements+branches):
- M7 -> test_channel_order_is_first_appearance_not_sorted (zebra-before-alpha fixture; sorted() mutant dies)
- M9 -> test_topology_is_windowed_not_full_history (106-message fixture; conflict edge evicted at the 100-window; pins messages/ruled/settled as full-history tallies vs edges/friction/phase as windowed monitor state; window=10**9 mutant dies on edges 53 != 50, friction 1/53 != 0.0)
- M12 -> test_trajectory_stride_counts_per_channel (two interleaved channels, 20 messages each; global-counter mutant dies on labels)
- Malformed lines legislated fail-loud: json.JSONDecodeError propagates (test_malformed_line_fails_loudly) - silent skipping would hide ledger corruption; missing/empty remain empty-summary.
Kill-probes re-run by the Steward: each mutant applied, its pin observed RED, readout.py restored byte-identical (git status clean) before the next. Full suite 233 green.
