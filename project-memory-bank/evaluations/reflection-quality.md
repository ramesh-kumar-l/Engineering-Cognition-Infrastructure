# Reflection Quality — Phase 6

> Source of truth for Phase 6 reflection acceptance.
> A phase cannot exit until the thresholds below are met on the integration test corpus.

## Metrics and Thresholds

| Metric | Threshold | Notes |
|--------|-----------|-------|
| Lesson creation rate | ≥ 1 lesson per retrospective run | On any corpus with ≥ 1 completed goal/task |
| Evidence coverage | ≥ 1 evidence item per lesson | Every lesson must link to a completed execution item |
| Supersession audit rate | 100% | Every supersession must produce an AuditEvent |
| LLM malformation tolerance | 100% | Retrospective completes (status=completed) even on empty/invalid JSON |
| Lesson–retrospective traceability | 100% | Every lesson carries a non-null `retrospective_id` |
| Manual lesson creation | 100% | `POST /lessons` creates a lesson without a retrospective run |

## Evaluation Protocol

**Corpus:** Minimum 5 completed goals + 5 completed tasks in the integration DB.

**Runner:** Integration test suite in `packages/reflection/tests/` (`@pytest.mark.integration`).
The 17 integration tests cover all metrics above.

**LLM requirement:** Tests use a stub LLM (no Ollama required). Real LLM quality
evaluation is deferred to the Ollama CI environment.

## Baseline Run

**Status:** Integration tests passing (stub LLM). Ollama run deferred.

| Date | Lesson rate | Evidence coverage | Supersession audit | Notes |
|------|-------------|-------------------|--------------------|-------|
| 2026-05-31 | ✅ ≥ 1 (stub) | ✅ 100% | ✅ 100% | Stub LLM; real quality TBD |

## Trustworthiness Checklist

- [x] **Verifiable** — every `Lesson` carries `retrospective_id` + evidence list.
- [x] **Auditable** — supersession events are in the shared `AuditEvent` table.
- [x] **Overridable** — lessons can be created manually; stub LLM gracefully handled.
- [x] **Traceable** — `LessonEvidence` links to source `Goal` / `Task` / `MemoryEntry`.
- [x] **Explainable** — lessons carry `claim` + `evidence_summary` fields.

## Real LLM Quality (to be completed)

When Ollama is available in CI (`@pytest.mark.llm_integration`):
- Claim precision: fraction of claims that accurately reflect the supporting evidence.
- Claim recall: fraction of significant patterns captured across the retrospective window.
- Target: precision ≥ 0.70, recall ≥ 0.50 (to be tightened after first real run).
