"""execution: roadmaps, goals, tasks, task_dependencies, execution_citations

Revision ID: 0004_execution
Revises: 0003_retrieval
Create Date: 2026-05-31
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0004_execution"
down_revision: Union[str, None] = "0003_retrieval"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE roadmaps (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(256) NOT NULL,
            description TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    op.execute("""
        CREATE TABLE goals (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(512) NOT NULL,
            description TEXT,
            status VARCHAR(32) NOT NULL DEFAULT 'pending',
            roadmap_id UUID REFERENCES roadmaps(id) ON DELETE SET NULL,
            source_memory_id UUID REFERENCES memory_entries(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    op.execute("""
        CREATE TABLE tasks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(512) NOT NULL,
            description TEXT,
            status VARCHAR(32) NOT NULL DEFAULT 'pending',
            goal_id UUID REFERENCES goals(id) ON DELETE SET NULL,
            position INTEGER NOT NULL DEFAULT 0,
            source_memory_id UUID REFERENCES memory_entries(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    op.execute("""
        CREATE TABLE task_dependencies (
            upstream_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
            downstream_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
            PRIMARY KEY (upstream_id, downstream_id)
        )
    """)

    op.execute("""
        CREATE TABLE execution_citations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            target_type VARCHAR(16) NOT NULL,
            target_id UUID NOT NULL,
            source_type VARCHAR(32) NOT NULL,
            source_id UUID NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            score FLOAT NOT NULL,
            title VARCHAR(512),
            source_uri VARCHAR(1024),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    op.execute("CREATE INDEX ix_goals_roadmap_id ON goals(roadmap_id)")
    op.execute("CREATE INDEX ix_goals_status ON goals(status)")
    op.execute("CREATE INDEX ix_tasks_goal_id ON tasks(goal_id)")
    op.execute("CREATE INDEX ix_tasks_status ON tasks(status)")
    op.execute(
        "CREATE INDEX ix_execution_citations_target "
        "ON execution_citations(target_type, target_id)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS execution_citations")
    op.execute("DROP TABLE IF EXISTS task_dependencies")
    op.execute("DROP TABLE IF EXISTS tasks")
    op.execute("DROP TABLE IF EXISTS goals")
    op.execute("DROP TABLE IF EXISTS roadmaps")
