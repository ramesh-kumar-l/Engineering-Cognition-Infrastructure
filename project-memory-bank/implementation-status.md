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

## Phase 4 — Engineering Memory ⬜

- ⬜ Hybrid retrieval (BM25 + pgvector + cross-encoder rerank).
- ⬜ Citation engine; "no answer without provenance" enforced at API.
- ⬜ Long-term memory store (versioned).
- ⬜ `evaluations/retrieval-benchmarks.md` with thresholds.
- ⬜ ADR (retrieval).

---

## Phase 5 — Execution Intelligence ⬜

- ⬜ Goal / Task / Roadmap models linked to source memory.
- ⬜ Status-change audit log.
- ⬜ "Why does this task exist?" returns cited justification.

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
