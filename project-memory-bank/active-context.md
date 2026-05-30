# Active Context

> **Read this first.** This file is the current "save state" of the project. It is updated at the end of every major feature and at every phase transition.

## Current Phase
**Phase 4 — Engineering Memory** *(unblocked; not yet started)*.

Phase 1 (Foundation) and Phase 2 (Knowledge Capture) are complete. See [implementation-status.md](implementation-status.md) for the exit-criteria checklist.

## Current Sprint Goal
*(Phase 4 sprint begins on next approval — see [master-roadmap.md § Phase 4](roadmaps/master-roadmap.md))*

Planned scope:
- pgvector indices + embedding generation wired to `EmbeddingProvider`.
- BM25 (Postgres FTS) retrieval.
- Hybrid retrieval: BM25 + pgvector + cross-encoder rerank.
- Citation engine: "no answer without provenance" at the API layer.
- ADR (retrieval strategy).
- `evaluations/retrieval-benchmarks.md` with accepted thresholds.

## Recently Completed
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
- **Embedding model family and dimension**. Default is 768-dim (`nomic-embed-text` via Ollama), settable via `ECI_LLM_EMBEDDING_DIM`. Confirm before creating pgvector index in P4.
- **Cross-encoder reranker choice**. To be settled by ADR in P4.
- **Deployment target order** (Tauri desktop vs. K8s server first). Revisit before P4 UI.

## Blockers
None.

## Risks Currently Top-of-Mind
See [risk-register/risks.md](risk-register/risks.md). Highest current:
- **R-001** Cloud LLM availability (mitigated by Ollama offline path).
- **R-002** Offline-Ollama hardware (research spike planned for P3).
- **R-003** Local-filesystem blob store is single-host (S3 adapter in P8 per ADR-004).

## Next Phase
**Phase 4 — Engineering Memory.** Per charter RULE 4, do not begin until approved.
