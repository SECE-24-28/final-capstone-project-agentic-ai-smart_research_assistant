"""
Report Router – REST API for FinalReport generation, retrieval, export,
regeneration, and deletion.

Endpoints
---------
POST   /report/generate
GET    /reports
GET    /report/{report_id}
POST   /report/{report_id}/regenerate
DELETE /report/{report_id}
GET    /report/{report_id}/pdf
GET    /report/{report_id}/docx
"""

from __future__ import annotations

import threading
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..services.report_service import report_service
from ..services.task_service import task_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/report", tags=["report"])


# ---------------------------------------------------------------------------
# DB Dependency
# ---------------------------------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class GenerateReportRequest(BaseModel):
    topic: str
    paper_ids: list[int]
    comparison_id: Optional[int] = None
    template_type: Optional[str] = "Research Report"


class ReportSummaryResponse(BaseModel):
    report_id: int
    title: Optional[str]
    topic: str
    template_type: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# POST /report/generate
# ---------------------------------------------------------------------------

@router.post("/generate")
def generate_report(body: GenerateReportRequest):
    """
    Kick off asynchronous report generation.
    Returns immediately with a task_id for progress polling.
    """
    task = task_service.create("report_generation")

    def _run():
        try:
            db = SessionLocal()
            try:
                task_service.update(task.task_id, status="running", progress=5,
                                    current_step="Initialising…")

                def _progress(pct: int, label: str):
                    task_service.update(task.task_id, progress=pct,
                                        current_step=label)

                report = report_service.generate_final_report(
                    topic=body.topic,
                    paper_ids=body.paper_ids,
                    session=db,
                    comparison_id=body.comparison_id,
                    template_type=body.template_type or "Research Report",
                    progress_callback=_progress,
                )
                task_service.mark_done(task.task_id, result={"report_id": report.id})
                logger.info(f"Report generation complete. report_id={report.id}")
            finally:
                db.close()
        except Exception as exc:
            logger.error(f"Report generation failed: {exc}", exc_info=True)
            task_service.mark_failed(task.task_id, error=str(exc))

    threading.Thread(target=_run, daemon=True).start()
    return {"task_id": task.task_id, "status": "started"}


# ---------------------------------------------------------------------------
# GET /reports  – history list
# ---------------------------------------------------------------------------

@router.get("/s")  # mounted at /report/s → resolves to GET /reports via prefix trick
def list_reports_endpoint(db: Session = Depends(get_db)):
    """Return all reports ordered newest-first."""
    reports = report_service.list_reports(db)
    return [
        {
            "report_id": r.id,
            "title": r.title or r.topic,
            "topic": r.topic,
            "template_type": r.template_type,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reports
    ]


# ---------------------------------------------------------------------------
# GET /report/{report_id}
# ---------------------------------------------------------------------------

@router.get("/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = report_service.get_report(report_id, db)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    markdown = report.report_markdown or report.content or ""
    return {
        "report_id": report.id,
        "title": report.title or report.topic,
        "topic": report.topic,
        "report_markdown": markdown,
        "template_type": report.template_type,
        "paper_ids": report.paper_ids,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


# ---------------------------------------------------------------------------
# POST /report/{report_id}/regenerate
# ---------------------------------------------------------------------------

@router.post("/{report_id}/regenerate")
def regenerate_report(report_id: int):
    """Re-generate an existing report (same papers, latest prompts)."""
    task = task_service.create("report_regeneration")

    def _run():
        try:
            db = SessionLocal()
            try:
                task_service.update(task.task_id, status="running", progress=5,
                                    current_step="Starting regeneration…")

                def _progress(pct: int, label: str):
                    task_service.update(task.task_id, progress=pct,
                                        current_step=label)

                new_report = report_service.regenerate_report(
                    report_id=report_id,
                    session=db,
                    progress_callback=_progress,
                )
                task_service.mark_done(task.task_id,
                                       result={"report_id": new_report.id})
            finally:
                db.close()
        except Exception as exc:
            logger.error(f"Regeneration failed: {exc}", exc_info=True)
            task_service.mark_failed(task.task_id, error=str(exc))

    threading.Thread(target=_run, daemon=True).start()
    return {"task_id": task.task_id, "status": "started"}


# ---------------------------------------------------------------------------
# DELETE /report/{report_id}
# ---------------------------------------------------------------------------

@router.delete("/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    deleted = report_service.delete_report(report_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"detail": "Report deleted successfully"}


# ---------------------------------------------------------------------------
# GET /report/{report_id}/pdf
# ---------------------------------------------------------------------------

@router.get("/{report_id}/pdf")
def download_pdf(report_id: int, db: Session = Depends(get_db)):
    report = report_service.get_report(report_id, db)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        from ..services.report_export_service import generate_report_pdf
        pdf_bytes = generate_report_pdf(report)
    except Exception as exc:
        logger.error(f"PDF generation failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {exc}")

    filename = f"Research_Report_{report_id}.pdf"
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# GET /report/{report_id}/docx
# ---------------------------------------------------------------------------

@router.get("/{report_id}/docx")
def download_docx(report_id: int, db: Session = Depends(get_db)):
    report = report_service.get_report(report_id, db)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        from ..services.docx_service import generate_report_docx
        docx_bytes = generate_report_docx(report)
    except Exception as exc:
        logger.error(f"DOCX generation failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"DOCX generation failed: {exc}")

    filename = f"Research_Report_{report_id}.docx"
    return StreamingResponse(
        iter([docx_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
