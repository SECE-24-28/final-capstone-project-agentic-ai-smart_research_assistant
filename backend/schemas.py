from typing import List, Optional
from pydantic import BaseModel, ConfigDict

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
    similarity_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class SummaryResponse(BaseModel):
    paper_id: int
    objective: Optional[str] = None
    methodology: Optional[str] = None
    findings: Optional[str] = None
    limitations: Optional[str] = None
    contributions: Optional[str] = None
    raw_text: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

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


class FinalReportResponse(BaseModel):
    id: int
    topic: str
    paper_ids: str
    content: str

    model_config = ConfigDict(from_attributes=True)


class TaskStatusResponse(BaseModel):
    task_id: str
    task_type: str
    status: str          # pending | running | done | failed
    progress: int        # 0-100
    current_step: str
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None


class TaskStartResponse(BaseModel):
    task_id: str
    message: str


# ─────────────────────────────────────────────────────────────────────────────
#  AUTO MODE SCHEMAS  (Phase 15)
# ─────────────────────────────────────────────────────────────────────────────

class AutoRequest(BaseModel):
    query: str
    paper_ids: Optional[List[int]] = None   # pre-selected papers (optional)


class AutoStartResponse(BaseModel):
    task_id: str
    workflow: str
    intent: str
    topic: str
    estimated_steps: int
    estimated_duration: str
    message: str


class WorkflowStepSchema(BaseModel):
    step_number: int
    agent_name: str
    description: str
    status: str   # pending | running | done | skipped | failed


class AutoResultResponse(BaseModel):
    task_id: str
    workflow: str
    intent: str
    topic: str
    result_type: str            # text | papers | mixed
    final_text: str
    papers: Optional[List[dict]] = None
    summaries: Optional[List[dict]] = None
    comparison: Optional[str] = None
    chat_answer: Optional[str] = None
    steps: Optional[List[WorkflowStepSchema]] = None
    error: Optional[str] = None
