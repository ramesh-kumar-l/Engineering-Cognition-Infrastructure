# Engineering Cognition Infrastructure (ECI)

A trustworthy, production-grade engineering memory.

> Trust over magic. Evidence over confidence. Offline-first, cloud-enhanced.

## Status
- **Phase 1 — Foundation** ✅
- **Phase 2 — Knowledge Capture** ✅
- **Phase 3 — Knowledge Compression** ⬜ (next)

See [`project-memory-bank/implementation-status.md`](project-memory-bank/implementation-status.md) for the full checklist, [`project-memory-bank/active-context.md`](project-memory-bank/active-context.md) for the current save state, and [`project-memory-bank/roadmaps/master-roadmap.md`](project-memory-bank/roadmaps/master-roadmap.md) for the eight phases.

## Quick start

```bash
make install          # uv sync workspace
make ci-local         # lint + type + unit + docs + smoke
make db-up            # start Postgres (docker compose)
make db-migrate       # alembic upgrade head
make test-integration # real-Postgres tests
uv run uvicorn eci_api.main:app --reload  # serve the API
```

## Layout

```
apps/api/                    FastAPI backend (P1+)
packages/observability/      OTel + Prometheus + structlog + Langfuse (P1)
packages/storage/            SQLAlchemy models + Alembic (P2)
packages/ingest/             Hashing, blob store, parsers, services (P2)
infra/docker/                Dockerfile (api) + docker-compose (postgres)
docs/                        MkDocs Material site
project-memory-bank/         Source of truth: charter, roadmap, ADRs, risks, evals
.github/workflows/ci.yml     CI: lint, type, test, docs, smoke + integration lane
```

## Governance
- Charter is ratified in [ADR-001](project-memory-bank/architecture-decisions/ADR-001-charter-ratification.md). One phase at a time.
- Every architecturally meaningful change ships with an ADR **before** code (RULE 5).
- Files stay ≤ 300 lines (ADR-003).
- Memory bank is updated at every major-feature boundary.
