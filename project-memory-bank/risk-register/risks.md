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

## Standing Risk Categories (to populate as phases land)
- **R-S1** Data exfiltration via prompt injection (relevant from P3).
- **R-S2** Citation/source poisoning (relevant from P4).
- **R-S3** Multi-tenant isolation failure (relevant from P7).
- **R-S4** Eval-set leakage into training data (relevant from P3).
- **R-S5** Disaster recovery — backup integrity (relevant from P8).

These are placeholders; concrete entries are opened in the phase that introduces them.

---

## Review history
| Date | Reviewer | Changes |
|---|---|---|
| 2026-05-30 | Project lead | Initial register; opened R-001, R-002. |
| 2026-05-30 | Project lead | P2 review; opened R-003 (single-host blob store). |
| 2026-05-30 | Project lead | P3 review; R-001 next review deferred to P4; R-002 partially mitigated (llama3.2 benchmarked). |
