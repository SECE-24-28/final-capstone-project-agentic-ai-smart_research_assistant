from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..schemas import ComparisonRequest, ComparisonResponse, CitationRequest, CitationResponse, ChatRequest, ChatResponse, SummaryResponse
from ..agents.coordinator import CoordinatorAgent
from ..services.citation_service import citation_service
from ..models import Summary

router = APIRouter(prefix="/agent", tags=["agent"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/summary", response_model=SummaryResponse)
def summary(paper_id: int, db: Session = Depends(get_db)):
    coordinator = CoordinatorAgent(db)
    try:
        summary_obj = coordinator.route_summary(paper_id)
        return summary_obj
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/compare", response_model=ComparisonResponse)
def compare(payload: ComparisonRequest, db: Session = Depends(get_db)):
    coordinator = CoordinatorAgent(db)
    try:
        comparison = coordinator.route_comparison(payload.paper_ids, payload.dimension)
        return ComparisonResponse(name=comparison.name, result=comparison.result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    coordinator = CoordinatorAgent(db)
    try:
        answer, sources = coordinator.route_chat(payload.question, payload.session_id, payload.paper_ids)
        return ChatResponse(answer=answer, sources=sources)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/citation", response_model=CitationResponse)
def citation(payload: CitationRequest):
    try:
        citation = citation_service.save_citation(payload.paper_id, payload.citation_type)
        return CitationResponse(citation_text=citation.citation_text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
