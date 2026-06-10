from sqlalchemy.orm import Session
from ..models import Summary, Paper
from ..services.llm_service import llm_service
from ..services.embedding_service import embedding_service
from ..services.vector_store import vector_store

class SummaryAgent:
    def __init__(self, session: Session):
        self.session = session

    def summarize_paper(self, paper_id: int) -> Summary:
        paper = self.session.get(Paper, paper_id)
        if not paper:
            raise ValueError("Paper not found")

        query = f"Summarize this academic paper and provide objective, methodology, findings, limitations, contributions. Paper title: {paper.title}." 
        if paper.abstract:
            query += f" Abstract: {paper.abstract}"

        top_chunks = []
        if vector_store.collection is not None:
            embeddings = embedding_service.embed_texts([query])
            results = vector_store.query(embeddings, n_results=5, where={"paper_id": paper.id})
            for item in results.get("documents", [[]])[0]:
                top_chunks.append(item)

        prompt = self.build_prompt(query, top_chunks)
        result_text = llm_service.generate(prompt, max_tokens=512)
        summary = Summary(
            paper_id=paper.id,
            objective="",
            methodology="",
            findings="",
            limitations="",
            contributions="",
            raw_text=result_text,
        )
        self.session.add(summary)
        self.session.commit()
        self.session.refresh(summary)
        return summary

    def build_prompt(self, query: str, chunks: list[str]) -> str:
        pieces = ["You are an academic summarizer.", query]
        if chunks:
            pieces.append("Use the following extracted document passages to ground your summary:")
            pieces.extend(chunks)
        pieces.append("Return a structured summary with objective, methodology, findings, limitations, and contributions.")
        return "\n\n".join(pieces)

summary_agent_class = SummaryAgent
