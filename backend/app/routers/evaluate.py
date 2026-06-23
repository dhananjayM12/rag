from fastapi import APIRouter

from app.schemas import EvaluateRequest, EvaluateResponse, RubricItem

router = APIRouter(prefix="/api", tags=["evaluate"])


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate(req: EvaluateRequest) -> EvaluateResponse:
    """Mains answer evaluation — stub.

    Returns a mock rubric so the UI can be built now. A later milestone will
    grade with a local LLM against a UPSC-style rubric (introduction, body,
    structure, dimensions covered, conclusion) and word-limit adherence.
    """
    word_count = len(req.answer.split())
    within_limit = word_count <= req.word_limit
    length_score = 1.0 if within_limit else 0.5

    rubric = [
        RubricItem(
            criterion="Structure (intro–body–conclusion)",
            score=0.0,
            max_score=3.0,
            feedback="AI grading coming soon.",
        ),
        RubricItem(
            criterion="Content & relevance",
            score=0.0,
            max_score=4.0,
            feedback="AI grading coming soon.",
        ),
        RubricItem(
            criterion="Dimensions / multi-perspective",
            score=0.0,
            max_score=2.0,
            feedback="AI grading coming soon.",
        ),
        RubricItem(
            criterion="Word-limit adherence",
            score=length_score,
            max_score=1.0,
            feedback=(
                f"{word_count} words (limit {req.word_limit})."
                if within_limit
                else f"Over the {req.word_limit}-word limit ({word_count} words)."
            ),
        ),
    ]
    return EvaluateResponse(
        overall_score=sum(r.score for r in rubric),
        max_score=sum(r.max_score for r in rubric),
        word_count=word_count,
        rubric=rubric,
        suggestions=[
            "Full AI evaluation will give per-paragraph feedback and a model answer.",
        ],
        status="coming_soon",
    )
