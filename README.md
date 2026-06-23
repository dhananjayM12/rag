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
| Worker | APScheduler — auto-fetches official feeds on a schedule |
| Database | PostgreSQL + pgvector |
| AI | Local/open models — hashing or sentence-transformers embeddings; extractive or local Ollama LLM |

Content is sourced from **official/open resources only** (UPSC syllabus, NCERT,
the Constitution, IMD, NITI Aayog, ministries, PIB, PRS, RBI) — safe for
commercial use.

## Quick start (Docker)

```bash
docker compose up --build
```

Brings up the full stack — `db` (Postgres + pgvector), `backend`, `frontend`,
and `worker`:

- Frontend: http://localhost:3000  (start at **/flowchart**)
- Backend API: http://localhost:8000  (`/docs` for OpenAPI)

The **backend** runs migrations, seeds the syllabus, and indexes seeded content
on startup. The **worker** fetches the configured official feeds immediately and
then every 6 hours (configurable), so current affairs stay fresh with no manual
step. Failing feeds are skipped, never crashing the loop.

### Optional: local LLM (Ollama) for generative answers

```bash
LLM_BACKEND=ollama docker compose --profile llm up --build
docker compose exec ollama ollama pull llama3   # one-time model pull
```

Without this, answers are **extractive** (faithful, grounded source text) and
need no model download.

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
    models.py          # SyllabusNode tree, Content, ContentChunk, Article(+Chunk)
    routers/           # syllabus, content, rag, evaluate (stub), articles
    seed/              # syllabus.json + loader
    services/embeddings.py  # hashing / sentence-transformers embedders
    rag/               # chunk, ingest, retriever, generator, ingest_sources
    rag/sources/       # SourceConnector + RSS connectors
    worker.py          # APScheduler-driven auto-ingestion loop
  alembic/             # migrations (creates pgvector extension)
  tests/               # pytest, SQLite-backed
frontend/
  app/                 # /, /flowchart, /topic/[slug], /ask, /evaluate, /current-affairs
  components/          # FlowChart, SyllabusNode, ContentDrawer
  lib/                 # api client, dagre layout
docker-compose.yml     # db + backend + frontend + worker (+ optional ollama)
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

## Automated current-affairs ingestion (Milestone 4)

The `worker` service auto-fetches the official feeds — **no manual step**:

- Runs an initial ingestion on startup, then every `INGEST_INTERVAL_MINUTES`
  (default **360** = 6 hours). Driven by `app/worker.py` (APScheduler).
- Feeds: `SOURCE_FEEDS` ("Name|url" RSS pairs; PIB, PRS, RBI by default) —
  official/open only, commercially safe. A failing feed is **skipped, not
  fatal**, so the loop survives outages.
- Connectors in `app/rag/sources/` (RSS via the standard library; add a source
  by implementing `SourceConnector`). Articles are de-duped on
  `(source, external_id)`, chunked + embedded into `article_chunks`, and
  retrieved alongside seeded content so `/ask` can cite current affairs.
  Endpoint `GET /api/articles`; UI at `/current-affairs`.

Manual one-off run (e.g. for local dev): `python -m app.rag.ingest_sources`.

## Roadmap (scaffolded, build next)

- **Answer evaluation** (`/api/evaluate`): rubric-based grading with a local LLM.
- **Tag articles to syllabus nodes** so current affairs appear on the relevant
  micro-topic pages.
- **Student features**: progress tracking + spaced revision, previous-year-question
  mapping to leaf nodes, current-affairs feed tagged to syllabus nodes, auth +
  subscription tiers, PWA/offline.
