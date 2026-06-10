from ..database import SessionLocal
from ..models import Citation, Paper

class CitationService:
    def __init__(self):
        self.session = SessionLocal()

    def format_ieee(self, paper: Paper, citation_type: str = "journal") -> str:
        authors = paper.authors or "Unknown authors"
        title = paper.title or "Untitled"
        year = paper.year or "n.d."
        journal = paper.journal or "Unknown source"
        doi = f"doi: {paper.doi}" if paper.doi else ""
        if citation_type == "conference":
            return f"{authors}, \"{title},\" in {journal}, {year}. {doi}".strip()
        return f"{authors}, \"{title},\" {journal}, {year}. {doi}".strip()

    def save_citation(self, paper_id: int, citation_type: str = "journal") -> Citation:
        paper = self.session.get(Paper, paper_id)
        if not paper:
            raise ValueError("Paper not found")
        text = self.format_ieee(paper, citation_type)
        citation = Citation(paper_id=paper_id, citation_type=citation_type, citation_text=text)
        self.session.add(citation)
        self.session.commit()
        self.session.refresh(citation)
        return citation

citation_service = CitationService()
