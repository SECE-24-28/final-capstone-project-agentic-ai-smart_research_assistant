"""
Report Service – Orchestrates Ollama-driven final report generation.

Pipeline
--------
1. Load selected papers from DB
2. Load cached summaries  (avoids re-running Summary Agent)
3. Load cached comparison (avoids re-running Comparison Agent)
4. Build an IEEE-style structured prompt
5. Call llm_service.generate()  →  Ollama qwen2.5:1.5b
6. Append factual citations from CitationService (no LLM hallucination)
7. Persist the FinalReport record

Template Support
----------------
Only "Research Report" is implemented. The *template_type* parameter is
wired through so future templates (Literature Survey, Technical Analysis,
Project Proposal) can be added without changing the interface.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from ..models import Paper, Summary, Comparison, FinalReport
from ..services.llm_service import llm_service
from ..services.citation_service import CitationService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _paper_ids_str(paper_ids: list[int]) -> str:
    return ",".join(str(i) for i in sorted(paper_ids))


def _build_prompt(
    topic: str,
    papers: list[Paper],
    summaries: list[Summary],
    comparison_text: Optional[str],
) -> str:
    """Construct the structured generation prompt."""

    paper_block = ""
    for p in papers:
        paper_block += f"\n### {p.title or 'Untitled'}\n"
        paper_block += f"- Authors: {p.authors or 'N/A'}\n"
        paper_block += f"- Year: {p.year or 'N/A'}\n"
        paper_block += f"- Journal: {p.journal or p.source or 'N/A'}\n"
        paper_block += f"- Abstract: {(p.abstract or '')[:300]}…\n"

    summary_block = ""
    for s in summaries:
        paper = next((p for p in papers if p.id == s.paper_id), None)
        label = paper.title if paper else f"Paper #{s.paper_id}"
        summary_block += f"\n### {label}\n"
        summary_block += f"- **Objective:** {s.objective or 'N/A'}\n"
        summary_block += f"- **Methodology:** {s.methodology or 'N/A'}\n"
        summary_block += f"- **Findings:** {s.findings or 'N/A'}\n"
        summary_block += f"- **Limitations:** {s.limitations or 'N/A'}\n"
        summary_block += f"- **Contributions:** {s.contributions or 'N/A'}\n"

    comparison_block = (
        f"\n## Comparative Analysis\n{comparison_text}\n"
        if comparison_text
        else "\n## Comparative Analysis\nNo comparison data available.\n"
    )

    prompt = f"""You are an expert academic researcher writing a formal IEEE-style research report.

Topic: {topic}

Selected Papers:
{paper_block}

Individual Summaries:
{summary_block}

{comparison_block}

Write a comprehensive, professional research report with EXACTLY these sections:

# {topic}: A Research Report

## Abstract
(2-3 sentence overview of the research area, its significance, and what this report covers)

## Research Context
(Background, motivation, and importance of the research topic)

## Selected Papers
(Brief bibliographic overview of the papers included in this study)

