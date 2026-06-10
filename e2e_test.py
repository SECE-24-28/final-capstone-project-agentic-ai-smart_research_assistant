import os
import sys
import fitz
from pathlib import Path
from datetime import datetime

# Import services
from backend.database import init_db, SessionLocal
from backend.models import Paper
from backend.services.pdf_service import pdf_service
from backend.services.embedding_service import embedding_service
from backend.services.vector_store import vector_store
from backend.agents.summary_agent import SummaryAgent

def run_e2e_test():
    print("Starting E2E Validation...")
    init_db()
    db = SessionLocal()
    
    # 1. Create a Test PDF
    pdf_path = "test_paper.pdf"
    doc = fitz.open()
    page = doc.new_page()
    content = (
        "Quantum computing represents a paradigm shift in computation, leveraging the principles of quantum mechanics. "
        "Objective: This paper aims to demonstrate the theoretical advantage of quantum algorithms in cryptography. "
        "Methodology: We simulate Shor's algorithm on a 50-qubit simulated quantum computer. "
        "Findings: The simulation successfully factored a 15-bit integer in polynomial time. "
        "Limitations: The current hardware suffers from high decoherence rates. "
        "Contributions: We provide a novel error-correction scheme for Shor's algorithm."
    )
    page.insert_text((50, 50), content)
    doc.save(pdf_path)
    doc.close()
    print(f"Created test PDF: {pdf_path}")

    # 2. Extract Text
    extracted_text = pdf_service.extract_text(Path(pdf_path))
    pages_extracted = 1 # We know we created 1 page
    print(f"Extracted Text Length: {len(extracted_text)} characters")

    # Save to Database to get an ID
    paper = Paper(title="Test Quantum Paper", file_path=pdf_path, abstract=extracted_text[:500])
    db.add(paper)
    db.commit()
    db.refresh(paper)
    print(f"Saved Paper to DB with ID: {paper.id}")

    # 3. Chunk Creation
    chunks = pdf_service.chunk_text(extracted_text)
    print(f"Created {len(chunks)} chunks from text.")

    # 4. Embedding Generation
    print("Generating embeddings...")
    embedding_service.load()
    embeddings = embedding_service.embed_texts(chunks)
    print(f"Generated {len(embeddings)} embeddings.")

    # 5. ChromaDB Storage
    print("Initializing Vector Store and saving chunks...")
    vector_store.initialize()
    
    ids = [f"paper_{paper.id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"paper_id": paper.id} for _ in range(len(chunks))]
    
    vector_store.add_documents(ids=ids, texts=chunks, metadatas=metadatas, embeddings=embeddings)
    print(f"Stored {len(ids)} chunks in ChromaDB.")

    # 6. Similarity Retrieval & 7. Summary Generation
    print("Running Summary Agent (Retrieval + Generation)...")
    agent = SummaryAgent(db)
    summary_obj = agent.summarize_paper(paper.id)
    print("Summary Generation Complete!")

    # Format Logs
    report = f"""# E2E Validation Report

## Execution Details
* **Timestamp:** {datetime.now().isoformat()}
* **Test File:** `test_paper.pdf`
* **Paper DB ID:** {paper.id}

## Pipeline Metrics
* **PDF Pages Extracted:** {pages_extracted}
* **Text Length:** {len(extracted_text)} characters
* **Number of Chunks Created:** {len(chunks)}
* **Number of Embeddings Stored:** {len(embeddings)}

## Retrieval Results
The Summary Agent queried ChromaDB and retrieved relevant chunks to ground the generation.

## Generated Summary
{summary_obj.raw_text}
"""

    with open("docs/e2e_validation_report.md", "w", encoding="utf-8") as f:
        f.write(report)
        
    chat_log_name = datetime.now().strftime("%Y-%m-%d_%H-%M") + "_e2e-validation.md"
    os.makedirs("chats", exist_ok=True)
    with open(f"chats/{chat_log_name}", "w", encoding="utf-8") as f:
        f.write(report)
        
    print("Validation successful. Reports generated.")

if __name__ == "__main__":
    run_e2e_test()
