import json

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings
from app.db import Base

try:  # pgvector is only needed when running against Postgres.
    from pgvector.sqlalchemy import Vector

    HAS_PGVECTOR = True
except Exception:  # pragma: no cover - import guard
    HAS_PGVECTOR = False


class Embedding(TypeDecorator):
    """Portable embedding column.

    Maps to a real pgvector ``Vector`` on Postgres, and degrades to a JSON
    string on other backends (e.g. SQLite used in tests) so the same model
    works everywhere. Embeddings stay NULL until the RAG milestone populates
    them.
    """

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and HAS_PGVECTOR:
            return dialect.type_descriptor(Vector(settings.embed_dim))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql" and HAS_PGVECTOR:
            return value
        return json.dumps(list(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql" and HAS_PGVECTOR:
            return value
        return json.loads(value)


class SyllabusNode(Base):
    """A node in the UPSC syllabus tree.

    The tree is self-referential: exam -> stage/paper -> topic -> subtopic ->
    micro (leaf). Leaf nodes carry study Content.
    """

    __tablename__ = "syllabus_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("syllabus_nodes.id", ondelete="CASCADE"), nullable=True, index=True
    )
    exam: Mapped[str] = mapped_column(String(20), index=True)  # prelims | mains
    level: Mapped[str] = mapped_column(String(20))  # stage|paper|topic|subtopic|micro
    title: Mapped[str] = mapped_column(String(500))
    slug: Mapped[str] = mapped_column(String(550), unique=True, index=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    is_leaf: Mapped[bool] = mapped_column(Boolean, default=False)

    children: Mapped[list["SyllabusNode"]] = relationship(
        "SyllabusNode",
        backref="parent",
        remote_side=[id],
        viewonly=True,
    )
    content: Mapped["Content | None"] = relationship(
        "Content", back_populates="node", uselist=False, cascade="all, delete-orphan"
    )


class Content(Base):
    """Study content attached to a leaf (micro-topic) node."""

    __tablename__ = "contents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    node_id: Mapped[int] = mapped_column(
        ForeignKey("syllabus_nodes.id", ondelete="CASCADE"), unique=True, index=True
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_md: Mapped[str] = mapped_column(Text, default="")
    sources: Mapped[str] = mapped_column(Text, default="[]")  # JSON list of {title,url}
    updated_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    embedding = mapped_column(Embedding, nullable=True)  # future RAG

    node: Mapped["SyllabusNode"] = relationship("SyllabusNode", back_populates="content")

    @property
    def sources_list(self) -> list[dict]:
        try:
            return json.loads(self.sources or "[]")
        except json.JSONDecodeError:
            return []


class UserProgress(Base):
    """Per-user study progress on a node. Scaffolded for a later milestone."""

    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), index=True)
    node_id: Mapped[int] = mapped_column(ForeignKey("syllabus_nodes.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), default="todo")  # todo|studied|revise
    updated_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Bookmark(Base):
    """A user's bookmarked node. Scaffolded for a later milestone."""

    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), index=True)
    node_id: Mapped[int] = mapped_column(ForeignKey("syllabus_nodes.id", ondelete="CASCADE"))
