# Active Context

> **Read this first.** This file is the current "save state" of the project. It is updated at the end of every major feature and at every phase transition.

## Current Phase
**Phase 8 — Production Hardening** ✅ **COMPLETE — All 8 phases done. System is GA-ready.**

All phases 1–8 are complete. See [implementation-status.md](implementation-status.md) for the full exit-criteria checklist.

## Current Sprint Goal
Phase 8 delivered on 2026-05-31. No active sprint.

**Post-GA follow-up items (not blocking GA):**
- `scripts/migrate_blobs_to_s3.py` — blob migration helper (R-006).
- First DR drill — scheduled within 2 weeks of GA deployment.
- SLO measurement baseline — requires 1 week of production traffic.
- Ollama CI environment — unblocks corpus benchmarks in `scripts/eval_gate.py`.

## Recently Completed
- **2026-06-03** Frontend Phase B — Ingest + Compress ✅ (`apps/web/`)
  - Ingest screen: document upload (`POST /documents`) + note capture (`POST /notes`) with
    dedup/provenance result card and typed `?documentId=` handoff to Compress.
  - Compress screen: run pipeline (`POST /compress/documents/{id}`), summaries + mental-model
    views, embed-for-search panel (`POST /retrieval/embed/...`). Fail-closed on LLM-down.
  - 9/9 Vitest pass; `npm run build` clean. Backend run with `ECI_IDENTITY_AUTH_DISABLED=true`;
    no backend code changed. See [frontend/frontend-design.md](frontend/frontend-design.md).
  - Frontend Phase A (scaffold + Search slice) completed prior. Next: Phase C — Execution.
  - Env note: Ollama not installed here → Compress/Embed/Search-embedding return 5xx by design.

- **2026-05-31** Phase 8 — Production Hardening ✅
  - `packages/ingest/s3_blob_store.py` — S3BlobStore adapter; `ECI_BLOB_BACKEND=s3`; R-003 mitigated.
  - `.github/workflows/security.yml` — pip-audit + bandit + trufflehog + trivy; weekly + per-PR.
  - `.github/workflows/release.yml` — eval gate + dep scan + Docker build + GHCR push + staging deploy.
  - `scripts/eval_gate.py` — verifies all 4 eval contract files; blocks release on regression.
  - `project-memory-bank/evaluations/reflection-quality.md` — P6 thresholds defined.
  - `project-memory-bank/slos/slos.md` — 5 SLOs; error budget policy.
  - `project-memory-bank/runbooks/disaster-recovery.md` — backup/restore/drill protocol.
  - `infra/docker/docker-compose.prod.yml` — full prod stack (API + DB + Prometheus + Grafana + Alertmanager).
  - `infra/prometheus/` — prometheus.yml + 6 alert rules (availability, latency p95/p99, auth deny, service down, ingest error).
  - `infra/grafana/` — 8-panel SLO dashboard auto-provisioned.
  - `infra/alertmanager/alertmanager.yml` — severity routing + inhibit rules.
  - `infra/docker/api.Dockerfile` — all 9 packages; HEALTHCHECK; non-root hardened.
  - ADR-010 ratified; risk register updated.

- **2026-05-31** Phase 7 — Enterprise ✅
  - `packages/identity/` — TenantService, UserService, TokenService, OIDCService; RBAC roles + guards.
  - `tenants`, `users` tables; `tenant_id` nullable FK column on all 9 data tables; migration `0006_enterprise`.
  - `POST/GET /tenants`, `POST/GET/PATCH /users`, `GET /auth/login`, `POST /auth/callback`.
  - JWT-based auth: local HS256 JWT issued after OIDC code exchange; dev bypass via env flag (AP-3).
  - `require_write` / `require_admin` FastAPI dependencies; `eci_auth_denied_total` Prometheus counter.
  - Per-source retrieval filtering: `tenant_id` threaded into FTS + vector SQL queries.
  - Tenant isolation verified by 5 negative integration tests; RBAC unit tests (10 tests); service tests (14 tests).
  - ADR-009 ratified; system-patterns.md updated.

- **2026-05-31** Phase 6 — Reflection Engine ✅
  - `packages/reflection/` — RetrospectiveService, LessonService, PatternExtractor; evidence_helpers; DTOs + errors.
  - `retrospectives`, `lessons`, `lesson_evidence` tables; migration `0005_reflection`.
  - `POST/GET /retrospectives`, `POST/GET /lessons`, `POST /lessons/{id}/supersede`.
  - Synchronous retrospective run: collect completed goals/tasks → LLM pattern extraction → lesson creation.
  - Lesson supersession with AuditEvent trail; LessonEvidence as separate table (not reusing ExecutionCitation).
  - 17 integration tests; ADR-008 ratified; `evaluations/reflection-quality.md` thresholds set.

