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

## Phase 6 — Reflection Engine ✅

- ✅ `packages/reflection/` — `RetrospectiveService`, `LessonService`, `PatternExtractor`; `evidence_helpers`; DTOs + errors.
- ✅ Storage: `retrospectives`, `lessons`, `lesson_evidence` tables; Alembic migration `0005_reflection`.
- ✅ Storage models: `Retrospective`, `Lesson`, `LessonEvidence` — registered in `eci_storage.models`.
- ✅ API: `POST/GET /retrospectives`, `GET /retrospectives/{id}`, `POST/GET /lessons`, `GET /lessons/{id}`, `POST /lessons/{id}/supersede`.
- ✅ Synchronous retrospective run: create → collect execution history → LLM pattern extraction → create lessons → complete.
- ✅ LLM malformation tolerated: empty/invalid JSON → retrospective completes with 0 lessons.
- ✅ Lesson supersession: `supersedes_id` FK + old status → `superseded`; audited via shared `AuditEvent` table.
- ✅ Lesson evidence: separate `lesson_evidence` table (coarser than retrieval chunks; goal/task/memory_entry pointers + summary).
- ✅ Integration tests: lesson service (7 tests), retrospective service (7 tests), evidence invariants (3 tests).
- ✅ ADR-008 (reflection domain model) — Accepted.
- ✅ `evaluations/reflection-quality.md` — thresholds defined; Ollama baseline run deferred.

**Quality gates:** Architecture ✅ (ADR-008) · Security ✅ (write paths audited; actor tracked) · Testing ✅ (integration tests against real Postgres + stub LLM) · Observability ✅ (structlog per operation) · Documentation ✅ (ADR + eval contract + system-patterns) · Performance ✅ (indexed retrospective/lesson status columns; scoped queries limit corpus size).

---

## Phase 7 — Enterprise ✅

- ✅ `packages/identity/` — TenantService, UserService, TokenService, OIDCService; config, errors, dto, rbac; ADR-009.
- ✅ Storage: `tenants`, `users` tables; `tenant_id` nullable column on documents, notes, roadmaps, goals, tasks, memory_entries, chunk_embeddings, retrospectives, lessons; Alembic migration `0006_enterprise`.
- ✅ Storage models: `Tenant`, `User` — registered in `eci_storage.models`.
- ✅ RBAC at API boundary: `get_request_context`, `require_write`, `require_admin` FastAPI dependencies; `eci_auth_denied_total{reason}` Prometheus counter.
- ✅ OIDC SSO: `GET /auth/login` → authorization URL; `POST /auth/callback` → code exchange → local HS256 JWT. Dev bypass via `ECI_IDENTITY_AUTH_DISABLED=true`.
- ✅ Tenant management: `POST/GET/GET /tenants` (admin-only).
- ✅ User management: `POST/GET/GET /users`, `PATCH /users/{id}/role`; list scoped to caller's tenant.
- ✅ Tenant isolation: `list_goals/tasks/roadmaps` accept `tenant_id` filter; routers pass `ctx.tenant_id`.
- ✅ Per-source retrieval access control: `RetrievalRequest.tenant_id` threaded into FTS + vector SQL queries; citations from other tenants excluded at query time.
- ✅ Integration tests: tenant service (6 tests), user service (8 tests), RBAC unit tests (10 tests), tenant isolation negative tests (5 tests).
- ✅ ADR-009 (enterprise RBAC model) — Accepted.

**Quality gates:** Security ✅ (RBAC enforced at boundary; deny events logged + metered; cross-tenant read rejected at router) · Architecture ✅ (ADR-009) · Testing ✅ (isolation negative tests pass; RBAC unit tests) · Observability ✅ (`eci_auth_denied_total` counter; structlog per auth event) · Documentation ✅ (ADR-009 + system-patterns updated) · Performance ✅ (tenant_id indexed on all data tables; no regression on list paths).

---

## Phase 8 — Production Hardening ✅

