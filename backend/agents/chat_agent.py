from sqlalchemy.orm import Session
from ..models import ChatHistory, Paper
from ..services.llm_service import llm_service
from ..services.embedding_service import embedding_service
from ..services.vector_store import vector_store

class ChatAgent:
    def __init__(self, session: Session):
        self.session = session

    def chat(self, question: str, session_id: str | None = None, paper_ids: list[int] | None = None) -> tuple[str, list[str]]:
        query_embedding = embedding_service.embed_texts([question])
        where_filter = None
        if paper_ids:
            where_filter = {"paper_id": {"$in": paper_ids}}

        sources = []
        context_chunks = []
        if vector_store.collection is not None:
            results = vector_store.query(query_embedding, n_results=5, where=where_filter)
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            for doc, md in zip(documents, metadatas):
                context_chunks.append(doc)
                if md:
                    sources.append(str(md))

        prompt = self.build_prompt(question, context_chunks)
        answer = llm_service.generate(prompt, max_tokens=384)

        chat_record = ChatHistory(
            paper_id=paper_ids[0] if paper_ids else None,
            session_id=session_id,
            user_question=question,
            assistant_answer=answer,
            source_references=','.join(sources) if sources else None,
        )
        self.session.add(chat_record)
        self.session.commit()
        self.session.refresh(chat_record)
        return answer, sources

    def build_prompt(self, question: str, chunks: list[str]) -> str:
        prompt = ["You are a grounded research assistant.", "Answer the question using only the provided document excerpts.", f"Question: {question}"]
        if chunks:
            prompt.append("Context:")
            prompt.extend(chunks)
        prompt.append("Answer in a concise, structured manner and cite source passages when available.")
        return "\n\n".join(prompt)

chat_agent_class = ChatAgent
