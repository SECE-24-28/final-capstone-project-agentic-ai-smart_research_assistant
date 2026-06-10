from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..schemas import PaperCreate, PaperResponse
from ..agents.search_agent import SearchAgent

router = APIRouter(prefix="/search", tags=["search"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/paper", response_model=PaperResponse)
def create_paper(paper: PaperCreate, db: Session = Depends(get_db)):
    agent = SearchAgent(db)
    try:
        created = agent.create_paper(paper.dict())
        return created
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/papers", response_model=list[PaperResponse])
def list_papers(db: Session = Depends(get_db)):
    agent = SearchAgent(db)
    return agent.get_papers()
