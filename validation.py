import sys
import logging

logging.basicConfig(level=logging.INFO)

print("--- Starting Runtime Validation ---")

# Test 1: Database
try:
    from backend.database import init_db
    init_db()
    print("[OK] Database initialized")
except Exception as e:
    print(f"[FAIL] Database initialization failed: {e}")
    sys.exit(1)

# Test 2: ChromaDB
try:
    from backend.services.vector_store import vector_store
    vector_store.initialize()
    print("[OK] ChromaDB initialized")
except Exception as e:
    print(f"[FAIL] ChromaDB initialization failed: {e}")
    sys.exit(1)

# Test 3: Embedding Model
try:
    from backend.services.embedding_service import embedding_service
    embedding_service.load()
    print("[OK] Embedding model loaded")
except Exception as e:
    print(f"[FAIL] Embedding model load failed: {e}")
    sys.exit(1)

# Test 4: LLM Model
try:
    from backend.services.llm_service import llm_service
    llm_service.load()
    print("[OK] Qwen LLM loaded")
except Exception as e:
    print(f"[FAIL] Qwen LLM load failed: {e}")
    sys.exit(1)

print("--- Validation Complete ---")
