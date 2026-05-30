# System Patterns

This file records architectural patterns, standards, and conventions that span the codebase. Specific decisions live as ADRs in [architecture-decisions/](architecture-decisions/); patterns here describe how the system is composed.

## Architectural Principles (from charter)
- **AP-1** — Memory is the product. Everything else supports memory.
- **AP-2** — Evidence before inference. All generated outputs carry source references.
- **AP-3** — Offline-first. Cloud-enhanced. Never cloud-dependent.
- **AP-4** — Human-in-control. AI recommends; humans decide.
- **AP-5** — Composable modules. No tightly coupled subsystems.
- **AP-6** — Long-term ownership. Avoid vendor lock-in.

## Ratified Architecture Decisions
| ADR | Title | Status |
|---|---|---|
| [ADR-001](architecture-decisions/ADR-001-charter-ratification.md) | Charter ratification | Accepted |
| [ADR-002](architecture-decisions/ADR-002-technology-stack.md) | Technology stack | Accepted |
| [ADR-003](architecture-decisions/ADR-003-repo-and-branching.md) | Repository layout and branching | Accepted |
| [ADR-004](architecture-decisions/ADR-004-storage-layout.md) | Storage layout for captured knowledge | Accepted |
| [ADR-005](architecture-decisions/ADR-005-llm-runtime.md) | LLM runtime abstraction | Accepted |

## Cross-cutting Patterns

### Modularity contract
- **Hard limit: 300 lines per source file.** A file exceeding this is split — domain by domain, not arbitrarily.
- One module = one responsibility. `goal_service.py`, `calendar_service.py`, not `services.py`.
- Public surface of each package is declared in `__init__.py`; nothing else is re-exported.

### Observability contract
Every request-handling code path emits:
- **One OpenTelemetry trace** (root span on the request, child spans on internal stages).
- **One Prometheus counter increment** keyed by route + outcome.
- **One structured log line** per stage of interest, with `trace_id` correlation.
- **Langfuse span** for any LLM call (Phase 3+).

Local development uses console exporters; production uses OTLP endpoints + Prometheus scrape + Langfuse SDK. See `packages/observability/`.

### Evidence-before-inference pattern
Any service that returns a generated artifact (summary, answer, lesson, recommendation) must also return:
- A non-empty list of source references (record IDs + content hashes).
- A reasoning trace summary the user can inspect.
- A confidence signal (categorical, not a fabricated float).

The API layer refuses to serve generated responses that omit sources (fail closed).

### Offline-first pattern (AP-3)
LLM runtime, embedding generation, and retrieval all expose a unified interface with at least one offline-capable implementation (Ollama for LLM, local embedding model for vectors, local pgvector for storage). Cloud providers are opt-in via configuration; never the default.

### Auditability pattern
Every write path (ingest, status change, lesson supersession, role grant) appends to an immutable audit log with: actor, action, prior_state, new_state, timestamp, reason. The audit log is itself a memory record and is queryable.

## Standards
- **Language:** Python 3.12 for backend; TypeScript 5.x for frontend (Phase 4+); SQL for storage.
- **Style:** `ruff` for Python lint+format; `prettier` for TS/JS/Markdown.
- **Types:** strict typing (`mypy --strict` or `basedpyright`); no `Any` without a comment justifying it.
- **Tests:** integration tests against a real Postgres (no DB mocks — per global feedback memory).
- **Commits:** conventional commits; PRs reference the ADR they implement or the phase exit criterion they satisfy.
- **Docs:** every public function has a one-line docstring; complex invariants explained in module-level docstring.

### Ingestion + provenance pattern (P2)
Captured content has two lifetimes:
- **Raw bytes** — immutable, content-addressed (sha256), stored in a `BlobStore` (filesystem locally; S3 adapter in P8).
- **Parsed records** — `Document` (linked to a `RawBlob`) or `Note` (inline body, content-hashed with source + author + captured_at).

Every ingest is idempotent at the database boundary via `UNIQUE(content_hash)`. Replays return the existing record and emit a `*.dedup` audit event.

Every ingest records `source`, `captured_at`, `ingested_at`, `ingested_by`. The audit trail is append-only.

Services are split per aggregate (`document_service.py` ≈ 150 lines, `note_service.py` ≈ 100 lines) rather than a shared `ingest_service.py`. Parsers are split per kind.

### LLM runtime abstraction pattern (P3)
`packages/llm/` exposes `LLMProvider` and `EmbeddingProvider` as `runtime_checkable` Protocols.
Callers never import a concrete class — only the Protocol and the factory function
`create_llm_provider(config)`. Switching providers is a one-env-var change (`ECI_LLM_PROVIDER`).

- `OllamaProvider` — offline default; requires only `httpx`.
- `OpenAIProvider`, `AnthropicProvider`, `OpenRouterProvider` — optional; raise
  `LLMProviderNotAvailable` on instantiation if the required package is absent.

`EmbeddingProvider` is defined but not wired to storage until Phase 4.

### Compression pipeline pattern (P3)
`CompressionService.compress(request)` orchestrates three independent stages in sequence:
1. `SummarizationService` → 3 `Summary` DB records (short / medium / long).
2. `MentalModelService` → 1 `MentalModel` DB record (claims, entities, relationships, playbook).
3. `PlaybookService` → stored inside `MentalModel.playbook` JSONB field.

Each stage emits an OTel span. Malformed JSON from the LLM degrades gracefully
(empty fields) rather than raising, per AP-2 (partial evidence > no evidence).

## Patterns Deferred to Later Phases
- LLM-runtime abstraction → Phase 3 ✅ (done).
- Hybrid retrieval + citation pattern → Phase 4.
- Execution + traceability pattern → Phase 5.
- Reflection + lesson register pattern → Phase 6.
- RBAC + tenancy pattern → Phase 7.
- Release pattern (eval-gated, SLO-monitored) → Phase 8.
