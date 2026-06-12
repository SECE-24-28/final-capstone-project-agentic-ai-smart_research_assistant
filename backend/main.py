from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db
from .routers import search, upload, agent, report

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search)
app.include_router(upload)
app.include_router(agent)
app.include_router(report)


@app.on_event("startup")
def startup_event():
    init_db()
    from .services.llm_service import llm_service
    from .services.embedding_service import embedding_service
    from .services.ollama_service import ollama_service
    import logging

    logger = logging.getLogger("backend.main")

    # Check Ollama status and log provider info
    is_ollama_ready, latency, msg = ollama_service.health_check()
    if is_ollama_ready:
        logger.info("LLM Provider: Ollama")
        logger.info(f"Model: {settings.ollama_model}")
        logger.info(f"Status: Connected (Latency: {latency:.3f}s)")
    else:
        logger.error(f"⚠️  Ollama server not running on localhost:11434 (Error: {msg})")
        logger.error("Backend running with NO LLM Provider available. Generation will fail.")

    # Load embedding model immediately (blocking – fast)
    embedding_service.load()

    # LLM load is a no-op for Ollama (model lives in the Ollama daemon)
    llm_service.load()


@app.get("/")
def root():
    return {"message": "IEEE Research Assistant backend is running."}


# ── Convenience alias so frontend can GET /reports (plural) ─────────────────
from fastapi import Request
from fastapi.responses import JSONResponse
from .database import SessionLocal
from .services.report_service import report_service as _rs


@app.get("/reports")
def list_all_reports():
    """Top-level /reports alias for the frontend."""
    db = SessionLocal()
    try:
        reports = _rs.list_reports(db)
        return [
            {
                "report_id": r.id,
                "title": r.title or r.topic,
                "topic": r.topic,
                "template_type": r.template_type,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reports
        ]
    finally:
        db.close()
