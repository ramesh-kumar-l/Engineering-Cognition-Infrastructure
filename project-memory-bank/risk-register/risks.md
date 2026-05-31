# Risk Register

Living list of risks, mitigations, and owners. Reviewed at every phase exit; risks are not just appended, they are revisited.

Risk states: **Open** · **Mitigated** · **Accepted** · **Closed**.

---

## R-001 — Cloud LLM availability and pricing volatility
- **State:** Open (partially mitigated)
- **Opened:** 2026-05-30 (P1)
- **Owner:** Project lead
- **Description:** ECI depends on LLM behavior for compression, summarization, and (later) generation. Cloud providers can change pricing, rate limits, model behavior, or availability without notice.
- **Impact:** Service degradation, cost spikes, behavioral drift between releases.
- **Mitigation in place:** AP-3 (offline-first) — Ollama is the default runtime; cloud providers are opt-in. LLM runtime abstraction (P3) ensures provider switching is a config change.
- **Residual risk:** Offline-Ollama performance may not match cloud models for some tasks. Tracked under R-002.
- **Next review:** End of P4.

---

## R-002 — Offline Ollama hardware requirements
- **State:** Open
- **Opened:** 2026-05-30 (P1)
- **Owner:** Project lead
- **Description:** Running a useful local LLM (compression / mental-model extraction) requires meaningful GPU/CPU resources that not all target users have.
- **Impact:** Some users cannot use the offline path; AP-3 weakens for them.
- **Mitigation in place:** None yet.
- **Planned mitigation:** P3 research spike — benchmark several model sizes for the P3 evaluation set; document minimum-viable hardware; design a "small offline + cloud fallback" mode that does not violate AP-3 (cloud is enhancement, not requirement).
- **Mitigation in place:** P3 research noted. Benchmarked against `llama3.2` (3B). Small models are sufficient for summarization; mental-model extraction benefits from larger models (7B+).
- **Next review:** Start of P4.

---

## R-003 — Local-filesystem blob store is single-host
- **State:** Open (acceptable for P2 local/dev; mitigation deferred)
- **Opened:** 2026-05-30 (P2)
- **Owner:** Project lead
- **Description:** `LocalBlobStore` writes blobs to a single filesystem root. Horizontal API scaling will read/write to disjoint disks, breaking content addressing.
- **Impact:** Cannot scale horizontally beyond one host until an S3-compatible adapter ships.
- **Mitigation in place:** `BlobStore` Protocol isolates the seam; ADR-004 commits to a P8 S3 adapter without touching ingest services.
- **Planned mitigation:** P8 — `S3BlobStore` adapter with MinIO for local parity. New ADR at adapter time.
- **Next review:** Start of P8.

---

## R-004 — Retrieval corpus empty at evaluation time
- **State:** Mitigated
- **Opened:** 2026-05-30 (P4)
- **Owner:** Project lead
- **Description:** The embedding step must be run before search works. A cold deployment has an empty vector index, causing all searches to return 0 results.
- **Mitigation in place:** `has_citations=False` in `RetrievalResult` surfaces this clearly. API returns 200 with an empty `results` list rather than 500. Documented in `active-context.md` open decisions.

---

## R-005 — Ollama model weights not in DR backup
- **State:** Accepted
- **Opened:** 2026-05-31 (P8)
- **Owner:** Project lead
- **Description:** Ollama model weights (e.g., `nomic-embed-text`, `llama3.2`) are not included in the Postgres backup. A full restore requires re-pulling models from the Ollama registry.
- **Impact:** DR restore time is extended by model pull time (5–30 min depending on model size and bandwidth).
- **Accepted because:** Models are versioned and reproducible from the registry. The RPO for weights is effectively 0 (they don't change). The RTO extension is acceptable.
- **Next review:** If Ollama registry becomes unavailable or models are deprecated.

---

## R-006 — Single-tenant blob migration to S3 not automated
- **State:** Open
- **Opened:** 2026-05-31 (P8)
- **Owner:** Project lead
- **Description:** Existing local-filesystem blobs are not automatically migrated when switching `ECI_BLOB_BACKEND=s3`. A migration script is needed.
- **Impact:** Data in `LocalBlobStore` is not accessible via `S3BlobStore` without manual migration.
- **Mitigation in place:** `S3BlobStore` and `LocalBlobStore` key layouts are identical, so a simple `aws s3 sync` suffices.
- **Planned mitigation:** Add `scripts/migrate_blobs_to_s3.py` in a follow-up PR.

---

## R-003 — Local-filesystem blob store is single-host (UPDATED)
- **State:** Mitigated (P8)
- **Opened:** 2026-05-30 (P2)
- **Owner:** Project lead
- **Description:** `LocalBlobStore` writes to a single filesystem root; cannot scale horizontally.
- **Mitigation:** `S3BlobStore` adapter shipped in P8. Switch by setting `ECI_BLOB_BACKEND=s3`. `BlobStore` Protocol unchanged; ingest services untouched.
- **Residual risk:** See R-006 (migration script pending).

---

## Standing Risk Categories (resolved)
- **R-S1** Data exfiltration via prompt injection — mitigated by prompt isolation in `OllamaProvider`; no user-supplied strings in system prompts.
- **R-S2** Citation/source poisoning — mitigated by `UNIQUE(content_hash)` + per-tenant retrieval filter.
- **R-S3** Multi-tenant isolation failure — mitigated by 5 negative integration tests (P7) + service-level `tenant_id` filter.
- **R-S4** Eval-set leakage into training data — accepted; eval corpus is internal only.
- **R-S5** Disaster recovery — backup integrity — see R-005; DR runbook documented and drill scheduled.

---

## Review history
| Date | Reviewer | Changes |
|---|---|---|
| 2026-05-30 | Project lead | Initial register; opened R-001, R-002. |
| 2026-05-30 | Project lead | P2 review; opened R-003 (single-host blob store). |
| 2026-05-30 | Project lead | P3 review; R-001 next review deferred to P4; R-002 partially mitigated (llama3.2 benchmarked). |
| 2026-05-31 | Project lead | P8 review; R-003 mitigated (S3 adapter); opened R-004, R-005, R-006; standing categories resolved. |
