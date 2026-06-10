import os
import time
import fitz
import logging
from pathlib import Path

from backend.database import init_db, SessionLocal
from backend.models import Paper
from backend.services.pdf_service import pdf_service
from backend.services.embedding_service import embedding_service
from backend.services.vector_store import vector_store
from backend.agents.summary_agent import SummaryAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_synthetic_pdf(path: str, pages: int):
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page()
        content = f"Page {i+1} of synthetic academic paper on AI.\n" * 20
        if i == 0:
            content = "Objective: To study artificial intelligence.\n" + content
        elif i == 1:
            content = "Methodology: We trained a massive neural network using backpropagation.\n" + content
        elif i == pages // 2:
            content = "Findings: The model achieved 95% accuracy on the test dataset.\n" + content
        elif i == pages - 2:
            content = "Limitations: The hardware was insufficient for real-time processing.\n" + content
        elif i == pages - 1:
            content = "Contributions: A novel architecture for efficient training.\n" + content
            
        page.insert_text((50, 50), content)
    doc.save(path)
    doc.close()
    return path

def run_test(pdf_path: str, size_label: str, report_lines: list):
    print(f"\n{'='*50}\nTesting {size_label} PDF Workflow\n{'='*50}")
    
    db = SessionLocal()
    
    # 1. Extraction
    t0 = time.time()
    extracted_text = pdf_service.extract_text(Path(pdf_path))
    t_extract = time.time() - t0
    
    # Save Paper
    paper = Paper(title=f"Test {size_label} Paper", file_path=pdf_path, abstract="Test abstract")
    db.add(paper)
    db.commit()
    db.refresh(paper)
    
    # 2. Chunking
    chunks = pdf_service.chunk_text(extracted_text)
    
    # 3. Embedding
    t0 = time.time()
    embeddings = embedding_service.embed_texts(chunks)
    t_embed = time.time() - t0
    
    # 4. Storage
    vector_store.initialize()
    ids = [f"p_{paper.id}_c_{i}" for i in range(len(chunks))]
    metadatas = [{"paper_id": paper.id} for _ in range(len(chunks))]
    vector_store.add_documents(ids=ids, texts=chunks, metadatas=metadatas, embeddings=embeddings)
    
    # 5. Summarization (Retrieval + Generation)
    agent = SummaryAgent(db)
    
    t0 = time.time()
    summary = agent.summarize_paper(paper.id)
    t_summary = time.time() - t0
    
    total_time = t_extract + t_embed + t_summary
    
    print(f"\n--- Metrics ---")
    print(f"Extraction Time: {t_extract:.2f}s")
    print(f"Chunks: {len(chunks)}")
    print(f"Embedding Time: {t_embed:.2f}s")
    print(f"Summary Time (Retrieval+Gen): {t_summary:.2f}s")
    print(f"Total Time: {total_time:.2f}s")
    
    print(f"\n--- Validated Summary Object ---")
    print(f"Objective: {bool(summary.objective)} ({len(summary.objective)} chars)")
    print(f"Methodology: {bool(summary.methodology)} ({len(summary.methodology)} chars)")
    print(f"Findings: {bool(summary.findings)} ({len(summary.findings)} chars)")
    print(f"Limitations: {bool(summary.limitations)} ({len(summary.limitations)} chars)")
    print(f"Contributions: {bool(summary.contributions)} ({len(summary.contributions)} chars)")
    
    report_lines.extend([
        f"### {size_label} PDF Metrics",
        f"- **Extraction Time:** {t_extract:.2f}s",
        f"- **Chunk Count:** {len(chunks)}",
        f"- **Embedding Time:** {t_embed:.2f}s",
        f"- **Summary Gen Time:** {t_summary:.2f}s",
        f"- **Total Workflow Time:** {total_time:.2f}s",
        "\n**Extraction Results Validation:**",
        f"- Objective Extracted: `{'Yes' if summary.objective else 'No'}`",
        f"- Methodology Extracted: `{'Yes' if summary.methodology else 'No'}`",
        f"- Findings Extracted: `{'Yes' if summary.findings else 'No'}`",
        f"- Limitations Extracted: `{'Yes' if summary.limitations else 'No'}`",
        f"- Contributions Extracted: `{'Yes' if summary.contributions else 'No'}`\n"
    ])
    
    db.close()

def main():
    init_db()
    
    report = [
        "# Phase 2: Summary Agent Validation Report\n",
        "This report measures the end-to-end extraction, vectorization, and summarization pipeline using local ML models.\n"
    ]
    
    small_pdf = create_synthetic_pdf("small_test.pdf", 3)
    run_test(small_pdf, "Small (3 pages)", report)
    
    medium_pdf = create_synthetic_pdf("medium_test.pdf", 12)
    run_test(medium_pdf, "Medium (12 pages)", report)
    
    os.makedirs("docs", exist_ok=True)
    with open("docs/phase2_summary_agent_report.md", "w") as f:
        f.write("\n".join(report))
        
    print("\nPhase 2 Complete. Report generated.")

if __name__ == "__main__":
    main()
