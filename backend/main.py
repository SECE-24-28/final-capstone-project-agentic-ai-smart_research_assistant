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

app.include_router(search.router)
app.include_router(upload.router)
app.include_router(agent.router)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def root():
    return {"message": "IEEE Research Assistant backend is running."}
