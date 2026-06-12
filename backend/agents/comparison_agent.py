from sqlalchemy.orm import Session
from ..models import Comparison, Paper, Summary
from ..services.llm_service import llm_service
from .summary_agent import SummaryAgent

class ComparisonAgent:
    def __init__(self, session: Session):
        self.session = session
        self.summary_agent = SummaryAgent(session)

    def compare_papers(self, paper_ids: list[int], dimension: str | None = None) -> Comparison:
        papers = self.session.query(Paper).filter(Paper.id.in_(paper_ids)).all()
        if len(papers) < 2:
            raise ValueError("Comparison requires at least two papers")

        comparison_name = f"comparison_{'_'.join(str(pid) for pid in paper_ids)}"
        if dimension:
            comparison_name += f"_{dimension.replace(' ', '_')}"

        # Caching: Check if already exists
        existing = self.session.query(Comparison).filter(Comparison.name == comparison_name).first()
        if existing:
            return existing

        system_prompt = (
            "You are an expert academic research analyst. "
            "Your task is to synthesize and compare multiple research papers based strictly on the provided summaries. "
            "Do NOT hallucinate information. If a detail is missing, state that it is not provided. "
            "You MUST output your comparison exactly as requested."
        )

        prompt = self.build_prompt(papers, dimension)
        result = llm_service.generate(prompt, max_tokens=2048, system_prompt=system_prompt)
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
            
            # Use summary if available, else generate it
            summary = self.session.query(Summary).filter(Summary.paper_id == paper.id).first()
            if not summary:
                summary = self.summary_agent.summarize_paper(paper.id)

            intro.append(f"- Objective: {summary.objective or 'Not provided'}")
            intro.append(f"- Methodology: {summary.methodology or 'Not provided'}")
            intro.append(f"- Findings: {summary.findings or 'Not provided'}")
            intro.append(f"- Limitations: {summary.limitations or 'Not provided'}")
            intro.append(f"- Contributions: {summary.contributions or 'Not provided'}")
            if summary.raw_text:
                intro.append(f"- Full Summary:\n{summary.raw_text}")
                
            intro.append("\n")
            
        intro.append("--- END INPUT DATA ---")
        intro.append("\nINSTRUCTIONS:")
        intro.append(
            "Provide a structured comparative analysis of the above papers. "
            "1. First, generate a professional markdown table summarizing the key aspects of the papers. "
            "The table MUST be formatted exactly like this:\n"
            "| Aspect | [Paper 1 Title] | [Paper 2 Title] |\n"
            "|---|---|---|\n"
            "| Objective | ... | ... |\n"
            "| Methodology | ... | ... |\n"
            "| Dataset | ... | ... |\n"
            "| Results | ... | ... |\n"
            "| Limitations | ... | ... |\n"
            "| Contributions | ... | ... |\n\n"
            "2. After the table, you MUST include the following exact headings with your detailed analysis:\n"
            "## Similarities\n"
            "## Differences\n"
            "## Research Trends\n"
            "## Future Research Directions"
        )
                     
        if dimension:
            intro.append(f"\nSpecifically focus your analysis and recommendation on this dimension: {dimension}")
            
        return "\n".join(intro)

comparison_agent_class = ComparisonAgent
