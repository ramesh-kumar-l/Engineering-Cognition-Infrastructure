# Reflection Quality Evaluation

Phase 6 exit criterion. Records the metrics and thresholds used to accept the reflection engine.

## Metrics

| Metric | Definition | Acceptance Threshold |
|---|---|---|
| **Lesson yield** | Lessons generated per retrospective run on the held-out corpus | ≥ 1 lesson per run |
| **Evidence coverage** | % of generated lessons that carry ≥ 1 piece of evidence | 100% |
| **Citation traceability** | % of evidence items whose `source_id` resolves to an existing goal/task | ≥ 95% |
| **Supersession integrity** | Old lesson status = `superseded` after a supersession call | 100% (enforced by test) |
| **Audit completeness** | Every supersession has a corresponding `AuditEvent` row | 100% (enforced by test) |

## Evaluation corpus

- Held-out set: 5 completed goals and 12 completed tasks from the integration test fixture corpus.
- Cadences exercised: `weekly`, `monthly`, `milestone` — all three must produce ≥ 1 lesson on this corpus.
- Scope modes exercised: `global` (no scope filter), `goal`-scoped, `roadmap`-scoped.

## Run conditions

- Provider: stub LLM for integration test CI.
- Provider: Ollama (`nomic-embed-text` / `llama3` family) for the baseline run. Results appended below once first Ollama run is completed.

## Baseline run

*(Pending first Ollama run — to be populated before Phase 7 begins.)*

| Date | Provider | Corpus size | Lessons generated | Evidence coverage | Notes |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

## Known limitations

- LLM hallucination risk: a generated lesson claim may not match the evidence. Mitigated by requiring human review of auto-generated lessons before acting on them (trustworthiness: overridable).
- Empty-corpus runs: when no completed goals/tasks exist, the retrospective completes with 0 lessons (by design — not a failure). Monitored via `lesson_count = 0` sentinel.
