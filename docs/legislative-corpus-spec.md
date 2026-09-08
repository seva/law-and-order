# Legislative Corpus Spec — marker-family generalization from public dispute archives

Status: specification + provenance protocol. **Committed before any corpus contact** (polity-004 discipline: protocol precedes generation; here: protocol precedes collection). Owner direction 2026-09-08, verbatim: "Let's record B & C as decision debts. And proceed with A." Decide record + RAROC forecast: the direction's GitHub issue.

## Purpose

The legislation's disclosed binding gap is coverage of real unauthored phrasing: polity-004's refund-triggering texts are stance-neutral under pre-generalization markers (0.000 before, 0.172 after family generalization — `docs/polity-004/record.md`), and the generalized families were derived from the project's own diagnostic vocabulary with 7 residuals disclosed not fitted (Mechanism 2, `docs/critic-mechanism2-verdict-2026-09-05.md`). Public dispute archives carry the phrasing the law must see but has never been exposed to. This direction grows the marker families and rules against that evidence — the Mechanism-2 pattern repeated with independent, non-project-authored source material.

This is legislative work, not measurement: no polity number is a target. Standing validation gates (below) keep every prior measurement honest through the change.

## Corpus sources (home of the 2026-09-08 online research)

Selected from a Grok web-search survey of where user-to-user consumer conflict happens online (run 2026-09-08; tool-record sources; key claims): Reddit carries the highest public, searchable dispute volume — r/Scams (~1.39M members, ~740 new posts/day at survey time), r/legaladvice (~2.2M), r/Upwork, r/Fiverr, r/slavelabour (non-payment, scope creep, ghosting), r/AmazonSeller (refunds-as-weapon). Discord trading/commission servers carry higher intensity per transaction but are private (mode C decision debt). Facebook/Telegram groups: high volume, near-zero structure. Platform dispute centers: closed.

Corpus selection for A: **public Reddit dispute threads** — r/Scams, r/Upwork, r/Fiverr, r/slavelabour. Self-text posts only (the dispute narrative); title + body. [ASSUMPTION tagged at selection time: subreddit activity levels as reported by the survey; verified at fetch time by the manifest counts, not trusted.]

## Interface (Phase Gate)

Reddit was surveyed in Phase 2 (`docs/platform-survey.md`: asyncpraw auth model, moderation surfaces). Collection interface declared: **public JSON endpoints, unauthenticated, read-only, rate-limited by the collector (≤1 req/s, per-request backoff)**. No implementation code is written against undiscovered interfaces; if the public endpoints prove unusable (blocked/rate-wall), the fallback (asyncpraw client-credentials app) is an Owner-provisioned external dependency and gets surfaced per CYCLE.md Autonomy — not silently adopted.

## Provenance and privacy protocol (binding before any fetch)

Terminal bound row 3 (`docs/scope.md`, positional): "Secrets never surfaced; message content never persisted to repo, ledger, or logs (privacy by signature)" — protected margin: participant trust and platform standing, "live humans, not personas."

Declared interpretation for this direction (a rule, not an exemption):

1. **Corpus text is transient input.** Post titles/bodies are fetched into process memory, consumed by the extraction pipeline, and never written to the repo, ledger, logs, artifacts, or test fixtures. No full sentence, paragraph, or post ever lands in a committed file.
2. **What persists:** (a) the **manifest** — subreddit, fetch date, post public IDs, permalinks, post scores/counts, train-vs-holdout assignment; pointers to public content, not content; (b) **derived legislative artifacts** — marker families as short generalized fragments (precedent: the 48 standing noise-filter markers and the stance-marker families are already fragmentary vocabulary derived from an unauthored corpus, Mechanism 2; fragment ceiling declared: ≤5 words per marker, generalized to families — inflection/contraction variants — never verbatim sentences); (c) **coverage statistics** — counts and ratios, never examples-in-context; a coverage claim may cite a post ID + the matched marker, never the surrounding text.
3. **Reproducibility by pointer:** the Critic re-fetches by manifest IDs to verify any coverage claim. Reproducibility does not require persistence; persistence of content is what row 3 forbids.
4. **Collection hygiene:** read-only, unauthenticated, rate-limited; no private/quarantined communities; posts older than 24h at fetch time (avoid live-moderation interference); editing/flairing/engagement with source communities is forbidden (neutral arbitration — the project never participates in the conflicts it studies).
5. **Authorship boundary:** corpus content is authored by third parties and stays third-party. The project derives *vocabulary coverage* from it. Nothing from the corpus enters any polity, any measurement fixture, or any conflict-generating surface — the corpus feeds the law, never the arena (prime directive: conflict content never authored, edited, or selected; a corpus fragment planted into a dispute would be selection).

