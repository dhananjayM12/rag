from datetime import datetime

from pydantic import BaseModel


class Source(BaseModel):
    title: str
    url: str | None = None


class TreeNode(BaseModel):
    """A syllabus node with its nested children (recursive)."""

    id: int
    slug: str
    title: str
    exam: str
    level: str
    is_leaf: bool
    position: int
    has_content: bool = False
    children: list["TreeNode"] = []


TreeNode.model_rebuild()


class NodeDetail(BaseModel):
    id: int
    slug: str
    title: str
    exam: str
    level: str
    is_leaf: bool
    parent_slug: str | None = None
    breadcrumb: list[dict] = []


class ContentOut(BaseModel):
    node_slug: str
    title: str
    summary: str | None = None
    body_md: str
    sources: list[Source] = []
    updated_at: datetime | None = None
    has_content: bool = True


# ---- Stub feature schemas (RAG + answer evaluation) ----


class ArticleOut(BaseModel):
    id: int
    source: str
    title: str
    url: str | None = None
    published_at: str | None = None
    summary: str


class AskRequest(BaseModel):
    question: str
    node_slug: str | None = None


class RelatedTopic(BaseModel):
    slug: str
    title: str
    score: float


class AskResponse(BaseModel):
    answer: str
    citations: list[Source] = []
    related: list[RelatedTopic] = []
    status: str = "ok"


class EvaluateRequest(BaseModel):
    question: str
    answer: str
    word_limit: int = 250


class RubricItem(BaseModel):
    criterion: str
    score: float
    max_score: float
    feedback: str


class EvaluateResponse(BaseModel):
    overall_score: float
    max_score: float
    word_count: int
    rubric: list[RubricItem]
    suggestions: list[str]
    status: str = "coming_soon"
