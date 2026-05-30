# Active Context

> **Read this first.** This file is the current "save state" of the project. It is updated at the end of every major feature and at every phase transition.

## Current Phase
**Phase 5 — Execution Intelligence** *(unblocked; not yet started)*.

Phases 1–4 are complete. See [implementation-status.md](implementation-status.md) for the exit-criteria checklist.

## Current Sprint Goal
*(Phase 5 sprint begins on next approval — see [master-roadmap.md § Phase 5](roadmaps/master-roadmap.md))*

Planned scope:
- `Goal`, `Task`, `Roadmap` domain models with dependency edges and status.
- Every execution item linked back to the source memory (citation chain from P4).
- Status-change audit log (actor, before, after, reason).
- `GET /goals/{id}/why` — returns source citations justifying the goal.

## Recently Completed
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
**Phase 5 — Execution Intelligence.** Per charter RULE 4, do not begin until approved.
