from sqlalchemy.orm import Session
from ..models import Paper
from ..services.paper_search_service import paper_search_service

class SearchAgent:
    def __init__(self, session: Session):
        self.session = session

    def search_and_store(self, topic: str, limit: int = 5) -> list[Paper]:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"SearchAgent.search_and_store: topic='{topic}', limit={limit}")

        results = paper_search_service.search_topic(topic, limit=limit)
        saved_papers = []
        new_saved_count = 0

        for res in results:
            # Check if paper already exists by title
            existing = self.session.query(Paper).filter(Paper.title == res["title"]).first()
            if not existing:
                paper = Paper(
                    title=res["title"],
                    authors=res["authors"],
                    abstract=res["abstract"],
                    year=res["year"],
                    doi=res["doi"],
                    source=res["source"],
                    file_path=res["url"]  # Store OpenAlex ID URL as file_path placeholder
                )
                self.session.add(paper)
                self.session.commit()
                self.session.refresh(paper)
                new_saved_count += 1
            else:
                paper = existing

            # Attach similarity score as a transient attribute (not persisted to DB)
            paper.similarity_score = res.get("similarity_score", None)
            saved_papers.append(paper)

        logger.info(
            f"SearchAgent.search_and_store: {new_saved_count} new papers_saved, "
            f"{len(saved_papers)} total papers_returned"
        )
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
