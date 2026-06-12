from sqlalchemy.orm import Session
from ..models import ChatHistory, Paper
from ..services.llm_service import llm_service
from ..services.embedding_service import embedding_service
from ..services.vector_store import vector_store

class ChatAgent:
    def __init__(self, session: Session):
        self.session = session

    def chat(self, question: str, session_id: str | None = None, paper_ids: list[int] | None = None) -> tuple[str, list[str]]:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"ChatAgent.chat: session_id={session_id}, paper_ids={paper_ids}, question='{question}'")
        
        sources = []
        context_chunks = []

        # Only perform vector search when paper_ids are specified (document-grounded mode)
        if paper_ids:
            query_embedding = embedding_service.embed_texts([question])
            where_filter = None
            if len(paper_ids) == 1:
                where_filter = {"paper_id": paper_ids[0]}
            else:
                where_filter = {"paper_id": {"$in": paper_ids}}

            if vector_store.collection is not None:
                results = vector_store.query(query_embedding, n_results=5, where=where_filter)
                if results and "documents" in results and results["documents"]:
                    documents = results["documents"][0]
                    metadatas = results["metadatas"][0]
                    distances = results.get("distances", [[0]*len(documents)])[0]
                    logger.info(f"ChatAgent.chat: retrieved {len(documents)} chunks. Distances: {distances}")
                    for doc, md in zip(documents, metadatas):
                        context_chunks.append(doc)
                        if md:
                            sources.append(str(md))
                else:
                    logger.warning("ChatAgent.chat: No chunks from VectorStore. Falling back to paper abstracts.")

            # Abstract fallback when vector store is empty for specified papers
            if not context_chunks:
                papers = self.session.query(Paper).filter(Paper.id.in_(paper_ids)).all()
                for p in papers:
                    if p.abstract:
                        context_chunks.append(f"Abstract of '{p.title}': {p.abstract}")
                        sources.append(f"{{'paper_id': {p.id}, 'source': 'abstract'}}")
                        logger.info(f"ChatAgent.chat: Using abstract fallback for paper_id={p.id}")

                if not context_chunks:
                    logger.warning("ChatAgent.chat: No abstracts found either. Returning not-found message.")
                    answer = "I could not find any relevant information in the selected documents to answer your question."
                    return answer, sources

        if context_chunks:
            # Document-grounded mode: answer strictly from provided context
            system_prompt = (
                "You are a strict, grounded academic research assistant. "
                "You MUST answer the user's question using ONLY the provided document excerpts. "
                "If the provided context does not contain the answer, say 'I cannot answer this based on the provided context.' "
                "Do NOT use outside knowledge. Do NOT hallucinate."
            )
            prompt = self.build_prompt(question, context_chunks)
        else:
            # General assistant mode: no documents selected, answer from LLM knowledge
            logger.info("ChatAgent.chat: No documents provided. Switching to general assistant mode.")
            system_prompt = (
                "You are a helpful, knowledgeable academic research assistant. "
                "Answer the user's question clearly and concisely. "
                "If asked for ideas, projects, or explanations, provide helpful, accurate information."
            )
            prompt = question

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
