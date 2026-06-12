from sqlalchemy.orm import Session
from ..models import Summary, Paper
from ..services.llm_service import llm_service
from ..services.embedding_service import embedding_service
from ..services.vector_store import vector_store

class SummaryAgent:
    def __init__(self, session: Session):
        self.session = session

    def summarize_paper(self, paper_id: int) -> Summary:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"SummaryAgent.summarize_paper called for paper_id={paper_id}")
        
        # Caching: Check if summary already exists
        existing_summary = self.session.query(Summary).filter(Summary.paper_id == paper_id).first()
        if existing_summary:
            logger.info(f"SummaryAgent.summarize_paper: Found existing summary for paper_id={paper_id}. Returning cached result.")
            return existing_summary

        paper = self.session.get(Paper, paper_id)
        if not paper:
            logger.error(f"SummaryAgent.summarize_paper: Paper not found for paper_id={paper_id}")
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
                
        logger.info(f"SummaryAgent.summarize_paper: Retrieved {len(top_chunks)} chunks from vector store.")

        prompt = self.build_prompt(query, top_chunks)
        logger.info(f"SummaryAgent.summarize_paper: Starting LLM generation.")
        result_text = llm_service.generate(prompt, max_tokens=1024)
        logger.info(f"SummaryAgent.summarize_paper: LLM generation complete. Parsing result.")
        
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
        logger.info(f"SummaryAgent.summarize_paper: Saved new summary to DB for paper_id={paper_id}")
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
        import re
        import logging
        logger = logging.getLogger(__name__)

        sections = {"Objective": "", "Methodology": "", "Findings": "", "Limitations": "", "Contributions": ""}
        current_section = None
        found_sections = 0
        
        for line in text.split('\n'):
            line_stripped = line.strip()
            
            # Use regex to find header variants (e.g. "### Objective", "**Objective**:", "Objective:")
            header_match = re.search(r'^(?:#+\s*|\*+)?(Objective|Methodology|Findings|Limitations|Contributions)(?:\*+:?)?', line_stripped, re.IGNORECASE)
            
            if header_match:
                header = header_match.group(1).capitalize()
                if header in sections:
                    current_section = header
                    found_sections += 1
                    continue
            
            if current_section:
                sections[current_section] += line + "\n"
                
        # Clean up whitespace
        for k in sections:
            sections[k] = sections[k].strip()
            
        logger.info(f"SummaryAgent.parse_summary: Found {found_sections} recognized sections.")

        # Fallback if Ollama completely ignores markdown formatting and returns a plaintext block
        if found_sections == 0 and text.strip():
            logger.warning("SummaryAgent.parse_summary: Failed to parse structured markdown. Falling back to raw text.")
            sections["Objective"] = text.strip()
            sections["Findings"] = "(See Objective section for complete raw summary)"

        return sections

summary_agent_class = SummaryAgent
