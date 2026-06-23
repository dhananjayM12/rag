from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Content, SyllabusNode
from app.schemas import ContentOut, Source

router = APIRouter(prefix="/api/content", tags=["content"])


@router.get("/{node_slug}", response_model=ContentOut)
def get_content(node_slug: str, db: Session = Depends(get_db)) -> ContentOut:
    node = db.scalar(select(SyllabusNode).where(SyllabusNode.slug == node_slug))
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    content = db.scalar(select(Content).where(Content.node_id == node.id))
    if not content:
        # Node exists but has no authored content yet.
        return ContentOut(
            node_slug=node.slug,
            title=node.title,
            summary=None,
            body_md="_Content for this micro-topic is coming soon._",
            sources=[],
            updated_at=None,
            has_content=False,
        )

    sources = [Source(**s) for s in content.sources_list]
    return ContentOut(
        node_slug=node.slug,
        title=node.title,
        summary=content.summary,
        body_md=content.body_md,
        sources=sources,
        updated_at=content.updated_at,
        has_content=True,
    )
