"""Embedding service interface.

Milestone 1 does not compute embeddings. This module defines the seam so the
RAG milestone can plug in a local model (e.g. sentence-transformers
``intfloat/multilingual-e5-small`` or an Indic model) without touching call
sites. Keeping it lazy means the flowchart build pulls in no heavy ML deps.
"""

from __future__ import annotations

from app.config import settings


class EmbeddingModel:
    """Abstract embedder. Returns vectors of length ``settings.embed_dim``."""

    def embed(self, texts: list[str]) -> list[list[float]]:  # pragma: no cover
        raise NotImplementedError


class NoopEmbeddingModel(EmbeddingModel):
    """Default no-op used in Milestone 1: returns zero vectors."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * settings.embed_dim for _ in texts]


def get_embedder() -> EmbeddingModel:
    """Factory. Swap the implementation here when wiring the RAG milestone."""
    return NoopEmbeddingModel()
