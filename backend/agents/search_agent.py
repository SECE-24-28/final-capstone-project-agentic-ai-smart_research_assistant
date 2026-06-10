from sqlalchemy.orm import Session
from ..models import Paper
from ..services.paper_search_service import paper_search_service

class SearchAgent:
    def __init__(self, session: Session):
        self.session = session

    def search_and_store(self, topic: str, limit: int = 5) -> list[Paper]:
        results = paper_search_service.search_topic(topic, limit=limit)
        saved_papers = []
        for res in results:
            # Check if paper already exists
            existing = self.session.query(Paper).filter(Paper.title == res["title"]).first()
            if not existing:
                paper = Paper(
                    title=res["title"],
                    authors=res["authors"],
                    abstract=res["abstract"],
                    year=res["year"],
                    doi=res["doi"],
                    source=res["source"],
                    file_path=res["url"] # Store OpenAlex ID URL as file_path placeholder
                )
                self.session.add(paper)
                self.session.commit()
                self.session.refresh(paper)
                saved_papers.append(paper)
            else:
                saved_papers.append(existing)
                
        return saved_papers

    def create_paper(self, paper_data: dict) -> Paper:
        paper = Paper(**paper_data)
        self.session.add(paper)
        self.session.commit()
        self.session.refresh(paper)
        return paper

    def get_papers(self, limit: int = 20):
        return self.session.query(Paper).order_by(Paper.created_at.desc()).limit(limit).all()

search_agent_class = SearchAgent
