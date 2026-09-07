# Live Pairing Policy — Specification

Status: specification + component contract. Committed before the wiring integration it gates. The wiring step (live behavior change) has its own verification and lands separately.

---

## Why this exists

Open Question 5 was resolved 2026-09-06 by extracting settlement semantics into `adjudication.SettlementService` — a stateful component above the stateless adapter contract. The declared remainder, and the binding question for any live measurement: the live Discord envelope drops author identity at the ingest seam by design, while the service's institutional memory is keyed by (speaker, counterpart) pairs. This spec decides how live messages map onto dispute pairs. Until it exists, the live surface runs first-instance match semantics while the measurement apparatus runs settlement semantics — the split that blocks live measurement of what the sim measures.

## Design facts this spec builds on

- The service API: `note(speaker, counterpart, text)` records dispute state without adjudicating; `observe(speaker, counterpart, text)` adjudicates through due process when ripe and returns the rulings to pronounce; dispute keys are `f"{source}:{a|b}"` (sorted, pipe-joined) and enter the signal digest.
- The kernel's identity-freedom guarantee is about MERITS: rulings are a function of (text, ruleset, boundaries); no identity enters the action, rule, or appellate outcome. Persona keys in the sim (names) already key state without entering merits — live speaker keys are the same role.
- Wiring today: every message → `StateMachine.step` → pronounce → channel-scoped enforcement; the bot skips its own messages (loop-breaker, untouched by this spec).

## Pairing semantics

A live message maps to a `PairEvent(channel, speaker, referenced_speaker, text)` — platform-neutral descriptor; wiring extracts `referenced_speaker` from the Discord reply reference (author of the referenced message, when resolvable) and uses opaque platform author keys as speaker tokens.

Counterpart resolution, in order:

1. **Reference-first.** An explicit reply reference resolves the counterpart: the author being replied to. This is the platform's own conversational signal — strongest available, and it survives multi-party channels where adjacency is ambiguous. References bypass the recency window: a reply to a participant absent from the tracker's bounded memory still resolves (pinned by test; added at Critic repair N7 — the bypass had been decided by code alone).
2. **Self-reference is ignored.** A message referencing its own author (edits, self-replies) falls through to adjacency.
3. **Adjacency fallback.** No usable reference → the counterpart is the most recent other speaker in the same channel (conversation adjacency within a bounded recency window).
4. **Fresh state → None.** No reference and no other speaker recorded in the channel → no counterpart: no dispute exists yet.

Recency memory is **bounded** (window = 8 most recent speaker entries per channel, declared constant): a long-lived bot must not grow memory without limit. Consequence, declared: after a flood of one-speaker messages, adjacency yields None until another speaker enters the window — unpaired messages fall to the continuity rule below, which is first-instance pronunciation, i.e. today's behavior. Bounded memory degrades to the status quo, never to garbage.

Channels are isolated: recency state never crosses channels.

## Continuity rule (wiring step contract, declared here)

- Paired messages (`counterpart ≠ None`): the service governs — `observe` returns the rulings to pronounce (first-instance and, on appeal, appellate); when the service is silent (unripe, unmatched, inert), wiring falls back to first-instance `StateMachine.step` so pronunciation continuity is preserved. No message pronounces twice.
- Unpaired messages: first-instance `StateMachine.step` — exactly today's live semantics — and the event feeds recency state.
- Pronouncement-first enforcement ordering and channel-scoped coercion are untouched (Owner ruling 2026-09-05).

## Res-judicata scope on live channels — declared divergence from the sim

In the sim, a settled pair never re-opens (finite populations, finite horizons). On a live channel, permanent silence after one settlement is wrong: conflicts recur between the same people. Declared policy: **finality attaches to the dispute, not the pair.** A settlement is res judicata — the same ruling is never re-litigated — but the pair's in-dispute memory clears at settlement, so a NEW dispute between the same parties can arise and receive due process afresh. Implementation requirement for the wiring step: `SettlementService` gains an explicit clear path exercised at settlement (contract change, ARCHITECTURE same-commit); until then the service's post-settlement short-circuit is correct for the sim and inert for live (wiring does not integrate yet).

