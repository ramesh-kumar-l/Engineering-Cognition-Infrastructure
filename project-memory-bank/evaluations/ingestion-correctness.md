# ingestion-correctness — Evaluation Contract

## Metric
Three properties measured per ingestion:

1. **Round-trip integrity.** For a sample of inputs, the persisted `Document.body` (or `Note.body`) matches the parser's output of the original bytes byte-for-byte after Unicode normalization.
2. **Idempotency rate.** For N random inputs ingested twice each, exactly 2N audit events are produced, of which N are `*.create` and N are `*.dedup`. No duplicate `documents`/`notes` rows exist.
3. **Provenance coverage.** 100% of persisted records carry `source`, `ingested_at`, `ingested_by`. Records derived from a raw blob carry a resolvable `raw_blob_id`.

## Accepted thresholds (Phase 2 exit)
- Round-trip integrity: **100%** on the held-out P2 corpus (markdown, plaintext, small PDFs).
- Idempotency: **100%** match of the audit-event expectation above.
- Provenance coverage: **100%**.

Changing any threshold requires a follow-up ADR.

## Held-out set
- Location: `project-memory-bank/evaluations/data/ingestion/` (added when the corpus is curated).
- Seed: a small in-repo synthetic set (5 markdown, 5 plaintext, 2 PDFs) for CI; a larger set lives outside the repo and is pulled by `make eval-fetch` in P3.
- Leakage: held-out files are flagged with a marker key in their frontmatter; ingestion service refuses to write them outside the test DB (enforced by a P3 ADR).

## Runner
- Unit + service tests cover (1) and (2) on every commit (`pytest -m integration`).
- A dedicated CI job (added in P3) runs the full held-out corpus and writes a Run row below.

## Runs
| Date | Commit | Round-trip | Idempotency | Provenance | Notes |
|---|---|---|---|---|---|
| *first run lands in P2 CI* |
