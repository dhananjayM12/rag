# PrepPath — UPSC Study App

A commercializable UPSC preparation web app.

- **Milestone 1** — an **interactive flowchart of the entire syllabus**, drilling
  from exam → paper → topic → subtopic → **micro-topic leaf nodes that carry
  source-backed study content**.
- **Milestone 2** — a **local RAG Q&A** system (`/ask`): questions are embedded,
  matched against indexed content via vector search, and answered with
  citations. Runs fully locally; pluggable embedder (hashing or
  sentence-transformers) and LLM (extractive or Ollama).
- **Milestone 3** — **official-source ingestion**: pulls current-affairs items
  from official RSS feeds (PIB, PRS), stores them as `articles`, and indexes
  them into the same retrieval pipeline so the AI can answer about the latest
  updates with source links. Browse them at `/current-affairs`.

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

## Official-source ingestion (Milestone 3)

```bash
# Fetch + index the configured feeds (PIB, PRS by default):
python -m app.rag.ingest_sources
```

- Feeds are set via `SOURCE_FEEDS` ("Name|url" pairs) in `backend/.env.example`.
  Official/open sources only — commercially safe.
- Connectors live in `app/rag/sources/` (RSS via the standard library; add new
  connectors by implementing `SourceConnector`). A failing feed is skipped, not
  fatal. Articles are de-duped on `(source, external_id)`.
- Ingested articles are chunked + embedded into `article_chunks` and retrieved
  alongside seeded content, so `/ask` can cite current affairs. List endpoint:
  `GET /api/articles`; UI at `/current-affairs`.
- Not run at container start (network may be restricted) — run it manually or on
  a schedule (cron).

## Roadmap (scaffolded, build next)

- **Answer evaluation** (`/api/evaluate`): rubric-based grading with a local LLM.
- **Tag articles to syllabus nodes** so current affairs appear on the relevant
  micro-topic pages.
- **Student features**: progress tracking + spaced revision, previous-year-question
  mapping to leaf nodes, current-affairs feed tagged to syllabus nodes, auth +
  subscription tiers, PWA/offline.
