from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..services.pdf_service import pdf_service
from ..models import Paper
from ..schemas import UploadResponse

router = APIRouter(prefix="/upload", tags=["upload"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/pdf", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    saved_path = pdf_service.save_upload(file.filename, contents)
    text = pdf_service.extract_text(saved_path)
    paper = Paper(title=file.filename, file_path=str(saved_path))
    if text:
        paper.abstract = text[:1000]
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return UploadResponse(paper_id=paper.id, file_path=str(saved_path), message="PDF uploaded and saved successfully.")
