# Final Project Report: Smart Research Assistant

## 1. Abstract
The Smart Research Assistant is an end-to-end, multi-agent AI platform designed to accelerate academic literature reviews. By integrating local LLMs (Ollama), vector databases (ChromaDB), and specialized autonomous agents, the system orchestrates the entire research lifecycle: from paper discovery and structured summarization to comparative analysis and final report generation.

## 2. System Architecture
The application follows a decoupled client-server architecture:
- **Frontend**: React + Vite + TailwindCSS. Uses Server-Sent Events (SSE) for real-time AI token streaming and asynchronous task polling.
- **Backend**: FastAPI. Manages REST endpoints, asynchronous task queues, and SQLite database persistence.
- **AI Layer**: Ollama running locally (qwen2.5:1.5b), integrated via a unified `llm_service` to eliminate external API dependencies.

## 3. Multi-Agent Design
The platform utilizes specialized agents, each governed by strict system prompts and output schemas:
1. **Search Agent**: Connects to the OpenAlex API to retrieve metadata and abstracts.
2. **Summary Agent**: Extracts Objective, Methodology, Findings, and Limitations. Features robust fallback parsing to guarantee data integrity.
3. **Comparison Agent**: Synthesizes multiple paper summaries into a rigid Markdown table, analyzing trends and highlighting gaps.
4. **Chat Agent**: Features dual-mode operation:
   - *General Mode*: Operates as a standard ChatGPT-like assistant when no papers are selected.
   - *RAG Mode*: Grounded strictly to ChromaDB context when papers are selected.

## 4. Advanced RAG & Cosine Similarity
### Vector Pipeline
When PDFs are uploaded or texts are queried, they are embedded using `BAAI/bge-small-en-v1.5` and stored in ChromaDB. The Chat Agent queries this database to inject high-relevance chunks directly into its prompt.

### Search Ranking
Instead of relying solely on OpenAlex's native sorting, retrieved abstracts are vectorized. The user's query is also vectorized, and a numpy-based **Cosine Similarity** function calculates the exact semantic distance. Papers are then re-ranked locally, and the score is displayed directly in the UI.

## 5. Report Generation & Export Engine
The `ReportService` acts as the final orchestrator. It executes a high-efficiency pipeline:
1. Gathers the user's selected papers.
2. Retrieves *cached* summaries and comparisons from SQLite to avoid redundant LLM generation time and compute costs.
3. Directs the LLM to write a comprehensive Abstract, Insights, and Future Work section based on the cached context.
4. **Citation Service:** Calculates accurate IEEE formatting from the paper's metadata and explicitly appends the bibliography, effectively neutralizing the LLM hallucination risk.

**Exports:** The resulting Markdown is processed through modular services:
- `reportlab.platypus` for highly-structured, justified PDF generation.
- `python-docx` for native Microsoft Word styling and heading layouts.

## 6. Performance Metrics & Stability
- **SQLite WAL Mode**: Enabled Write-Ahead Logging to prevent database locking during heavy concurrent Agent tasks.
- **Task Tracking**: Long-running LLM inferences (Summary, Comparison, Report) are moved off the main thread into a global `CoordinatorRun` task tracker, providing the frontend with real-time progress bars.

## 7. Conclusion
The Smart Research Assistant successfully demonstrates how localized, quantized models can be composed into highly effective, structured workflow pipelines. By combining vector heuristics with caching and strict Agent roles, the platform presents a production-ready solution for academic synthesis.
