import os
import time
import fitz
import logging
from pathlib import Path

from backend.database import init_db, SessionLocal
from backend.models import Paper, ChatHistory
from backend.services.pdf_service import pdf_service
from backend.services.embedding_service import embedding_service
from backend.services.vector_store import vector_store
from backend.agents.chat_agent import ChatAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_synthetic_pdf(path: str):
    doc = fitz.open()
    page = doc.new_page()
    content = (
        "Title: Deep Learning for Oceanic Thermal Energy Conversion\n\n"
        "Objective: The objective of this paper is to apply deep reinforcement learning (RL) to optimize "
        "the thermodynamic efficiency of Oceanic Thermal Energy Conversion (OTEC) plants.\n\n"
        "Methodology: We developed a Twin Delayed DDPG (TD3) agent and trained it on a simulated OTEC environment. "
        "The architecture of the neural network consists of 4 hidden layers with 256 units each. "
        "We did not use quantum computing; the models were trained on standard A100 GPUs.\n\n"
        "Findings: The key findings show that the TD3 agent improved net power output by 14.5% compared to "
        "traditional PID controllers.\n\n"
        "Limitations: The primary limitation identified was the high computational overhead during training, "
        "which prevents real-time online adaptation on edge devices.\n\n"
        "Future Work: Future work proposed includes testing the algorithm on a physical pilot plant and exploring "
        "meta-learning to reduce training time."
    )
    page.insert_text((50, 50), content)
    doc.save(path)
    doc.close()
    return path

def main():
    print(f"\n{'='*50}\nStarting Chat Agent Validation\n{'='*50}")
    init_db()
    db = SessionLocal()
    
    # 1. Pipeline Setup
    pdf_path = create_synthetic_pdf("chat_test.pdf")
    extracted_text = pdf_service.extract_text(Path(pdf_path))
    
    paper = Paper(title="OTEC RL Paper", file_path=pdf_path, abstract="Test abstract")
    db.add(paper)
    db.commit()
    db.refresh(paper)
    
    chunks = pdf_service.chunk_text(extracted_text)
    
    t0 = time.time()
    embeddings = embedding_service.embed_texts(chunks)
    t_embed = time.time() - t0
    
    vector_store.initialize()
    ids = [f"p_{paper.id}_c_{i}" for i in range(len(chunks))]
    metadatas = [{"paper_id": paper.id} for _ in range(len(chunks))]
    vector_store.add_documents(ids=ids, texts=chunks, metadatas=metadatas, embeddings=embeddings)
    
    agent = ChatAgent(db)
    
    questions = [
        "What is the objective of the paper?",
        "What methodology was used?",
        "What is the architecture of the neural network?",
        "Did they use quantum computing?",
        "What are the key findings?",
        "What limitations were identified?",
        "What future work was proposed?",
        "What is the capital of France?", # Unrelated
        "How do I bake a chocolate cake?" # Unrelated
    ]
    
    report_lines = [
        "# Phase 3: Chat Agent Validation Report",
        "\nThis report validates the Conversational RAG workflow end-to-end.\n",
        "## Corpus Ingestion Metrics",
        f"- Embedding Time: {t_embed:.2f}s",
        f"- Context Size: {len(chunks)} chunks stored\n",
        "## Evaluation Results\n"
    ]
    
    total_q_time = 0
    
    for i, q in enumerate(questions):
        print(f"\nQ{i+1}: {q}")
        t0 = time.time()
        # Track retrieval explicitly by intercepting
        query_emb = embedding_service.embed_texts([q])
        t_ret_start = time.time()
        results = vector_store.query(query_emb, n_results=5, where={"paper_id": paper.id})
        t_ret_end = time.time()
        
        answer, sources = agent.chat(q, paper_ids=[paper.id])
        t_total = time.time() - t0
        total_q_time += t_total
        
        print(f"Retrieval Time: {t_ret_end - t_ret_start:.3f}s")
        print(f"Total Response Time: {t_total:.2f}s")
        print(f"Sources retrieved: {len(sources)}")
        print(f"Answer: {answer}")
        
        report_lines.extend([
            f"### Q{i+1}: {q}",
            f"- **Retrieval Time:** {t_ret_end - t_ret_start:.3f}s",
            f"- **Total Time:** {t_total:.2f}s",
            f"- **Sources Used:** {len(sources)}",
            f"- **Answer:** {answer}\n"
        ])
    
    # 10. Test empty retrieval (non-existent paper ID)
    print("\nQ10 (Empty Retrieval Test): What is OTEC?")
    t0 = time.time()
    answer, sources = agent.chat("What is OTEC?", paper_ids=[999999])
    t_total = time.time() - t0
    
    print(f"Sources retrieved: {len(sources)}")
    print(f"Answer: {answer}")
    
    report_lines.extend([
        f"### Q10: What is OTEC? (Simulating Empty Retrieval)",
        f"- **Total Time:** {t_total:.2f}s",
        f"- **Sources Used:** {len(sources)}",
        f"- **Answer:** {answer}\n"
    ])
    
    os.makedirs("docs", exist_ok=True)
    with open("docs/phase3_chat_agent_report.md", "w") as f:
        f.write("\n".join(report_lines))
        
    print(f"\nAll 10 questions processed in {total_q_time + t_total:.2f}s.")
    print("Report generated: docs/phase3_chat_agent_report.md")

if __name__ == "__main__":
    main()
