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
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        contents = await file.read()
        saved_path = pdf_service.save_upload(file.filename, contents)
        text = pdf_service.extract_text(saved_path)
        paper = Paper(title=file.filename, file_path=str(saved_path))
        if text:
            paper.abstract = text[:1000]
        db.add(paper)
        db.commit()
        db.refresh(paper)
        
        # RAG pipeline: chunk and store in VectorStore
        if text:
            logger.info(f"Chunking text for paper_id={paper.id}")
            chunks = pdf_service.chunk_text(text)
            if chunks:
                from ..services.embedding_service import embedding_service
                from ..services.vector_store import vector_store
                
                logger.info(f"Generating embeddings for {len(chunks)} chunks.")
                embeddings = embedding_service.embed_texts(chunks)
                
                ids = [f"paper_{paper.id}_chunk_{i}" for i in range(len(chunks))]
                metadatas = [{"paper_id": paper.id} for i in range(len(chunks))]
                
                logger.info(f"Adding {len(chunks)} chunks to vector store.")
                vector_store.add_documents(ids=ids, texts=chunks, metadatas=metadatas, embeddings=embeddings)
                logger.info(f"Successfully stored chunks in VectorStore for paper_id={paper.id}")

    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        logger.error(f"Upload failed: {error_msg}")
        raise HTTPException(status_code=500, detail=str(e) + "\n" + error_msg)

    return UploadResponse(paper_id=paper.id, file_path=str(saved_path), message="PDF uploaded and saved successfully.")
