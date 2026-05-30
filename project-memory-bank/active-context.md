# Active Context

> **Read this first.** This file is the current "save state" of the project. It is updated at the end of every major feature and at every phase transition.

## Current Phase
**Phase 3 — Knowledge Compression** *(unblocked; not yet started)*.

Phase 1 (Foundation) and Phase 2 (Knowledge Capture) are complete. See [implementation-status.md](implementation-status.md) for the exit-criteria checklist.

## Current Sprint Goal
*(Phase 3 sprint begins on next approval — see [master-roadmap.md § Phase 3](roadmaps/master-roadmap.md))*

Planned scope:
- LLM runtime abstraction (Ollama default; OpenAI/Anthropic/OpenRouter via config).
- Multi-level summarization pipeline.
- Mental-model extraction.
- Playbook templates.
- ADR-005 — LLM runtime abstraction.
- `evaluations/summarization-faithfulness.md` contract with accepted threshold.

## Recently Completed
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
- **LLM runtime — Ollama model default**. To be settled by ADR-005 in P3.
- **Embedding model family and dimension**. To be settled by ADR in P3.
- **Deployment target order** (Tauri desktop vs. K8s server first). Revisit before P4 UI.

## Blockers
None.

## Risks Currently Top-of-Mind
See [risk-register/risks.md](risk-register/risks.md). Highest current:
- **R-001** Cloud LLM availability (mitigated by Ollama offline path).
- **R-002** Offline-Ollama hardware (research spike planned for P3).
- **R-003** Local-filesystem blob store is single-host (S3 adapter in P8 per ADR-004).

## Next Phase
**Phase 3 — Knowledge Compression.** Per charter RULE 4, do not begin until approved.
