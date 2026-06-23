# PrepPath — UPSC Study App

A commercializable UPSC preparation web app.

- **Milestone 1** — an **interactive flowchart of the entire syllabus**, drilling
  from exam → paper → topic → subtopic → **micro-topic leaf nodes that carry
  source-backed study content**.
- **Milestone 2** — a **local RAG Q&A** system (`/ask`): questions are embedded,
  matched against ingested official-source content via vector search, and
  answered with citations. Runs fully locally; pluggable embedder (hashing or
  sentence-transformers) and LLM (extractive or Ollama).

Mains answer-evaluation remains a wired stub for the next milestone.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 14 (App Router, TypeScript), React Flow + dagre, Tailwind |
| Backend | FastAPI, SQLAlchemy 2, Alembic |
| Database | PostgreSQL + pgvector (vector column ready for RAG) |
| AI (later) | Local/open models — sentence-transformers embeddings, local LLM for Q&A and grading |

Content is sourced from **official/open resources only** (UPSC syllabus, NCERT,
the Constitution, IMD, NITI Aayog, ministries) — safe for commercial use.

## Quick start (Docker)

```bash
docker compose up --build
```

- Frontend: http://localhost:3000  (start at **/flowchart**)
- Backend API: http://localhost:8000  (`/docs` for OpenAPI)

The backend container runs migrations and seeds the syllabus automatically.

## Local development

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Postgres (recommended): set DATABASE_URL, then:
alembic upgrade head
python -m app.seed.syllabus_seed
uvicorn app.main:app --reload
# Tests run against SQLite, no DB needed:
pytest
```

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

## How the flowchart works

- `GET /api/syllabus/tree` returns the nested syllabus. The frontend flattens it,
  tracks an `expanded` set, computes the visible sub-graph, and lays it out with
  **dagre** (`frontend/lib/layout.ts`).
- Click an internal node to expand/collapse; click a **leaf (📄)** to open the
  content drawer, which loads `GET /api/content/{slug}` and renders the markdown
  with sources. A search box expands the path to any topic and centers it.
- Seed content lives in `backend/app/seed/syllabus.json` (10 fully-written
  micro-topics; the rest are navigable placeholders).

## Project layout

```
backend/
  app/
    models.py          # SyllabusNode tree, Content (+ pgvector embedding), progress/bookmark stubs
    routers/           # syllabus, content, rag (stub), evaluate (stub)
    seed/              # syllabus.json + loader
    services/embeddings.py  # seam for the local embedding model (RAG milestone)
  alembic/             # migrations (creates pgvector extension)
  tests/               # pytest, SQLite-backed
frontend/
  app/                 # /, /flowchart, /topic/[slug], /ask, /evaluate
  components/          # FlowChart, SyllabusNode, ContentDrawer
  lib/                 # api client, dagre layout
docker-compose.yml
```

## RAG Q&A pipeline (Milestone 2)

```
content (markdown) → chunk → embed (local) → content_chunks (+ vector)
question → embed → vector search (pgvector / cosine) → top-k chunks
        → generate answer (extractive or local LLM) + citations + related topics
```

- Rebuild the index any time with `python -m app.rag.ingest`.
- Code: `app/rag/{chunk,ingest,retriever,generator}.py`,
  `app/services/embeddings.py`. Switch backends via env (`EMBEDDING_BACKEND`,
  `LLM_BACKEND`) — see `backend/.env.example`.

## Roadmap (scaffolded, build next)

- **Answer evaluation** (`/api/evaluate`): rubric-based grading with a local LLM.
- **Source ingestion**: pull fresh content from official feeds (PIB, PRS, etc.)
  into the same chunk/embed pipeline for current-affairs coverage.
- **Student features**: progress tracking + spaced revision, previous-year-question
  mapping to leaf nodes, current-affairs feed tagged to syllabus nodes, auth +
  subscription tiers, PWA/offline.
