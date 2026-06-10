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
            if len(paper_ids) == 1:
                where_filter = {"paper_id": paper_ids[0]}
            else:
                where_filter = {"paper_id": {"$in": paper_ids}}

        sources = []
        context_chunks = []
        if vector_store.collection is not None:
            results = vector_store.query(query_embedding, n_results=5, where=where_filter)
            if results and "documents" in results and results["documents"]:
                documents = results["documents"][0]
                metadatas = results["metadatas"][0]
                
                for doc, md in zip(documents, metadatas):
                    context_chunks.append(doc)
                    if md:
                        sources.append(str(md))

        # Handle empty retrieval to prevent hallucination
        if not context_chunks:
            answer = "I could not find any relevant information in the uploaded documents to answer your question."
        else:
            system_prompt = (
                "You are a strict, grounded academic research assistant. "
                "You MUST answer the user's question using ONLY the provided document excerpts. "
                "If the provided context does not contain the answer, you MUST say 'I cannot answer this based on the provided context.' "
                "Do NOT use outside knowledge. Do NOT hallucinate."
            )
            
            prompt = self.build_prompt(question, context_chunks)
            answer = llm_service.generate(prompt, max_tokens=384, system_prompt=system_prompt)

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
        prompt = ["--- PROVIDED CONTEXT ---"]
        prompt.extend(chunks)
        prompt.append("------------------------\n")
        prompt.append(f"Question: {question}")
        prompt.append("Answer concisely using ONLY the context above:")
        return "\n".join(prompt)

chat_agent_class = ChatAgent