## Identity-freedom compatibility — argued, disclosed, and flagged

- **Merits untouched:** speaker keys route state; they never enter `Dispute` content, rule matching, reactions, or appellate merits. Rulings remain a function of (text, ruleset, boundaries) — the kernel guarantee holds by construction. Content-blindness of the resolution is contract-pinned (`test_resolution_is_content_blind`: structurally identical sequences differing only in text resolve identically — a text-dependent mutation of `resolve` fails the suite, verified by mutation probe at Critic repair N2; the original "pins content-blind" claim was false as first written).
- **Digest provenance changes, disclosed:** wiring will construct the service with a live source prefix, so signal digests become `sha256("<prefix>:<speaker|counterpart>:<text>")` — the digest's provenance field derives from pseudonymous platform author keys (hashed nowhere, joined plainly). Sim digests already carry persona names; live digests would carry platform pseudonyms. This widens what "author identity is dropped at the seam" means: identity is dropped from MERITS, retained (pseudonymously) in digest PROVENANCE. **Flagged for the Owner as an interpretation item, not self-adjudicated** — same discipline as the reaction generalization's fit question. If the Owner rules provenance must stay identity-free, the mitigation is a wiring-side alias map (per-channel rotating pseudonyms), and pairing keys become aliases; the component contract below is alias-agnostic and unchanged either way.

## What this spec does not decide

- Discord-specific extraction (reference resolution edge cases: cross-channel references, deleted authors, webhook messages) — wiring step, against recorded fixtures. Degenerate tokens (empty-string or missing speaker/channel/reference values) are wiring-extraction responsibility as well: the component is garbage-in-garbage-out by contract — an empty counterpart token would produce a degenerate dispute key (`<prefix>:|a`), which is why the guard lives at the extraction site, pinned there (Critic repair N6, disclosed not silently delegated).
- Multi-party disputes (3+ speakers, one dispute): out of scope; the institution is binary, like the kernel's `Dispute(claim, counterclaim)`.
- The recency window's exact size beyond "bounded and declared": 8 is the initial value; change is legislative, pinned by `test_recency_window_value_is_legislated` (added at Critic repair N1 — the original flood test was parametric in the constant and could not detect an unbounded deque or a window resize; both mutations now fail the suite, verified by mutation probe).

## Verification (red contract, `tests/test_pairing.py`)

1. Fresh channel resolves None; adjacency pairs consecutive speakers.
2. Reference takes priority over recency; self-reference is ignored (falls to adjacency).
3. Recency excludes the speaker; channels are isolated.
4. Recency window is bounded: a same-speaker flood yields None, never a stale or garbage counterpart; a new speaker restores adjacency.
5. Replay determinism: independent trackers, identical event sequences, identical resolutions.
6. Dispute-key convention ties to the settlement service: `dispute_key` output reproduces the exact signal-digest source string of a `SettlementService` ruling for the same pair and text.
7. Event descriptor is immutable (frozen/slotted).
8. (Critic repairs N1/N2/N3/N7, 2026-09-06) The window value is legislated (`RECENCY_WINDOW == 8`); EVICTED speakers do not resolve (distinct-prior-speaker eviction, not same-speaker flood — kills unbounded-deque and window-resize mutations); resolution is content-blind (kills text-dependent mutations); reference resolutions feed recency; references bypass the window (unseen referenced speaker resolves). Mutation-sensitivity of 8 verified empirically: the Critic's M1/M2/M4 mutations flip the strengthened tests red, revert restores green.

The suite, coverage (module 100%), and the ARCHITECTURE component row in the same commit as the component complete the step. The wiring step's verification is separate and includes live-gateway evidence.
