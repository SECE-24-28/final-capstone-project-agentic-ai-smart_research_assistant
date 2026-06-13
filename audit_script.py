import asyncio
import httpx
from sqlalchemy import text
from backend.database import engine, SessionLocal
from backend.models import Paper, Summary, Comparison, Citation, FinalReport, ChatHistory
from backend.services.ollama_service import ollama_service
from backend.config import settings
import json
import os

results = {}

def check_db():
    db_status = {"tables": [], "wal": False, "schema_ok": True}
    inspector = __import__('sqlalchemy').inspect(engine)
    tables = inspector.get_table_names()
    db_status["tables"] = tables
    
    with engine.connect() as conn:
        res = conn.execute(text("PRAGMA journal_mode;"))
        mode = res.scalar()
        db_status["wal"] = (mode.upper() == "WAL")
    results["database"] = db_status

def check_ollama():
    try:
        ok, lat, msg = ollama_service.health_check()
        results["ollama"] = {"ok": ok, "model": settings.ollama_model, "msg": msg, "latency": lat}
    except Exception as e:
        results["ollama"] = {"ok": False, "error": str(e)}

async def run_api_tests():
    api_results = {}
    async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=120.0) as client:
        # Search Validation
        try:
            r = await client.get("/search/topic", params={"query": "Federated Learning", "limit": 2})
            r.raise_for_status()
            data = r.json()
            api_results["search"] = {"ok": True, "count": len(data), "has_scores": all("similarity_score" in p for p in data)}
            
            if data:
                # Add a paper for summary validation
                p_r = await client.post("/search/add", json=data[0])
                paper_id = p_r.json().get("id")
                api_results["search"]["paper_id"] = paper_id
                
                # Summary Validation
                if paper_id:
                    s_r = await client.post(f"/agent/summary?paper_id={paper_id}")
                    s_data = s_r.json()
                    api_results["summary"] = {"ok": True, "task_id": s_data.get("task_id")}
                    
                    # Wait for task
                    task_id = s_data.get("task_id")
                    if task_id:
                        for _ in range(30):
                            t_r = await client.get(f"/agent/task/{task_id}")
                            t_data = t_r.json()
                            if t_data.get("status") == "done":
                                api_results["summary"]["result"] = t_data.get("result")
                                break
                            await asyncio.sleep(2)
        except Exception as e:
            api_results["search"] = {"ok": False, "error": str(e)}
            
    results["api"] = api_results

check_db()
check_ollama()
asyncio.run(run_api_tests())

with open("audit_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("Audit script finished.")