## Individual Paper Summaries
(Detailed breakdown of each paper's objective, methodology, findings, and contributions)

## Comparative Analysis
(Synthesise the comparison data above into a coherent narrative comparing the papers)

## Key Findings
(Bullet-point list of the most important findings across all papers)

## Research Insights
(Your expert synthesis of what the collected research means for the field)

## Future Work
(3-5 specific, concrete directions for future research in this area)

Do NOT include a References section — it will be added separately.
Write in formal academic English. Be specific and analytical. Do not hallucinate facts."""

    return prompt


# ---------------------------------------------------------------------------
# Main service class
# ---------------------------------------------------------------------------

class ReportService:
    """
    Generates, retrieves, deletes, and regenerates FinalReport records.

    Always call methods with an active SQLAlchemy Session (injected by the
    router via dependency injection).
    """

    # ── Generation ──────────────────────────────────────────────────────────

    def generate_final_report(
        self,
        topic: str,
        paper_ids: list[int],
        session: Session,
        comparison_id: Optional[int] = None,
        template_type: str = "Research Report",
        progress_callback=None,
    ) -> FinalReport:
        """
        Full pipeline: load cached data → prompt Ollama → build markdown → save.

        progress_callback(pct, label) is called at each stage so the caller
        can push updates to the task tracker.
        """

        def _progress(pct: int, label: str):
            if progress_callback:
                progress_callback(pct, label)
            logger.info(f"[ReportService] {pct}% – {label}")

        # 1. Collect papers
        _progress(10, "Collecting papers…")
        papers = session.query(Paper).filter(Paper.id.in_(paper_ids)).all()
        if not papers:
            raise ValueError(f"No papers found for IDs: {paper_ids}")

        # 2. Load cached summaries
        _progress(30, "Loading cached summaries…")
        summaries: list[Summary] = []
        summary_ids: list[int] = []
        for paper in papers:
            latest = (
                session.query(Summary)
                .filter(Summary.paper_id == paper.id)
                .order_by(Summary.id.desc())
                .first()
            )
            if latest:
                summaries.append(latest)
                summary_ids.append(latest.id)

        # 3. Load cached comparison
        _progress(50, "Loading cached comparison…")
        comparison_text: Optional[str] = None
        resolved_comparison_id: Optional[int] = comparison_id

        if comparison_id:
            comp = session.get(Comparison, comparison_id)
            if comp:
                comparison_text = comp.result
        else:
            # Auto-find the most recent comparison that covers these paper IDs
            ids_str = _paper_ids_str(paper_ids)
            comp = (
                session.query(Comparison)
                .filter(Comparison.paper_ids == ids_str)
                .order_by(Comparison.id.desc())
                .first()
            )
            if comp:
                comparison_text = comp.result
                resolved_comparison_id = comp.id

        # 4. Generate with Ollama
        _progress(70, "Generating report with Ollama…")
        prompt = _build_prompt(topic, papers, summaries, comparison_text)
        report_body = llm_service.generate(
            prompt,
            system_prompt=(
                "You are an expert academic researcher producing IEEE-style "
                "research reports. Be precise, formal, and analytical."
            ),
        )

        # 5. Append factual citations (no LLM hallucination)
        _progress(90, "Formatting output and generating references…")
        citation_svc = CitationService()
        references: list[str] = []
        for i, paper in enumerate(papers, 1):
            ref = citation_svc.format_ieee(paper)
            references.append(f"[{i}] {ref}")

        references_section = "\n## References\n\n" + "\n\n".join(references)
        full_markdown = report_body.strip() + "\n\n" + references_section

        # 6. Build a title
        title = f"{topic}: A Research Report"

        # 7. Persist
        report = FinalReport(
            title=title,
            topic=topic,
            paper_ids=_paper_ids_str(paper_ids),
            summary_ids=",".join(str(i) for i in summary_ids),
            comparison_id=resolved_comparison_id,
            report_markdown=full_markdown,
            template_type=template_type,
        )
        session.add(report)
        session.commit()
        session.refresh(report)

        _progress(100, "Complete!")
        return report

    # ── Retrieval ────────────────────────────────────────────────────────────

    def get_report(self, report_id: int, session: Session) -> Optional[FinalReport]:
        return session.get(FinalReport, report_id)

    def list_reports(self, session: Session, limit: int = 50) -> list[FinalReport]:
        return (
            session.query(FinalReport)
            .order_by(FinalReport.created_at.desc())
            .limit(limit)
            .all()
        )

    # ── Regenerate ───────────────────────────────────────────────────────────

    def regenerate_report(
        self,
        report_id: int,
        session: Session,
        progress_callback=None,
    ) -> FinalReport:
        """
        Recreate the report using the *same* paper_ids and comparison_id
        stored on the existing record.  The old record is deleted afterwards
        so the new one takes its place in history.
        """
        old = session.get(FinalReport, report_id)
        if not old:
            raise ValueError(f"Report {report_id} not found")

        paper_ids = [int(i) for i in old.paper_ids.split(",") if i.strip()]
        topic = old.topic
        comparison_id = old.comparison_id
        template_type = old.template_type or "Research Report"

        # Delete old record first so auto-incrementing ID is clean
        session.delete(old)
        session.commit()

        return self.generate_final_report(
            topic=topic,
            paper_ids=paper_ids,
            session=session,
            comparison_id=comparison_id,
            template_type=template_type,
            progress_callback=progress_callback,
        )

    # ── Delete ───────────────────────────────────────────────────────────────

    def delete_report(self, report_id: int, session: Session) -> bool:
        report = session.get(FinalReport, report_id)
        if not report:
            return False
        session.delete(report)
        session.commit()
        return True


# Singleton
report_service = ReportService()
