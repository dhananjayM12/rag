"""Vector retrieval over all indexed chunks (seeded content + articles).

Uses pgvector cosine distance on Postgres to shortlist per table; falls back to
in-Python cosine elsewhere (e.g. SQLite in tests). Candidates from both sources
are merged and ranked together.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import ArticleChunk, ContentChunk
from app.services.embeddings import cosine_similarity, get_embedder


@dataclass
class RetrievedChunk:
    text: str
    title: str
    kind: str  # "topic" | "article"
    score: float
    slug: str | None = None  # internal syllabus topic
    url: str | None = None  # external article link
    sources: list[dict] = field(default_factory=list)


def _candidates(db: Session, model, qvec: list[float], k: int):
    """Shortlist rows from one chunk table."""
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        try:
            stmt = (
                select(model).order_by(model.embedding.cosine_distance(qvec)).limit(k)
            )
            return list(db.scalars(stmt).all())
        except Exception:
            pass
    return list(db.scalars(select(model)).all())


def _emb(value) -> list[float]:
    if value is None:
        return []
    if isinstance(value, str):  # safety: JSON-encoded
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return []
    return list(value)


def retrieve(db: Session, query: str, k: int | None = None) -> list[RetrievedChunk]:
    k = k or settings.rag_top_k
    qvec = get_embedder().embed_one(query)

    results: list[RetrievedChunk] = []

    for c in _candidates(db, ContentChunk, qvec, k):
        results.append(
            RetrievedChunk(
                text=c.text,
                title=c.node_title,
                kind="topic",
                slug=c.node_slug,
                sources=c.sources_list,
                score=cosine_similarity(qvec, _emb(c.embedding)),
            )
        )

    for a in _candidates(db, ArticleChunk, qvec, k):
        results.append(
            RetrievedChunk(
                text=a.text,
                title=a.title,
                kind="article",
                url=a.url,
                sources=[{"title": f"{a.title} ({a.source})", "url": a.url}],
                score=cosine_similarity(qvec, _emb(a.embedding)),
            )
        )

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:k]
