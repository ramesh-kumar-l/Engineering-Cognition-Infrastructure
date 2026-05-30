# Architecture Decision Records

Every architecturally meaningful decision (storage, runtime, retrieval, auth, deployment, observability) is recorded here **before code is written**. Charter RULE 5.

## Status values
- **Proposed** — drafted, not yet ratified.
- **Accepted** — ratified; binding.
- **Superseded by ADR-NNN** — replaced; keep file for history.
- **Rejected** — considered, not chosen; keep file for history.
- **Deprecated** — no longer applies; not yet replaced.

## Index
| ADR | Title | Status |
|---|---|---|
| [ADR-001](ADR-001-charter-ratification.md) | Charter ratification | Accepted |
| [ADR-002](ADR-002-technology-stack.md) | Technology stack | Accepted |
| [ADR-003](ADR-003-repo-and-branching.md) | Repository layout and branching | Accepted |

## Template
Copy `_template.md` (below). One ADR per decision. Filename: `ADR-NNN-short-kebab-title.md`.

```markdown
# ADR-NNN — <title>

- **Status:** Proposed | Accepted | Superseded by ADR-NNN | Rejected | Deprecated
- **Date:** YYYY-MM-DD
- **Deciders:** <names>
- **Phase:** P<N>

## Context
What problem are we solving? What forces are at play?

## Decision
What we will do. State it as a directive.

## Consequences
Positive, negative, and neutral. What becomes easier? What becomes harder? What is now off the table?

## Alternatives Considered
For each: what it was, why we did not choose it.

## Compliance
How a reviewer (human or agent) can verify this decision is being followed.
```
