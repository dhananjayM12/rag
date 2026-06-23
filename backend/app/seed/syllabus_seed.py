"""Seed the syllabus tree and leaf content from ``syllabus.json``.

Idempotent: it clears existing syllabus data and re-inserts, so it is safe to
run on every container start. Run with ``python -m app.seed.syllabus_seed``.
"""

import json
import re
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db import SessionLocal, engine, Base
from app.models import Bookmark, Content, SyllabusNode, UserProgress

DATA_FILE = Path(__file__).with_name("syllabus.json")


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def _unique_slug(base: str, used: set[str]) -> str:
    slug = base or "node"
    i = 2
    while slug in used:
        slug = f"{base}-{i}"
        i += 1
    used.add(slug)
    return slug


def _insert(
    db: Session,
    node: dict,
    parent: SyllabusNode | None,
    exam: str,
    used_slugs: set[str],
    position: int,
) -> None:
    children = node.get("children", [])
    content = node.get("content")
    is_leaf = not children

    slug = _unique_slug(slugify(node["title"]), used_slugs)
    row = SyllabusNode(
        parent_id=parent.id if parent else None,
        exam=node.get("exam", exam),
        level=node["level"],
        title=node["title"],
        slug=slug,
        position=position,
        is_leaf=is_leaf,
    )
    db.add(row)
    db.flush()  # assign row.id

    if content:
        db.add(
            Content(
                node_id=row.id,
                summary=content.get("summary"),
                body_md=content.get("body_md", ""),
                sources=json.dumps(content.get("sources", [])),
            )
        )

    for i, child in enumerate(children):
        _insert(db, child, row, row.exam, used_slugs, i)


def run() -> dict:
    # Ensure tables exist (no-op if Alembic already created them).
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        # Clear in FK-safe order.
        db.execute(delete(UserProgress))
        db.execute(delete(Bookmark))
        db.execute(delete(Content))
        db.execute(delete(SyllabusNode))
        db.commit()

        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        used_slugs: set[str] = set()
        for i, top in enumerate(data):
            _insert(db, top, None, top.get("exam", "mains"), used_slugs, i)
        db.commit()

        n_nodes = db.query(SyllabusNode).count()
        n_content = db.query(Content).count()

    summary = {"nodes": n_nodes, "content": n_content}
    print(f"Seeded syllabus: {summary['nodes']} nodes, {summary['content']} content leaves.")
    return summary


if __name__ == "__main__":
    run()
