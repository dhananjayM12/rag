"""articles and article_chunks for official-source ingestion

Revision ID: 0003_articles
Revises: 0002_content_chunks
Create Date: 2026-06-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.config import settings

revision: str = "0003_articles"
down_revision: Union[str, None] = "0002_content_chunks"
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
        "articles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("external_id", sa.String(length=600), nullable=False),
        sa.Column("title", sa.String(length=600), nullable=False),
        sa.Column("url", sa.String(length=800), nullable=True),
        sa.Column("published_at", sa.String(length=60), nullable=True),
        sa.Column("body", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "fetched_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.UniqueConstraint("source", "external_id", name="uq_article_source_extid"),
    )
    op.create_index("ix_articles_source", "articles", ["source"])

    op.create_table(
        "article_chunks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "article_id",
            sa.Integer(),
            sa.ForeignKey("articles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=600), nullable=False),
        sa.Column("url", sa.String(length=800), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("text", sa.Text(), nullable=False),
        _embedding_column(),
    )
    op.create_index("ix_article_chunks_article_id", "article_chunks", ["article_id"])


def downgrade() -> None:
    op.drop_index("ix_article_chunks_article_id", table_name="article_chunks")
    op.drop_table("article_chunks")
    op.drop_index("ix_articles_source", table_name="articles")
    op.drop_table("articles")
