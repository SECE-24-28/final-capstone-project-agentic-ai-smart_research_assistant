# Architecture Analysis: IEEE Research Assistant

## Project Overview
The IEEE Research Assistant is a multi-agent AI system designed to automate the academic literature review process. It leverages a local Large Language Model (LLM) and Retrieval Augmented Generation (RAG) to process research papers, generate summaries, perform comparative analyses, and answer user queries. The system is built for offline privacy and zero-cost operation, making it ideal for academic environments.

## Core Agents
- **Search Agent:** Interfaces with the CrossRef API (or mock data) to retrieve paper metadata (title, authors, year, DOI) and store it in the local database.
- **Summary Agent:** Uses RAG to extract key information (objective, methodology, findings, limitations) from uploaded PDFs and generates structured summaries.
- **Comparison Agent:** Synthesizes multiple stored summaries to provide side-by-side and thematic comparisons of different research works.
- **Chat Agent:** Provides a conversational interface for users to ask specific questions about uploaded papers, grounded in retrieved context from ChromaDB.

## Generation Services
- **Citation Service:** A deterministic service that formats paper metadata into IEEE-standard citation strings.
- **Research Gap Service:** Analyzes a collection of summaries to identify unexplored areas or contradictions in the current literature.
- **Literature Review Service:** Assembles a full, multi-section academic literature review based on the synthesized knowledge of multiple papers.

## RAG Workflow
1. **Ingestion:** PDF upload -> Text extraction (PyMuPDF) -> Text cleaning.
2. **Processing:** Recursive character chunking (500 tokens, 50-token overlap).
3. **Storage:** Chunks are embedded using `all-MiniLM-L6-v2` and stored in ChromaDB with metadata (paper_id, page_number).
4. **Retrieval:** Semantic search (cosine similarity) retrieves the top 3-5 most relevant chunks for a given query or task.
5. **Augmentation:** Retrieved chunks are injected into a task-specific prompt for the local LLM.

## Database Design
- **SQLite + SQLAlchemy:** Lightweight, serverless, and file-based persistence.
- **Key Tables:** `Session`, `Paper`, `Summary`, `Comparison`, `Citation`, `LiteratureReview`, `ChatHistory`.
- **Relational Integrity:** Foreign keys link all data to specific sessions and papers, ensuring clear data ownership and easy cleanup.

## API Design
- **FastAPI:** High-performance, async-capable REST API.
- **Endpoints:**
    - `POST /api/search`: Metadata lookup.
    - `POST /api/upload`: PDF processing and vectorization.
    - `POST /api/agent/summarize`: RAG summarization.
    - `POST /api/agent/compare`: Multi-paper analysis.
    - `POST /api/agent/cite`: IEEE citation generation.
    - `POST /api/chat`: Grounded Q&A.
    - `GET /api/report/{session_id}`: Full session data export.

## LangGraph Design
- **Coordinator Pattern:** A central coordinator node manages user intent and routes state to specialized agent/service nodes.
- **State Management:** `ResearchState` (TypedDict) tracks user inputs, retrieved context, LLM outputs, and results across the graph.
- **Persistence Node:** A dedicated node for writing results to SQLite after each agent/service execution.

## Local LLM Architecture
- **Model:** `Qwen/Qwen2.5-1.5B-Instruct`.
- **Optimization:** Loaded in `bfloat16` for memory efficiency; uses `device_map="auto"` for hardware acceleration.
- **Singleton Pattern:** LLM and Embedding models are loaded once at startup to avoid per-request overhead.
- **Quantization:** Optional 4-bit quantization support for 8GB RAM environments.

## Folder Structure Review
- **Standardized:** Clear separation of `frontend/` (React/Vite) and `backend/` (FastAPI).
- **Service-Oriented:** Logic is partitioned into `agents/` (orchestration), `services/` (domain logic), and `database/` (persistence).
- **Environment Management:** Root-level `pyproject.toml` and `uv.lock` follow modern UV conventions.

## Risks
- **Inference Speed:** CPU-only inference on 1.5B models may take 20-60 seconds, which might test user patience.
- **Model Reasoning Ceiling:** A 1.5B model may struggle with complex academic synthesis across more than 3-4 papers simultaneously.
- **PDF Extraction Artifacts:** Complex academic layouts (tables, formulas, multi-columns) can introduce noise during text extraction.

## Feasibility Review
- **High Feasibility:** The tech stack (FastAPI, React, SQLite, ChromaDB) is highly productive. The 7-day timeline is tight but achievable for a 2-developer team if they prioritize the Core MVP features.

## Suggested Improvements
- **Streaming Responses:** Implement SSE (Server-Sent Events) to stream LLM outputs to the UI, improving perceived speed.
- **Advanced Chunking:** Implement "Semantic Chunking" or "Parent-Document Retrieval" for better context accuracy.
- **Enhanced PDF Parsing:** Add logic to detect and ignore references/appendices during chunking to save context window.

## Missing Implementation Details
- **Prompt Engineering:** Detailed system prompts for each agent need to be finalized and tested for small-model instruction following.
- **Session Cleanup:** Logic for expiring or cleaning up old sessions and their associated files/vector stores.
- **Concurrency Strategy:** Handling multiple concurrent LLM requests on CPU-bound hardware (likely needs a simple task queue or semaphore).

## Recommended Implementation Order
1. **Foundation:** Initialize UV project, FastAPI app, SQLite models, and LLM singletons.
2. **Pipeline:** Implement PDF upload, text extraction, and ChromaDB vectorization.
3. **Core Features:** Implement Search Agent and Summary Agent (with UI).
4. **Advanced Features:** Implement Chat Agent and Comparison Agent.
5. **Services:** Implement Citation, Gap, and Literature Review services.
6. **Polish:** End-to-end testing, error handling, and performance optimization.
