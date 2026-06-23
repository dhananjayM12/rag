"""Vector retrieval over content chunks.

Uses pgvector's cosine distance on Postgres; falls back to in-Python cosine
similarity elsewhere (e.g. SQLite in tests). Both return the top-k chunks.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import ContentChunk
from app.services.embeddings import cosine_similarity, get_embedder


@dataclass
class RetrievedChunk:
    chunk: ContentChunk
    score: float


def retrieve(db: Session, query: str, k: int | None = None) -> list[RetrievedChunk]:
    k = k or settings.rag_top_k
    qvec = get_embedder().embed_one(query)

    if db.bind is not None and db.bind.dialect.name == "postgresql":
        try:
            stmt = (
                select(ContentChunk)
                .order_by(ContentChunk.embedding.cosine_distance(qvec))
                .limit(k)
            )
            chunks = list(db.scalars(stmt).all())
            # cosine_distance = 1 - cosine_similarity
            return [
                RetrievedChunk(c, cosine_similarity(qvec, list(c.embedding)))
                for c in chunks
            ]
        except Exception:
            pass  # fall through to Python path

    chunks = list(db.scalars(select(ContentChunk)).all())
    scored = [
        RetrievedChunk(c, cosine_similarity(qvec, c.embedding or []))
        for c in chunks
    ]
    scored.sort(key=lambda r: r.score, reverse=True)
    return scored[:k]
