from sqlalchemy.orm import Session
from ..models import Paper, Summary, Comparison, GapAnalysis
from ..services.llm_service import llm_service

class GapAgent:
    def __init__(self, session: Session):
        self.session = session

    def analyze_gaps(self, topic: str, paper_ids: list[int], comparison_id: int | None = None) -> GapAnalysis:
        papers = self.session.query(Paper).filter(Paper.id.in_(paper_ids)).all()
        if not papers:
            raise ValueError("No papers found for gap analysis")

        comparison = None
        if comparison_id:
            comparison = self.session.query(Comparison).filter(Comparison.id == comparison_id).first()
            
        system_prompt = (
            "You are a strict academic research analyst specialized in identifying research gaps. "
            "Your task is to analyze the provided paper summaries and comparative analysis to identify unexplored areas, limitations, and future directions. "
            "Anti-Hallucination Rules: "
            "1. Use ONLY the provided information. "
            "2. If there is no evidence for a contradiction or gap, explicitly state 'Insufficient Evidence'. "
            "3. NEVER invent or fabricate research gaps, missing datasets, or evaluation methods outside the provided context."
        )

        prompt = self.build_prompt(topic, papers, comparison)
        result = llm_service.generate(prompt, max_tokens=1536, system_prompt=system_prompt)
        
        gap_analysis = GapAnalysis(
            topic=topic,
            paper_ids=','.join(map(str, paper_ids)),
            result=result
        )
        self.session.add(gap_analysis)
        self.session.commit()
        self.session.refresh(gap_analysis)
        return gap_analysis

    def build_prompt(self, topic: str, papers: list[Paper], comparison: Comparison | None) -> str:
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

        intro.append("--- INSTRUCTIONS ---")
        intro.append(
            "Analyze the above literature to identify research gaps. "
            "You MUST format your response strictly using the following headings:\n"
            "## Research Gaps\n"
            "## Unexplored Areas\n"
            "## Contradictions\n"
            "## Future Research Directions\n"
            "## Recommended Research Opportunities\n"
            "For each section, ground your claims in the provided text. Mention 'Missing Datasets' or 'Missing Evaluation Methods' under Unexplored Areas if applicable."
        )

        return "\n".join(intro)

gap_agent_class = GapAgent