- ✅ S3 BlobStore adapter — `packages/ingest/src/eci_ingest/s3_blob_store.py`; `ECI_BLOB_BACKEND=s3`; optional `boto3` dep; key layout mirrors `LocalBlobStore`; `reset_blob_store()` for test isolation. ADR-010.
- ✅ Security CI pipeline — `.github/workflows/security.yml`: `pip-audit` (dep CVE), `bandit` (SAST), `trufflehog` (secrets), `trivy` (container + SBOM). Runs on every PR + weekly cron.
- ✅ Release workflow — `.github/workflows/release.yml`: eval gate + dep scan must pass; Docker image built + pushed to GHCR; deploy-staging environment gate.
- ✅ Eval gate — `scripts/eval_gate.py`: verifies all 4 eval contract files + thresholds; blocks release on missing or regressed contracts; extends to corpus benchmarks when `ECI_EVAL_CORPUS_AVAILABLE=true`.
- ✅ `evaluations/reflection-quality.md` — P6 thresholds defined; stub-LLM baseline recorded.
- ✅ CI mypy coverage expanded — all 9 packages now covered in `ci.yml`.
- ✅ SLO definitions — `project-memory-bank/slos/slos.md`: 5 SLOs (availability 99.5%, p95 ≤ 500ms, p99 ≤ 1500ms, citation coverage 100%, Recall@5 ≥ 0.70); error budget policy.
- ✅ Grafana SLO dashboard — `infra/grafana/dashboards/eci-slo.json`: 8 panels (availability, latency p95/p99, auth denies, request rate, latency timeseries, ingest throughput, deny timeseries); auto-provisioned.
- ✅ Prometheus alerts — `infra/prometheus/alerts/eci.yml`: 6 alert rules covering all SLO burn rates + service-down + ingest errors.
- ✅ Alertmanager config — `infra/alertmanager/alertmanager.yml`: severity routing (critical / warning); inhibit rules.
- ✅ Production docker-compose — `infra/docker/docker-compose.prod.yml`: API + Postgres + Prometheus + Grafana + Alertmanager; volume management; healthchecks.
- ✅ Dockerfile updated — all 9 packages included; `HEALTHCHECK` directive; non-root hardening.
- ✅ DR runbook — `project-memory-bank/runbooks/disaster-recovery.md`: backup cadence, restore procedure, DR drill protocol, RTO/RPO targets (2h/24h); drill log (first drill scheduled post-GA).
- ✅ ADR-010 ratified — S3 adapter, security toolchain, SLO definitions, eval gating all decided and documented.
- ✅ Risk register updated — R-003 mitigated; R-004/R-005/R-006 opened and triaged; standing categories resolved.

**Quality gates:** Security ✅ (SAST + dep scan + container scan in CI) · Architecture ✅ (ADR-010) · Testing ✅ (eval gate in release; integration tests in release workflow) · Observability ✅ (Grafana dashboards + Prometheus alerts + Alertmanager provisioned) · Documentation ✅ (ADR-010 + SLOs + DR runbook + eval contracts all present) · Performance ✅ (SLO thresholds defined; alert rules enforce them continuously).

---

## Frontend (`apps/web/`) — additive UI over the GA backend

Source of truth: `project-memory-bank/frontend/frontend-design.md`. React 18 · TS strict · Vite · Tailwind v4 + Radix · TanStack Query/Router · Zod · Vitest. Hard 300-line file cap. Surfaces existing API provenance — never re-derives evidence.

- ✅ **Phase A — Scaffold + Search**: app shell (left rail/top bar/live health pill), typed `fetch` client + Zod validation, dev-bypass auth, Vite `/api`→:8000 proxy. Search slice with `CitationCard` + `HasCitationsBanner` + `retrieval_stages` chip.
- ✅ **Phase B — Ingest + Compress**: `POST /documents` + `POST /notes` with dedup/provenance card and `?documentId=` handoff; compress pipeline run, summaries, mental-model, embed-for-search. Fail-closed when LLM down.
- ✅ **Phase C — Execution**: roadmaps → goals → tasks master-detail; status transitions; cycle-safe task dependencies; shared `WhyDrawer` rendering `GET /goals|tasks/{id}/why`. **One approved backend fix** (the only one): create paths thread `ctx.tenant_id` (lists were tenant-scoped but creates wrote NULL → empty lists); `apps/api/dev_seed.py` idempotently seeds the dev tenant+user, auth-disabled only.
- ✅ **Phase D — Reflection**: `RetrospectivePanel` (run by cadence + notes; selectable list) + `LessonPanel` (status filter, manual capture); `LessonCard` with confidence/scope/status badges, supersession lineage, inline supersede (`POST /lessons/{id}/supersede`). New shared `EvidenceList` (fail-closed AP-2) + reusable `EvidenceEditor`. No backend change.
- ⬜ **Phase E — Observability & guidance polish**: live `/metrics` summary, SLO panel, docs deep-links, onboarding/next-step nudges + full-experience validation.

**Status:** 15/15 Vitest pass; `npm run build` clean (287 modules). Phases A–D verified live against the running API. **Env note:** Compress/Embed/Search-embedding and retrospective lesson-extraction need an LLM provider (Ollama not installed in this dev env → those paths 5xx / yield 0 lessons; UI fails closed). Ingest, Execution, and manual Reflection capture are LLM-free.
