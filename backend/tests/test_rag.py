import pytest

from app.rag import ingest
from app.rag.chunk import chunk_markdown


@pytest.fixture(scope="module", autouse=True)
def _ingest():
    # conftest already created tables and seeded the syllabus.
    return ingest.run()


def test_chunker_packs_blocks():
    md = "## H\n\n" + ("word " * 100) + "\n\n" + ("more " * 100)
    chunks = chunk_markdown(md, target=200, hard_max=400)
    assert len(chunks) >= 2
    assert all(c.strip() for c in chunks)


def test_ingest_creates_chunks(_ingest):
    assert _ingest["chunks"] > 0


def test_ask_retrieves_classical_dances(client):
    res = client.post(
        "/api/ask",
        json={"question": "What are the classical dances of India?"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert len(body["answer"]) > 50
    slugs = [r["slug"] for r in body["related"]]
    assert "classical-dances-of-india" in slugs
    assert body["related"][0]["slug"] == "classical-dances-of-india"
    assert len(body["citations"]) >= 1


def test_ask_retrieves_fundamental_rights(client):
    body = client.post(
        "/api/ask",
        json={"question": "Explain the fundamental rights in the Constitution"},
    ).json()
    slugs = [r["slug"] for r in body["related"]]
    assert "fundamental-rights" in slugs


def test_related_scores_descending(client):
    body = client.post(
        "/api/ask", json={"question": "monsoon mechanism in India"}
    ).json()
    scores = [r["score"] for r in body["related"]]
    assert scores == sorted(scores, reverse=True)
