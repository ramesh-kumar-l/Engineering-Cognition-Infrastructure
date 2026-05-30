# ADR-003 — Repository Layout and Branching

- **Status:** Accepted
- **Date:** 2026-05-30
- **Deciders:** Project lead
- **Phase:** P1

## Context
The repository must support a multi-language, multi-service product over multiple years without devolving into a tangle of services and one-off scripts. The charter calls for composable modules (AP-5) and long-term ownership (AP-6).

## Decision

### Layout — single repository, workspace-organized
```
.
├── apps/                  # Deployable applications
│   ├── api/               # FastAPI backend (P1+)
│   └── web/               # React frontend (P4+)
├── packages/              # Reusable libraries imported by apps
│   ├── observability/     # Tracing, metrics, logging, Langfuse (P1)
│   ├── storage/           # SQLAlchemy models, migrations (P2)
│   ├── ingest/            # Ingestion pipeline (P2)
│   ├── compression/       # Summarization, mental models (P3)
│   ├── retrieval/         # Hybrid retrieval + citation (P4)
│   ├── execution/         # Goals, tasks, roadmaps (P5)
│   ├── reflection/        # Lessons, retrospectives (P6)
│   └── auth/              # RBAC, audit (P7)
├── infra/                 # Deployment artifacts
│   ├── docker/            # Per-app Dockerfiles
│   └── k8s/               # Manifests (P8)
├── docs/                  # MkDocs site (mounts project-memory-bank/)
├── project-memory-bank/   # The bank — source of truth for context (RULE 1)
├── scripts/               # Operational scripts (smoke, db utilities, etc.)
├── .github/workflows/     # CI definitions
├── Makefile               # Single entry point: install, lint, test, smoke, docs, ci-local
└── pyproject.toml         # uv workspace root
```

Packages and apps are not created until their phase begins (RULE 4). The directories above declare the *intended* layout so contributors know where new code goes.

### Modularity contract
- **One file ≤ 300 lines.** Split by domain; never by line count alone.
- **One responsibility per module.** `goal_service.py`, not `services.py`.
- **Public surface declared in `__init__.py`.** Anything not re-exported is private to the package.

### Branching
- **`main`** — protected; production-ready. Tagged for releases (P8+).
- **`develop`** — protected; integration branch for feature work. PRs target `develop`; CI must be green.
- **`feat/<phase>-<short-name>`** — feature branches off `develop`.
- **`fix/<short-name>`** — bug fixes; can target `develop` or `main` for hotfix.
- **`chore/<short-name>`** — non-functional work.

PRs require:
- Linked phase exit criterion or ADR.
- Green CI (lint, type-check, test, docs build).
- Memory bank update (`active-context.md`, `progress.md`, `implementation-status.md`) for any feature-shaped change.

### Commits
Conventional commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`). Commit subjects ≤ 72 chars; bodies explain *why*, not *what*.

## Consequences
**Positive.**
- A single repo lets memory bank, ADRs, code, and infra evolve together. No cross-repo drift.
- The package boundary is explicit; cross-package imports must go through the public `__init__.py`.
- The 300-line rule keeps individual files navigable to humans *and* to LLMs (low-token reads).

**Negative.**
- Monorepo CI must be careful about scope (later phases will introduce path-filtered jobs).
- The 300-line rule occasionally requires splitting cohesive code; accepted trade-off.

**Neutral.**
- `develop` as the integration branch is a deliberate choice over trunk-based; revisit at P8 if release cadence demands it.

## Alternatives Considered
- **Polyrepo (one per service).** Rejected: cross-cutting changes (e.g., observability contract update) become coordination problems; memory bank cannot live next to code.
- **Trunk-based with feature flags.** Rejected for now: we have no flag infrastructure yet; revisit P8.
- **No file-size limit.** Rejected: contradicts the modularity goal and the LLM-read-friendly principle.

## Compliance
A reviewer can verify by:
1. `git ls-files | xargs wc -l` reports no source file > 300 lines (CI check added in P8; warned in P1).
2. New packages appear under `packages/`, not buried in `apps/`.
3. Every PR references either an ADR or a phase exit criterion.
