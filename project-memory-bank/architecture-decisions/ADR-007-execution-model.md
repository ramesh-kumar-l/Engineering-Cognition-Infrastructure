# ADR-007 — Execution Intelligence Model

**Status:** Accepted
**Date:** 2026-05-31
**Deciders:** Engineering Cognition Infrastructure team

## Context

Phase 5 introduces execution intelligence: Goals, Tasks, and Roadmaps that trace back to the source memory that justified them. The key design tension is between normalisation (FK-enforced links) and flexibility (polymorphic citation targets). A secondary concern is audit trail completeness — every status change must be recorded with prior and new state.

## Decisions

### 1. Domain model hierarchy

`Roadmap → Goal → Task`, with one-to-many relationships at each level. A Task can also exist without a Goal (free-standing). A Goal can exist without a Roadmap. This is deliberately loose: forcing every task into a goal would make the model unusable during exploratory phases.

### 2. Status stored as VARCHAR(32), validated in service layer

SQLAlchemy native Enum types create a Postgres `ENUM` type that is painful to migrate (ALTER TYPE ADD VALUE requires a new transaction). Storing status as a plain `VARCHAR(32)` and enforcing the valid-value set in Python keeps migrations clean. The set of valid statuses is: `pending`, `in_progress`, `completed`, `blocked`, `cancelled`.

### 3. Citation linkage via `ExecutionCitation` table (polymorphic, no FK on target_id)

Goals and Tasks each accumulate `ExecutionCitation` rows that store the citation data at write time. The `target_type` + `target_id` columns are polymorphic (no FK constraint on `target_id`) — this avoids a two-column nullable FK pattern and makes the citation table queryable across entity types. Trade-off: referential integrity is enforced at the application layer, not the DB.

Citations are submitted by the client at creation time, sourced from a prior `/retrieval/search` or `/memory/search` response. This avoids coupling the execution service to the retrieval system and keeps each service independently deployable.

### 4. Status-change audit via the existing `AuditEvent` table

Phase 2 already provides `AuditEvent` with `actor`, `action`, `target_type`, `target_id`, `prior_state`, `new_state`, `reason`. Re-using this table for execution status changes avoids a second audit log and keeps all write-path auditing in one queryable location. The `actor` field defaults to `"system"` until P7 adds real auth.

### 5. Task dependency edges as a separate `task_dependencies` association table

Many-to-many self-referential. A simple BFS cycle check is run before inserting any edge — `DependencyCycleError` is raised if the edge would create a cycle. Cycle detection is sufficient for P5 corpus sizes; if graphs grow into the thousands of nodes, replace with a topological-sort-based check in P6/P7.

## Alternatives Rejected

| Option | Reason rejected |
|--------|----------------|
| Native Postgres ENUM for status | ALTER TYPE ADD VALUE is non-transactional in PG; painful in Alembic |
| FK on `execution_citations.target_id` | Would require two nullable FK columns (goal_id, task_id) duplicating the ChunkEmbedding pattern; polymorphic join is cleaner |
| Separate audit table per entity | Fragments queryability; existing AuditEvent already captures the required fields |
| Recursive CTE for cycle detection | Overkill for P5; BFS over in-memory edges is O(V+E) and adequate |

## Consequences

- Migrations stay clean; status changes do not require schema migrations.
- The `why` endpoint (`GET /goals/{id}/why`) returns pre-stored citations — no live retrieval at query time, deterministic and fast.
- Multi-user actor identity (`actor != "system"`) is wired in P7 without schema changes.
- See [[ADR-004]] for storage layout; [[ADR-006]] for citation chain from P4.
