"""Answer generation from retrieved chunks.

Two local backends:

- ``extractive`` (default): returns the most relevant grounded passage(s)
  verbatim. No model required — answers are always faithful to the sources.
- ``ollama``: calls a local LLM over HTTP to synthesise an answer from the
  retrieved context. Falls back to extractive on any error.

Select with ``LLM_BACKEND`` (see ``app.config``).
"""

from __future__ import annotations

import httpx

from app.config import settings
from app.rag.retriever import RetrievedChunk

NO_CONTEXT = (
    "I couldn't find relevant material in the indexed sources yet. "
    "Try rephrasing, or explore the syllabus map."
)

PROMPT_TEMPLATE = (
    "You are a UPSC study assistant. Answer the question using ONLY the context "
    "below, which comes from official sources. Be concise and factual. If the "
    "context is insufficient, say so.\n\n"
    "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
)


def _build_context(results: list[RetrievedChunk]) -> str:
    return "\n\n---\n\n".join(f"[{r.title}]\n{r.text}" for r in results)


def extractive_answer(results: list[RetrievedChunk]) -> str:
    if not results:
        return NO_CONTEXT
    top = results[0]
    answer = top.text
    # Add a second passage if it's from a different topic/article and relevant.
    for r in results[1:]:
        if r.title != top.title and r.score > 0.1:
            answer += f"\n\n**Related — {r.title}:**\n{r.text}"
            break
    return answer


def _ollama_answer(question: str, results: list[RetrievedChunk]) -> str:
    prompt = PROMPT_TEMPLATE.format(
        context=_build_context(results), question=question
    )
    resp = httpx.post(
        f"{settings.ollama_url}/api/generate",
        json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json().get("response", "").strip() or NO_CONTEXT


def generate_answer(question: str, results: list[RetrievedChunk]) -> str:
    if not results:
        return NO_CONTEXT
    if settings.llm_backend == "ollama":
        try:
            return _ollama_answer(question, results)
        except Exception:
            return extractive_answer(results)
    return extractive_answer(results)
