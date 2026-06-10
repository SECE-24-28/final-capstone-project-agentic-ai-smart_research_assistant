from pydantic import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
VECTOR_DIR = BASE_DIR / "vectorstore"
DATABASE_FILE = BASE_DIR / "database" / "research_assistant.db"

class Settings(BaseSettings):
    app_name: str = "IEEE Research Assistant"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    llm_model_name: str = "Qwen/Qwen2.5-1.5B-Instruct"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    chroma_collection_name: str = "research_chunks"

    max_pdf_chunk_chars: int = 2000
    max_rag_chunks: int = 5

    class Config:
        env_file = ".env"

settings = Settings()
