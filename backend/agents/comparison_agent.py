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

        prompt = self.build_prompt(papers, dimension)
        result = llm_service.generate(prompt, max_tokens=512)
        comparison_name = f"comparison_{'_'.join(str(pid) for pid in paper_ids)}"
        comparison = Comparison(name=comparison_name, paper_ids=','.join(map(str, paper_ids)), result=result)
        self.session.add(comparison)
        self.session.commit()
        self.session.refresh(comparison)
        return comparison

    def build_prompt(self, papers: list[Paper], dimension: str | None = None) -> str:
        intro = ["You are a research comparison engine.", "Compare the following papers."]
        if dimension:
            intro.append(f"Focus the comparison on: {dimension}.")
        for paper in papers:
            intro.append(f"Paper {paper.id}: {paper.title}")
            if paper.abstract:
                intro.append(f"Abstract: {paper.abstract}")
        intro.append("Provide a structured side-by-side analysis by objective, methodology, findings, limitations, and relative strengths.")
        return "\n\n".join(intro)

comparison_agent_class = ComparisonAgent