- **2026-05-31** Phase 5 — Execution Intelligence ✅
  - `packages/execution/` — GoalService, TaskService, RoadmapService; citation_helpers; audit_service.
  - `roadmaps`, `goals`, `tasks`, `task_dependencies`, `execution_citations` tables; migration `0004_execution`.
  - POST/GET /roadmaps, POST/GET/PATCH /goals, POST/GET/PATCH /tasks, POST /tasks/{id}/dependencies.
  - `GET /goals/{id}/why` + `GET /tasks/{id}/why` — return pre-stored citations (no live retrieval).
  - Citation chain inherited at creation: clients submit citations from prior `/retrieval/search`.
  - Status-change audit reuses existing `AuditEvent` table (actor, prior_state, new_state, reason).
  - BFS cycle detection for task dependency graph; `DependencyCycleError` on violation.
  - 24 integration tests; ADR-007 ratified.

- **2026-05-30** Phase 4 — Engineering Memory ✅
  - `packages/retrieval/` — EmbeddingService, FTSService, VectorService, RRFReranker, HybridRetriever, CitationEngine, MemoryService.
  - `chunk_embeddings` + `memory_entries` tables; migration `0003_retrieval` (pgvector HNSW + GIN FTS indices).
  - POST /retrieval/embed/*, POST /retrieval/search, POST+GET /memory/entries, POST /memory/search.
  - Citation enforcement: every result carries source_id + URI + title; `has_citations` explicit.
  - Unit tests (RRF, 6 tests) + integration tests (embedding, retrieval, memory).
  - ADR-006 ratified (RRF over neural reranker — AP-3 offline-first).
  - `evaluations/retrieval-benchmarks.md` thresholds set.

- **2026-05-30** Phase 3 — Knowledge Compression ✅
  - `packages/llm/` — LLMProvider + EmbeddingProvider Protocols; OllamaProvider (offline default, httpx only); OpenAI/Anthropic/OpenRouter adapters (optional, lazy-imported).
  - `create_llm_provider()` + `create_embedding_provider()` factory — provider switch = one env-var change.
  - `packages/compression/` — SummarizationService (3 levels), MentalModelService, PlaybookService, TextChunker, CompressionService orchestrator.
  - `summaries` + `mental_models` tables; Alembic migration `0002_compression`.
  - POST /compress/documents/{id}, POST /compress/notes/{id}, GET summaries, GET mental-model.
  - Unit tests (stub LLM, no Ollama needed) + integration tests (real Postgres + stub LLM).
  - ADR-005 ratified; evaluations/summarization-faithfulness.md thresholds set.

- **2026-05-30** Phase 2 — Knowledge Capture ✅
  - Storage models (`raw_blobs`, `documents`, `notes`, `audit_events`) with Alembic migration `0001_initial`.
  - Idempotent ingestion via `UNIQUE(content_hash)` + audit events for both `create` and `dedup`.
  - Parsers for markdown, plaintext, PDF — each its own module.
  - `POST /documents` (multipart) and `POST /notes` (JSON) endpoints.
  - Real-Postgres integration tests (no DB mocks); `docker-compose.yml` for local Postgres.
  - ADR-004 (storage layout) ratified.
  - `evaluations/ingestion-correctness.md` contract drafted with P2 thresholds.

- **2026-05-30** Phase 1 — Foundation ✅
  - Memory bank populated; ADR-001/002/003 ratified.
  - Observability spine (OpenTelemetry tracing + Prometheus metrics + structlog + Langfuse stub).
  - FastAPI app with `/healthz`, `/readyz`, `/metrics`.
  - `make smoke` proves end-to-end wiring with console exporters.
  - GitHub Actions CI: lint + type + unit + docs build + smoke; separate integration job with Postgres service.
  - MkDocs Material renders the memory bank.

## Open Decisions
- **Embedding model family and dimension**. Settled at 768-dim (`nomic-embed-text` via Ollama). HNSW index created for this dimension. Changing dimension = drop + recreate index.
- **Neural cross-encoder reranker**. Deferred (ADR-006). Revisit at P6 when lesson corpus is large enough to measure uplift.
- **Deployment target order** (Tauri desktop vs. K8s server first). Revisit before P5 UI.

## Blockers
None.

## Risks Currently Top-of-Mind
See [risk-register/risks.md](risk-register/risks.md). Highest current:
- **R-001** Cloud LLM availability (mitigated by Ollama offline path).
- **R-002** Offline-Ollama hardware (research spike planned for P5).
- **R-003** Local-filesystem blob store is single-host (S3 adapter in P8 per ADR-004).
- **R-004** (new) Empty corpus at retrieval time — embedding step must be run before search works. Mitigated by clear API error surface and `has_citations=False` response.

## Next Phase
**None — all 8 phases complete.** ECI is GA-ready as of 2026-05-31.
Post-GA work items are tracked above under Current Sprint Goal.
