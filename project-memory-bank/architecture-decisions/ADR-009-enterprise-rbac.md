# ADR-009 — Enterprise: RBAC, Multi-Tenancy, and OIDC SSO

- **Status:** Accepted
- **Date:** 2026-05-31
- **Deciders:** Project lead
- **Phase:** P7

## Context
ECI served a single implicit user through Phases 1–6. Phase 7 introduces multi-user, multi-tenant operation: team workspaces, OIDC-based authentication, and role-based access control (RBAC) at the API boundary.

Four decisions are ratified here. Each is independently necessary for the P7 exit criteria.

## Decision 1 — Identity model: Tenant + User with role column

**Tenant** (workspace) is the isolation boundary: data stored by Tenant A is never readable by Tenant B. A **User** belongs to exactly one Tenant and carries a **role** column (`admin`, `member`, `viewer`). This is the simplest role model that satisfies the P7 exit criteria without adding a separate RBAC rules table.

**Alternatives considered:**
- Resource-level permissions table: rejected for P7; adds complexity without a demonstrated need.
- Multi-tenant role-per-resource: deferred; revisit if P8 requires fine-grained document ACLs.

## Decision 2 — Tenant isolation via tenant_id column on all data tables

Every data-bearing table (documents, notes, goals, tasks, roadmaps, memory_entries, chunk_embeddings, retrospectives, lessons) receives a nullable `tenant_id UUID` column. Nullable to preserve backward compatibility with P1–P6 data; application-layer enforcement ensures new writes always carry a tenant_id. Service-layer list methods accept an optional `tenant_id` filter; when provided, only that tenant's records are returned.

**Alternatives considered:**
- Postgres Row-Level Security (RLS): more automatic, but adds operational complexity (SET SESSION, connection pooling caveats). Deferred to P8 if needed.
- Separate databases per tenant: rejected; too expensive operationally.

## Decision 3 — JWT-based auth with OIDC; local HS256 token as session token

Authentication flow:
1. Client calls `GET /auth/login` → backend returns OIDC authorization URL.
2. User authenticates at OIDC provider; provider redirects to `POST /auth/callback` with code + tenant_id.
3. Backend exchanges code for OIDC ID token (RS256), validates it, finds/creates the User record, issues a short-lived local HS256 JWT.
4. Client uses the local JWT as a Bearer token on all subsequent requests.

**Why local JWT instead of forwarding the OIDC JWT?**
- Avoids dependency on OIDC provider JWKS endpoint on every request (offline-first, AP-3).
- Allows embedding ECI-specific claims (tenant_id, role) without relying on OIDC claims.
- Local token can be invalidated by rotating the secret without touching the OIDC provider.

**Dev bypass**: when `ECI_IDENTITY_AUTH_DISABLED=true`, the auth dependency returns a fixed dev context. No OIDC provider needed for local development or integration tests.

## Decision 4 — RBAC enforced at API boundary; denies logged and metered

The auth dependency (`get_request_context`) is injected into every router endpoint. Write paths use `require_write` (minimum role: `member`). Admin-only paths use `require_admin`. Deny events increment `eci_auth_denied_total{reason}` counter and emit a structured log line — observable without touching audit tables.

## Consequences

**Positive.**
- Single OIDC provider wired end-to-end satisfies P7 exit criteria; more providers are config-only changes.
- Nullable `tenant_id` means P1–P6 integration tests continue to pass without modification.
- Local JWT and the dev bypass make the system offline-capable (AP-3) even after auth is wired.

**Negative.**
- `tenant_id` denormalized into every table: orphan rows remain if a tenant is deleted (mitigated by nullable FK; accepted for P7).
- Short-lived HS256 tokens require secret rotation to revoke; no per-token revocation list in P7. Acceptable for initial enterprise rollout.
- OIDC exchange requires a network call to the provider; mitigated by the dev bypass for offline scenarios.

## Compliance
A reviewer can verify by:
1. Every list endpoint in integration tests accepts a `tenant_id` filter and returns only matching records.
2. `eci_auth_denied_total` counter increments on RBAC deny (verified by `test_rbac.py`).
3. `POST /users` with a `viewer` token returns 403 (verified by isolation tests).
4. Tenant A's documents are not returned in Tenant B's retrieval results (isolation tests).
