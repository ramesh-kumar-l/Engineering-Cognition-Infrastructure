"""enterprise: tenants, users, tenant_id columns on all data tables

Revision ID: 0006_enterprise
Revises: 0005_reflection
Create Date: 2026-05-31
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0006_enterprise"
down_revision: Union[str, None] = "0005_reflection"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE tenants (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(256) NOT NULL,
            slug VARCHAR(64) NOT NULL UNIQUE,
            status VARCHAR(16) NOT NULL DEFAULT 'active',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX ix_tenants_slug ON tenants(slug)")
    op.execute("CREATE INDEX ix_tenants_status ON tenants(status)")

    op.execute("""
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            email VARCHAR(256) NOT NULL,
            display_name VARCHAR(256),
            role VARCHAR(16) NOT NULL DEFAULT 'member',
            external_id VARCHAR(256),
            status VARCHAR(16) NOT NULL DEFAULT 'active',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX ix_users_tenant_id ON users(tenant_id)")
    op.execute("CREATE INDEX ix_users_email ON users(email)")
    op.execute("CREATE INDEX ix_users_external_id ON users(external_id)")
    op.execute("CREATE INDEX ix_users_status ON users(status)")

    # Add nullable tenant_id to all data-bearing tables.
    # Nullable for backward compatibility with P1–P6 data.
    _data_tables = [
        "documents",
        "notes",
        "roadmaps",
        "goals",
        "tasks",
        "memory_entries",
        "chunk_embeddings",
        "retrospectives",
        "lessons",
    ]
    for table in _data_tables:
        op.execute(f"""
            ALTER TABLE {table}
            ADD COLUMN tenant_id UUID REFERENCES tenants(id) ON DELETE SET NULL
        """)
        op.execute(f"CREATE INDEX ix_{table}_tenant_id ON {table}(tenant_id)")


def downgrade() -> None:
    _data_tables = [
        "documents", "notes", "roadmaps", "goals", "tasks",
        "memory_entries", "chunk_embeddings", "retrospectives", "lessons",
    ]
    for table in _data_tables:
        op.execute(f"DROP INDEX IF EXISTS ix_{table}_tenant_id")
        op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS tenant_id")

    op.execute("DROP TABLE IF EXISTS users")
    op.execute("DROP TABLE IF EXISTS tenants")
