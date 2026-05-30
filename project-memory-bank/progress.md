# Progress

Reverse-chronological log of completed work, milestones, and lessons. New entries go on top. Lessons feed back into [system-patterns.md](system-patterns.md) when they generalize.

---

## 2026-05-30 — Phase 1 Foundation complete

**Completed.**
- Memory bank populated: `projectbrief.md`, `product-context.md`, `system-patterns.md`, `tech-context.md`, `active-context.md`, `progress.md`, `implementation-status.md`.
- Memory bank subdirectories created: `architecture-decisions/`, `research/`, `evaluations/`, `roadmaps/`, `risk-register/`.
- ADR-001 (charter ratification), ADR-002 (technology stack), ADR-003 (repo + branching) ratified.
- Repo skeleton: `apps/`, `packages/`, `infra/`, `docs/`, `scripts/`.
- Observability package (`packages/observability/`) wired with OpenTelemetry tracing, Prometheus metrics, structlog logging, and a Langfuse client stub. Console exporters as default; OTLP/Langfuse activated via env.
- FastAPI stub (`apps/api/`) exposes `/healthz`, `/readyz`, and `/metrics`. One root span + one counter increment + one structured log per request.
- `make smoke` produces a trace, a metric, and a log — proves end-to-end wiring without external infrastructure.
- MkDocs Material site renders the memory bank (`mkdocs build --strict` clean).
- GitHub Actions CI workflow committed: lint (`ruff`), type-check (`mypy`), test (`pytest`), docs build (`mkdocs build --strict`).
- Initial risk register seeded with R-001 (cloud LLM availability) and R-002 (Ollama hardware).

**Milestone:** Phase 1 exit criteria met — see [implementation-status.md](implementation-status.md). Phase 2 (Knowledge Capture) unblocked.

**Lessons learned (carried into later phases).**
- The 300-line file limit is enforced *as the package is being built*, not retroactively. Each observability subsystem became its own file from day one rather than waiting for `observability.py` to grow large.
- Default-on observability with **console exporters** lets the smoke target prove wiring without a running collector. This pattern (`local: console exporter; prod: OTLP env-configured`) carries forward.
- The memory bank is most useful when it is small and links to the source of truth (ADRs, roadmap) rather than duplicating it. Avoid rewriting charter content into multiple files.

---

## 2026-05-30 — Roadmap ratified

- ECI charter (system prompt) accepted as-is.
- Master roadmap (P1–P8) written to [roadmaps/master-roadmap.md](roadmaps/master-roadmap.md). Per-phase exit criteria, dependencies, and quality gates defined.
- Decisions explicitly deferred: Postgres/pgvector versions, embedding model, reranker, SSO provider, deployment-target ordering, evaluation thresholds, LLM cost ceiling. Each lives in the phase that owns it.

---

## Initial — Repository created

- `git init`, `LICENSE`, one-line `README.md` on branch `develop`. No project structure yet.
