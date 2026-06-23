"""Build the retrieval index: chunk all leaf content, embed, and store.

Idempotent — clears and rebuilds ``content_chunks``. Run with
``python -m app.rag.ingest``.
"""

from __future__ import annotations

import json

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db import Base, SessionLocal, engine
from app.models import Content, ContentChunk, SyllabusNode
from app.rag.chunk import chunk_markdown
from app.services.embeddings import get_embedder


def run() -> dict:
    Base.metadata.create_all(bind=engine)
    embedder = get_embedder()

    with SessionLocal() as db:  # type: Session
        db.execute(delete(ContentChunk))
        db.commit()

        rows = db.execute(
            select(Content, SyllabusNode).join(
                SyllabusNode, Content.node_id == SyllabusNode.id
            )
        ).all()

        pending: list[ContentChunk] = []
        texts: list[str] = []
        for content, node in rows:
            chunks = chunk_markdown(content.body_md or "")
            for i, ch in enumerate(chunks):
                pending.append(
                    ContentChunk(
                        content_id=content.id,
                        node_id=node.id,
                        node_slug=node.slug,
                        node_title=node.title,
                        position=i,
                        text=ch,
                        sources=content.sources or "[]",
                    )
                )
                # Prefix the topic title so it contributes to the embedding.
                texts.append(f"{node.title}\n{ch}")

        if pending:
            vectors = embedder.embed(texts)
            for chunk, vec in zip(pending, vectors):
                chunk.embedding = vec
            db.add_all(pending)
            db.commit()

        n = db.query(ContentChunk).count()

    print(f"Ingested {n} content chunks for retrieval.")
    return {"chunks": n}


if __name__ == "__main__":
    run()