## Anti-overfit structure (declared before collection)

- **Deterministic split by post ID hash** (SHA-256 of the public ID, even/odd or high/low half — fixed rule in the red contract, no discretionary assignment): families are derived from the **train** split only; coverage is measured and pinned on the **holdout** split; holdout residuals are disclosed, never fitted (Mechanism-2 discipline: the 7 residuals stand).
- **Fit-to-wording guardrail** (`docs/mechanism3-reaction-spec.md` generalization discipline carries over): markers must be linguistic families with a paradigm claim, not tailored strings; a family whose members fire only on corpus text and on no constructed novel-English battery is evidence of tailoring. Separate-instance Critic rules on the generalization before adoption, as 2026-09-05.
- **Standing validation gates (every legislative change, unchanged from Phase 8):** nonsense-content and empty-ruleset substitutions stay resolved-zero on every polity; every prior polity's measured history stays byte-identical (the generalization must widen coverage without disturbing settled behavior — if a family changes a polity measurement, that is pin drift: loud re-forge, Critic differential, disclosed consequence, never silent).
- **Booking untouched:** 0.172 is booked as measured (issue #9, 2026-09-08). Legislative evolution produces new measurements on new surfaces; it does not retroactively amend the booking.

## Decomposition (atomic steps; each has its verification statement)

- **A1 — this spec + provenance protocol committed before any fetch.** V=4, P=0.9, C=1. Verification: this file's commit predates any manifest/corpus artifact in the repo (`git log` order); repo contains zero corpus content at commit time.
- **A2 — collector + manifest (no content persistence).** V=4, P=0.7 (public-endpoint usability unverified), C=2. Verification: committed manifest for ≥2 subreddits with ≥100 posts each — IDs, permalinks, split assignment, counts; a repo-wide scan test asserts no fetched title/body text appears in any committed file (the pipeline's persistence signature makes content-capture unrepresentable, the ledger precedent); rate-limit honored (collector log: request timestamps ≥1s apart, log itself content-free).
- **A3 — red contract for the extraction component.** V=3, P=0.8, C=2. Verification: contract red on the committed spec's semantics (family derivation from transient text; deterministic split reproducibility; marker ceiling ≤5 words; coverage-stat output shape with no content field); suite green otherwise.
- **A4 — extraction run + legislative proposal + Critic.** V=4, P=0.6, C=3. Verification: proposed family expansion passes all standing gates (polities byte-identical; nonsense/empty zero; holdout coverage pinned with residuals disclosed); separate-instance Critic verdict committed before adoption; fit-to-wording question ruled by the Critic, surfaced to Owner if contested.

## Open questions

1. Marker-ceiling enforcement: the ≤5-word ceiling is declared here; its executing check (extraction-component contract in A3) does not exist yet — UNENFORCED until A3 lands (Lesson-Mechanism rule, declared per METHODOLOGY.md Record Economics).
2. Non-English text in public disputes: excluded from A (the families legislate English; the noise-filter precedent is English-scoped). Widening is a future legislative question.
3. Whether holdout coverage numbers enter any measurement claim or stay diagnostic: declared at A4 — diagnostic only, unless an Owner-booked measurement ever consumes live-corpus-derived law (it does not today).
