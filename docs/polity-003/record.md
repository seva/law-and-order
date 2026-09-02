# Polity-003 — Provenance Record

Recorded 2026-09-02 (session 3), after Critic challenge C1: provenance was self-report with no artifact. This file is the repair; the limitation at its end is recorded plainly.

## Generation protocol

Four separate subagent instances, one per domain (marketplace, debt, workplace, tenancy), each prompted with two opposed mandates and no cross-domain coordination. Each generated two minds × (4 claims + 3 noise lines). The project authored the mandates, the persona positions, and the 9-pair counterpart graph (arena); the conflict wording is the subagents'.

## The rejected first batch

A first generation round was run with an added prompt constraint banning rule-matching vocabulary (refund, breach, threat, appeal, and the v2 stance markers). The batch was rejected **whole** — no lines were cherry-picked from it into `minds.json` — because the ban itself authored the content's relationship to the legislation: it guaranteed zero rule coverage, making graded measurement impossible, which is exactly what polity-003 exists to enable. The second round carried the identical mandates with no vocabulary constraint. The accepted artifact containing rule-matching vocabulary ("refund" ×3 claims, "breach" ×1) is therefore not contamination — under Mechanism 1, only matched rules resolve, so content that cannot match any rule cannot be measured either.

## What this record cannot establish

Subagent transcripts are not persisted by the harness; the generation events exist only in the session that ran them. Provenance here is one level better than self-report (the protocol, the rejection, and its reason are recorded), but it is not cryptographic. If unauthored content must ever be proven rather than reported, the generation harness must persist mandates and outputs at generation time.

## Critic findings on the artifact (2026-09-02)

- v2 stance discrimination fails on unauthored phrasing: vendor's refusal ("I refuse to issue any refund…") misses R2's exact substring and receives R7 `order_refund` — 2 of the 5 resolved pairs resolved under a wrong-stance ruling. Stance-awareness does not survive vocabulary the project did not choose. v3 territory.
- Rule utilization 2/7: only R4/R7 fire. R5's only candidate ("Your threats are pathetic.") carries the `pathetic` marker and is dropped UNVALUED before matching — the authored noise filter swallows the polity's only threat. Mechanism 2 gap.
- Coverage grades marketplace/tenancy vocabulary; debt and workplace resolve 0/4 pairs. The graded delta is honest about this — that is what the measurement is for.
