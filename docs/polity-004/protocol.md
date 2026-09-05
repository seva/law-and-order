# Polity-004 — Provenance Protocol

Status: protocol. Committed **before** generation. The commit ordering (mandates precede outputs) is part of the evidence.

---

## Why this exists

The Critic falsified booking polity-003 because its authorship condition — "conflict produced by minds the project did not author" — was reported, not evidenced: subagent outputs were not persisted, so there was no way to prove the project did not author or edit the wording. This protocol makes the authorship boundary explicit and mechanically verifiable for polity-004 and every polity after it.

## Authorship boundary (declared, not hidden)

- **Authored by the project (arena):** this protocol; the generation mandates; the persona positions; the counterpart graph; the sim engine, rulesets, and measurement apparatus.
- **Not authored by the project (conflict):** the wording of every claim and noise line, returned by independent subagent instances in response to the mandates, and used **verbatim**.

The mandates are authored and disclosed. Whether authored mandates make the conflict authored is an interpretive question reserved to the Owner — this protocol does not resolve it; it removes every *other* defect from the authorship claim.

## Capture requirements

Each generation instance persists, in-repo:

- `mandates/<domain>.md` — the exact prompt sent, committed before generation.
- `provenance/<domain>.output.json` — the raw response, byte-for-byte, no edits.
- `record.md` — instance id, generation timestamp, and the sha256 of each output file.

## Invariants

1. **Verbatim.** Every claim and noise line in `minds.json` appears, character-for-character, in the corresponding `provenance/<domain>.output.json`. Enforced by `tests/sim/test_polity004_provenance.py`. If a line cannot be traced, the polity is invalid.
2. **No content selection.** A generation pass is accepted as produced. The only permitted re-draw is a malformed/non-JSON response, and that is a process act logged in `record.md`. Rejecting or editing content for any content reason is authorship and is prohibited.
3. **Neutral mandate.** Mandates prescribe the persona's situation, never the vocabulary, the presence or absence of rule-matching words, or the outcome.

## What this protocol proves, and what it cannot

- **Proves:** integrity — the wording was not authored, edited, or selected by the project after generation; separation — each domain's wording came from a distinct instance; authorship boundary — exactly what is authored vs unauthored, disclosed.
- **Cannot prove:** that AI-generated wording is "unauthored" in the strong sense the prime directive may require, nor that an authored mandate does not make the conflict authored. Those are the residual, and they belong to the Owner.

## Counterpart graph

Authored arena. Eight minds, four domains, nine symmetric pairs (identical structure to polity-003, disclosed as authored). The graph is law's arena, not the conflict.
