# ADR-002 — Technology Stack

- **Status:** Accepted
- **Date:** 2026-05-30
- **Deciders:** Project lead
- **Phase:** P1

## Context
The charter prescribes a preferred stack. This ADR commits to specific tools at the layer of granularity that affects daily work, while leaving version pinning and a few sub-choices to the phase that consumes them (per "Decisions Deferred" in the roadmap).

## Decision
Commit to the following stack:

| Layer | Choice | Rationale |
|---|---|---|
| Backend language | Python 3.12 | Mature LLM/ML ecosystem; aligns with charter. |
| Backend framework | FastAPI + Pydantic v2 | Async, typed, OpenAPI-native. |
| ORM | SQLAlchemy 2 (sync core; async opt-in per service) | Mature, type-safe, vendor-portable. |
| Primary store | PostgreSQL 16 + pgvector | Single store for relational + vector; supports AP-3 offline-first. Version locked in P2 ADR. |
| LLM runtime | Ollama (offline default), with OpenAI, Anthropic, OpenRouter as cloud options | AP-3 (offline-first), AP-6 (no vendor lock-in). |
| Embeddings | TBD (P3 ADR) | Deferred to P3. |
| Retrieval | Postgres FTS + pgvector + cross-encoder rerank | Local-first; reranker model chosen in P4. |
| Observability — traces | OpenTelemetry SDK + OTLP exporter | Industry standard; vendor-portable. |
| Observability — LLM | Langfuse | Purpose-built for LLM call tracing. |
| Observability — metrics | `prometheus_client` + Prometheus scrape | Standard. |
| Observability — logs | `structlog` with JSON in prod, console in local | Trace-correlated structured logs. |
| Frontend | React 18 + TypeScript 5 + Vite | Standard, typed, fast. |
| Desktop wrapper | Tauri 2 | Aligns with AP-3; Rust-based, small footprint. |
| Docs | MkDocs Material | Renders the memory bank; first-class search. |
| Packaging | `uv` workspace; per-app `pyproject.toml` | Fast, deterministic; modern Python tooling. |
| Lint / format | `ruff` (Python), `prettier` (TS/JS/Markdown) | Single fast tool per ecosystem. |
| Type-check | `mypy --strict` (initial); revisit `basedpyright` in P3 | Strict typing is non-negotiable. |
| Test | `pytest` (Python), `vitest` (TS) | Standard. |
| Containers | Docker | Standard. |
| Orchestration | Kubernetes (cloud); Tauri (desktop) | Charter-prescribed. K8s manifests live in P8. |
| CI | GitHub Actions | Standard; matches typical OSS expectations. |

## Consequences
**Positive.**
- Every choice has a credible offline-capable mode (AP-3) or is opt-in cloud (AP-6).
- The runtime is portable: Postgres + Python + Docker run on any modern host.
- LLM provider switching requires a config change, not a code change (enforced from P3).

**Negative.**
- Ollama requires meaningful local hardware; recorded as R-002. Mitigation deferred to P3 research.
- `pgvector` performance ceilings may force a future ADR if scale exceeds Postgres. Acceptable trade-off for now (charter prefers simpler solution).
- Tauri introduces Rust toolchain on developer machines. Deferred until P4 frontend work.

**Neutral.**
- Version pinning lives in `pyproject.toml`. Major-version upgrades require a follow-up ADR.

## Alternatives Considered
- **Node/TypeScript backend.** Rejected: Python's LLM/ML ecosystem (langchain, sentence-transformers, eval frameworks) is significantly more mature for the kinds of work P3+ requires.
- **Dedicated vector DB (Qdrant, Weaviate, Pinecone).** Rejected for now: pgvector is sufficient at the target scale and removes operational surface area. Will reconsider with evidence (P4 benchmarks) if needed.
- **Loguru / vanilla logging.** Rejected: structlog's structured-first model and trace correlation match the observability contract better.

## Compliance
A reviewer can verify by:
1. `pyproject.toml` declares the pinned versions of `fastapi`, `pydantic`, `sqlalchemy`, `opentelemetry-*`, `prometheus-client`, `structlog`, `langfuse`, `ruff`, `mypy`, `pytest`.
2. No service depends on a single LLM vendor at import time (P3+).
3. No code path requires a network call to succeed in `ECI_ENV=local` (AP-3).
