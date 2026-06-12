from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..schemas import (
    ComparisonRequest, ComparisonResponse, CitationRequest, CitationResponse,
    ChatRequest, ChatResponse, SummaryResponse,
    TaskStatusResponse, TaskStartResponse,
    AutoRequest, AutoStartResponse, AutoResultResponse, WorkflowStepSchema,
)
import re
import threading
import logging

logger = logging.getLogger(__name__)
from ..agents.coordinator import CoordinatorAgent
from ..agents.summary_agent import SummaryAgent
from ..agents.comparison_agent import ComparisonAgent
from ..agents.chat_agent import ChatAgent
from ..services.citation_service import citation_service
from ..services.llm_service import llm_service
from ..services.embedding_service import embedding_service
from ..services.vector_store import vector_store
from ..services.task_service import task_service
from ..models import Summary, Paper, CoordinatorRun
from ..agents.coordinator_agent import (
    AutonomousCoordinator, classify_intent, extract_topic, build_workflow,
)

router = APIRouter(prefix="/agent", tags=["agent"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────────────────────
#  TASK STATUS ENDPOINT
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/task/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    """Poll the progress of a long-running agent task."""
    record = task_service.get(task_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatusResponse(**record.to_dict())


# ─────────────────────────────────────────────────────────────────────────────
#  SYNCHRONOUS / INSTANT ENDPOINTS (Chat, Citation)
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
#  LONG-RUNNING ENDPOINTS WITH TASK TRACKING
# ─────────────────────────────────────────────────────────────────────────────

def _run_summary(task_id: str, paper_id: int):
    """Background worker for summary generation with progress updates."""
    logger.info(f"Worker Thread Start: _run_summary for task_id={task_id}, paper_id={paper_id}")
    db = SessionLocal()
    try:
        task_service.update(task_id, status="running", progress=5,
                            current_step="Loading paper data…")
        coordinator = CoordinatorAgent(db)

        task_service.update(task_id, progress=15,
                            current_step="Retrieving document chunks…")

        logger.info(f"Summary Generation Start: Coordinator routing summary for paper_id={paper_id}")
        summary_obj = coordinator.route_summary(paper_id)
        logger.info(f"Summary Generation End: summary object retrieved for task_id={task_id}")

        # Convert SQLAlchemy model to dict to avoid DetachedInstanceError after db.close()
        result_data = {
            "id": summary_obj.id,
            "paper_id": summary_obj.paper_id,
            "objective": summary_obj.objective,
            "methodology": summary_obj.methodology,
            "findings": summary_obj.findings,
            "limitations": summary_obj.limitations,
            "contributions": summary_obj.contributions,
            "raw_text": summary_obj.raw_text
        }

        task_service.mark_done(task_id, result=result_data)
        logger.info(f"Database Save & Task Done: task_id={task_id}")
    except Exception as exc:
        logger.error(f"Error in _run_summary for task_id={task_id}: {exc}", exc_info=True)
        task_service.mark_failed(task_id, str(exc))
    finally:
        db.close()


@router.post("/summary", response_model=TaskStartResponse)
def summary(paper_id: int):
    """Start async summary generation. Checks cache synchronously before spawning thread."""
    from ..models import Summary as SummaryModel
    record = task_service.create("summary")
    logger.info(f"Task_id creation: POST /agent/summary generated task_id={record.task_id} for paper_id={paper_id}")

    # Fast-path cache: check DB synchronously before spawning thread
    db = SessionLocal()
    try:
        existing = db.query(SummaryModel).filter(SummaryModel.paper_id == paper_id).first()
        if existing:
            logger.info(f"Cache hit (sync): Summary exists for paper_id={paper_id}. Marking task done immediately.")
            result_data = {
                "id": existing.id,
                "paper_id": existing.paper_id,
                "objective": existing.objective,
                "methodology": existing.methodology,
                "findings": existing.findings,
                "limitations": existing.limitations,
                "contributions": existing.contributions,
                "raw_text": existing.raw_text
            }
            task_service.mark_done(record.task_id, result=result_data)
            return TaskStartResponse(task_id=record.task_id, message="Summary served from cache")
    finally:
        db.close()

    # No cache hit: spawn background thread for full LLM generation
    threading.Thread(
        target=_run_summary,
        args=(record.task_id, paper_id),
        daemon=True,
    ).start()
    return TaskStartResponse(task_id=record.task_id,
                             message="Summary generation started")


@router.get("/summary/result/{task_id}", response_model=SummaryResponse)
def summary_result(task_id: str):
    """Retrieve the completed summary result for a task."""
    logger.info(f"GET /agent/summary/result/{task_id} requested")
    record = task_service.get(task_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if record.status == "failed":
        raise HTTPException(status_code=500, detail=record.error)
    if record.status != "done" or record.result is None:
        raise HTTPException(status_code=202, detail="Task still in progress")

    logger.info(f"GET /agent/summary/result/{task_id} returning valid SummaryResponse")
    return record.result




def _run_comparison(task_id: str, paper_ids: list, dimension: str | None):
    db = SessionLocal()
    try:
        task_service.update(task_id, status="running", progress=5,
                            current_step="Loading selected papers…")
        coordinator = CoordinatorAgent(db)

        task_service.update(task_id, progress=20,
                            current_step="Extracting paper metadata…")
        comparison = coordinator.route_comparison(paper_ids, dimension)

        task_service.mark_done(task_id, result=comparison)
    except Exception as exc:
        task_service.mark_failed(task_id, str(exc))
    finally:
        db.close()


@router.post("/compare", response_model=TaskStartResponse)
def compare(payload: ComparisonRequest):
    """Start async comparison. Poll /agent/task/{task_id} for progress."""
    record = task_service.create("comparison")
    threading.Thread(
        target=_run_comparison,
        args=(record.task_id, payload.paper_ids, payload.dimension),
        daemon=True,
    ).start()
    return TaskStartResponse(task_id=record.task_id,
                             message="Comparison started")


@router.get("/compare/result/{task_id}", response_model=ComparisonResponse)
def compare_result(task_id: str):
    record = task_service.get(task_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if record.status == "failed":
        raise HTTPException(status_code=500, detail=record.error)
    if record.status != "done" or record.result is None:
        raise HTTPException(status_code=202, detail="Task still in progress")
    comparison = record.result
    return ComparisonResponse(name=comparison.name, result=comparison.result)


# ─────────────────────────────────────────────────────────────────────────────
#  STREAMING ENDPOINTS  (SSE – text/event-stream)
# ─────────────────────────────────────────────────────────────────────────────

def _sse_token_generator(token_stream):
    """Wrap a token generator in SSE format: `data: <token>\n\n`"""
    try:
        for token in token_stream:
            # Escape newlines inside the token so SSE framing is preserved
            safe = token.replace("\n", "\\n")
            yield f"data: {safe}\n\n"
        yield "event: done\ndata: [DONE]\n\n"
    except Exception as exc:
        yield f"event: error\ndata: {str(exc)}\n\n"


@router.post("/chat/stream")
def chat_stream(payload: ChatRequest, db: Session = Depends(get_db)):
    """Stream Chat Agent responses token-by-token via SSE."""
    try:
        agent = ChatAgent(db)
        context_chunks = []

        # Only search vector store when paper_ids are provided
        if payload.paper_ids:
            query_embedding = embedding_service.embed_texts([payload.question])
            where_filter = None
            if len(payload.paper_ids) == 1:
                where_filter = {"paper_id": payload.paper_ids[0]}
            else:
                where_filter = {"paper_id": {"$in": payload.paper_ids}}

            if vector_store.collection is not None:
                results = vector_store.query(query_embedding, n_results=5, where=where_filter)
                if results and "documents" in results and results["documents"]:
                    context_chunks = results["documents"][0]

            # Abstract fallback when vector chunks empty but papers specified
            if not context_chunks:
                from ..models import Paper as PaperModel
                papers = db.query(PaperModel).filter(PaperModel.id.in_(payload.paper_ids)).all()
                for p in papers:
                    if p.abstract:
                        context_chunks.append(f"Abstract of '{p.title}': {p.abstract}")
                
                if not context_chunks:
                    def no_context():
                        msg = "I could not find any relevant information in the selected documents to answer your question."
                        yield f"data: {msg}\n\n"
                        yield "event: done\ndata: [DONE]\n\n"
                    return StreamingResponse(no_context(), media_type="text/event-stream")

        if context_chunks:
            # Document-grounded mode
            system_prompt = (
                "You are a strict, grounded academic research assistant. "
                "Answer ONLY using the provided document context. Do NOT hallucinate."
            )
            prompt = agent.build_prompt(payload.question, context_chunks)
        else:
            # General assistant mode - no documents selected
            system_prompt = (
                "You are a helpful, knowledgeable academic research assistant. "
                "Answer the user's question clearly and concisely. "
                "If asked for ideas, projects, or explanations, provide helpful, accurate information."
            )
            prompt = payload.question

        token_stream = llm_service.stream_generate(prompt, max_tokens=384, system_prompt=system_prompt)
        return StreamingResponse(_sse_token_generator(token_stream), media_type="text/event-stream")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/summary/stream")
def summary_stream(paper_id: int, db: Session = Depends(get_db)):
    """Stream Summary Agent responses token-by-token via SSE."""
    try:
        agent = SummaryAgent(db)
        paper = db.get(Paper, paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")

        query = f"Summarize this academic paper. Paper title: {paper.title}."
        if paper.abstract:
            query += f" Abstract: {paper.abstract}"

        top_chunks = []
        if vector_store.collection is not None:
            embeddings = embedding_service.embed_texts([query])
            results = vector_store.query(embeddings, n_results=5, where={"paper_id": paper.id})
            for item in results.get("documents", [[]])[0]:
                top_chunks.append(item)

        prompt = agent.build_prompt(query, top_chunks)
        token_stream = llm_service.stream_generate(prompt, max_tokens=1024)
        return StreamingResponse(_sse_token_generator(token_stream), media_type="text/event-stream")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/compare/stream")
def compare_stream(payload: ComparisonRequest, db: Session = Depends(get_db)):
    """Stream Comparison Agent responses token-by-token via SSE."""
    try:
        agent = ComparisonAgent(db)
        papers = db.query(Paper).filter(Paper.id.in_(payload.paper_ids)).all()
        if len(papers) < 2:
            raise HTTPException(status_code=400, detail="Comparison requires at least two papers")

        system_prompt = (
            "You are an expert academic research analyst. "
            "Compare the papers based strictly on the provided data. Do NOT hallucinate."
        )
        prompt = agent.build_prompt(papers, payload.dimension)
        token_stream = llm_service.stream_generate(prompt, max_tokens=1536, system_prompt=system_prompt)
        return StreamingResponse(_sse_token_generator(token_stream), media_type="text/event-stream")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ───────────────────────────────────────────────────────────────────────────────
#  AUTO MODE (Phase 15) – Autonomous Research Coordinator
# ───────────────────────────────────────────────────────────────────────────────

# In-memory store for completed coordinator results (task_id → CoordinatorResult)
_auto_results: dict = {}
_auto_results_lock = threading.Lock()


def _run_auto_coordinator(task_id: str, query: str, run_id: int):
    """Background worker: run the full autonomous pipeline and save result."""
    db = SessionLocal()
    try:
        task_service.update(task_id, status="running", progress=5,
                            current_step="Classifying intent…")
        ac = AutonomousCoordinator(db, task_service=task_service, task_id=task_id)
        result = ac.run(query)

        # Persist result in memory for /auto/result fetch
        with _auto_results_lock:
            _auto_results[task_id] = result

        # Update coordinator_run record
        run = db.get(CoordinatorRun, run_id)
        if run:
            from datetime import datetime
            run.status = "done" if not result.error else "failed"
            run.result_type = result.result_type
            run.completed_at = datetime.utcnow()
            db.commit()

        task_service.mark_done(task_id, result=result.to_dict())
    except Exception as exc:
        task_service.mark_failed(task_id, str(exc))
        run = db.get(CoordinatorRun, run_id)
        if run:
            run.status = "failed"
            db.commit()
    finally:
        db.close()


@router.post("/auto", response_model=AutoStartResponse)
def auto_coordinator(payload: AutoRequest):
    """
    Autonomous Research Coordinator endpoint.

    1. Classifies the user query intent.
    2. Builds a workflow plan.
    3. Starts a background task that executes all required agents.
    4. Returns a task_id + workflow plan so the frontend can poll progress.
    """
    intent  = classify_intent(payload.query)
    topic   = extract_topic(payload.query, intent)
    plan    = build_workflow(intent, topic)

    # Create task record
    record  = task_service.create("auto_coordinator")
    task_id = record.task_id

    # Persist coordinator run to DB
    db = SessionLocal()
    try:
        run = CoordinatorRun(
            workflow=plan.workflow_name,
            intent=intent.value,
            query=payload.query,
            topic=topic,
            task_id=task_id,
            status="running",
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        run_id = run.id
    finally:
        db.close()

    # Launch background pipeline
    threading.Thread(
        target=_run_auto_coordinator,
        args=(task_id, payload.query, run_id),
        daemon=True,
    ).start()

    return AutoStartResponse(
        task_id=task_id,
        workflow=plan.workflow_name,
        intent=intent.value,
        topic=topic,
        estimated_steps=len(plan.steps),
        estimated_duration=plan.estimated_duration,
        message=f"Auto pipeline started: {plan.workflow_name}",
    )


@router.get("/auto/result/{task_id}", response_model=AutoResultResponse)
def auto_result(task_id: str):
    """Retrieve the complete result of a finished Auto Mode pipeline."""
    # Check task service first
    task = task_service.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status == "failed":
        raise HTTPException(status_code=500, detail=task.error or "Pipeline failed")
    if task.status != "done":
        raise HTTPException(status_code=202, detail="Pipeline still in progress")

    # Retrieve full result from in-memory store
    with _auto_results_lock:
        result = _auto_results.get(task_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")

    plan = result.workflow
    steps = [
        WorkflowStepSchema(
            step_number=s.step_number,
            agent_name=s.agent_name,
            description=s.description,
            status=s.status,
        )
        for s in plan.steps
    ]

    return AutoResultResponse(
        task_id=task_id,
        workflow=plan.workflow_name,
        intent=plan.intent.value,
        topic=plan.topic,
        result_type=result.result_type,
        final_text=result.final_text or "",
        papers=result.papers or [],
        summaries=result.summaries or [],
        comparison=result.comparison,
        chat_answer=result.chat_answer,
        steps=steps,
        error=result.error,
    )
