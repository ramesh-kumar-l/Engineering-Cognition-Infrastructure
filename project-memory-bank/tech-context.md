# Technical Context

Concrete technology choices and current dependencies. See [ADR-002](architecture-decisions/ADR-002-technology-stack.md) for the ratification of this stack; this file tracks what is *actually wired up right now*.

## Stack (target end state)
| Layer | Choice |
|---|---|
| Backend | FastAPI + Pydantic v2 + SQLAlchemy 2 |
| Database | PostgreSQL 16 + pgvector |
| LLM runtime | Ollama (offline default), OpenAI, Anthropic, OpenRouter (cloud) |
| Retrieval | Postgres FTS (BM25-like) + pgvector + cross-encoder reranker |
| Observability | OpenTelemetry + Langfuse + Prometheus + Grafana |
| Frontend | React 18 + TypeScript 5 + Tauri (desktop wrapper) |
| Docs | MkDocs Material |
| Packaging | `uv` workspace; per-app `pyproject.toml` |
| Containers | Docker; Kubernetes for cloud server deployments |
| CI | GitHub Actions |

## Phase 1 + Phase 2 + Phase 3 Wired
- **Python 3.12** with `uv` workspace at the root.
- **FastAPI** at `apps/api/` exposing `/healthz`, `/readyz`, `/metrics`, `POST /documents`, `POST /notes`.
- **Observability package** at `packages/observability/`:
  - `tracing.py` — OpenTelemetry SDK; console exporter by default, OTLP via env.
  - `metrics.py` — `prometheus_client` registry: `eci_requests_total`, `eci_request_latency_seconds`, `eci_ingest_total`, `eci_ingest_bytes_total`.
  - `logging.py` — `structlog` with trace correlation.
  - `langfuse_export.py` — Langfuse client wrapper; no-op when unconfigured.
- **Storage package** at `packages/storage/`:
  - SQLAlchemy 2 models split one-per-aggregate (`raw_blobs`, `documents`, `notes`, `audit_events`).
  - Alembic migrations (`0001_initial`).
  - `session_scope()` context manager for unit-of-work callers.
- **Ingest package** at `packages/ingest/`:
  - `hashing.py` (sha256 helpers).
  - `BlobStore` Protocol + `LocalBlobStore` (filesystem, sharded).
  - Parsers per kind: `markdown.py`, `plaintext.py`, `pdf.py`.
  - Services per aggregate: `document_service.py`, `note_service.py`.
  - Shared audit helper.
- **Postgres** runs from `infra/docker/docker-compose.yml` using `pgvector/pgvector:pg16` (vector ext pre-installed for P3+).
- **MkDocs Material** site serving the memory bank.
- **GitHub Actions CI**: quick lane (lint + type + unit + docs + smoke) and integration lane (real Postgres + Alembic).
- **`make smoke`** proves observability wiring end-to-end (one trace, one metric, one log).

- **LLM package** at `packages/llm/`:
  - `LLMProvider` / `EmbeddingProvider` Protocols (`runtime_checkable`).
  - `OllamaProvider` + `OllamaEmbeddingProvider` — offline default, httpx only.
  - `OpenAIProvider`, `AnthropicProvider`, `OpenRouterProvider` — optional, lazy-imported.
  - `create_llm_provider(config)`, `create_embedding_provider(config)` factory functions.
  - `LLMConfig` (env prefix `ECI_LLM_`): `provider`, `model`, `ollama_host`, `openai_api_key`, etc.
- **Compression package** at `packages/compression/`:
  - `SummarizationService` (SHORT/MEDIUM/LONG prompts).
  - `MentalModelService` (JSON extraction: claims, entities, relationships).
  - `PlaybookService` (procedural extraction stored in MentalModel.playbook JSONB).
  - `TextChunker` (paragraph-aware, overlap-capable — Phase 4 embedding prep).
  - `CompressionService` orchestrator: fetches source → compress → persist.
- **New DB tables**: `summaries` (3 per source), `mental_models` (1 per source).
  Alembic migration `0002_compression`. CHECK constraints: exactly one of `document_id` / `note_id` is non-null.
- **API**: `POST /compress/documents/{id}`, `POST /compress/notes/{id}`,
  `GET /compress/documents/{id}/summaries`, `GET /compress/documents/{id}/mental-model`.
- **LLM provider singleton** in `dependencies.py` (`get_llm_provider`) — created once per process, swappable via `app.dependency_overrides` in tests.

## Not Yet Wired (deferred per phase)
| Item | Phase |
|---|---|
| Embeddings stored in pgvector | P4 |
| Hybrid retrieval | P4 |
| Frontend (React + Tauri) | P4 (initial), P5+ (full) |
| Cross-encoder reranker | P4 |
| RBAC + SSO | P7 |
| Kubernetes manifests | P8 |
| Grafana dashboards | P8 |

## Environment Variables (current)
| Var | Purpose | Default |
|---|---|---|
| `ECI_ENV` | `local` \| `dev` \| `prod` | `local` |
| `ECI_LOG_LEVEL` | structlog level | `INFO` |
| `ECI_LLM_PROVIDER` | LLM provider: `ollama`\|`openai`\|`anthropic`\|`openrouter` | `ollama` |
| `ECI_LLM_MODEL` | Model name for the selected provider | `llama3.2` |
| `ECI_LLM_OLLAMA_HOST` | Ollama server URL | `http://localhost:11434` |
| `ECI_LLM_OPENAI_API_KEY` | OpenAI / OpenRouter API key | unset |
| `ECI_LLM_ANTHROPIC_API_KEY` | Anthropic API key | unset |
| `ECI_LLM_EMBEDDING_MODEL` | Embedding model name | `nomic-embed-text` |
| `ECI_LLM_EMBEDDING_DIM` | Embedding vector dimension | `768` |
| `ECI_COMPRESSION_MAX_CONTENT_CHARS` | Max chars fed to LLM | `32000` |
| `ECI_COMPRESSION_EXTRACT_PLAYBOOKS` | Enable playbook extraction | `true` |
| `ECI_OTLP_ENDPOINT` | OTel collector endpoint | unset → console exporter |
| `ECI_PROMETHEUS_PORT` | metrics endpoint port | `9464` |
| `ECI_LANGFUSE_HOST` | Langfuse host | unset → no-op |
| `ECI_LANGFUSE_PUBLIC_KEY` | Langfuse public key | unset → no-op |
| `ECI_LANGFUSE_SECRET_KEY` | Langfuse secret key | unset → no-op |

No secrets are committed. `.env.example` documents required keys; `.env` is gitignored.

## Tooling Versions
- Python: `>=3.12,<3.13`
- `uv`: latest stable
- `ruff`: pinned in `pyproject.toml`
- `mypy`: pinned in `pyproject.toml`
- `pytest`: pinned in `pyproject.toml`
- Node (for docs / frontend): `>=20.10` (used from P4)

## Build / Run Quick Reference
- `make install` — sync workspace deps via `uv`.
- `make lint` — ruff + mypy.
- `make test` — pytest across packages.
- `make smoke` — runs the observability smoke script.
- `make docs` — serves MkDocs locally.
- `make docs-build` — strict build (used in CI).
