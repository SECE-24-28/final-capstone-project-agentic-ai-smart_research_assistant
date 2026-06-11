from sqlalchemy.orm import Session
from ..models import Comparison
from ..services.llm_service import llm_service
from ..models import Paper

class ComparisonAgent:
    def __init__(self, session: Session):
        self.session = session

    def compare_papers(self, paper_ids: list[int], dimension: str | None = None) -> Comparison:
        papers = self.session.query(Paper).filter(Paper.id.in_(paper_ids)).all()
        if len(papers) < 2:
            raise ValueError("Comparison requires at least two papers")

        system_prompt = (
            "You are an expert academic research analyst. "
            "Your task is to synthesize and compare multiple research papers based strictly on the provided summaries/abstracts. "
            "Identify similarities, differences, strengths, weaknesses, and research trends. "
            "Do NOT hallucinate information. If a detail is missing, state that it is not provided."
        )

        prompt = self.build_prompt(papers, dimension)
        result = llm_service.generate(prompt, max_tokens=1536, system_prompt=system_prompt)
        comparison_name = f"comparison_{'_'.join(str(pid) for pid in paper_ids)}"
        comparison = Comparison(name=comparison_name, paper_ids=','.join(map(str, paper_ids)), result=result)
        self.session.add(comparison)
        self.session.commit()
        self.session.refresh(comparison)
        return comparison

    def build_prompt(self, papers: list[Paper], dimension: str | None = None) -> str:
        intro = ["--- COMPARISON INPUT DATA ---"]
        for paper in papers:
            intro.append(f"### Paper {paper.id}: {paper.title}")
            if paper.authors:
                intro.append(f"Authors: {paper.authors}")
            
            # Use summary if available
            if paper.summaries:
                summary = paper.summaries[0]
                intro.append(f"- Objective: {summary.objective or 'Not provided'}")
                intro.append(f"- Methodology: {summary.methodology or 'Not provided'}")
                intro.append(f"- Findings: {summary.findings or 'Not provided'}")
                intro.append(f"- Limitations: {summary.limitations or 'Not provided'}")
                intro.append(f"- Contributions: {summary.contributions or 'Not provided'}")
            elif paper.abstract:
                intro.append(f"- Abstract: {paper.abstract}")
            else:
                intro.append("- No abstract or summary available.")
                
            intro.append("\n")
            
        intro.append("--- END INPUT DATA ---")
        intro.append("\nINSTRUCTIONS:")
        intro.append("Provide a structured comparative analysis of the above papers. "
                     "Organize your response using the following headings:\n"
                     "## Similarities\n## Differences\n## Strengths & Weaknesses\n## Research Trends")
                     
        if dimension:
            intro.append(f"\nSpecifically focus your analysis on this dimension: {dimension}")
            
        return "\n".join(intro)

comparison_agent_class = ComparisonAgent
