from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Content, SyllabusNode
from app.schemas import NodeDetail, TreeNode

router = APIRouter(prefix="/api/syllabus", tags=["syllabus"])


def _build_tree(nodes: list[SyllabusNode], content_node_ids: set[int]) -> list[TreeNode]:
    """Assemble a nested TreeNode list from a flat node list."""
    by_id: dict[int, TreeNode] = {}
    for n in nodes:
        by_id[n.id] = TreeNode(
            id=n.id,
            slug=n.slug,
            title=n.title,
            exam=n.exam,
            level=n.level,
            is_leaf=n.is_leaf,
            position=n.position,
            has_content=n.id in content_node_ids,
            children=[],
        )

    roots: list[TreeNode] = []
    present = set(by_id)
    for n in nodes:
        node = by_id[n.id]
        if n.parent_id in present:
            by_id[n.parent_id].children.append(node)
        else:
            roots.append(node)

    def sort_rec(items: list[TreeNode]) -> None:
        items.sort(key=lambda x: (x.position, x.id))
        for it in items:
            sort_rec(it.children)

    sort_rec(roots)
    return roots


def _descendant_ids(db: Session, root_id: int) -> set[int]:
    """Collect a node and all of its descendants (small trees, simple BFS)."""
    ids = {root_id}
    frontier = [root_id]
    while frontier:
        rows = db.execute(
            select(SyllabusNode.id).where(SyllabusNode.parent_id.in_(frontier))
        ).all()
        children = [r[0] for r in rows]
        new = [c for c in children if c not in ids]
        ids.update(new)
        frontier = new
    return ids


@router.get("/tree", response_model=list[TreeNode])
def get_tree(
    exam: str | None = Query(None, description="Filter by exam: prelims | mains"),
    root: str | None = Query(None, description="Return only the subtree under this slug"),
    db: Session = Depends(get_db),
) -> list[TreeNode]:
    content_node_ids = {r[0] for r in db.execute(select(Content.node_id)).all()}

    if root:
        root_node = db.scalar(select(SyllabusNode).where(SyllabusNode.slug == root))
        if not root_node:
            raise HTTPException(status_code=404, detail="Root node not found")
        ids = _descendant_ids(db, root_node.id)
        nodes = list(
            db.scalars(select(SyllabusNode).where(SyllabusNode.id.in_(ids))).all()
        )
    else:
        stmt = select(SyllabusNode)
        if exam:
            stmt = stmt.where(SyllabusNode.exam == exam)
        nodes = list(db.scalars(stmt).all())

    return _build_tree(nodes, content_node_ids)


@router.get("/node/{slug}", response_model=NodeDetail)
def get_node(slug: str, db: Session = Depends(get_db)) -> NodeDetail:
    node = db.scalar(select(SyllabusNode).where(SyllabusNode.slug == slug))
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Build a breadcrumb by walking up parents.
    crumb: list[dict] = []
    cur = node
    parent_slug = None
    while cur is not None:
        crumb.append({"slug": cur.slug, "title": cur.title, "level": cur.level})
        if cur is node and cur.parent_id is not None:
            p = db.get(SyllabusNode, cur.parent_id)
            parent_slug = p.slug if p else None
        cur = db.get(SyllabusNode, cur.parent_id) if cur.parent_id else None
    crumb.reverse()

    return NodeDetail(
        id=node.id,
        slug=node.slug,
        title=node.title,
        exam=node.exam,
        level=node.level,
        is_leaf=node.is_leaf,
        parent_slug=parent_slug,
        breadcrumb=crumb,
    )
