from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.rag.generator import generate_answer
from app.rag.retriever import retrieve
from app.schemas import AskRequest, AskResponse, RelatedTopic, Source

router = APIRouter(prefix="/api", tags=["rag"])


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest, db: Session = Depends(get_db)) -> AskResponse:
    """Retrieval-augmented Q&A over the ingested official-source content.

    Embeds the question (local embedder), retrieves the nearest content chunks
    via vector search, and generates a grounded answer with citations. Runs
    fully locally — see ``app.config`` to switch the embedder/LLM backends.
    """
    results = retrieve(db, req.question)

    answer = generate_answer(req.question, results)

    # Build de-duplicated related topics and source citations from the hits.
    related: list[RelatedTopic] = []
    seen_nodes: set[str] = set()
    citations: list[Source] = []
    seen_sources: set[tuple[str, str | None]] = set()

    for r in results:
        if r.score <= 0:
            continue
        if r.chunk.node_slug not in seen_nodes:
            seen_nodes.add(r.chunk.node_slug)
            related.append(
                RelatedTopic(
                    slug=r.chunk.node_slug,
                    title=r.chunk.node_title,
                    score=round(r.score, 3),
                )
            )
        for s in r.chunk.sources_list:
            key = (s.get("title", ""), s.get("url"))
            if key not in seen_sources:
                seen_sources.add(key)
                citations.append(Source(**s))

    return AskResponse(
        answer=answer,
        citations=citations,
        related=related,
        status="ok" if results else "no_results",
    )
