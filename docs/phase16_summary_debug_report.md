# Phase 16A Summary Debug Report

## Issue Diagnosis
The user reported that the Summary Agent would successfully complete the extraction task (progress reaching 100%), but the summary would not render on the frontend. 

## Investigation Findings
1. **Flow Trace:**
   - Client sends `POST /agent/summary/{paper_id}` -> Task created.
   - Background thread `_run_summary` executes `coordinator.route_summary(paper_id)`.
   - `route_summary` invokes `summary_agent.summarize_paper(paper_id)`.
   - `SummaryAgent` retrieves context, invokes the LLM, saves the SQLAlchemy `Summary` instance, and returns it.
   - The thread calls `task_service.mark_done(task_id, result=summary_obj)` and finally calls `db.close()`.

2. **The Bug:**
   - The SQLAlchemy object `summary_obj` was persisted in the in-memory `task_service`. 
   - When the client subsequently polled `GET /agent/summary/result/{task_id}`, FastAPI's Pydantic serialization attempted to access attributes on `summary_obj` (like `.paper_id`). 
   - Because `db.close()` was already called, this triggered a lazy-loading `DetachedInstanceError`, causing a silent 500 error on the backend and failing the frontend rendering.

## Resolution
The thread now serializes `summary_obj` into a flat Python dictionary before invoking `task_service.mark_done()`. The endpoint safely returns the dictionary data, ensuring stable JSON conversion.

## Enhancements
- Extensive end-to-end tracing logs were added.
- Caching logic was introduced to skip regeneration if a summary for the given `paper_id` already exists.
