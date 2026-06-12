# Phase 18: Research Report Generation & Export System

## Executive Summary
The Smart Research Assistant has been successfully upgraded into an end-to-end research workflow platform. Users can now search for papers, generate summaries, run comparative analyses, and finally synthesize all of this cached data into a comprehensive, formal IEEE-style **Research Report**. 

The pipeline guarantees high performance and cost-efficiency by strictly reusing the cached outputs from previous agents (Summary Agent, Comparison Agent) and directly injecting factual bibliographic references via the Citation Service to eliminate LLM reference hallucinations.

## 1. Database Schema Extension
The `FinalReport` model in `backend/models.py` was extended gracefully. To ensure no data loss of existing placeholders, we kept the legacy `content` column and added new specific fields:
- `title` (String)
- `summary_ids` (String)
- `comparison_id` (Integer)
- `report_markdown` (Text - Primary output destination)
- `template_type` (String - "Research Report")

## 2. Report Generation Pipeline
Located in `backend/services/report_service.py`, the pipeline executes asynchronously via the task tracking system:
1. **Load Selected Papers**: Retrieves target papers from SQLite.
2. **Load Cached Summaries**: Extracts the most recent `Summary` for each paper to avoid expensive re-runs.
3. **Load Cached Comparison**: Automatically links the most relevant `Comparison` result covering the selected papers.
4. **Ollama Generation**: A structured prompt is sent to `qwen2.5:1.5b` via the refactored `llm_service`.
5. **Reference Injection**: `CitationService` computes IEEE citations and forcefully appends them to the end of the markdown, preventing the LLM from hallucinating citations.

## 3. Export Services
Two new modular export engines were introduced:
- **PDF Export (`pdf_service.py`)**: Utilizes `reportlab.platypus` to convert the markdown into a heavily structured PDF with Cover Pages, Headings, Paragraph Justification, and Bullet Lists.
- **DOCX Export (`docx_service.py`)**: Utilizes `python-docx` to generate Microsoft Word documents applying native Word styles for Headings (Level 1-4) and Lists.

## 4. Frontend Integration
The `ReportsPage.jsx` was completely overhauled from a placeholder into a highly functional UI:
- **History Panel (Left Pane)**: Lists all generated reports in reverse-chronological order.
- **Report Viewer (Right Pane)**: Renders the active report using `react-markdown`.
- **Generate Modal**: Provides an intuitive UI to select a Topic and Paper IDs, hooking directly into the global polling task tracker.
- **Action Bar**: Provides instant access to Download PDF, Download DOCX, Regenerate (using same cached inputs), and Delete functionality.

## 5. API Endpoints Created
All endpoints are available under the `/report` router:
- `POST /report/generate`: Queue generation.
- `GET /reports`: List history.
- `GET /report/{id}`: Fetch specific report markdown.
- `POST /report/{id}/regenerate`: Recreate report using latest prompts.
- `DELETE /report/{id}`: Delete report.
- `GET /report/{id}/pdf`: Stream ReportLab PDF bytes.
- `GET /report/{id}/docx`: Stream DOCX bytes.

## 6. Success Criteria Met
- [x] Report generated purely using Ollama.
- [x] Cached summaries and comparisons are reused.
- [x] References strictly supplied by Citation Agent.
- [x] PDF export functional.
- [x] DOCX export functional.
- [x] Report History UI built out.
- [x] Project is fully demo-ready and capstone-ready.
