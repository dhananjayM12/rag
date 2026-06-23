"""content_chunks table for RAG retrieval

Revision ID: 0002_content_chunks
Revises: 0001_initial
Create Date: 2026-06-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.config import settings

revision: str = "0002_content_chunks"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _embedding_column() -> sa.Column:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
        from pgvector.sqlalchemy import Vector

        return sa.Column("embedding", Vector(settings.embed_dim), nullable=True)
    return sa.Column("embedding", sa.Text(), nullable=True)


def upgrade() -> None:
    op.create_table(
        "content_chunks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "content_id",
            sa.Integer(),
            sa.ForeignKey("contents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "node_id",
            sa.Integer(),
            sa.ForeignKey("syllabus_nodes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("node_slug", sa.String(length=550), nullable=False),
        sa.Column("node_title", sa.String(length=500), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("sources", sa.Text(), nullable=False, server_default="[]"),
        _embedding_column(),
    )
    op.create_index("ix_content_chunks_content_id", "content_chunks", ["content_id"])
    op.create_index("ix_content_chunks_node_id", "content_chunks", ["node_id"])


def downgrade() -> None:
    op.drop_index("ix_content_chunks_node_id", table_name="content_chunks")
    op.drop_index("ix_content_chunks_content_id", table_name="content_chunks")
    op.drop_table("content_chunks")
