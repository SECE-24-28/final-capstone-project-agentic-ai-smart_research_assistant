from typing import List, Optional
from pydantic import BaseModel

class PaperBase(BaseModel):
    title: str
    authors: Optional[str] = None
    abstract: Optional[str] = None
    year: Optional[str] = None
    doi: Optional[str] = None
    journal: Optional[str] = None
    source: Optional[str] = None

class SearchTopicRequest(BaseModel):
    topic: str
    limit: Optional[int] = 5

class PaperCreate(PaperBase):
    pass

class PaperResponse(PaperBase):
    id: int

    class Config:
        orm_mode = True

class SummaryResponse(BaseModel):
    paper_id: int
    objective: Optional[str]
    methodology: Optional[str]
    findings: Optional[str]
    limitations: Optional[str]
    contributions: Optional[str]

    class Config:
        orm_mode = True

class ComparisonRequest(BaseModel):
    paper_ids: List[int]
    dimension: Optional[str] = None

class ComparisonResponse(BaseModel):
    name: str
    result: str

class CitationRequest(BaseModel):
    paper_id: int
    citation_type: str = "journal"

class CitationResponse(BaseModel):
    citation_text: str

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    paper_ids: Optional[List[int]] = None

class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = None

class UploadResponse(BaseModel):
    paper_id: int
    file_path: str
    message: str

class GapAnalysisResponse(BaseModel):
    id: int
    topic: str
    paper_ids: str
    result: str

    class Config:
        orm_mode = True
