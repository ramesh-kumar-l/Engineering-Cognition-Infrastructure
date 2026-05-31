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
| ADR-006 | Retrieval strategy (RRF over neural reranker) | Accepted |
| [ADR-007](architecture-decisions/ADR-007-execution-model.md) | Execution intelligence model | Accepted |
| [ADR-008](architecture-decisions/ADR-008-reflection-model.md) | Reflection engine domain model | Accepted |
| [ADR-009](architecture-decisions/ADR-009-enterprise-rbac.md) | Enterprise RBAC, multi-tenancy, OIDC SSO | Accepted |
| [ADR-010](architecture-decisions/ADR-010-production-hardening.md) | Production hardening strategy | Accepted |

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

### Hybrid retrieval + citation pattern (P4)
`HybridRetriever.retrieve(request)` orchestrates:
1. `FTSService` (Postgres `websearch_to_tsquery` + GIN)
2. `VectorService` (pgvector HNSW cosine ANN)
3. `RRFReranker` (Reciprocal Rank Fusion, k=60)
4. `CitationEngine` (batch-fetches source titles + URIs)

"No answer without provenance" — `RetrievalResult.has_citations` is an explicit boolean; every `Citation` carries `source_id`, `source_uri`, `title`. See ADR-006.

### Execution + traceability pattern (P5)
`GoalService`, `TaskService`, `RoadmapService` form the execution domain (ADR-007):
- **Citation chain inherited at creation**: clients submit `CitationInput[]` (sourced from `/retrieval/search`) when creating goals or tasks; these are persisted as `ExecutionCitation` rows (polymorphic `target_type`/`target_id`).
- **`GET /goals/{id}/why` / `GET /tasks/{id}/why`**: return pre-stored citations — no live retrieval, deterministic, auditable.
- **Status changes audited via shared `AuditEvent` table**: every `update_status()` call appends `{action: "goal.status_change", prior_state: {status: ...}, new_state: {status: ...}}`.
- **Cycle-safe task dependencies**: `add_dependency()` runs BFS before inserting an edge; raises `DependencyCycleError` if the edge would close a cycle.

### Reflection + lesson register pattern (P6)
`RetrospectiveService`, `LessonService`, `PatternExtractor` form the reflection domain (ADR-008):
- **Synchronous retrospective runs**: `POST /retrospectives` creates a `Retrospective` row (status=`running`), queries completed goals/tasks in scope, calls `PatternExtractor` (LLM-backed, offline-first via Ollama), creates `Lesson` rows, then transitions status to `completed`. Async cadence deferred to P8.
- **`LessonEvidence` as a separate table**: evidence for lessons is coarser than retrieval chunks — it stores whole goal/task pointers + a human-readable summary of why the item supports the claim. Not reusing `ExecutionCitation` (different semantic).
- **Lesson supersession**: a new lesson that replaces an old one sets `supersedes_id = old_lesson_id`; the old lesson's status transitions to `superseded`. The transition is recorded in `AuditEvent` (same shared table used by P5 status changes).
- **LLM malformation is tolerated**: if the LLM returns malformed JSON or an empty array, the retrospective completes with 0 lessons — the caller can always create lessons manually via `POST /lessons`.
- **Reflection runs are themselves citable**: every `Lesson` carries `retrospective_id`; clients can trace a lesson back to the run that generated it and thence to the execution history.

### RBAC + tenancy pattern (P7)
`packages/identity/` exposes TenantService, UserService, TokenService, OIDCService (ADR-009):
- **Isolation boundary**: `tenant_id UUID` column (nullable) on all data tables. Service `list_*` methods accept `tenant_id: UUID | None`; when provided, only that tenant's records are returned.
- **Authentication**: `GET /auth/login` → OIDC authorization URL; `POST /auth/callback` exchanges code for a local HS256 JWT. Dev bypass: `ECI_IDENTITY_AUTH_DISABLED=true` injects a fixed dev context (offline-first, AP-3).
- **RBAC roles**: `admin > member > viewer`. Enforced at API boundary via `require_write` / `require_admin` FastAPI dependencies. Deny events increment `eci_auth_denied_total{reason}` counter and emit structured log lines.
- **Retrieval per-source filtering**: `RetrievalRequest.tenant_id` is threaded into FTSService and VectorService SQL queries (`AND tenant_id = :tenant_id`) when set. Citations returned only from the caller's tenant corpus.
- **Audit actor**: `RequestContext.actor` (email from JWT) is available for wiring into AuditEvent in P8.

### Release pattern (P8)
Every release candidate must pass before promotion to staging or production:
1. **Eval gate** (`scripts/eval_gate.py`) — all eval contract files present; corpus benchmarks pass when corpus available.
2. **Dependency scan** (`pip-audit`) — no HIGH/CRITICAL CVEs in the dependency tree.
3. **SAST** (`bandit -ll`) — no medium+ severity findings in `apps/` or `packages/`.
4. **Container scan** (`trivy`) — no CRITICAL/HIGH CVEs in the production Docker image.
5. **Docker image** built and pushed to GHCR; image digest recorded in the release artifact.
6. **Deploy** gated by a GitHub `staging` environment (required reviewers).

SLOs measured continuously via Prometheus + Grafana (`infra/grafana/dashboards/eci-slo.json`).
Alerts fire on burn-rate violations (`infra/prometheus/alerts/eci.yml`) → Alertmanager.

## Patterns Deferred to Later Phases
- LLM-runtime abstraction → Phase 3 ✅ (done).
- Hybrid retrieval + citation pattern → Phase 4 ✅ (done).
- Execution + traceability pattern → Phase 5 ✅ (done).
- Reflection + lesson register pattern → Phase 6 ✅ (done).
- RBAC + tenancy pattern → Phase 7 ✅ (done).
- Release pattern (eval-gated, SLO-monitored) → Phase 8 ✅ (done).
