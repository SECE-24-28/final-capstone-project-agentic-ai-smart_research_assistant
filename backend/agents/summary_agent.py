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

        query = f"Summarize this academic paper. Paper title: {paper.title}." 
        if paper.abstract:
            query += f" Abstract: {paper.abstract}"

        top_chunks = []
        if vector_store.collection is not None:
            # We want to retrieve relevant chunks based on a general summary intent
            embeddings = embedding_service.embed_texts([query])
            results = vector_store.query(embeddings, n_results=5, where={"paper_id": paper.id})
            for item in results.get("documents", [[]])[0]:
                top_chunks.append(item)

        prompt = self.build_prompt(query, top_chunks)
        result_text = llm_service.generate(prompt, max_tokens=1024)
        
        # Parse the structured response
        parsed = self.parse_summary(result_text)
        
        summary = Summary(
            paper_id=paper.id,
            objective=parsed.get("Objective", ""),
            methodology=parsed.get("Methodology", ""),
            findings=parsed.get("Findings", ""),
            limitations=parsed.get("Limitations", ""),
            contributions=parsed.get("Contributions", ""),
            raw_text=result_text,
        )
        self.session.add(summary)
        self.session.commit()
        self.session.refresh(summary)
        return summary

    def build_prompt(self, query: str, chunks: list[str]) -> str:
        pieces = [
            "You are an expert academic summarizer.", 
            query,
            "Based on the provided document passages, generate a detailed summary."
        ]
        if chunks:
            pieces.append("\n--- SOURCE PASSAGES ---")
            pieces.extend(chunks)
            pieces.append("-----------------------\n")
            
        pieces.append(
            "You MUST format your response using EXACTLY these markdown headers:\n"
            "## Objective\n"
            "## Methodology\n"
            "## Findings\n"
            "## Limitations\n"
            "## Contributions\n"
            "Do not use any other formatting. Put the relevant content under each header."
        )
        return "\n".join(pieces)

    def parse_summary(self, text: str) -> dict:
        sections = {"Objective": "", "Methodology": "", "Findings": "", "Limitations": "", "Contributions": ""}
        current_section = None
        
        for line in text.split('\n'):
            line_stripped = line.strip()
            if line_stripped.startswith("## "):
                header = line_stripped.replace("## ", "").strip()
                if header in sections:
                    current_section = header
                    continue
            
            if current_section:
                sections[current_section] += line + "\n"
                
        # Clean up whitespace
        for k in sections:
            sections[k] = sections[k].strip()
            
        return sections

summary_agent_class = SummaryAgent
