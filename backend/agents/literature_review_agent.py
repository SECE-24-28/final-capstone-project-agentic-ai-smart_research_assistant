from sqlalchemy.orm import Session
from ..models import Paper, Summary, Comparison, GapAnalysis, LiteratureReview
from ..services.llm_service import llm_service

class LiteratureReviewAgent:
    def __init__(self, session: Session):
        self.session = session

    def generate_review(self, topic: str, paper_ids: list[int], comparison_id: int | None = None, gap_id: int | None = None) -> LiteratureReview:
        paper_ids_str = ','.join(map(str, paper_ids))
        
        # Caching Layer: Check if we already generated a review for these exact papers
        existing_review = self.session.query(LiteratureReview).filter_by(topic=topic, paper_ids=paper_ids_str).first()
        if existing_review:
            return existing_review

        papers = self.session.query(Paper).filter(Paper.id.in_(paper_ids)).all()
        if not papers:
            raise ValueError("No papers found for literature review")

        comparison = None
        if comparison_id:
            comparison = self.session.query(Comparison).filter(Comparison.id == comparison_id).first()
            
        gap_analysis = None
        if gap_id:
            gap_analysis = self.session.query(GapAnalysis).filter(GapAnalysis.id == gap_id).first()
            
        system_prompt = (
            "You are an expert academic writer and senior researcher. "
            "Your task is to synthesize the provided paper summaries, comparative analyses, and gap analyses into a formal, cohesive Literature Review. "
            "Anti-Hallucination Rules: "
            "1. ONLY use information explicitly stated in the provided contexts. "
            "2. DO NOT invent citations, datasets, findings, or methodologies. "
            "3. If sufficient data is not available for a section, explicitly state 'Insufficient Evidence'. "
            "4. Maintain a formal, academic tone."
        )

        prompt = self.build_prompt(topic, papers, comparison, gap_analysis)
        result = llm_service.generate(prompt, max_tokens=2048, system_prompt=system_prompt)
        
        review = LiteratureReview(
            topic=topic,
            paper_ids=','.join(map(str, paper_ids)),
            result=result
        )
        self.session.add(review)
        self.session.commit()
        self.session.refresh(review)
        return review

    def build_prompt(self, topic: str, papers: list[Paper], comparison: Comparison | None, gap_analysis: GapAnalysis | None) -> str:
        intro = [f"--- RESEARCH TOPIC: {topic} ---", "--- PAPER SUMMARIES ---"]
        
        for paper in papers:
            intro.append(f"### Paper: {paper.title}")
            if paper.summaries:
                summary = paper.summaries[0]
                intro.append(f"Objective: {summary.objective or 'Not provided'}")
                intro.append(f"Methodology: {summary.methodology or 'Not provided'}")
                intro.append(f"Findings: {summary.findings or 'Not provided'}")
                intro.append(f"Limitations: {summary.limitations or 'Not provided'}")
            else:
                intro.append(f"Abstract: {paper.abstract or 'Not provided'}")
            intro.append("\n")

        if comparison:
            intro.append("--- EXISTING COMPARATIVE ANALYSIS ---")
            intro.append(comparison.result or "Not provided")
            intro.append("\n")

        if gap_analysis:
            intro.append("--- EXISTING GAP ANALYSIS ---")
            intro.append(gap_analysis.result or "Not provided")
            intro.append("\n")

        intro.append("--- INSTRUCTIONS ---")
        intro.append(
            "Synthesize the above information into a comprehensive Literature Review. "
            "You MUST format your response strictly using the following headings:\n"
            "## Introduction\n"
            "## Overview of Existing Research\n"
            "## Comparative Discussion\n"
            "## Research Gaps\n"
            "## Future Research Directions\n"
            "## Conclusion\n"
            "Ground all statements in the provided text."
        )

        return "\n".join(intro)

literature_review_agent_class = LiteratureReviewAgent
