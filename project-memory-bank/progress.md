# Progress

Reverse-chronological log of completed work, milestones, and lessons. New entries go on top. Lessons feed back into [system-patterns.md](system-patterns.md) when they generalize.

---

## 2026-05-30 — Phase 3 Knowledge Compression complete

**Completed.**
- **LLM runtime (`packages/llm/`).** `LLMProvider` + `EmbeddingProvider` Protocols; `OllamaProvider` offline default (httpx only); `OpenAIProvider`, `AnthropicProvider`, `OpenRouterProvider` as optional extras (lazy-import guards). `create_llm_provider()` factory driven by `LLMConfig`. Switching providers = one env-var change.
- **Compression pipeline (`packages/compression/`).** `SummarizationService` (3 levels: short/medium/long with level-specific prompts and token budgets), `MentalModelService` (JSON extraction with markdown-fence stripping and graceful fallback on parse failure), `PlaybookService` (procedural extraction stored in `MentalModel.playbook` JSONB), `TextChunker` (paragraph-aware, overlap-capable), `CompressionService` orchestrator.
- **Storage.** `summaries` table (3 rows per source), `mental_models` table (1 row per source, includes playbook field). Alembic migration `0002_compression`. CHECK constraints ensure each row has exactly one of `document_id` / `note_id` set.
- **API.** `POST /compress/documents/{id}`, `POST /compress/notes/{id}`, `GET /compress/documents/{id}/summaries`, `GET /compress/documents/{id}/mental-model`.
- **Testing.** Unit tests for chunker, summarizer, mental-model service (stub LLM — no Ollama required). Integration tests for `CompressionService` against real Postgres with stub LLM.
- **ADR-005** (LLM runtime abstraction) — Accepted.
- **`evaluations/summarization-faithfulness.md`** — thresholds set (faithfulness ≥ 0.90 SHORT/MEDIUM, ≥ 0.85 LONG; latency p95 budgets). Baseline run deferred to first Ollama run.

**Milestone:** Phase 3 exit criteria met. Phase 4 (Engineering Memory) unblocked.

**Lessons learned.**
- *Graceful JSON fallback is load-bearing.* LLMs often return markdown-fenced JSON or partial objects. Stripping fences and defaulting missing fields to `[]` means one bad LLM response never crashes the pipeline.
- *Optional deps should fail loudly on instantiation, not at import time.* Lazy-import guards in `openai.py` / `anthropic.py` mean `import eci_llm` always succeeds; the error only surfaces if you try to *use* an unavailable provider.
- *One LLM provider singleton per process is correct.* `httpx.Client` keeps a connection pool; creating one per request would be wasteful. The singleton in `dependencies.py` is overridable via `dependency_overrides` in tests.

---

## 2026-05-30 — Phase 2 Knowledge Capture complete

**Completed.**
- **Storage (`packages/storage/`).** SQLAlchemy 2 models split one-per-aggregate (`raw_blobs`, `documents`, `notes`, `audit_events`). Alembic migration `0001_initial` creates the schema. Engine + session factory in `database.py`; transactional `session_scope()` for unit-of-work callers. Tests run against real Postgres via a transactional fixture (no DB mocks — global feedback honoured).
- **Ingestion (`packages/ingest/`).** Content hashing isolated to `hashing.py`. `BlobStore` Protocol + `LocalBlobStore` shard by hash prefix; S3 adapter remains a one-file change per ADR-004. Parsers split per kind (`markdown.py`, `plaintext.py`, `pdf.py`) so individual reads stay tiny. Services split per aggregate (`document_service.py`, `note_service.py`) to keep each file <150 lines. Audit helper reused across services.
- **API.** `POST /documents` (multipart) and `POST /notes` (JSON) endpoints; per-route Prometheus counters; ingest exceptions mapped to 413/415/422.
- **Local infra.** `docker-compose.yml` runs `pgvector/pgvector:pg16` so the same image carries through to P3 embeddings. Separate `postgres-test` service under a `test` profile for CI parity.
- **ADR-004** (storage layout) — Accepted.
- **Evaluation contract** `evaluations/ingestion-correctness.md` — P2 thresholds: 100% round-trip / 100% idempotency / 100% provenance.

**Milestone:** Phase 2 exit criteria met — see [implementation-status.md](implementation-status.md). Phase 3 (Knowledge Compression) unblocked.

**Lessons learned.**
- *Idempotency at the database boundary, not the service layer.* `UNIQUE(content_hash)` plus `INSERT ... ON CONFLICT` would be even tighter; today we do `SELECT then INSERT`, which is correct under the SERIALIZABLE-friendly defaults but should be revisited with a high-concurrency benchmark in P8.
- *Per-aggregate services beat shared services.* `document_service.py` + `note_service.py` (≈150 lines each) read faster than a hypothetical `ingest_service.py` (≈300+) — both for humans and LLMs.
- *Audit events captured early are cheap; bolted on later they hurt.* Auditing was added in the first version of each service rather than retrofitted — already paid off when verifying dedup behavior in tests.

---

## 2026-05-30 — Phase 1 Foundation complete

**Completed.**
- Memory bank populated: 7 files including `implementation-status.md`.
- ADRs ratified: ADR-001 (charter), ADR-002 (stack), ADR-003 (repo + branching).
- Repo skeleton: `apps/`, `packages/`, `infra/`, `docs/`, `scripts/`, `.github/workflows/`.
- **Observability** spine in `packages/observability/`: OpenTelemetry tracing (console + OTLP), Prometheus metrics (`eci_requests_total`, `eci_request_latency_seconds`, `eci_ingest_total`, `eci_ingest_bytes_total`), structlog with trace correlation, Langfuse client wrapper (no-op when unconfigured). One `bootstrap()` entry.
- **API** stub: FastAPI app factory, lifespan-driven bootstrap, `/healthz`, `/readyz`, `/metrics`, `FastAPIInstrumentor` for auto-tracing.
- **CI** workflow: lint (`ruff`), format check, type-check (`mypy --strict`), tests, strict docs build, smoke. A separate integration job runs against a Postgres service.
- **Tooling**: `uv` workspace, `pyproject.toml`, `Makefile` (`install`, `lint`, `type`, `test`, `smoke`, `docs`, `ci-local`, `db-up`, `db-migrate`, `test-integration`).
- **MkDocs Material** site renders the memory bank.
- **Risk register** initialized: R-001 (cloud LLM availability), R-002 (Ollama hardware).

**Milestone:** Phase 1 exit criteria met. Phase 2 (Knowledge Capture) unblocked.

**Lessons learned.**
- The 300-line file limit is enforced *while* a package is being built. Each observability subsystem became its own file from day one.
- Console exporters as the default lets `make smoke` prove wiring without external infrastructure. Pattern: *local → console; prod → OTLP via env.*
- Memory bank is most useful when small and link-heavy, not when it duplicates charter content.

---

## 2026-05-30 — Roadmap ratified

- ECI charter accepted as-is.
- Master roadmap (P1–P8) written. Per-phase exit criteria, dependencies, and quality gates defined.

---

## Initial — Repository created

- `git init`, `LICENSE`, one-line `README.md` on branch `develop`. No project structure yet.
