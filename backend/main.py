from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db
from .routers import search, upload, agent

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search)
app.include_router(upload)
app.include_router(agent)

@app.on_event("startup")
def startup_event():
    init_db()
    # Pre-load heavy models on startup to avoid blocking the first request
    from .services.llm_service import llm_service
    from .services.embedding_service import embedding_service
    import threading
    
    # Load embedding model immediately
    embedding_service.load()
    
    # Load LLM in a background thread so the server port binds quickly
    threading.Thread(target=llm_service.load, daemon=True).start()

@app.get("/")
def root():
    return {"message": "IEEE Research Assistant backend is running."}
