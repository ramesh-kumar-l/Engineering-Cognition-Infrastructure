# Engineering Cognition Infrastructure (ECI)

> **Memory is the product.** ECI is a self-hosted, AI-powered second brain for engineering teams — capturing knowledge, compressing it with LLMs, making it retrievable with citations, and turning it into traceable execution.

[![CI](https://github.com/ramesh152/engineering-cognition-infrastructure/actions/workflows/ci.yml/badge.svg)](https://github.com/ramesh152/engineering-cognition-infrastructure/actions/workflows/ci.yml)
[![Security Scan](https://github.com/ramesh152/engineering-cognition-infrastructure/actions/workflows/security.yml/badge.svg)](https://github.com/ramesh152/engineering-cognition-infrastructure/actions/workflows/security.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What is ECI?

ECI solves a problem every engineering team faces: **knowledge that lives only in people's heads, Slack threads, and stale wikis**. When an engineer leaves, a post-mortem ages, or a decision gets revisited six months later, the institutional memory is gone.

ECI is an infrastructure layer that:

1. **Captures** documents, notes, PDFs, and Markdown with full provenance into a content-addressed store.
2. **Compresses** raw content into summaries, mental models, and playbooks via a swappable LLM runtime (Ollama offline by default; OpenAI/Anthropic as optional upgrades).
3. **Retrieves** knowledge via hybrid search (Postgres full-text + pgvector HNSW) with mandatory source citations — **no answer without provenance**.
4. **Executes** — Goals, tasks, and roadmaps are created from retrieval results and inherit the citation chain that justifies them.
5. **Reflects** — Periodic retrospectives extract structured lessons from execution history, building compounding institutional memory.
6. **Governs** — Multi-tenant RBAC, OIDC SSO, and per-tenant retrieval isolation for enterprise teams.
7. **Operates** — SLO monitoring, Grafana dashboards, Prometheus alerts, eval-gated releases, and a DR runbook.

**Status: All 8 phases complete. GA-ready as of 2026-05-31.**

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ECI System                                  │
│                                                                     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌─────────────────┐  │
│  │Ingestion │──▶│Compression│──▶│ Retrieval│──▶│   Execution     │  │
│  │  P2      │   │  P3 (LLM)│   │ P4 (FTS  │   │   P5 (Goals/    │  │
│  │          │   │          │   │+pgvector │   │   Tasks/        │  │
│  │Documents │   │Summaries │   │+RRF)     │   │   Roadmaps)     │  │
│  │Notes     │   │Mental    │   │          │   │                 │  │
│  │PDFs      │   │Models    │   │Citations │   │ Citation chain  │  │
│  └──────────┘   └──────────┘   └──────────┘   └───────┬─────────┘  │
│                                                         │            │
│  ┌──────────────────────┐   ┌───────────────────────────▼─────────┐ │
│  │   Identity (P7)      │   │   Reflection Engine (P6)            │ │
│  │   RBAC / OIDC / JWT  │   │   Retrospectives → Lessons          │ │
│  │   Multi-tenancy      │   │   Pattern extraction (LLM)          │ │
│  └──────────────────────┘   └─────────────────────────────────────┘ │
│                                                                     │
│  ─────────────────── Cross-cutting ─────────────────────────────   │
│  OpenTelemetry · Prometheus · Structlog · Langfuse · Alembic        │
└─────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI 0.115, Pydantic v2, Uvicorn |
| ORM + Migrations | SQLAlchemy 2 (sync), Alembic |
| Database | PostgreSQL 16 + pgvector (HNSW + GIN FTS) |
| LLM Runtime | Ollama (offline default) · OpenAI · Anthropic · OpenRouter |
| Embeddings | `nomic-embed-text` via Ollama, 768-dim HNSW cosine |
| Retrieval | BM25 (Postgres `websearch_to_tsquery`) + pgvector ANN + RRF |
| Identity | OIDC + local HS256 JWT (`python-jose`) |
| Observability | OpenTelemetry, Prometheus, Structlog, Langfuse |
| Dashboards | Grafana 11, Alertmanager |
| CI/CD | GitHub Actions (lint · type · test · security · release) |
| Packaging | `uv` workspace monorepo, `hatchling` per-package builds |
| Container | Docker multi-stage, non-root hardened, GHCR published |
| Blob Storage | Local filesystem (dev) · S3/MinIO (production) |

---

## Repository Layout

```
.
├── apps/
│   └── api/                  # FastAPI application (eci-api)
├── packages/
│   ├── observability/        # OTel + Prometheus + Structlog + Langfuse
│   ├── storage/              # SQLAlchemy models + Alembic migrations
│   ├── ingest/               # Document/note ingestion + BlobStore
│   ├── llm/                  # LLM provider Protocol + adapters
│   ├── compression/          # Summarization + mental-model + playbook
│   ├── retrieval/            # Hybrid retrieval + citation engine + memory
│   ├── execution/            # Goals, tasks, roadmaps, audit log
│   ├── reflection/           # Retrospectives + lesson register
│   └── identity/             # Tenants, users, RBAC, OIDC, JWT
├── infra/
│   ├── docker/               # Dockerfiles + compose files
│   ├── prometheus/           # Scrape config + 6 alert rules
│   ├── alertmanager/         # Routing + inhibit rules
│   └── grafana/              # Auto-provisioned SLO dashboard
├── scripts/
│   └── eval_gate.py          # Release-blocking eval contract checker
├── project-memory-bank/      # Living architecture record
│   ├── architecture-decisions/   # ADR-001 through ADR-010
│   ├── evaluations/          # Eval contracts + thresholds
│   ├── slos/                 # SLO definitions + error budget policy
│   ├── runbooks/             # Disaster recovery runbook
│   └── risk-register/        # Living risk register
├── docs/                     # MkDocs Material documentation source
├── pyproject.toml            # Workspace root + dev dependencies
├── requirements.txt          # Flat pip-compatible requirements
├── requirements-dev.txt      # Dev + CI tools
├── requirements-llm-cloud.txt # Optional cloud LLM provider extras
└── .github/workflows/        # ci.yml · security.yml · release.yml
```

---

## Quick Start

See **[QuickStarterGuide.md](QuickStarterGuide.md)** for full step-by-step instructions.

**TL;DR (5 commands):**

```bash
uv sync --all-packages
docker compose -f infra/docker/docker-compose.yml up -d postgres
cp .env.example .env  # set ECI_DB_URL; ECI_IDENTITY_AUTH_DISABLED=true
uv run alembic -c packages/storage/alembic.ini upgrade head
uv run uvicorn eci_api.main:app --reload --port 8000
# → http://localhost:8000/docs
```

---

## API Reference

Interactive documentation: `http://localhost:8000/docs`

### Ingestion

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/documents` | Ingest a document (multipart file + metadata) |
| `POST` | `/notes` | Ingest a short-form note (JSON) |

### Compression

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/compress/documents/{id}` | Compress → 3 summary levels + mental model |
| `GET` | `/compress/documents/{id}/summaries` | Retrieve summaries |
| `GET` | `/compress/documents/{id}/mental-model` | Retrieve mental model |

### Retrieval

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/retrieval/embed/documents/{id}` | Chunk + embed into vector index |
| `POST` | `/retrieval/search` | Hybrid search with mandatory citations |
| `POST` | `/memory/entries` | Create curated memory entry |
| `POST` | `/memory/search` | Search memory entries |

### Execution

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/goals` | Create goal (with citation chain) |
| `PATCH` | `/goals/{id}` | Update status (audited) |
| `GET` | `/goals/{id}/why` | Citations justifying this goal |
| `POST` | `/tasks` | Create task |
| `POST` | `/tasks/{id}/dependencies` | Add dependency (BFS cycle-checked) |
| `GET` | `/tasks/{id}/why` | Citations justifying this task |

### Reflection

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/retrospectives` | Run retrospective (LLM pattern extraction) |
| `POST` | `/lessons` | Create lesson manually |
| `POST` | `/lessons/{id}/supersede` | Supersede a lesson (audited) |

### Identity

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/auth/login` | OIDC authorization URL |
| `POST` | `/auth/callback` | Exchange code → local JWT |
| `POST` | `/tenants` | Create tenant (admin only) |
| `PATCH` | `/users/{id}/role` | Change user role (admin only) |

### System

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/healthz` | Liveness check |
| `GET` | `/readyz` | Readiness check |
| `GET` | `/metrics` | Prometheus metrics |

---

## LLM Provider Configuration

Switching providers is a one-env-var change — no code edits:

```dotenv
# Ollama offline (default)
ECI_LLM_PROVIDER=ollama
ECI_LLM_OLLAMA_HOST=http://localhost:11434
ECI_LLM_MODEL=llama3.2

# OpenAI
ECI_LLM_PROVIDER=openai
ECI_LLM_API_KEY=sk-...
ECI_LLM_MODEL=gpt-4o-mini

# Anthropic
ECI_LLM_PROVIDER=anthropic
ECI_LLM_API_KEY=sk-ant-...
ECI_LLM_MODEL=claude-haiku-4-5-20251001
```

Install cloud extras: `pip install -r requirements-llm-cloud.txt`

---

## Running Tests

```bash
# Unit tests (no external dependencies)
uv run pytest -m "not integration and not llm_integration"

# Integration tests (requires Postgres)
ECI_TEST_DB_URL=postgresql+psycopg://eci:eci@localhost:5432/eci_test \
  uv run pytest -m integration -v

# Full suite with LLM (requires Ollama)
ECI_TEST_DB_URL=... ECI_LLM_OLLAMA_HOST=http://localhost:11434 \
  uv run pytest -v
```

---

## CI/CD

| Workflow | Trigger | Gates |
|----------|---------|-------|
| `ci.yml` | Every push/PR | ruff · mypy · pytest · mkdocs · smoke |
| `security.yml` | PRs + weekly | pip-audit · bandit · trufflehog · trivy |
| `release.yml` | `v*` tags | eval gate · dep scan · Docker → GHCR · staging deploy |

---

## Observability & SLOs

| SLO | Target | Alert Rule |
|-----|--------|------------|
| Availability | ≥ 99.5% | `ECILowAvailability` (critical) |
| Latency p95 | ≤ 500 ms | `ECIHighLatencyP95` (warning) |
| Latency p99 | ≤ 1500 ms | `ECIHighLatencyP99` (critical) |
| Citation coverage | 100% | Eval gate blocks release |
| Retrieval Recall@5 | ≥ 0.70 | Eval gate blocks release |

Start the full observability stack:

```bash
docker compose -f infra/docker/docker-compose.prod.yml up -d
# Grafana → http://localhost:3000  (admin/admin)
# Prometheus → http://localhost:9090
```

The production compose build keeps `eci-api` as the canonical image and also tags the same build as `docker-ingestion-api` for legacy compatibility. Treat `docker-ingestion-api` as deprecated and migrate future automation to `eci-api`.

---

## Production Deployment

```bash
export POSTGRES_PASSWORD=<strong>
export ECI_JWT_SECRET=<32-char-random>
export GRAFANA_ADMIN_PASSWORD=<password>

docker compose -f infra/docker/docker-compose.prod.yml up -d
```

`POSTGRES_PASSWORD` and `ECI_JWT_SECRET` are now required inputs. Compose will fail fast if either is missing instead of starting an unhealthy stack with blank secrets.
If any of the default host ports are already taken, override `ECI_API_PORT`, `ECI_PROMETHEUS_HOST_PORT`, `ECI_ALERTMANAGER_PORT`, or `ECI_GRAFANA_PORT` before `docker compose up`.

For Kubernetes, use the GHCR image: `ghcr.io/<org>/eci-api:<version>`

DR runbook: [`project-memory-bank/runbooks/disaster-recovery.md`](project-memory-bank/runbooks/disaster-recovery.md)  
RTO: 2 hours · RPO: 24 hours

---

## Architecture Decisions

| ADR | Decision |
|-----|---------|
| ADR-001 | Charter ratification |
| ADR-002 | Technology stack |
| ADR-003 | Repository and branching layout |
| ADR-004 | Storage layout (raw blobs + parsed records) |
| ADR-005 | LLM runtime abstraction (provider Protocol + factory) |
| ADR-006 | Retrieval strategy (RRF over neural reranker, offline-first) |
| ADR-007 | Execution intelligence model |
| ADR-008 | Reflection engine domain model |
| ADR-009 | Enterprise RBAC, multi-tenancy, OIDC SSO |
| ADR-010 | Production hardening (S3, security CI, eval gate, SLOs, DR) |

Full ADR log: [`project-memory-bank/architecture-decisions/`](project-memory-bank/architecture-decisions/)

---

## Contributing

1. Read the charter ([ADR-001](project-memory-bank/architecture-decisions/ADR-001-charter-ratification.md)) and coding patterns ([system-patterns.md](project-memory-bank/system-patterns.md)).
2. **300-line file limit** — hard limit; split files before adding.
3. Integration tests must hit a **real Postgres** — no database mocks.
4. Every PR must reference the ADR or phase exit criterion it implements.
5. Pre-push: `uv run ruff check . && uv run mypy . && uv run pytest -m "not integration"`

---

## Documentation

```bash
uv run mkdocs serve   # → http://localhost:8001
```

---

## License

MIT. See [LICENSE](LICENSE).

---

*Built on six architectural principles — AP-3 above all: cloud-enhanced, never cloud-dependent.*
