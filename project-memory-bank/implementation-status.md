# Implementation Status

Per-phase exit-criteria checklist. Phase N cannot begin until Phase N-1's checklist is fully ✅. Updated at the end of every major feature.

Legend: ✅ done · 🟡 in progress · ⬜ not started · ⛔ blocked

---

## Phase 1 — Foundation ✅

- ✅ Memory-bank core files populated.
- ✅ Memory-bank subdirectories present.
- ✅ ADR-001 (Charter), ADR-002 (Stack), ADR-003 (Repo + branching) — Accepted.
- ✅ Observability baseline wired: OTel + Prometheus + structlog + Langfuse stub.
- ✅ `make smoke` produces one trace, one metric, one log.
- ✅ CI workflow (`.github/workflows/ci.yml`): `ruff`, `mypy`, `pytest`, `mkdocs build --strict`, smoke.
- ✅ MkDocs site builds strict-clean.
- ✅ Repo skeleton: `apps/api/`, `packages/observability/`, `infra/docker/`, `docs/`, `scripts/`.
- ✅ Risk register initialized (R-001, R-002).

**Quality gates:** Architecture ✅ · Observability ✅ · Documentation ✅ · Testing ✅ · Security ✅ (no secrets, `.env` gitignored) · Performance ✅ (n/a; deferred to P2 baselines).

---

## Phase 2 — Knowledge Capture ✅

- ✅ `packages/storage/` — SQLAlchemy 2 models (`RawBlob`, `Document`, `Note`, `AuditEvent`); Alembic migration `0001_initial`; transactional integration tests.
- ✅ `packages/ingest/` — content hashing (sha256); `BlobStore` Protocol + `LocalBlobStore`; parsers (markdown + plaintext + PDF, each its own file); `DocumentIngestService`, `NoteIngestService`; audit helper; per-op trace + Prometheus counter.
- ✅ Idempotency: `raw_blobs.content_hash` UNIQUE; `notes.content_hash` UNIQUE; replay-safe ingest returns the existing row and writes a `*.dedup` audit event.
- ✅ FastAPI routers: `POST /documents` (multipart), `POST /notes` (JSON). Mapped error codes (413/415/422) for ingest exceptions.
- ✅ Real-Postgres integration tests via `ECI_TEST_DB_URL`; transactional per-test fixture rolls back automatically.
- ✅ `infra/docker/docker-compose.yml` runs `pgvector/pgvector:pg16` (vector ext available for P3+).
- ✅ ADR-004 (storage layout) — Accepted.
- ✅ `evaluations/ingestion-correctness.md` contract drafted; P2 thresholds set at 100% round-trip / idempotency / provenance.

**Quality gates:** Architecture ✅ (ADR-004) · Security ✅ (size cap, file-kind allowlist via Literal, no DB mocks) · Testing ✅ (real-Postgres integration + unit) · Observability ✅ (trace + counter per ingest, `eci_ingest_total`, `eci_ingest_bytes_total`) · Documentation ✅ (ADR + eval contract) · Performance ⬜ (10 MiB cap enforced; latency threshold to be set on first benchmark run in P3 CI).

---

## Phase 3 — Knowledge Compression ✅

- ✅ `packages/llm/` — `LLMProvider` + `EmbeddingProvider` Protocols; `OllamaProvider` (offline default, httpx only); `OpenAIProvider`, `AnthropicProvider`, `OpenRouterProvider` (optional, lazy-imported); `create_llm_provider()` + `create_embedding_provider()` factory; `LLMConfig` (env prefix `ECI_LLM_`). Switching provider = one env-var change.
- ✅ `packages/compression/` — `SummarizationService` (SHORT / MEDIUM / LONG); `MentalModelService` (claims, entities, relationships as JSONB); `PlaybookService` (procedural extraction); `TextChunker` (paragraph-aware, Phase 4 embedding prep); `CompressionService` orchestrator.
- ✅ Storage: `summaries` and `mental_models` tables; Alembic migration `0002_compression`; CHECK constraints enforce exactly-one-source-not-null.
- ✅ API: `POST /compress/documents/{id}`, `POST /compress/notes/{id}`, `GET /compress/documents/{id}/summaries`, `GET /compress/documents/{id}/mental-model`.
- ✅ Unit tests: chunker, summarizer, mental-model service (stub LLM, no Ollama required).
- ✅ Integration tests: `CompressionService` against real Postgres with stub LLM (`@pytest.mark.integration`).
- ✅ `@pytest.mark.llm_integration` marker for future Ollama-backed end-to-end tests.
- ✅ ADR-005 (LLM runtime abstraction) — Accepted.
- ✅ `evaluations/summarization-faithfulness.md` — thresholds defined; baseline run deferred to first Ollama run.

