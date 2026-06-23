"""initial schema: syllabus tree, content, progress, bookmarks

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.config import settings

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _embedding_column() -> sa.Column:
    """Vector column on Postgres+pgvector, JSON text elsewhere."""
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
        from pgvector.sqlalchemy import Vector

        return sa.Column("embedding", Vector(settings.embed_dim), nullable=True)
    return sa.Column("embedding", sa.Text(), nullable=True)


def upgrade() -> None:
    op.create_table(
        "syllabus_nodes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "parent_id",
            sa.Integer(),
            sa.ForeignKey("syllabus_nodes.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("exam", sa.String(length=20), nullable=False),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("slug", sa.String(length=550), nullable=False, unique=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_leaf", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_syllabus_nodes_parent_id", "syllabus_nodes", ["parent_id"])
    op.create_index("ix_syllabus_nodes_exam", "syllabus_nodes", ["exam"])
    op.create_index("ix_syllabus_nodes_slug", "syllabus_nodes", ["slug"], unique=True)

    op.create_table(
        "contents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "node_id",
            sa.Integer(),
            sa.ForeignKey("syllabus_nodes.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("body_md", sa.Text(), nullable=False, server_default=""),
        sa.Column("sources", sa.Text(), nullable=False, server_default="[]"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        _embedding_column(),
    )

    op.create_table(
        "user_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(length=100), nullable=False, index=True),
        sa.Column(
            "node_id",
            sa.Integer(),
            sa.ForeignKey("syllabus_nodes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="todo"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
    )

    op.create_table(
        "bookmarks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(length=100), nullable=False, index=True),
        sa.Column(
            "node_id",
            sa.Integer(),
            sa.ForeignKey("syllabus_nodes.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("bookmarks")
    op.drop_table("user_progress")
    op.drop_table("contents")
    op.drop_index("ix_syllabus_nodes_slug", table_name="syllabus_nodes")
    op.drop_index("ix_syllabus_nodes_exam", table_name="syllabus_nodes")
    op.drop_index("ix_syllabus_nodes_parent_id", table_name="syllabus_nodes")
    op.drop_table("syllabus_nodes")
