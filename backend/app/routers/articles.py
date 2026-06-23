from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Article
from app.schemas import ArticleOut

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("", response_model=list[ArticleOut])
def list_articles(
    source: str | None = Query(None, description="Filter by source, e.g. PIB"),
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[ArticleOut]:
    stmt = select(Article).order_by(Article.id.desc())
    if source:
        stmt = stmt.where(Article.source == source)
    stmt = stmt.limit(limit)

    out: list[ArticleOut] = []
    for a in db.scalars(stmt).all():
        summary = a.body if len(a.body) <= 280 else a.body[:277] + "…"
        out.append(
            ArticleOut(
                id=a.id,
                source=a.source,
                title=a.title,
                url=a.url,
                published_at=a.published_at,
                summary=summary,
            )
        )
    return out