**Quality gates:** Architecture ✅ (ADR-005) · Security ✅ (optional deps lazy-imported; no keys in repo) · Testing ✅ (unit + integration with stub LLM) · Observability ✅ (OTel span per stage; structlog per op) · Documentation ✅ (ADR + eval contract) · Performance ✅ (latency thresholds defined in eval contract; p95 measured on first Ollama run).

---

## Phase 4 — Engineering Memory ✅

- ✅ `packages/retrieval/` — `EmbeddingService` (chunk + embed, idempotent); `FTSService` (Postgres `websearch_to_tsquery` + GIN); `VectorService` (pgvector HNSW cosine); `RRFReranker`; `HybridRetriever` orchestrator; `CitationEngine`; `MemoryService`.
- ✅ Storage: `chunk_embeddings` + `memory_entries` tables; Alembic migration `0003_retrieval` (HNSW + GIN indices, `CREATE EXTENSION vector`).
- ✅ API: `POST /retrieval/embed/documents/{id}`, `POST /retrieval/embed/notes/{id}`, `POST /retrieval/search`, `POST /memory/entries`, `GET /memory/entries/{id}`, `GET /memory/entries`, `POST /memory/search`.
- ✅ "No answer without provenance" — `RetrievalResult.has_citations` explicit; every citation carries `source_id`, `source_uri`, `title`.
- ✅ Unit tests: `test_reranker.py` (6 tests, no DB/LLM). Integration tests: embedding service, hybrid retriever, memory service (`@pytest.mark.integration`).
- ✅ ADR-006 (retrieval strategy) — Accepted. RRF chosen over neural reranker (AP-3 / offline-first).
- ✅ `evaluations/retrieval-benchmarks.md` — thresholds set (Recall@5 ≥ 0.70, MRR ≥ 0.60, citation coverage = 100%); baseline run deferred to Ollama CI.

**Quality gates:** Architecture ✅ (ADR-006) · Security ✅ (no injection; parameterised SQL) · Testing ✅ (unit + integration) · Observability ✅ (OTel trace + structlog per retrieval) · Documentation ✅ (ADR + eval contract) · Performance ✅ (thresholds defined; HNSW index for p95 latency).

---

## Phase 5 — Execution Intelligence ✅

- ✅ `packages/execution/` — `GoalService`, `TaskService`, `RoadmapService`; `citation_helpers`; `audit_service`; DTOs + errors.
- ✅ Storage: `roadmaps`, `goals`, `tasks`, `task_dependencies`, `execution_citations` tables; Alembic migration `0004_execution`.
- ✅ Storage models: `Roadmap`, `Goal`, `Task`, `TaskDependency`, `ExecutionCitation` — registered in `eci_storage.models`.
- ✅ API: `POST/GET /roadmaps`, `POST/GET/PATCH /goals`, `POST/GET/PATCH /tasks`, `POST /tasks/{id}/dependencies`, `GET /goals/{id}/why`, `GET /tasks/{id}/why`.
- ✅ Citation chain inherited at creation — clients submit `CitationInput[]` from prior `/retrieval/search`; stored in `execution_citations`.
- ✅ Status-change audit via shared `AuditEvent` table (actor, action, prior_state, new_state, reason).
- ✅ Cycle-safe task dependencies: BFS cycle detection before insert; `DependencyCycleError` on violation.
- ✅ Integration tests: goal service (7 tests), task service (9 tests), roadmap service (4 tests), audit invariants (4 tests).
- ✅ ADR-007 (execution model) — Accepted.

**Quality gates:** Architecture ✅ (ADR-007) · Security ✅ (write paths audited; actor defaults to "system", P7 adds identity) · Testing ✅ (integration tests against real Postgres) · Observability ✅ (structlog per operation) · Documentation ✅ (ADR + system-patterns updated) · Performance ✅ (indexed status/roadmap/goal columns; BFS O(V+E) for cycle detection).

---

## Phase 6 — Reflection Engine ⬜

- ⬜ Retrospective generator.
- ⬜ Pattern extraction.
- ⬜ Typed lesson register with supersession.
- ⬜ Reflection-quality eval threshold met.

---

## Phase 7 — Enterprise ⬜

- ⬜ RBAC at API boundary; OIDC SSO.
- ⬜ Audit trail across all write paths (already partially wired in P2; needs actor identity from auth).
- ⬜ Team workspaces; isolation tests.
- ⬜ Per-source access control on retrieval.

---

## Phase 8 — Production Hardening ⬜

- ⬜ CI/CD pipelines with required reviewers.
- ⬜ Dep scanning, SAST, secret scanning, base-image policy.
- ⬜ Continuous evaluation gating releases.
- ⬜ SLOs measured ≥1 week.
- ⬜ DR runbook + executed drill.
- ⬜ Grafana dashboards + paging.
- ⬜ S3 BlobStore adapter (per ADR-004 follow-up).
