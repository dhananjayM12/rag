"""Ingest documents from official/open sources into the RAG index.

Fetches each configured source feed, upserts ``articles`` (de-duped on
source+external_id), then chunks + embeds new/updated articles into
``article_chunks`` so they're retrievable alongside the seeded content.

Run with ``python -m app.rag.ingest_sources``. Network failures on any one
source are logged and skipped so a single bad feed never aborts the run.
"""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db import Base, SessionLocal, engine
from app.models import Article, ArticleChunk
from app.rag.chunk import chunk_markdown
from app.rag.sources.base import FetchedDoc, SourceConnector
from app.rag.sources.rss import default_connectors
from app.services.embeddings import get_embedder


def _upsert_article(db: Session, doc: FetchedDoc) -> tuple[Article, bool]:
    existing = db.scalar(
        select(Article).where(
            Article.source == doc.source, Article.external_id == doc.external_id
        )
    )
    changed = True
    if existing:
        changed = existing.body != doc.body or existing.title != doc.title
        existing.title = doc.title
        existing.url = doc.url
        existing.published_at = doc.published_at
        existing.body = doc.body
        article = existing
    else:
        article = Article(
            source=doc.source,
            external_id=doc.external_id,
            title=doc.title,
            url=doc.url,
            published_at=doc.published_at,
            body=doc.body,
        )
        db.add(article)
    db.flush()
    return article, changed


def _reindex_article(db: Session, article: Article) -> None:
    db.execute(delete(ArticleChunk).where(ArticleChunk.article_id == article.id))
    embedder = get_embedder()
    chunks = chunk_markdown(article.body) or [article.body]
    texts = [f"{article.title}\n{c}" for c in chunks]
    vectors = embedder.embed(texts)
    for i, (c, vec) in enumerate(zip(chunks, vectors)):
        db.add(
            ArticleChunk(
                article_id=article.id,
                source=article.source,
                title=article.title,
                url=article.url,
                position=i,
                text=c,
                embedding=vec,
            )
        )


def run(connectors: list[SourceConnector] | None = None) -> dict:
    Base.metadata.create_all(bind=engine)
    connectors = connectors if connectors is not None else default_connectors()

    fetched = 0
    indexed = 0
    errors: list[str] = []

    with SessionLocal() as db:
        for connector in connectors:
            try:
                docs = connector.fetch()
            except Exception as exc:  # network / parse error — skip this source
                errors.append(f"{connector.name}: {exc}")
                continue
            for doc in docs:
                fetched += 1
                article, changed = _upsert_article(db, doc)
                if changed:
                    _reindex_article(db, article)
                    indexed += 1
            db.commit()

        total_articles = db.query(Article).count()
        total_chunks = db.query(ArticleChunk).count()

    result = {
        "fetched": fetched,
        "indexed": indexed,
        "total_articles": total_articles,
        "total_chunks": total_chunks,
        "errors": errors,
    }
    print(
        f"Source ingestion: fetched={fetched} indexed={indexed} "
        f"articles={total_articles} chunks={total_chunks}"
    )
    for e in errors:
        print(f"  skipped {e}")
    return result


if __name__ == "__main__":
    run()
