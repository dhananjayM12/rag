from fastapi import APIRouter

from app.schemas import AskRequest, AskResponse

router = APIRouter(prefix="/api", tags=["rag"])


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    """RAG Q&A — stub.

    Milestone 1 ships the contract only. A later milestone will: embed the
    question with a local sentence-transformers model, retrieve the nearest
    content chunks via pgvector, and generate a grounded answer with a local
    LLM, returning real citations.
    """
    return AskResponse(
        answer=(
            "AI answers are coming soon. This will retrieve from official UPSC "
            "and government sources and cite them inline."
        ),
        citations=[],
        status="coming_soon",
    )
