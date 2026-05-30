# ADR-004 — Storage Layout for Captured Knowledge

- **Status:** Accepted
- **Date:** 2026-05-30
- **Deciders:** Project lead
- **Phase:** P2

## Context
Phase 2 introduces persistent state. Captured content has two distinct lifetimes:
1. **Raw bytes** — the original file as it was received. Immutable. Used for re-parse, audit, dispute resolution.
2. **Parsed records** — normalized representations (Documents, Notes) that downstream phases query.

We also need provenance, idempotent ingest, and a clean upgrade path to object storage (S3/MinIO) without rewriting code.

## Decision

### 1. Two stores, one source of truth per concern
- **Blob store** holds raw bytes, addressed by `content_hash` (sha256 hex).
  - Local/dev: filesystem at `ECI_BLOB_ROOT`, sharded by hash prefix: `<root>/<hash[:2]>/<hash[2:4]>/<hash>`.
  - Prod: pluggable `BlobStore` Protocol; S3-compatible adapter to be added by ADR in P8.
- **Postgres** holds metadata and parsed records: `raw_blobs`, `documents`, `notes`, `audit_events`.

### 2. Tables (P2)
- `raw_blobs(id UUID PK, content_hash TEXT UNIQUE, size_bytes BIGINT, content_type TEXT, created_at TIMESTAMPTZ)`
- `documents(id UUID PK, raw_blob_id UUID FK→raw_blobs.id, kind TEXT, title TEXT, body TEXT, source TEXT, author TEXT, tags TEXT[], metadata JSONB, captured_at TIMESTAMPTZ, ingested_at TIMESTAMPTZ, ingested_by TEXT)`
- `notes(id UUID PK, body TEXT, source TEXT, author TEXT, tags TEXT[], metadata JSONB, captured_at TIMESTAMPTZ, ingested_at TIMESTAMPTZ, ingested_by TEXT, content_hash TEXT UNIQUE)`
- `audit_events(id UUID PK, actor TEXT, action TEXT, target_type TEXT, target_id UUID, prior_state JSONB, new_state JSONB, reason TEXT, occurred_at TIMESTAMPTZ)`

### 3. Idempotency
- `raw_blobs.content_hash` is `UNIQUE`. Ingest performs `INSERT … ON CONFLICT (content_hash) DO NOTHING` then `SELECT`. Documents tied to a re-uploaded blob return the existing record. The audit log distinguishes `ingest.document.create` from `ingest.document.dedup`.
- For Notes (inline body, no blob), idempotency uses `notes.content_hash` computed from `sha256(body || source || author || captured_at)`.

### 4. Provenance
Every record carries `source`, `captured_at` (when the content was created at the origin), `ingested_at` (when ECI received it), and `ingested_by` (actor identity — stubbed as `"system"` until P7 RBAC).

### 5. Soft-delete / retention
Out of scope for P2. Audit events are the immutable record. Retention policy lives in a later ADR if it becomes needed.

### 6. Migrations
Alembic, single linear history. First migration is `0001_initial` creating the four tables. Schema changes require a new migration, never an edit to an existing one.

## Consequences
**Positive.**
- Raw bytes and parsed records evolve independently; re-parse with a new pipeline is trivial.
- `BlobStore` Protocol makes S3 adoption a one-file change.
- `UNIQUE(content_hash)` makes idempotency a database guarantee, not application bookkeeping.

**Negative.**
- Filesystem blob store is single-host; horizontal scaling requires the S3 adapter (P8).
- JSONB metadata is flexible but can hide schema drift. Mitigation: structured columns for the well-known fields; JSONB only for source-specific extras.

**Neutral.**
- No multi-tenancy fields yet (no `team_id`). P7 will add them via a follow-up ADR + migration.

## Alternatives Considered
- **Single `content` BYTEA column on documents** — rejected: bloats hot tables, defeats re-parse, no future S3 path.
- **Document DB (Mongo, etc.)** — rejected: contradicts ADR-002 stack and removes relational guarantees we need for audit + execution graphs.
- **Append-only event log only (no relational tables)** — rejected: P4 retrieval needs structured queries; pure event sourcing is premature.

## Compliance
A reviewer can verify by:
1. `raw_blobs.content_hash` has a `UNIQUE` constraint.
2. Re-ingesting identical bytes returns the original `document.id` and writes an `ingest.document.dedup` audit event.
3. No code under `packages/ingest/` references `boto3` or any cloud SDK — the `BlobStore` Protocol is the only seam.
