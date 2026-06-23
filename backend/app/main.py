from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import content, evaluate, rag, syllabus

app = FastAPI(
    title="UPSC Study App API",
    description="Backend for the UPSC study app: syllabus flowchart, "
    "RAG Q&A (stub), and answer evaluation (stub).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(syllabus.router)
app.include_router(content.router)
app.include_router(rag.router)
app.include_router(evaluate.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
