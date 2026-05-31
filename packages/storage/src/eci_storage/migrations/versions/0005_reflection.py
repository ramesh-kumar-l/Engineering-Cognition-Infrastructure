"""reflection: retrospectives, lessons, lesson_evidence

Revision ID: 0005_reflection
Revises: 0004_execution
Create Date: 2026-05-31
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0005_reflection"
down_revision: Union[str, None] = "0004_execution"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE retrospectives (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            cadence VARCHAR(16) NOT NULL,
            scope_type VARCHAR(16),
            scope_id UUID,
            status VARCHAR(16) NOT NULL DEFAULT 'running',
            started_at TIMESTAMPTZ NOT NULL,
            completed_at TIMESTAMPTZ,
            notes TEXT,
            lesson_count INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    op.execute("""
        CREATE TABLE lessons (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            retrospective_id UUID REFERENCES retrospectives(id) ON DELETE SET NULL,
            claim TEXT NOT NULL,
            scope VARCHAR(32) NOT NULL DEFAULT 'global',
            confidence VARCHAR(8) NOT NULL DEFAULT 'medium',
            status VARCHAR(16) NOT NULL DEFAULT 'active',
            supersedes_id UUID REFERENCES lessons(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    op.execute("""
        CREATE TABLE lesson_evidence (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
            source_type VARCHAR(32) NOT NULL,
            source_id UUID NOT NULL,
            summary TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    op.execute("CREATE INDEX ix_retrospectives_status ON retrospectives(status)")
    op.execute("CREATE INDEX ix_lessons_retrospective_id ON lessons(retrospective_id)")
    op.execute("CREATE INDEX ix_lessons_status ON lessons(status)")
    op.execute("CREATE INDEX ix_lesson_evidence_lesson_id ON lesson_evidence(lesson_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS lesson_evidence")
    op.execute("DROP TABLE IF EXISTS lessons")
    op.execute("DROP TABLE IF EXISTS retrospectives")
