from sqlalchemy.orm import Session
from ..models import Paper
from ..services.embedding_service import embedding_service

class SearchAgent:
    def __init__(self, session: Session):
        self.session = session

    def create_paper(self, paper_data: dict) -> Paper:
        paper = Paper(**paper_data)
        self.session.add(paper)
        self.session.commit()
        self.session.refresh(paper)
        return paper

    def get_papers(self, limit: int = 20):
        return self.session.query(Paper).order_by(Paper.created_at.desc()).limit(limit).all()

search_agent_class = SearchAgent
