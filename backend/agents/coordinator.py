# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from .search_agent import SearchAgent
from .summary_agent import SummaryAgent
from .comparison_agent import ComparisonAgent
from .chat_agent import ChatAgent

class CoordinatorAgent:
    def __init__(self, session: Session):
        self.session = session
        self.search_agent = SearchAgent(session)
        self.summary_agent = SummaryAgent(session)
        self.comparison_agent = ComparisonAgent(session)
        self.chat_agent = ChatAgent(session)

    def route_search(self, paper_data: dict):
        return self.search_agent.create_paper(paper_data)

    def route_summary(self, paper_id: int):
        return self.summary_agent.summarize_paper(paper_id)

    def route_comparison(self, paper_ids: list[int], dimension: str | None = None):
        return self.comparison_agent.compare_papers(paper_ids, dimension)

    def route_chat(self, question: str, session_id: str | None = None, paper_ids: list[int] | None = None):
        return self.chat_agent.chat(question, session_id=session_id, paper_ids=paper_ids)

coordinator_class = CoordinatorAgent
