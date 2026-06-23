"""Embedding service.

Local / open by default. Two backends:

- ``HashingEmbedder`` (default): a zero-dependency, fully-local bag-of-words
  hashing embedding. Deterministic across processes and good enough for lexical
  retrieval, so the app works out of the box with no model download.
- ``SentenceTransformerEmbedder``: better semantic quality via a local
  sentence-transformers model (e.g. ``intfloat/multilingual-e5-small``, also
  good for Hindi/Indic text). Lazily imported so it's only needed when enabled.

Select with ``EMBEDDING_BACKEND`` (see ``app.config``).
"""

from __future__ import annotations

import hashlib
import math
import re

from app.config import settings

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _l2_normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0:
        return vec
    return [v / norm for v in vec]


class EmbeddingModel:
    """Abstract embedder. Returns vectors of length ``settings.embed_dim``."""

    dim: int = settings.embed_dim

    def embed(self, texts: list[str]) -> list[list[float]]:  # pragma: no cover
        raise NotImplementedError

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


class HashingEmbedder(EmbeddingModel):
    """Deterministic hashed bag-of-words embedding (no external dependencies)."""

    def __init__(self, dim: int | None = None) -> None:
        self.dim = dim or settings.embed_dim

    def _index(self, token: str) -> int:
        digest = hashlib.md5(token.encode("utf-8")).digest()[:4]
        return int.from_bytes(digest, "big") % self.dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for text in texts:
            vec = [0.0] * self.dim
            for tok in _tokenize(text):
                vec[self._index(tok)] += 1.0
            out.append(_l2_normalize(vec))
        return out


class SentenceTransformerEmbedder(EmbeddingModel):
    """Local sentence-transformers embedder (lazy import)."""

    def __init__(self, model_name: str | None = None) -> None:
        from sentence_transformers import SentenceTransformer  # lazy

        self._model = SentenceTransformer(model_name or settings.embedding_model)
        self.dim = self._model.get_sentence_embedding_dimension()

    def embed(self, texts: list[str]) -> list[list[float]]:
        vecs = self._model.encode(texts, normalize_embeddings=True)
        return [list(map(float, v)) for v in vecs]


_cached: EmbeddingModel | None = None


def get_embedder() -> EmbeddingModel:
    """Return the configured embedder, falling back to hashing if needed."""
    global _cached
    if _cached is not None:
        return _cached

    if settings.embedding_backend == "sentence-transformers":
        try:
            _cached = SentenceTransformerEmbedder()
        except Exception:  # model/dep missing — degrade gracefully
            _cached = HashingEmbedder()
    else:
        _cached = HashingEmbedder()
    return _cached


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
