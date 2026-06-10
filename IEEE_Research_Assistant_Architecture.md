# IEEE Research Assistant Using Multi-Agent AI
## Software Architecture Specification Document — Revised Edition

**Version:** 2.0  
**Date:** June 2026  
**Team Size:** 2 Developers  
**Timeline:** 1 Week (7 Days)  
**Project Type:** Engineering Mini Project  
**Classification:** Internal — Academic Use  
**Status:** Final — Approved for Submission

---

## Table of Contents

1. Executive Summary
2. Project Objectives
3. Problem Statement
4. Proposed Solution
5. Why Multi-Agent Architecture?
6. Why Local AI Instead of Cloud APIs?
7. Functional Requirements
8. MVP Scope
9. Multi-Agent Architecture
10. System Architecture
11. Local LLM Architecture
12. Model Optimization Strategy
13. RAG Architecture
14. Technology Stack Justification
15. Project Folder Structure
16. Database Design
17. API Design
18. LangGraph Design
19. Development Plan
20. Evaluation Metrics
21. Testing Strategy
22. Risk Analysis
23. Known Limitations
24. Cost Analysis
25. Future Enhancements
26. Conclusion

---

## 1. Executive Summary

### 1.1 Problem Statement

Conducting a thorough literature review is one of the most time-intensive and cognitively demanding phases of academic research. Students and researchers must search across multiple sources, read and comprehend dozens of papers, extract key findings, identify thematic overlaps, locate knowledge gaps, and produce correctly formatted IEEE citations — all before writing begins. This process can take weeks and is prone to human error, inconsistency, and oversight.

### 1.2 Existing Challenges

- Manual literature searches across disparate databases are slow and incomplete.
- Reading and summarizing individual papers requires significant time investment.
- Comparing multiple papers for methodology, findings, and limitations is error-prone when done manually.
- Identifying research gaps requires deep domain synthesis across many sources simultaneously.
- IEEE citation formatting is tedious and frequently contains errors when produced manually.
- Writing a structured literature review requires synthesizing all of the above at once.
- Most existing AI tools are proprietary, cloud-dependent, expensive, and unsuitable for offline academic environments.

### 1.3 Proposed Solution

This project proposes a **Multi-Agent AI Research Assistant** that automates the complete literature review pipeline. The system uses a coordinated set of specialized AI agents and generation services — each responsible for a discrete task — orchestrated by a central Coordinator Agent via LangGraph. All AI inference runs locally using `Qwen/Qwen2.5-1.5B-Instruct` through Hugging Face Transformers, embeddings via `sentence-transformers/all-MiniLM-L6-v2`, and semantic search via ChromaDB. No cloud APIs or paid services of any kind are required.

### 1.4 Expected Benefits

- Reduces literature review preparation time from weeks to hours.
- Produces consistent, reproducible summaries and citations.
- Enables AI-powered conversational queries directly over uploaded PDFs.
- Runs entirely on local hardware with zero API cost and full offline capability.
- Protects data privacy — no research content is ever transmitted to external servers.
- Provides a practical demonstration of multi-agent AI, RAG, and LangGraph in a real-world academic context.

---

## 2. Project Objectives

The following measurable objectives define the success criteria for this project:

1. **Search Integration:** The system must retrieve research paper metadata from an accessible source given a keyword query within 10 seconds.
2. **PDF Processing:** The system must extract full text from an uploaded PDF and store it in the vector database within 30 seconds for a standard 10-page paper.
3. **Summarization:** The system must generate a structured summary (objective, methodology, findings, limitations) for any processed paper using the local LLM.
4. **Comparison:** The system must compare two or more uploaded papers across defined dimensions and return a structured comparison report.
5. **Citation Generation:** The system must produce a correctly formatted IEEE citation string for any processed paper using structured metadata — no LLM generation required for this step.
6. **Research Gap Analysis:** The system must identify and articulate potential research gaps based on a set of uploaded paper summaries (secondary feature, post-core-MVP).
7. **Literature Review Generation:** The system must generate a structured literature review section covering introduction, thematic groupings, gaps, and conclusion (secondary feature, post-core-MVP).
8. **RAG-Powered Chat:** The system must answer natural-language questions about uploaded papers using retrieved context from ChromaDB.
9. **Local Execution:** All model inference must run on local hardware without any internet-dependent API calls after the initial model download.
10. **Completion within Timeline:** All core MVP features must be implemented, tested, and demonstrated within 7 calendar days by a 2-developer team.

---

## 3. Problem Statement

Academic research begins with a literature review — the systematic identification, reading, analysis, and synthesis of existing scholarly work relevant to a research question. Despite being foundational to the research process, literature review is widely acknowledged as:

**Time-Consuming:** A thorough review of 20–30 papers can take 2–4 weeks for a graduate student, representing a significant barrier to research productivity.

**Cognitively Demanding:** Researchers must simultaneously track themes, methodologies, datasets, findings, and contradictions across many sources while formulating their own analytical perspective.

**Error-Prone:** Manual citation formatting, especially to IEEE standards, frequently contains errors. Human summaries are subjective and may omit critical details.

**Inaccessible to Automated Tools:** Most AI-powered research tools (Semantic Scholar AI, Elicit, ResearchRabbit) are either proprietary, require internet access, impose usage costs, or do not support deep PDF analysis with conversational query.

**Fragmented:** No single tool covers the complete workflow — from paper search to final literature review generation — within a single integrated offline-capable interface.

For students in resource-constrained environments, or those working in offline or privacy-sensitive settings, cloud-dependent AI tools are not a viable option. A local, open-source, multi-capable system that respects data privacy and operates without subscription fees is a genuine and unaddressed academic need.

---

## 4. Proposed Solution

The IEEE Research Assistant is a web-based application with a React frontend and FastAPI backend. At its core is a multi-agent AI system orchestrated using LangGraph. The system distinguishes between two categories of components: **Core Agents**, which involve LLM-driven reasoning and RAG retrieval, and **Generation Services**, which produce structured outputs using deterministic logic and optionally light LLM formatting.

**Core Agents (LLM + RAG):**

- A **Search Agent** queries available metadata APIs and returns structured paper records.
- A **Summary Agent** processes uploaded PDFs through a RAG pipeline, extracting and summarizing key academic content using the local LLM.
- A **Comparison Agent** receives multiple paper summaries and performs structured comparative analysis using the LLM.
- A **Chat Agent** enables conversational interaction with uploaded papers using ChromaDB retrieval and LLM-based response generation.

**Generation Services (deterministic + optional LLM formatting):**

- A **Citation Service** produces IEEE-formatted citation strings directly from structured paper metadata in the database.
- A **Research Gap Service** synthesizes stored summaries to identify unexplored research directions using the LLM.
- A **Literature Review Service** assembles a complete, structured academic literature review section from all processed materials using the LLM.

**Coordinator Agent** routes all user requests to the appropriate agent or service, manages state via LangGraph, and assembles final responses.

All AI computation is performed locally. The `Qwen/Qwen2.5-1.5B-Instruct` model handles text generation. The `sentence-transformers/all-MiniLM-L6-v2` model produces dense vector embeddings. ChromaDB stores and retrieves embeddings. SQLite persists metadata, sessions, and generated content. UV manages all Python dependencies from the project root.

---

## 5. Why Multi-Agent Architecture?

### 5.1 Limitations of a Single-Agent Approach

A single LLM agent tasked with the entire literature review pipeline would face the following problems:

- **Context Overload:** A 1.5B parameter model has a limited effective context window. Feeding entire papers, comparison logic, citation rules, and chat history into a single prompt rapidly degrades output quality.
- **Task Confusion:** A generalist prompt mixing summarization, comparison, gap analysis, and literature review generation produces mediocre results across all tasks simultaneously, because the model cannot optimize for any one task.
- **No Specialization:** Each literature review sub-task has a distinct output structure, prompting strategy, and validation requirement. A single agent cannot optimize for all of these at once.
- **Debugging Difficulty:** When a monolithic agent fails, isolating the source of failure — search, summarization, comparison, or generation — is significantly harder than isolating a discrete agent.
- **Scalability:** Adding new capabilities to a monolithic agent requires restructuring the entire prompt and routing logic.

### 5.2 Advantages of Multi-Agent Architecture

- **Specialization:** Each agent receives a focused, minimal prompt optimized for its specific task. The Summary Agent uses an academic summarization prompt; the Comparison Agent uses a structured comparative analysis prompt. Output quality improves substantially when the prompt is short and single-purpose.
- **Modularity:** Each agent and service can be implemented, tested, debugged, and improved in isolation without affecting others.
- **State Management:** LangGraph enables explicit state tracking across agent transitions, making the system auditable, deterministic, and reliable.
- **Separation of Concerns:** The distinction between Core Agents (LLM-dependent) and Generation Services (deterministic) ensures that simple tasks like citation formatting do not unnecessarily consume model inference time or introduce hallucination risk.
- **Extensibility:** New agents (Trend Analyzer, Recommendation Agent) can be added to the LangGraph graph without modifying existing agent implementations.

### 5.3 Why Agent Specialization Improves Performance on Small Models

For a 1.5B parameter model, prompt complexity and length are the primary determinants of output quality. Shorter, focused prompts with a single, clearly scoped instruction produce significantly better outputs than long, multi-objective prompts. By routing each task to a specialized agent with a curated system prompt and focused context, the coordinator ensures the model receives exactly the context it needs. This is the core reason why a multi-agent approach with a small local model outperforms a single-agent approach on the same hardware.

---

## 6. Why Local AI Instead of Cloud APIs?

### 6.1 Overview

This project deliberately selects local, open-source AI models over cloud API services. This is not simply a cost decision — it reflects a set of principled technical and academic choices that are appropriate for this use case.

### 6.2 Benefits of Local AI

**Zero API Cost**
Cloud AI APIs (OpenAI GPT-4, Google Gemini, Anthropic Claude) charge on a per-token basis. For a research assistant that processes dozens of full academic papers, generates summaries, comparisons, and literature reviews, the cumulative API cost would be substantial and unpredictable. Local inference has zero ongoing cost after hardware acquisition.

**Offline Capability**
Once the model weights are downloaded, the entire system operates without any internet connection. This is essential for researchers working in low-connectivity environments, on institutional networks with restricted external access, or in areas with unreliable internet.

**Data Privacy**
When using cloud APIs, user data — including the full text of uploaded research papers, research questions, and generated outputs — is transmitted to third-party servers. This raises significant concerns for researchers working on unpublished work, confidential data, or proprietary research. With local inference, no data ever leaves the user's machine.

**Academic Ownership**
A project built on local, open-source models is fully owned by the academic team. There is no dependency on a vendor's API versioning, deprecation schedule, or pricing changes. The system can be reproduced, evaluated, and submitted for academic review without any third-party service dependency.

**No Vendor Lock-in**
The architecture is model-agnostic at the inference layer. Switching from Qwen2.5-1.5B to any other Hugging Face Transformers-compatible model requires changing a single configuration value — not rearchitecting the system. This flexibility is not available with cloud APIs.

### 6.3 Tradeoffs of Local AI

**Smaller Models**
Due to hardware constraints, this project uses `Qwen/Qwen2.5-1.5B-Instruct`, a 1.5B parameter model. This is significantly smaller than cloud models (GPT-4 is estimated at hundreds of billions of parameters). Output quality on complex reasoning and synthesis tasks will be lower than what cloud APIs can produce.

**Slower Inference**
Without a dedicated GPU, local inference takes considerably longer than cloud API responses. Summarizing a 10-page paper may take 20–60 seconds on CPU. This is an acceptable tradeoff for an offline academic tool but would be unacceptable for a real-time production application.

**Limited Reasoning Capability**
A 1.5B model has reduced capacity for multi-hop reasoning, mathematical analysis, and nuanced academic synthesis compared to larger models. The RAG architecture and structured prompting strategy compensate for this by supplying relevant context directly, but the model's reasoning ceiling remains a genuine constraint.

### 6.4 Why Local AI Was Selected for This Project

The project's requirements — zero cost, offline capability, data privacy, and academic reproducibility — collectively make local AI the only appropriate choice. The research assistant is designed for students and researchers, many of whom cannot access or afford cloud APIs. The tradeoffs in output quality and inference speed are acceptable for this use case, and the RAG architecture substantially mitigates the quality gap by grounding all outputs in retrieved source text rather than relying solely on the model's parametric knowledge.

---

## 7. Functional Requirements

### 7.1 Core Agent: Search Agent

**Responsibilities:**
- Accept a keyword query from the user.
- Search for research paper metadata from available sources (CrossRef API, with local mock data fallback).
- Return structured paper records including title, authors, abstract, year, DOI, and journal.
- Store retrieved metadata in the SQLite `Paper` table for later reference.

**Inputs:**
- Query string (e.g., "transformer attention mechanisms NLP")
- Optional filters: year range, number of results

**Outputs:**
- List of paper records (title, authors, year, abstract, DOI, source)
- Confirmation of storage in database

---

### 7.2 Core Agent: Summary Agent

**Responsibilities:**
- Accept a paper ID corresponding to an uploaded and processed PDF.
- Retrieve relevant text chunks from ChromaDB using semantic search, filtered to the specified paper.
- Construct a focused RAG prompt injecting retrieved chunks as context.
- Generate a structured summary using the local LLM covering: research objective, methodology, datasets used, key findings, limitations, and contributions.
- Store the generated summary in the SQLite `Summary` table.

**Inputs:**
- Paper ID
- Optional: custom focus question

**Outputs:**
- Structured summary object (objective, methodology, findings, limitations, contributions)
- Stored summary record

---

### 7.3 Core Agent: Comparison Agent

**Responsibilities:**
- Accept two or more paper IDs.
- Retrieve stored summaries for each paper from the SQLite `Summary` table.
- Construct a structured comparison prompt using the retrieved summaries as context.
- Generate a comparative analysis covering: research objectives, methodologies, datasets, findings, limitations, and relative strengths.
- Store the comparison result in the SQLite `Comparison` table.

**Inputs:**
- List of paper IDs (minimum 2)
- Optional: specific comparison dimension (e.g., "methodology only")

**Outputs:**
- Structured comparison report (per-paper breakdown and cross-paper synthesis)
- Stored comparison record

---

### 7.4 Core Agent: Chat Agent

**Responsibilities:**
- Accept a natural-language question from the user about one or more uploaded papers.
- Retrieve the most semantically relevant text chunks from ChromaDB for the specified paper(s).
- Construct a RAG prompt combining the question with retrieved context.
- Generate a grounded answer using the local LLM.
- Append the conversation turn to the SQLite `ChatHistory` table.

**Inputs:**
- User question (string)
- Session ID
- Paper ID(s) scope (optional — if not specified, searches across all uploaded papers in the session)

**Outputs:**
- AI-generated answer string
- Source chunk references (paper title, page number, chunk index)
- Updated chat history record

---

### 7.5 Generation Service: Citation Service

**Responsibilities:**
- Accept a paper ID.
- Retrieve paper metadata (title, authors, year, journal, volume, issue, pages, DOI) directly from the SQLite `Paper` table.
- Format the metadata as a correctly structured IEEE citation string using deterministic string assembly — no LLM call required.
- Support both journal article and conference paper citation formats.
- Store the citation string in the SQLite `Citation` table.

**Inputs:**
- Paper ID
- Citation type: "journal" or "conference"

**Outputs:**
- IEEE-formatted citation string
- Stored citation record

**Note:** Citation generation is implemented as a deterministic service, not an LLM-based agent, because IEEE citation format is a strict template that is fully computable from structured metadata. This eliminates hallucination risk for citation output entirely.

---

### 7.6 Generation Service: Research Gap Service

**Responsibilities:**
- Accept a set of paper IDs (minimum 3 recommended for meaningful synthesis).
- Retrieve stored summaries for all specified papers from SQLite.
- Construct a synthesis prompt instructing the LLM to identify common themes, methodological overlaps, contradictions, and unexplored directions across the set.
- Generate a structured research gap analysis.
- Store the result in the SQLite `LiteratureReview` table under `review_type = "gap_analysis"`.

**Inputs:**
- List of paper IDs
- Optional: domain context string provided by the user

**Outputs:**
- Structured gap analysis (identified themes, common limitations, suggested future directions)
- Stored record

---

### 7.7 Generation Service: Literature Review Service

**Responsibilities:**
- Accept a set of paper IDs.
- Retrieve summaries, available comparisons, and gap analysis from SQLite for all specified papers.
- Construct a multi-part generation prompt that provides the LLM with the full synthesized context.
- Generate a structured academic literature review including: introduction, thematic categorization, methodology comparison, findings synthesis, identified gaps, and conclusion.
- Store the full review in the SQLite `LiteratureReview` table under `review_type = "full_review"`.

**Inputs:**
- List of paper IDs
- Optional: research topic context provided by the user

**Outputs:**
- Complete structured literature review (multi-section academic text)
- Stored review record

---

## 8. MVP Scope

Given the 2-developer, 7-day constraint, scope is explicitly tiered. The team commits to the core tier and attempts the secondary tier as time permits.

### 8.1 Must Build — Core MVP

The following items must be completed for a successful project demonstration:

- UV project initialization at the project root with `pyproject.toml` and `uv.lock`
- FastAPI backend with all core endpoints
- LangGraph coordinator with 4 core agents wired
- PDF upload endpoint with PyMuPDF text extraction and chunking pipeline
- ChromaDB embedding storage and retrieval (sentence-transformers/all-MiniLM-L6-v2)
- Qwen/Qwen2.5-1.5B-Instruct inference loaded via Hugging Face Transformers
- Shared model singleton loaded once at startup via `llm_service.py`
- SQLite database with all required schema tables (SQLAlchemy ORM)
- Search Agent — CrossRef API query, SQLite storage, mock fallback
- Summary Agent — RAG-based structured summary generation
- Comparison Agent — multi-paper structured comparison
- Chat Agent — RAG-based conversational Q&A with source references
- Citation Service — deterministic IEEE citation string generation
- React + Vite + Tailwind CSS frontend
- Search results UI panel
- PDF upload UI panel
- Summary display view
- Comparison display view
- Chat interface with source chunk references
- IEEE citation display panel

### 8.2 Secondary Features — Build if Time Allows (Days 5–6)

These features are valuable but deferred if core MVP is not yet stable:

- Research Gap Service — LLM-based gap identification from stored summaries
- Literature Review Service — LLM-based full review generation
- Research gap display panel in the frontend
- Literature review display panel in the frontend
- Session report aggregation endpoint (`GET /api/report/{session_id}`)
- Loading indicators and progress feedback for long LLM tasks

### 8.3 Future Features — Post-Submission

The following are out of scope for the 1-week timeline and are documented as future work:

- Semantic Scholar and arXiv API integration
- Trend Analysis Agent
- Recommendation Agent
- Export to DOCX format
- Export to LaTeX format
- Figure and image understanding from PDF content
- Streaming LLM responses via server-sent events
- User authentication and multi-user session support
- Docker containerization for portable deployment
- Fine-tuned or quantized model for academic domain performance

---

## 9. Multi-Agent Architecture

### 9.1 Component Overview

```
CORE AGENTS (LLM + RAG)         GENERATION SERVICES (deterministic + LLM)
------------------------         ------------------------------------------
Search Agent                     Citation Service
Summary Agent                    Research Gap Service
Comparison Agent                 Literature Review Service
Chat Agent
```

### 9.2 High-Level Coordinator Flow

```
User Request
     |
     v
Coordinator Agent (LangGraph)
     |
     +---> [intent: search]      --> Search Agent
     |                                    |
     +---> [intent: summarize]   --> Summary Agent
     |                                    |
     +---> [intent: compare]     --> Comparison Agent
     |                                    |
     +---> [intent: chat]        --> Chat Agent
     |                                    |
     +---> [intent: cite]        --> Citation Service (deterministic)
     |                                    |
     +---> [intent: gaps]        --> Research Gap Service
     |                                    |
     +---> [intent: review]      --> Literature Review Service
     |                                    |
     +---> [intent: unknown]     --> Error Handler
     |
     v
  Component Output
     |
     v
  State Update (LangGraph)
     |
     v
  Persist to SQLite
     |
     v
  JSON Response to Frontend
```

### 9.3 Coordinator Agent Internal Flow

```
Incoming API Request
     |
     v
  Read intent from request body
     |
     v
  Validate required parameters
  (paper_ids, session_id, question, etc.)
     |
     v
  Set state.intent and state.current_component
     |
     v
  Route via LangGraph conditional edge
     |
     v
  Receive structured result from component
     |
     v
  Trigger persist_node (write to SQLite)
     |
     v
  Format and return JSON response
```

### 9.4 Summary Agent Internal Flow

```
Input: paper_id
  |
  v
Fetch paper record from SQLite
  |
  v
Embed summarization query with all-MiniLM-L6-v2
  |
  v
Query ChromaDB — filter by paper_id, retrieve top-5 chunks
  |
  v
Build focused RAG prompt
  [SYSTEM]: Academic summarizer role
  [CONTEXT]: top-5 retrieved chunks
  [INSTRUCTION]: Structured summary fields
  |
  v
Send to Qwen2.5-1.5B-Instruct
  |
  v
Parse LLM output into structured fields
  |
  v
Store in SQLite Summary table
  |
  v
Return structured summary to Coordinator
```

### 9.5 Chat Agent Internal Flow

```
Input: question + session_id + optional paper_ids
  |
  v
Embed question with all-MiniLM-L6-v2
  |
  v
Query ChromaDB
  Filter by: paper_ids (if scoped)
  Retrieve: top-5 chunks by cosine similarity
  |
  v
Build RAG chat prompt
  [SYSTEM]: Grounded assistant role
  [CONTEXT]: top-5 retrieved chunks
  [QUESTION]: user question
  |
  v
Send to Qwen2.5-1.5B-Instruct
  |
  v
Parse LLM answer
  |
  v
Append to ChatHistory in SQLite (role: "assistant")
  |
  v
Return answer + source chunk references
```

### 9.6 Citation Service Flow (Deterministic — No LLM)

```
Input: paper_id + citation_type ("journal" | "conference")
  |
  v
Fetch paper metadata from SQLite
  (authors, title, journal, year, volume, issue, pages, doi)
  |
  v
Apply IEEE citation template
  Journal format:
    [N] A. Author, "Title," Journal, vol. X, no. Y, pp. Z, Year.
  Conference format:
    [N] A. Author, "Title," in Proc. Conf. Name, Year, pp. Z.
  |
  v
Store citation string in SQLite Citation table
  |
  v
Return formatted citation string
```

### 9.7 Research Gap Service Flow

```
Input: paper_ids + optional domain_context
  |
  v
Fetch stored summaries for all paper_ids from SQLite
  |
  v
Concatenate summaries into synthesis context
  |
  v
Build gap analysis prompt
  [SYSTEM]: Research synthesizer role
  [CONTEXT]: all summaries
  [INSTRUCTION]: Identify themes, gaps, future directions
  |
  v
Send to Qwen2.5-1.5B-Instruct
  |
  v
Parse and structure output
  |
  v
Store in SQLite LiteratureReview table (type: "gap_analysis")
  |
  v
Return structured gap analysis
```

---

## 10. System Architecture

### 10.1 Layered Architecture Overview

```
+----------------------------------------------------------+
|                   PRESENTATION LAYER                     |
|           React + Vite + Tailwind CSS + React Query      |
|  Search | Upload | Summary | Compare | Chat | Review     |
+----------------------------------------------------------+
                           |
                      HTTP / REST (JSON)
                           |
+----------------------------------------------------------+
|                      API LAYER                           |
|                    FastAPI Backend                       |
|       Routers: search, upload, agents, chat, report      |
+----------------------------------------------------------+
                           |
+----------------------------------------------------------+
|                  ORCHESTRATION LAYER                     |
|             LangGraph + LangChain                        |
|   Coordinator --> Core Agents + Generation Services      |
+----------------------------------------------------------+
              |                          |
+-------------------------+  +---------------------------+
|       AI / ML LAYER     |  |       DATA LAYER          |
|                         |  |                           |
| Qwen2.5-1.5B-Instruct   |  | SQLite                    |
| (Hugging Face           |  | (via SQLAlchemy ORM)      |
|  Transformers)          |  |                           |
|                         |  | ChromaDB                  |
| all-MiniLM-L6-v2        |  | (Vector Store,            |
| (Sentence Transformers) |  |  persisted to disk)       |
|                         |  |                           |
| PyMuPDF                 |  | /backend/uploads/         |
| (PDF text extraction)   |  | (uploaded PDF files)      |
+-------------------------+  +---------------------------+
```

### 10.2 Frontend Component Tree

```
frontend/src/
  |
  +-- App.jsx (router root)
  |
  +-- pages/
  |     +-- Home.jsx           (dashboard / session overview)
  |     +-- Search.jsx         (paper search interface)
  |     +-- Upload.jsx         (PDF upload interface)
  |     +-- Review.jsx         (literature review + gap analysis)
  |     +-- Chat.jsx           (RAG chat interface)
  |
  +-- components/
        +-- Layout.jsx         (navigation shell)
        +-- SearchPanel.jsx    (query input + results list)
        +-- UploadPanel.jsx    (drag-drop upload + progress)
        +-- SummaryView.jsx    (structured summary display)
        +-- ComparisonView.jsx (side-by-side comparison display)
        +-- ChatInterface.jsx  (message thread + source refs)
        +-- CitationList.jsx   (IEEE citation strings)
        +-- ReviewPanel.jsx    (literature review sections)
        +-- GapPanel.jsx       (research gap analysis display)
        +-- Spinner.jsx        (loading indicator)
        +-- ErrorAlert.jsx     (error message display)
```

### 10.3 Backend Module Structure

```
backend/
  |
  +-- main.py                  (FastAPI app entry, startup events)
  +-- config.py                (model paths, DB path, constants)
  |
  +-- routers/
  |     +-- search.py          (POST /api/search)
  |     +-- upload.py          (POST /api/upload)
  |     +-- agents.py          (POST /api/agent/*)
  |     +-- chat.py            (POST /api/chat)
  |     +-- report.py          (GET /api/report/{session_id})
  |
  +-- agents/
  |     +-- coordinator.py     (LangGraph graph + state machine)
  |     +-- state.py           (ResearchState TypedDict)
  |     +-- search_agent.py    (CrossRef query + storage)
  |     +-- summary_agent.py   (RAG retrieval + LLM summary)
  |     +-- comparison_agent.py(multi-summary LLM comparison)
  |     +-- chat_agent.py      (RAG retrieval + LLM chat)
  |
  +-- services/
  |     +-- llm_service.py     (Qwen model singleton + generate())
  |     +-- embedding_service.py (all-MiniLM-L6-v2 singleton)
  |     +-- pdf_service.py     (PyMuPDF extraction + chunking)
  |     +-- search_service.py  (CrossRef API + mock fallback)
  |     +-- citation_service.py(deterministic IEEE formatter)
  |     +-- gap_service.py     (LLM-based gap synthesis)
  |     +-- review_service.py  (LLM-based review generation)
  |
  +-- database/
  |     +-- models.py          (SQLAlchemy table definitions)
  |     +-- session.py         (database session factory)
  |     +-- init_db.py         (create tables on startup)
  |     +-- research_assistant.db (SQLite file, auto-created)
  |
  +-- vectorstore/
  |     +-- chroma_client.py   (ChromaDB init + collection ops)
  |     +-- chroma_db/         (ChromaDB persistent storage)
  |
  +-- schemas/
  |     +-- paper.py
  |     +-- summary.py
  |     +-- comparison.py
  |     +-- citation.py
  |     +-- chat.py
  |     +-- review.py
  |
  +-- uploads/                 (uploaded PDFs, organized by session)
```

### 10.4 Request Lifecycle (Summarize Example)

```
User clicks "Summarize" on a paper
  |
  v
React fires POST /api/agent/summarize { paper_id, session_id }
  |
  v
FastAPI router validates request via Pydantic schema
  |
  v
LangGraph graph invoked with initial ResearchState
  |
  v
Coordinator node sets intent = "summarize"
  |
  v
Conditional edge routes to summary_node
  |
  v
Summary Agent:
  1. Fetches paper record from SQLite
  2. Embeds summarization query with all-MiniLM-L6-v2
  3. Queries ChromaDB (filter: paper_id, top-5 chunks)
  4. Builds RAG prompt with retrieved context
  5. Calls llm_service.generate() -> Qwen2.5-1.5B-Instruct
  6. Parses structured output (objective, findings, etc.)
  |
  v
persist_node writes Summary record to SQLite
  |
  v
LangGraph returns final state.agent_result
  |
  v
FastAPI serializes to JSON response
  |
  v
React Query updates SummaryView component
```

---

## 11. Local LLM Architecture

### 11.1 Selected Model: Qwen/Qwen2.5-1.5B-Instruct

**Model Card:**

| Property | Value |
|---|---|
| Model ID | Qwen/Qwen2.5-1.5B-Instruct |
| Parameter Count | 1.5 Billion |
| Architecture | Decoder-only Transformer |
| Context Window | Up to 32,768 tokens |
| Format | Instruction-tuned (Qwen chat template) |
| License | Apache 2.0 |
| Source | Hugging Face Hub |
| Download Size | Approximately 3 GB (bf16) |

### 11.2 Why Qwen2.5-1.5B-Instruct Was Selected

- **Hardware Accessibility:** At 1.5B parameters, the model fits comfortably in RAM on machines with as little as 8 GB, making it suitable for standard development laptops without a GPU.
- **Instruction Following:** The `-Instruct` variant is fine-tuned for instruction following using supervised fine-tuning and RLHF, which is critical for structured output tasks (summarization, comparison, review generation).
- **Reduced from 3B:** The previous architecture specified 3B, which imposes higher memory and inference-time costs. Moving to 1.5B provides better feasibility on constrained hardware while retaining acceptable instruction-following quality, especially when combined with RAG grounding.
- **Apache 2.0 License:** Fully open for academic and commercial use without restrictions.
- **Hugging Face Native:** Loadable via standard `AutoModelForCausalLM` and `AutoTokenizer` APIs; no custom inference server required.
- **UV Compatibility:** All inference dependencies (`torch`, `transformers`, `accelerate`) are standard pip packages installable via UV.

### 11.3 Advantages

- Zero API cost — runs entirely on local hardware after model download.
- No internet dependency during inference.
- Full control over generation parameters (temperature, max tokens, top_p, repetition penalty).
- Supports the Qwen2.5 chat template for structured prompt formatting.
- Compatible with `torch`, `transformers`, and `accelerate` ecosystem.
- Smaller size than 3B means faster loading and lower peak RAM usage.

### 11.4 Limitations

- Output quality is lower than larger models on complex multi-document synthesis.
- Inference on CPU is slow — 20–60 seconds per generation depending on task and hardware.
- Hallucination risk is inherent; RAG grounding is essential to mitigate it.
- Limited capacity for multi-hop reasoning across many papers simultaneously.
- May struggle to produce full literature reviews in a single pass; generation should be scoped to focused sections.

### 11.5 Hardware Requirements

```
Minimum Configuration (CPU Only):
  RAM:     8 GB  (model requires ~3.5 GB in bfloat16; rest for OS and app)
  CPU:     Modern multi-core (Intel Core i5/i7 or AMD Ryzen 5/7)
  Storage: 8 GB free (model weights + ChromaDB + SQLite + uploads)

Recommended Configuration:
  RAM:     12 GB
  CPU:     Modern multi-core with AVX2 support
  Storage: 15 GB free
  GPU:     NVIDIA with 4+ GB VRAM (optional but significantly faster)

Optimal Configuration:
  RAM:     16 GB
  GPU:     NVIDIA with 4–6 GB VRAM (CUDA 11.8 or 12.x)
  Storage: 20 GB free

Inference Speed Estimates:
  CPU only (8 GB RAM):    20–60 seconds per generation
  CPU only (16 GB RAM):   15–45 seconds per generation
  GPU (4 GB VRAM):         3–8 seconds per generation
  GPU (6 GB VRAM):         2–5 seconds per generation
```

### 11.6 Prompt Flow

```
Agent-Specific System Prompt
(e.g., "You are an academic summarizer. Be concise and structured.")
  |
  v
Context Injection Block
(Retrieved chunks from ChromaDB inserted as [CONTEXT])
  |
  v
Task Instruction
(e.g., "Summarize the paper above using the following fields: ...")
  |
  v
Qwen2.5 Chat Template Applied
(apply_chat_template with tokenize=False)
  |
  v
Tokenization via AutoTokenizer
  |
  v
Model.generate() called with generation parameters
  |
  v
Decode output token IDs to string
  |
  v
Post-process: strip prompt echo, parse structured fields
  |
  v
Return clean structured output to calling agent
```

### 11.7 Generation Parameters

```
Task-Specific Defaults:

Summary Generation:
  max_new_tokens:      512
  temperature:         0.3
  top_p:               0.9
  repetition_penalty:  1.1
  do_sample:           True

Chat Response:
  max_new_tokens:      256
  temperature:         0.4
  top_p:               0.9
  repetition_penalty:  1.1
  do_sample:           True

Literature Review / Gap Analysis:
  max_new_tokens:      768
  temperature:         0.3
  top_p:               0.9
  repetition_penalty:  1.15
  do_sample:           True

Comparison:
  max_new_tokens:      512
  temperature:         0.25
  top_p:               0.9
  repetition_penalty:  1.1
  do_sample:           True
```

---

## 12. Model Optimization Strategy

### 12.1 Overview

A 1.5B parameter model loaded with default settings on CPU can have unacceptable inference times for an interactive research assistant. The following optimization strategies are applied in the `llm_service.py` singleton to maximize inference performance within the available hardware.

### 12.2 Precision Optimization

By default, Hugging Face Transformers loads model weights in float32, which doubles memory usage unnecessarily on modern hardware. The system loads the model in `bfloat16` (or `float16` on older hardware) instead. This halves the model's memory footprint — from approximately 6 GB to approximately 3 GB — and enables faster matrix operations on CPUs with AVX support and on any CUDA GPU.

```
Loading strategy:
  torch_dtype = torch.bfloat16   (preferred on modern hardware)
  torch_dtype = torch.float16    (fallback for older GPUs)
  torch_dtype = torch.float32    (fallback for pure CPU without AVX)
```

### 12.3 Device Auto-Detection

The system uses `device_map="auto"` from the `accelerate` library to automatically detect available hardware and assign model layers accordingly. The priority order is:

```
Detection Priority:
  1. CUDA GPU (NVIDIA) — fastest; model loaded fully to GPU VRAM
  2. MPS (Apple Silicon) — good CPU-adjacent performance on Mac
  3. CPU — fallback; functional but slower
```

This eliminates the need for hardware-specific configuration code. The same `llm_service.py` works correctly on both GPU-equipped and CPU-only machines without modification.

### 12.4 Optional 4-Bit Quantization

For machines with very limited RAM (8 GB minimum, heavy system load), 4-bit quantization via the `bitsandbytes` library can be enabled. Quantization reduces the model from ~3 GB (bfloat16) to approximately 1.2 GB in memory, at the cost of a small reduction in output quality.

```
Quantization is optional and disabled by default.
Enable via config flag: USE_4BIT_QUANTIZATION = True

When enabled:
  BitsAndBytesConfig:
    load_in_4bit = True
    bnb_4bit_compute_dtype = torch.bfloat16
    bnb_4bit_use_double_quant = True
    bnb_4bit_quant_type = "nf4"
```

Quantization is recommended for demonstration machines with 8 GB RAM and no GPU.

### 12.5 Shared Model Singleton

Both the LLM and the embedding model are expensive to load (10–30 seconds each). Loading them per-request would make the system unusable. The `llm_service.py` and `embedding_service.py` modules implement a singleton pattern:

```
Application Startup (FastAPI lifespan event):
  |
  v
llm_service.load_model()
  Load Qwen2.5-1.5B-Instruct once
  Hold in module-level variable
  |
  v
embedding_service.load_model()
  Load all-MiniLM-L6-v2 once
  Hold in module-level variable
  |
  v
All agent requests share the same loaded model instances
No model is loaded more than once per application lifecycle
```

### 12.6 Prompt Length Management

The 1.5B model degrades in quality when the prompt becomes very long. Prompt length is actively managed:

```
Maximum context budget per task:
  System prompt:        ~100 tokens  (fixed per agent)
  Retrieved chunks:     ~1,000 tokens (5 chunks × ~200 tokens each)
  Task instruction:     ~100 tokens  (fixed per task)
  Total input budget:   ~1,200 tokens

If retrieved chunks exceed budget:
  Truncate to top-3 chunks instead of top-5
  Apply hard token limit during chunk assembly
```

### 12.7 Memory Optimization Summary

```
Strategy                        Memory Saving    Quality Impact
-------                         -------------    --------------
bfloat16 precision              50% reduction    Negligible
device_map="auto"               Offloads to GPU  Positive (faster)
Shared model singleton          No duplication   None
4-bit quantization (optional)   80% reduction    Minor reduction
Prompt length capping           No impact        Minor reduction at edges
```

---

## 13. RAG Architecture

### 13.1 Overview

Retrieval Augmented Generation (RAG) is the core mechanism that enables the system to generate accurate, grounded outputs from uploaded papers. Rather than relying on the model's parametric knowledge (which may be incorrect, outdated, or hallucinated), the system retrieves the most relevant excerpts from the actual paper and provides them directly in the prompt context. RAG is applied in the Summary Agent, Chat Agent, Comparison Agent, Research Gap Service, and Literature Review Service.

### 13.2 PDF Ingestion Pipeline

```
User Uploads PDF via /api/upload
  |
  v
FastAPI receives file (multipart/form-data)
  |
  v
Validate: file is PDF, size within limit
  |
  v
Save to /backend/uploads/<session_id>/<uuid>_<filename>.pdf
  |
  v
PyMuPDF (fitz) opens PDF
  |
  v
Extract text page by page
  |
  v
Clean and normalize extracted text:
  - Remove repeated headers and footers
  - Normalize whitespace and line breaks
  - Fix hyphenated word splits across lines
  - Strip non-printable characters
  |
  v
Attempt to extract title from PDF metadata
  Fallback: use first non-empty line of page 1
  |
  v
Create Paper record in SQLite
  (title, source="upload", pdf_path, is_processed=False)
  |
  v
Pass cleaned full text to chunking stage
```

### 13.3 Chunking Strategy

```
Full Cleaned Paper Text
  |
  v
RecursiveCharacterTextSplitter (LangChain)
  Chunk size:   500 tokens   (~350-400 words)
  Overlap:      50 tokens    (~35-40 words)
  Separators:   ["\n\n", "\n", ". ", " "]
  |
  v
Each chunk is tagged with metadata:
  paper_id:         integer (FK to Paper table)
  page_number:      integer (approximate page)
  chunk_index:      integer (sequential 0, 1, 2, ...)
  source_filename:  string  (original filename)
  session_id:       string  (owning session UUID)
  |
  v
Chunk list passed to embedding stage
```

The 50-token overlap ensures that sentences and concepts at chunk boundaries are not lost — a question whose answer spans two chunk boundaries will still be covered by at least one chunk.

### 13.4 Embedding and Vector Storage

```
Text Chunks (with metadata)
  |
  v
embedding_service: sentence-transformers/all-MiniLM-L6-v2
  Output: 384-dimensional dense float vector per chunk
  |
  v
ChromaDB collection
  Collection name: "papers_{session_id}" or shared "papers"
  |
  v
Each stored document:
  id:        "{paper_id}_{chunk_index}"
  embedding: [384 floats]
  document:  chunk text string
  metadata:  paper_id, page_number, chunk_index, session_id
  |
  v
ChromaDB persisted to disk at:
  backend/vectorstore/chroma_db/
```

### 13.5 Retrieval Flow

```
Query or Task (from agent)
  |
  v
Embed query text with all-MiniLM-L6-v2
  (same model as ingestion — ensures vector space consistency)
  |
  v
ChromaDB similarity search
  Metric:    cosine similarity
  Filter:    WHERE paper_id IN [paper_ids] (if scoped)
  Retrieve:  top-k chunks (k=5 default, k=3 if prompt budget tight)
  |
  v
Ranked chunk list (score, text, metadata)
  |
  v
Assemble context string from chunks
  Format: "--- Source: {title}, Page {page} ---\n{chunk_text}\n\n"
  |
  v
Context string injected into agent prompt
```

### 13.6 RAG Prompt Template

```
[SYSTEM]
You are an academic research assistant. You answer questions and
generate outputs based ONLY on the provided context. If the context
does not contain the answer, say "Not found in the provided document."

[CONTEXT]
--- Source: {paper_title}, Page {page_num} ---
{chunk_text_1}

--- Source: {paper_title}, Page {page_num} ---
{chunk_text_2}

...up to 5 chunks...

[QUESTION / INSTRUCTION]
{agent-specific task instruction}

[RESPONSE]
```

### 13.7 RAG Quality Considerations

- Chunk overlap prevents context loss at boundaries.
- Metadata filtering scopes retrieval to the specific paper(s) in question.
- Temperature set to 0.3 for all RAG tasks to reduce hallucination.
- The system prompt explicitly prohibits the model from generating content not found in the context.
- Source chunk metadata (paper title, page number, chunk index) is returned to the frontend alongside the answer, enabling users to verify claims against the original document.
- For Comparison and Review tasks, summaries stored in SQLite (rather than raw chunks) are used as context to avoid exceeding the model's effective context budget.

---

## 14. Technology Stack Justification

### 14.1 Frontend Technologies

**React + Vite**
React is the industry-standard component-based JavaScript library. Vite provides near-instant hot module replacement and fast cold start during development, which is critical for a 7-day project. This pairing minimizes frontend build tooling overhead.

**Tailwind CSS**
Utility-first CSS eliminates the need to write custom stylesheets or maintain separate CSS files. All styling is applied inline via semantic class names, significantly reducing context-switching during development and enabling rapid UI assembly.

**React Query**
Manages server state, request caching, loading states, error boundaries, and background refetching out of the box. Eliminates the need for manual `useEffect` + `useState` patterns for API calls, which is a significant boilerplate reduction for two developers under time pressure.

**Axios**
A widely used HTTP client with cleaner error handling, interceptor support, and better ergonomics than the native Fetch API.

### 14.2 Backend Technologies

**FastAPI**
FastAPI provides automatic OpenAPI documentation generation, native Pydantic integration for schema validation, async request handling, and excellent performance. It is the most productive Python API framework for AI projects due to its type annotation system and native support for async model inference integration.

### 14.3 AI Orchestration

**LangGraph**
LangGraph provides a graph-based state machine for orchestrating multi-component AI workflows. It enables explicit state management, conditional routing between agents and services, and a clean separation between orchestration logic and component logic. It is the correct tool for a coordinator-agent pattern with multiple possible execution paths.

**LangChain**
Provides reusable building blocks including the `RecursiveCharacterTextSplitter` for chunking, prompt template utilities, and document loader abstractions. Reduces the amount of infrastructure code that must be written from scratch.

### 14.4 Local AI

**Qwen/Qwen2.5-1.5B-Instruct (Hugging Face Transformers)**
Selected for hardware accessibility (3.5 GB in bfloat16), Apache 2.0 license, strong instruction following for its size, and native compatibility with the Hugging Face Transformers ecosystem. The 1.5B size is appropriate for the project's target hardware (student laptops). See Section 11 for detailed justification.

**sentence-transformers/all-MiniLM-L6-v2**
A fast, lightweight, high-quality embedding model producing 384-dimensional vectors. It is specifically designed for semantic similarity tasks and performs well on domain-general text including academic content. Its small size (~80 MB) means it loads quickly and has negligible memory overhead compared to the LLM.

### 14.5 Data Storage

**ChromaDB**
A local, embedded vector database that requires no external server. It integrates natively with LangChain, supports metadata filtering essential for scoping searches to individual papers, and persists to disk automatically. The simplest viable vector store for a local-only project.

**SQLite via SQLAlchemy**
SQLite requires no database server, is embedded in Python's standard library, and is file-based. SQLAlchemy provides a clean ORM layer for model definitions and type-safe queries. For a 2-developer, 1-week project, this combination requires no infrastructure setup and has zero operational overhead.

### 14.6 PDF Processing

**PyMuPDF (fitz)**
The fastest and most reliable open-source PDF text extraction library. Handles multi-column academic paper layouts, preserves page boundaries, extracts document metadata, and runs without external dependencies. Superior to `pdfplumber` and `pypdf` for academic paper content quality.

### 14.7 Validation

**Pydantic**
FastAPI uses Pydantic natively. All API request and response shapes are defined as Pydantic models, providing automatic validation, serialization, and clear error messages for invalid inputs.

### 14.8 Package Management

**UV**
UV is a modern Python package manager written in Rust that replaces pip and pip-tools. It provides 10–100x faster dependency resolution than pip, deterministic installs via a lockfile (`uv.lock`), and integrated virtual environment management. For this project, UV is especially valuable because the ML dependency tree (PyTorch, Transformers, accelerate, sentence-transformers) is large and resolves slowly with pip. UV's lockfile at the project root ensures both developers have identical environments.

---

## 15. Project Folder Structure

`pyproject.toml` and `uv.lock` are located at the project root, not inside the backend directory. This is the correct UV project convention and ensures the lock file governs the entire project's Python environment.

```
ieee-research-assistant/              (project root)
|
+-- pyproject.toml                    # UV project config + all Python dependencies
+-- uv.lock                           # UV lockfile — deterministic installs
+-- README.md                         # Project overview and quick-start guide
|
+-- frontend/                         # React + Vite frontend application
|   +-- public/                       # Static assets (favicon, etc.)
|   +-- src/
|   |   +-- components/
|   |   |   +-- Layout.jsx
|   |   |   +-- SearchPanel.jsx
|   |   |   +-- UploadPanel.jsx
|   |   |   +-- SummaryView.jsx
|   |   |   +-- ComparisonView.jsx
|   |   |   +-- ChatInterface.jsx
|   |   |   +-- CitationList.jsx
|   |   |   +-- ReviewPanel.jsx
|   |   |   +-- GapPanel.jsx
|   |   |   +-- Spinner.jsx
|   |   |   +-- ErrorAlert.jsx
|   |   +-- pages/
|   |   |   +-- Home.jsx
|   |   |   +-- Search.jsx
|   |   |   +-- Upload.jsx
|   |   |   +-- Review.jsx
|   |   |   +-- Chat.jsx
|   |   +-- hooks/
|   |   |   +-- useSearch.js
|   |   |   +-- useSummarize.js
|   |   |   +-- useCompare.js
|   |   |   +-- useChat.js
|   |   |   +-- useReview.js
|   |   +-- api/
|   |   |   +-- client.js             # Axios instance config
|   |   |   +-- endpoints.js          # API URL constants
|   |   +-- App.jsx
|   |   +-- main.jsx
|   |   +-- index.css
|   +-- index.html
|   +-- vite.config.js
|   +-- tailwind.config.js
|   +-- package.json
|
+-- backend/                          # FastAPI backend application
|   +-- main.py                       # App entry point; registers routers; startup events
|   +-- config.py                     # Model IDs, DB path, upload path, constants
|   |
|   +-- routers/
|   |   +-- search.py                 # POST /api/search
|   |   +-- upload.py                 # POST /api/upload
|   |   +-- agents.py                 # POST /api/agent/* (summarize, compare, cite, gaps, review)
|   |   +-- chat.py                   # POST /api/chat
|   |   +-- report.py                 # GET /api/report/{session_id}
|   |
|   +-- agents/
|   |   +-- coordinator.py            # LangGraph graph definition + conditional routing
|   |   +-- state.py                  # ResearchState TypedDict
|   |   +-- search_agent.py           # Search Agent: CrossRef + SQLite storage
|   |   +-- summary_agent.py          # Summary Agent: ChromaDB retrieval + LLM
|   |   +-- comparison_agent.py       # Comparison Agent: summary retrieval + LLM
|   |   +-- chat_agent.py             # Chat Agent: ChromaDB retrieval + LLM
|   |
|   +-- services/
|   |   +-- llm_service.py            # Qwen2.5-1.5B singleton: load + generate()
|   |   +-- embedding_service.py      # all-MiniLM-L6-v2 singleton: load + embed()
|   |   +-- pdf_service.py            # PyMuPDF extraction + LangChain chunking
|   |   +-- search_service.py         # CrossRef API client + mock fallback
|   |   +-- citation_service.py       # Deterministic IEEE citation formatter
|   |   +-- gap_service.py            # Research gap synthesis via LLM
|   |   +-- review_service.py         # Literature review generation via LLM
|   |
|   +-- database/
|   |   +-- models.py                 # SQLAlchemy ORM table models
|   |   +-- session.py                # Database session factory (get_db)
|   |   +-- init_db.py               # Create all tables on startup
|   |   +-- research_assistant.db    # SQLite database file (auto-created)
|   |
|   +-- vectorstore/
|   |   +-- chroma_client.py          # ChromaDB client init, add_documents, query
|   |   +-- chroma_db/               # ChromaDB on-disk persistence directory
|   |
|   +-- schemas/
|   |   +-- paper.py
|   |   +-- summary.py
|   |   +-- comparison.py
|   |   +-- citation.py
|   |   +-- chat.py
|   |   +-- review.py
|   |
|   +-- uploads/                      # Uploaded PDF storage (auto-created)
|       +-- <session_uuid>/
|           +-- <uuid>_paper.pdf
|
+-- docs/                             # Project documentation
    +-- architecture.md               # This document
    +-- api_reference.md              # Full API endpoint reference
    +-- setup_guide.md               # UV setup, model download, run instructions
    +-- prompts/                      # Agent system prompt templates (documented)
        +-- summary_prompt.md
        +-- comparison_prompt.md
        +-- gap_prompt.md
        +-- review_prompt.md
```

### Folder Explanation Notes

`pyproject.toml` / `uv.lock` at root — UV project files govern the entire Python environment from the project root. Both developers use `uv sync` from the root to install all dependencies identically.

`backend/agents/` — Contains only the four Core Agents plus the coordinator and state definition. Generation Services are separate from agents by design, reflecting their different execution model (deterministic or simple LLM calls without RAG retrieval).

`backend/services/` — Contains both infrastructure services (llm, embedding, pdf, search) and the Generation Services (citation, gap, review). Services are reusable across agents and can be called directly by the coordinator for service-type intents.

`backend/vectorstore/chroma_db/` — Auto-created by ChromaDB on first write. This directory should be excluded from version control (add to `.gitignore`).

`backend/uploads/` — Session-scoped subdirectories prevent filename collisions across concurrent sessions.

---

## 16. Database Design

All relational data is stored in SQLite via SQLAlchemy ORM. The database file is auto-created at `backend/database/research_assistant.db` on startup via `init_db.py`.

### 16.1 Session Table

| Field | Type | Description |
|---|---|---|
| id | INTEGER (PK, autoincrement) | Unique session identifier |
| session_uuid | VARCHAR(36) | UUID string for frontend session tracking |
| created_at | DATETIME | Timestamp of session creation |
| updated_at | DATETIME | Timestamp of last activity in session |
| name | VARCHAR(255) | Optional user-defined session label |

**Purpose:** Groups all user activity (papers, summaries, chats, reviews) into logical work sessions. Each browser session is assigned a UUID and maps to one Session record.

---

### 16.2 Paper Table

| Field | Type | Description |
|---|---|---|
| id | INTEGER (PK, autoincrement) | Unique paper identifier |
| session_id | INTEGER (FK → Session.id) | Owning session |
| title | TEXT | Paper title |
| authors | TEXT | Comma-separated author names |
| year | INTEGER | Publication year |
| journal | VARCHAR(512) | Journal or conference name |
| volume | VARCHAR(50) | Journal volume number |
| issue | VARCHAR(50) | Journal issue number |
| pages | VARCHAR(50) | Page range (e.g., "123–145") |
| doi | VARCHAR(255) | Digital Object Identifier |
| abstract | TEXT | Paper abstract |
| source | VARCHAR(50) | "upload" or "search" |
| pdf_path | VARCHAR(512) | Relative path to PDF file (nullable for search-only records) |
| chroma_collection_id | VARCHAR(255) | ChromaDB collection identifier for this paper's chunks |
| is_processed | BOOLEAN | True once PDF has been chunked and embedded in ChromaDB |
| created_at | DATETIME | Record creation timestamp |

**Purpose:** Central registry of all papers encountered in a session. Referenced by all other tables. The `is_processed` flag gates access to RAG-based features.

---

### 16.3 Summary Table

| Field | Type | Description |
|---|---|---|
| id | INTEGER (PK, autoincrement) | Unique summary identifier |
| paper_id | INTEGER (FK → Paper.id) | Associated paper (UNIQUE constraint) |
| objective | TEXT | Extracted research objective |
| methodology | TEXT | Described research methodology |
| datasets | TEXT | Datasets or benchmarks mentioned |
| findings | TEXT | Key findings and results |
| limitations | TEXT | Stated limitations of the work |
| contributions | TEXT | Claimed contributions |
| raw_summary | TEXT | Full LLM-generated text before parsing |
| created_at | DATETIME | Generation timestamp |

**Purpose:** Stores structured summaries generated by the Summary Agent. One summary per paper. Summaries are reused by the Comparison Agent, Gap Service, and Review Service to avoid repeated LLM calls.

---

### 16.4 Comparison Table

| Field | Type | Description |
|---|---|---|
| id | INTEGER (PK, autoincrement) | Unique comparison identifier |
| session_id | INTEGER (FK → Session.id) | Owning session |
| paper_ids | TEXT | JSON array string of compared paper IDs |
| comparison_text | TEXT | Full LLM-generated comparison report |
| dimensions | TEXT | JSON array of comparison dimensions used |
| created_at | DATETIME | Generation timestamp |

**Purpose:** Stores multi-paper comparison reports generated by the Comparison Agent. One record per comparison request (a new comparison of the same papers generates a new record).

---

### 16.5 Citation Table

| Field | Type | Description |
|---|---|---|
| id | INTEGER (PK, autoincrement) | Unique citation identifier |
| paper_id | INTEGER (FK → Paper.id) | Associated paper |
| citation_type | VARCHAR(50) | "journal" or "conference" |
| citation_text | TEXT | IEEE-formatted citation string |
| created_at | DATETIME | Generation timestamp |

**Purpose:** Stores deterministically generated IEEE citations. No LLM is involved in citation generation — all content comes from structured metadata in the Paper table.

---

### 16.6 LiteratureReview Table

| Field | Type | Description |
|---|---|---|
| id | INTEGER (PK, autoincrement) | Unique review identifier |
| session_id | INTEGER (FK → Session.id) | Owning session |
| paper_ids | TEXT | JSON array string of included paper IDs |
| review_type | VARCHAR(50) | "full_review" or "gap_analysis" |
| content | TEXT | Full generated text (review or gap analysis) |
| topic_context | TEXT | Optional user-provided topic description |
| created_at | DATETIME | Generation timestamp |

**Purpose:** Stores both literature reviews and research gap analyses, differentiated by `review_type`. Generated by the Literature Review Service and Research Gap Service respectively.

---

### 16.7 ChatHistory Table

| Field | Type | Description |
|---|---|---|
| id | INTEGER (PK, autoincrement) | Unique message identifier |
| session_id | INTEGER (FK → Session.id) | Owning session |
| paper_ids | TEXT | JSON array of paper IDs in scope for this exchange |
| role | VARCHAR(10) | "user" or "assistant" |
| content | TEXT | Full message text |
| source_chunks | TEXT | JSON array of source chunk references (assistant turns only) |
| created_at | DATETIME | Message timestamp |

**Purpose:** Stores the full conversational history for the Chat Agent. Records are ordered by `created_at` for chronological rendering. The `source_chunks` field enables the frontend to display source references for each assistant response.

---

## 17. API Design

All endpoints are prefixed with `/api`. FastAPI automatically generates interactive OpenAPI documentation at `/docs` (Swagger UI) and `/redoc` (ReDoc).

### 17.1 Search Papers

**Endpoint:** `POST /api/search`  
**Purpose:** Trigger the Search Agent to query CrossRef for papers by keyword and store results.

**Request:**
```
{
  "query":       string,   -- Search keywords (required)
  "session_id":  string,   -- Session UUID (required)
  "max_results": integer,  -- Default: 10
  "year_from":   integer,  -- Optional year filter
  "year_to":     integer   -- Optional year filter
}
```

**Response:**
```
{
  "papers": [
    {
      "id":       integer,
      "title":    string,
      "authors":  string,
      "year":     integer,
      "journal":  string,
      "doi":      string,
      "abstract": string,
      "source":   "search"
    }
  ],
  "total": integer
}
```

---

### 17.2 Upload PDF

**Endpoint:** `POST /api/upload`  
**Purpose:** Upload a PDF file, extract text, chunk it, embed it, and store in ChromaDB.

**Request:** `multipart/form-data`
```
file:        <PDF binary>
session_id:  string
```

**Response:**
```
{
  "paper_id":      integer,
  "title":         string,
  "pages":         integer,
  "chunks_stored": integer,
  "status":        "processed"
}
```

---

### 17.3 Summarize Paper

**Endpoint:** `POST /api/agent/summarize`  
**Purpose:** Generate a structured RAG-based summary for an uploaded paper.

**Request:**
```
{
  "paper_id":   integer,
  "session_id": string
}
```

**Response:**
```
{
  "summary_id":    integer,
  "paper_id":      integer,
  "objective":     string,
  "methodology":   string,
  "datasets":      string,
  "findings":      string,
  "limitations":   string,
  "contributions": string
}
```

---

### 17.4 Compare Papers

**Endpoint:** `POST /api/agent/compare`  
**Purpose:** Generate a structured multi-paper comparison report.

**Request:**
```
{
  "paper_ids":  [integer, integer, ...],  -- Minimum 2
  "session_id": string,
  "dimensions": [string, ...]             -- Optional: ["methodology", "findings"]
}
```

**Response:**
```
{
  "comparison_id":   integer,
  "paper_ids":       [integer],
  "comparison_text": string,
  "dimensions":      [string]
}
```

---

### 17.5 Generate Citation

**Endpoint:** `POST /api/agent/cite`  
**Purpose:** Generate a deterministic IEEE-formatted citation from stored paper metadata.

**Request:**
```
{
  "paper_id":      integer,
  "citation_type": "journal" | "conference",
  "session_id":    string
}
```

**Response:**
```
{
  "citation_id":   integer,
  "paper_id":      integer,
  "citation_type": string,
  "citation_text": string
}
```

---

### 17.6 Generate Literature Review

**Endpoint:** `POST /api/agent/review`  
**Purpose:** Generate a structured academic literature review from a set of papers.

**Request:**
```
{
  "paper_ids":     [integer, ...],
  "session_id":    string,
  "topic_context": string       -- Optional: research area description
}
```

**Response:**
```
{
  "review_id":   integer,
  "paper_ids":   [integer],
  "content":     string,
  "review_type": "full_review"
}
```

---

### 17.7 Generate Gap Analysis

**Endpoint:** `POST /api/agent/gaps`  
**Purpose:** Identify research gaps from a set of paper summaries.

**Request:**
```
{
  "paper_ids":      [integer, ...],
  "session_id":     string,
  "domain_context": string   -- Optional: domain area context
}
```

**Response:**
```
{
  "gap_id":      integer,
  "paper_ids":   [integer],
  "content":     string,
  "review_type": "gap_analysis"
}
```

---

### 17.8 Chat with Papers

**Endpoint:** `POST /api/chat`  
**Purpose:** Submit a question; receive an RAG-grounded answer from the Chat Agent.

**Request:**
```
{
  "question":   string,
  "session_id": string,
  "paper_ids":  [integer, ...]   -- Optional: scope to specific papers
}
```

**Response:**
```
{
  "answer": string,
  "source_chunks": [
    {
      "paper_id":    integer,
      "paper_title": string,
      "page_number": integer,
      "chunk_index": integer,
      "excerpt":     string
    }
  ],
  "history_id": integer
}
```

---

### 17.9 Get Session Report

**Endpoint:** `GET /api/report/{session_id}`  
**Purpose:** Retrieve all generated content for a session in a single response.

**Response:**
```
{
  "session_id":    string,
  "papers":        [...],
  "summaries":     [...],
  "comparisons":   [...],
  "citations":     [...],
  "reviews":       [...],
  "chat_history":  [...]
}
```

---

## 18. LangGraph Design

### 18.1 State Object (ResearchState)

The LangGraph state is a `TypedDict` that is passed through and updated by each node in the graph.

```
ResearchState:
  session_id:           string        -- Owning session UUID
  intent:               string        -- Set by coordinator (search/summarize/etc.)
  paper_ids:            List[int]     -- Target paper IDs for this request
  query:                string        -- Search query (Search Agent)
  question:             string        -- User question (Chat Agent)
  domain_context:       string        -- Optional context (Gap/Review services)
  citation_type:        string        -- "journal" or "conference"
  retrieved_chunks:     List[dict]    -- ChromaDB results (set by agents)
  llm_output:           string        -- Raw LLM generation text
  agent_result:         dict          -- Structured output from agent/service
  service_result:       dict          -- Structured output from generation service
  error:                string|None   -- Error message if any step fails
  current_component:    string        -- Active agent or service name
  completed:            bool          -- True after persist_node completes
```

### 18.2 LangGraph Graph Structure

```
START
  |
  v
[coordinator_node]
  Read request, set intent, validate params
  |
  v
[conditional_router_edge]
  |
  +-- intent == "search"     --> [search_node]       --> [persist_node] --> END
  |
  +-- intent == "summarize"  --> [summary_node]      --> [persist_node] --> END
  |
  +-- intent == "compare"    --> [comparison_node]   --> [persist_node] --> END
  |
  +-- intent == "chat"       --> [chat_node]         --> [persist_node] --> END
  |
  +-- intent == "cite"       --> [citation_service_node] -> [persist_node] -> END
  |
  +-- intent == "gaps"       --> [gap_service_node]  --> [persist_node] --> END
  |
  +-- intent == "review"     --> [review_service_node] -> [persist_node] -> END
  |
  +-- intent == "unknown"    --> [error_node]        --> END
```

### 18.3 Node Responsibilities

```
coordinator_node:
  - Read intent from request body
  - Validate required state fields for that intent
  - Set state.intent, state.current_component
  - Pass state to conditional router

[agent nodes] (search, summary, comparison, chat):
  - Perform retrieval (ChromaDB or SQLite)
  - Construct prompt
  - Call llm_service.generate()
  - Parse structured output
  - Write to state.agent_result

[service nodes] (citation, gap, review):
  - Fetch required data from SQLite
  - Apply deterministic formatting or call llm_service.generate()
  - Write to state.service_result

persist_node:
  - Determine which result field to read (agent_result or service_result)
  - Write record to appropriate SQLite table via SQLAlchemy
  - Set state.completed = True

error_node:
  - Log error details
  - Set state.completed = True
  - Return error payload
```

### 18.4 State Transition Example (Chat Agent)

```
Initial state entering coordinator_node:
  session_id     = "abc-123"
  intent         = ""
  question       = "What dataset did the authors use?"
  paper_ids      = [3]
  completed      = False

After coordinator_node:
  intent             = "chat"
  current_component  = "chat_agent"

After chat_node:
  retrieved_chunks   = [{text, page, chunk_index, paper_id}, ...]
  llm_output         = "<raw LLM response string>"
  agent_result       = {
    answer: "The authors used the ImageNet dataset...",
    source_chunks: [{paper_id: 3, page: 4, chunk_index: 12, excerpt: "..."}]
  }

After persist_node:
  completed = True
  (ChatHistory record created in SQLite)

Return:
  state.agent_result serialized as JSON response
```

### 18.5 Error Handling Strategy

```
Each node wrapped in try/except
  |
  v
On exception:
  state.error = error message string
  |
  v
After each node, error_check_edge evaluates state.error
  |
  +-- state.error is None    --> continue to next node
  |
  +-- state.error is not None --> route to error_node immediately
                                    |
                                    v
                                  Log error
                                  Set state.completed = True
                                  Return HTTP 500 with error details
```

---

## 19. Development Plan

### Team Roles

**Developer A:** Backend specialist — FastAPI setup, LangGraph wiring, agent implementation, LLM and embedding services, database layer.

**Developer B:** Frontend and integration specialist — React UI, Axios/React Query integration, PDF upload pipeline, ChromaDB client, end-to-end testing.

---

### Day 1 — Environment Setup and Project Foundation

**Developer A:**
- Initialize UV project at root: `uv init`, create `pyproject.toml` with all backend dependencies
- Configure FastAPI application with health check endpoint
- Set up SQLAlchemy models (`models.py`) and `init_db.py`
- Verify `Qwen/Qwen2.5-1.5B-Instruct` loads correctly in bfloat16 via Hugging Face Transformers
- Verify `all-MiniLM-L6-v2` embedding model loads and produces correct vector shape
- Implement `llm_service.py` and `embedding_service.py` singletons (load once, shared)

**Developer B:**
- Initialize frontend with Vite + React + Tailwind CSS (`npm create vite@latest`)
- Set up project routing structure and Layout component
- Configure Axios client (`client.js`) and React Query provider
- Set up ChromaDB client (`chroma_client.py`) and verify persistence to disk
- Create base placeholder components for all UI panels

**Deliverable:** Both frontend and backend run locally. Model loads without error. Database initializes. ChromaDB persists a test document.

---

### Day 2 — PDF Pipeline, Embeddings, and Search

**Developer A:**
- Implement `pdf_service.py`: PyMuPDF extraction, text cleaning, LangChain chunking
- Implement `chroma_client.py`: `add_documents()`, `query_documents()`, metadata filtering
- Implement `search_service.py`: CrossRef API query + mock JSON fallback
- Implement `POST /api/search` and `POST /api/upload` endpoints (full pipeline)

**Developer B:**
- Build `UploadPanel.jsx` component: drag-and-drop, file type validation, progress indication
- Build `SearchPanel.jsx` component: query input, results list with paper cards
- Wire `/api/search` to `SearchPanel` via React Query hook (`useSearch.js`)
- Wire `/api/upload` to `UploadPanel` with success/error feedback

**Deliverable:** User can search for papers (CrossRef results displayed). User can upload a PDF; text is extracted, chunked, and stored in ChromaDB. Both are verified end-to-end.

---

### Day 3 — Summary Agent, Citation Service, LangGraph Skeleton

**Developer A:**
- Implement `summary_agent.py`: RAG retrieval + structured prompt + LLM call + output parsing
- Implement `citation_service.py`: deterministic IEEE string formatter (journal + conference)
- Implement `ResearchState` TypedDict in `state.py`
- Implement LangGraph coordinator skeleton in `coordinator.py`
- Wire search, summarize, and cite intents into the graph
- Implement `POST /api/agent/summarize` and `POST /api/agent/cite` endpoints

**Developer B:**
- Build `SummaryView.jsx`: structured field display (objective, methodology, findings, etc.)
- Build `CitationList.jsx`: citation string display with copy-to-clipboard
- Integrate summarize endpoint via `useSummarize.js` hook
- Integrate citation endpoint
- Add loading spinners and error alerts

**Deliverable:** Summary Agent generates structured summaries from uploaded PDFs and displays in UI. IEEE citations generated deterministically from metadata.

---

### Day 4 — Chat Agent and Comparison Agent

**Developer A:**
- Implement `chat_agent.py`: ChromaDB semantic retrieval + RAG chat prompt + LLM response + source references
- Implement `comparison_agent.py`: SQLite summary retrieval + structured comparison prompt + LLM
- Wire chat and comparison intents into LangGraph coordinator
- Implement `POST /api/chat` and `POST /api/agent/compare` endpoints

**Developer B:**
- Build `ChatInterface.jsx`: message thread, user input field, source chunk accordion
- Build `ComparisonView.jsx`: structured per-paper breakdown display
- Wire chat endpoint via React Query mutation
- Wire comparison endpoint
- Test Chat Agent with real academic PDFs and verify source references display correctly

**Deliverable:** Chat Agent answers paper questions with grounded responses and source references. Comparison Agent produces structured multi-paper comparison. All four Core Agents are functional.

---

### Day 5 — Secondary Features: Gap Service and Literature Review Service

**Developer A (if core MVP is stable):**
- Implement `gap_service.py`: retrieve stored summaries + gap synthesis prompt + LLM
- Implement `review_service.py`: retrieve summaries + comparisons + full review prompt + LLM
- Wire gap and review intents into LangGraph
- Implement `POST /api/agent/gaps`, `POST /api/agent/review`, `GET /api/report/{session_id}` endpoints

**Developer B (if core MVP is stable):**
- Build `GapPanel.jsx`: gap analysis display
- Build `ReviewPanel.jsx`: literature review multi-section display
- Implement session report page (aggregated view of all outputs)
- Polish navigation and overall UX flow across all panels

**Note:** If any Core Agent from Day 3–4 is not fully stable, Day 5 is used to fix those issues first. Gap and Review features are deferred to secondary status.

**Deliverable:** Secondary services implemented (if Day 3–4 stable). Gap analysis and full literature review generated and displayed in UI.

---

### Day 6 — Integration Testing and Bug Fixing

**Both Developers — full day reserved for testing:**
- End-to-end workflow test: search → upload → summarize → compare → chat → citations
- Test with at least 3 real academic PDFs from arXiv (text-based, not scanned)
- Verify IEEE citation format correctness against reference examples
- Verify ChromaDB retrieval returns relevant chunks (qualitative check)
- Verify Chat Agent responses are grounded and source references are accurate
- Fix all critical bugs found during testing

**Developer A focus:** Backend edge cases — empty PDFs, very large PDFs (30+ pages), LLM generation timeout, database constraint violations, ChromaDB collection not found.

**Developer B focus:** Frontend edge cases — loading states, error message display, long response text layout, mobile viewport basics.

**Deliverable:** All core features working end-to-end without crashes. Known bugs documented.

---

### Day 7 — Final Polish, Documentation, and Demo Preparation

**Both Developers:**
- Apply final bug fixes from Day 6 testing
- Check inference performance — if CPU inference is too slow, enable 4-bit quantization in `config.py`
- Write `docs/setup_guide.md`: UV installation, model download steps, run instructions
- Write `docs/api_reference.md`: final endpoint documentation
- Prepare demonstration script and sequence
- Final code review and cleanup (remove debug prints, clean up comments)
- Commit all changes to version control; tag demo release

**Deliverable:** Fully functional MVP ready for faculty demonstration and academic submission.

---

## 20. Evaluation Metrics

### 20.1 Search Agent

| Metric | Definition | Target |
|---|---|---|
| Search Accuracy | Proportion of returned papers that are genuinely relevant to the query topic | > 70% judged relevant by developer review |
| Result Completeness | Number of valid results returned per query | Minimum 5 results for non-niche queries |
| Latency | Time from query submission to results displayed in UI | < 10 seconds |

### 20.2 Summary Agent

| Metric | Definition | Target |
|---|---|---|
| Field Completeness | Proportion of required fields (objective, methodology, findings, limitations, contributions) populated in output | 5 out of 5 fields non-empty |
| Factual Consistency | Manual check: does the summary contradict the original paper? | No contradictions in 80% of test cases |
| Human Evaluation | Two developers read the paper and rate the summary on a 1–5 scale for accuracy and coverage | Average rating ≥ 3.5 / 5 |

### 20.3 Comparison Agent

| Metric | Definition | Target |
|---|---|---|
| Coverage | Does the comparison address all specified dimensions? | All requested dimensions present in output |
| Correctness | Manual check: are the stated differences accurate vs the original papers? | No factual errors in 80% of test cases |

### 20.4 Chat Agent

| Metric | Definition | Target |
|---|---|---|
| Groundedness | Proportion of answers that reference content actually present in the retrieved chunks | > 85% of answers grounded in source |
| Faithfulness | Does the answer contradict the source document? | No contradictions in 80% of test cases |
| Source Recall | Are relevant source chunks returned alongside the answer? | Source chunks present for all responses |
| Latency | Time from question submission to answer displayed | < 90 seconds on CPU, < 15 seconds on GPU |

### 20.5 RAG System

| Metric | Definition | Target |
|---|---|---|
| Retrieval Precision | Proportion of retrieved chunks that are relevant to the query | > 60% of top-5 chunks relevant |
| Retrieval Recall | Proportion of relevant chunks in the collection that appear in the top-5 results | Best-effort; no hard target for MVP |
| Chunk Coverage | Does at least one retrieved chunk contain the answer for known-answer test questions? | > 80% of test questions answered by top-5 |

### 20.6 Overall System

| Metric | Definition | Target |
|---|---|---|
| End-to-End Latency (core path) | Search + Upload + Summarize + Cite (no LLM bottleneck) | < 60 seconds total |
| LLM Task Latency (CPU) | Average time for a single LLM generation task | < 60 seconds (acceptable for academic tool) |
| System Stability | Number of unhandled exceptions during demonstration workflow | Zero crashes during demo |
| User Satisfaction | Informal rating from faculty evaluator during demonstration | "Meets expectations" or above |

---

## 21. Testing Strategy

### 21.1 Unit Testing

Each component is tested in isolation before integration.

- `llm_service.py`: verify model loads, `generate()` returns a non-empty string for a test prompt.
- `embedding_service.py`: verify `embed()` returns a vector of length 384.
- `pdf_service.py`: tested with three PDFs — clean single-column, two-column, and a short abstract-only paper.
- `citation_service.py`: tested against 5 reference IEEE journal citations and 5 conference citations, validated character-by-character.
- `chroma_client.py`: test `add_documents()` → `query_documents()` round-trip with metadata filter.
- Pydantic schemas: test valid and invalid request bodies for all 9 endpoints.

**Tool:** `pytest`, managed via UV (`uv run pytest`)

### 21.2 Integration Testing

- `POST /api/upload`: file binary → PDF text extracted → chunks embedded → ChromaDB stored → Paper record created.
- `POST /api/agent/summarize`: paper_id → ChromaDB retrieval → LLM call → structured fields → SQLite Summary record.
- `POST /api/chat`: question + paper_ids → ChromaDB retrieval → LLM answer → source chunks → ChatHistory record.
- Full linear workflow: search → upload → summarize → compare → cite → (if available: gaps → review).

**Tool:** `pytest` with `httpx` async test client for FastAPI endpoints.

### 21.3 RAG Testing

- **Retrieval Relevance:** Prepare 5 test questions with known answers present in specific chunks. Verify the answer chunk appears in the top-5 retrieved results for each.
- **Chunk Boundary Test:** Ask one question whose answer spans two adjacent chunks. Verify overlap prevents the answer from being missed.
- **Metadata Filter Test:** Upload two different papers; ask a question scoped to paper A. Verify no chunks from paper B appear in results.
- **Out-of-Scope Test:** Ask a question whose answer is not in any uploaded paper. Verify the LLM responds that the information is not available in the provided context rather than fabricating an answer.

### 21.4 Service and Agent Testing

- **Summary Agent:** For 2 test papers, compare generated summary fields against the actual abstract and introduction. Verify all 5 fields are populated and contain plausible content.
- **Citation Service:** Validate all generated citation strings against the IEEE citation style guide using 10 known examples.
- **Comparison Agent:** Input 2 papers with known methodological differences. Verify the comparison output identifies those differences explicitly.
- **Chat Agent:** Ask 5 factual questions per test paper whose answers are in the text. Verify the answer is correct and the correct source chunk is returned.

### 21.5 User Acceptance Testing

Executed during Days 6–7 as the demonstration rehearsal:

1. Search "attention mechanism NLP 2023" — verify at least 5 results returned.
2. Upload a known arXiv PDF — verify successful processing message with chunk count.
3. Trigger summarization — verify all 5 structured fields populated with plausible content.
4. Generate IEEE citation — verify format is correct against a known reference example.
5. Ask a specific factual question in chat — verify answer is grounded with source reference.
6. Upload a second paper and run comparison — verify both papers addressed in output.
7. (If secondary features built): Generate gap analysis — verify at least 3 gaps identified.
8. (If secondary features built): Generate literature review — verify introduction, themes, and conclusion sections present.

---

## 22. Risk Analysis

### 22.1 Model Performance Risk

**Risk:** Qwen2.5-1.5B-Instruct produces low-quality, hallucinated, or structurally incorrect outputs for academic summarization and comparison tasks.

**Likelihood:** High (inherent to small models)  
**Impact:** High

**Mitigation:**
- RAG grounding ensures the model has direct source text — it need not rely on parametric knowledge.
- Temperature set to 0.25–0.3 for structured tasks to reduce randomness.
- Structured output prompts use numbered fields with explicit labels; the model is instructed to fill each field independently.
- If a required field is missing from the output, a single re-prompt is attempted before returning a partial result.
- Output quality limitations are documented in the Known Limitations section and disclosed to evaluators.

---

### 22.2 Hardware Constraints Risk

**Risk:** Development machines have insufficient RAM or no GPU, making inference times prohibitively slow for the demonstration.

**Likelihood:** Medium  
**Impact:** High

**Mitigation:**
- Model is loaded in bfloat16 by default (~3.5 GB RAM) rather than float32 (~6 GB RAM).
- `device_map="auto"` automatically uses any available GPU without code changes.
- 4-bit quantization is available as a config flag for machines with only 8 GB RAM.
- `max_new_tokens` is capped per task type to control worst-case latency.
- Pre-generated outputs are prepared as a demonstration fallback if live inference is too slow on the evaluation machine.

---

### 22.3 PDF Extraction Quality Risk

**Risk:** Uploaded PDFs are scanned images or have complex layouts (two-column, equations, tables) that produce garbled extracted text.

**Likelihood:** Medium  
**Impact:** Medium

**Mitigation:**
- The upload endpoint detects near-zero character extraction (fewer than 100 characters for a multi-page PDF) and returns a clear "scanned PDF not supported" error message.
- For MVP testing, only text-based PDFs from arXiv or IEEE Xplore (which are reliably text-based) are used.
- The Known Limitations section documents this restriction explicitly.
- OCR support via Tesseract is marked as a future enhancement.

---

### 22.4 Hallucination Risk

**Risk:** The LLM generates plausible but factually incorrect summaries, comparisons, or gap analyses.

**Likelihood:** High (inherent to all LLMs)  
**Impact:** Medium

**Mitigation:**
- RAG grounding is the primary defense for all content-generating components. The LLM is instructed to use only the provided context.
- Citation generation does not use the LLM at all — it is fully deterministic.
- Source chunk references are returned alongside all RAG outputs, enabling users to verify claims against the original document.
- System prompts for all agents include an explicit instruction: "If the information is not present in the provided context, state that it is not found."

---

### 22.5 Timeline Risk

**Risk:** Implementation complexity or unforeseen bugs cause the team to miss the 7-day deadline.

**Likelihood:** Medium  
**Impact:** High

**Mitigation:**
- The MVP scope is strictly tiered (Core / Secondary / Future). Secondary features are attempted only if the core is stable by end of Day 4.
- Day 6 is fully reserved for integration testing and bug fixing — no new feature development on Day 6.
- All agents share the same `llm_service.py` singleton — no duplicated inference infrastructure.
- Git version control is used from Day 1 with daily commits to prevent code loss.
- If a secondary feature is not complete by Day 6, it is documented as a known limitation rather than causing a delay to the submission.

---

### 22.6 CrossRef API Dependency Risk

**Risk:** The CrossRef API is unavailable, rate-limited, or returns insufficient results during development or the demonstration.

**Likelihood:** Low  
**Impact:** Medium

**Mitigation:**
- API responses for repeated queries are cached in SQLite after the first successful fetch.
- A local JSON file of 20 representative mock paper records is prepared as a fallback data source.
- `search_service.py` automatically switches to mock data if the CrossRef API returns an error or times out.

---

## 23. Known Limitations

### 23.1 Small Model Limitations

`Qwen/Qwen2.5-1.5B-Instruct` is a 1.5 billion parameter model. It has significantly lower reasoning capacity than large cloud models. Outputs for complex synthesis tasks — particularly literature reviews and research gap analysis — may be shallow, miss nuanced themes, or fail to integrate multiple paper perspectives coherently. Users should treat generated outputs as drafts that require human review and editing, not as final academic text.

### 23.2 Scanned PDF Limitations

The system uses PyMuPDF for text extraction, which requires that PDFs contain embedded text layers. PDFs that are scanned images — a common format for older academic papers — cannot be processed in the current MVP. Attempting to upload such a PDF will return an error. OCR support is a documented future enhancement.

### 23.3 Research Gap Analysis Uncertainty

The Research Gap Service uses the LLM to synthesize summaries of multiple papers and identify unexplored directions. The quality of this output is heavily dependent on the number of papers provided (more papers yield better coverage), the quality of the individual summaries, and the model's capacity for synthesis. Identified gaps should be treated as suggestions for human evaluation rather than authoritative research claims.

### 23.4 Literature Review Quality Dependence

The Literature Review Service depends entirely on the quality of the summaries stored in SQLite for each paper. If summaries are incomplete or contain inaccuracies, the generated literature review will reflect those deficiencies. The 1.5B model may also struggle with very long review generation — outputs are capped at 768 tokens, which produces a short review section rather than a full-length academic literature review.

### 23.5 Hardware Dependency for Inference Speed

The system's usability is directly tied to the inference speed of the local machine. On CPU-only hardware with 8 GB RAM, a single summarization task may take 30–60 seconds. This is acceptable for an academic demonstration but would be unsatisfactory in a production research environment. A GPU with 4+ GB VRAM resolves this constraint, reducing inference time to 2–8 seconds.

### 23.6 Single User, Single Session Design

The MVP architecture is designed for a single user working in a single session at a time. There is no authentication system, no concurrent session isolation at the API layer, and no user management. Multi-user support is documented as a future enhancement.

---

## 24. Cost Analysis

This project is designed for zero ongoing operational cost, with all software components under open-source licenses.

### 24.1 Software Cost

| Component | License | Cost |
|---|---|---|
| React, Vite, Tailwind CSS, React Query, Axios | MIT | $0 |
| FastAPI, LangGraph, LangChain | MIT | $0 |
| Qwen/Qwen2.5-1.5B-Instruct | Apache 2.0 | $0 |
| Hugging Face Transformers, Accelerate | Apache 2.0 | $0 |
| sentence-transformers/all-MiniLM-L6-v2 | Apache 2.0 | $0 |
| BitsAndBytes (optional quantization) | MIT | $0 |
| ChromaDB | Apache 2.0 | $0 |
| SQLite | Public Domain | $0 |
| SQLAlchemy | MIT | $0 |
| PyMuPDF (fitz) | AGPL v3 (academic use) | $0 |
| UV Package Manager | MIT | $0 |
| Python 3.11+ | PSF License | $0 |
| **Total Software Cost** | | **$0** |

### 24.2 API Cost

| Service | Notes | Cost |
|---|---|---|
| Qwen2.5-1.5B-Instruct inference | Fully local | $0 |
| all-MiniLM-L6-v2 embeddings | Fully local | $0 |
| ChromaDB vector operations | Fully local | $0 |
| CrossRef API (paper search) | Free public API, rate-limited | $0 |
| **Total API Cost** | | **$0** |

### 24.3 Hardware Cost

| Resource | Notes | Cost |
|---|---|---|
| Development laptops | Existing developer hardware | $0 (already owned) |
| GPU (optional) | Existing GPU if available | $0 (already owned) |
| Cloud compute or hosting | Not required — fully local | $0 |
| **Total Hardware Cost** | | **$0** |

### 24.4 Development Cost

| Resource | Detail |
|---|---|
| Developer A | 7 days × 8 hours = 56 hours (academic project — no salary cost) |
| Developer B | 7 days × 8 hours = 56 hours (academic project — no salary cost) |
| **Total Development Cost** | **$0 (academic context)** |

### 24.5 Total Project Cost

```
Total Project Cost (Software + API + Hardware + Development):  $0
```

The entire system is built and operated with zero financial expenditure, demonstrating that a capable, privacy-preserving, locally-run AI research assistant can be constructed entirely from open-source components.

---

## 25. Future Enhancements

The following enhancements are outside the 1-week MVP scope and are documented here for academic completeness and post-project continuity.

### 25.1 Trend Analysis Agent

A dedicated agent that analyzes publication years, citation frequencies, and keyword co-occurrence across a large set of papers to identify emerging research directions and declining areas within a domain. Would require integration with Semantic Scholar or OpenAlex for citation count data.

### 25.2 Recommendation Agent

Given a user's uploaded papers and a stated research focus, this agent suggests related papers not yet in the session. Would leverage ChromaDB similarity search over a pre-indexed corpus of abstracts combined with metadata-based filtering by year and citation count.

### 25.3 Multi-Document Reasoning

Enhanced Chat Agent capable of reasoning coherently across many papers simultaneously, handling multi-hop questions that require synthesizing information from two or more documents. Would require improved context management and possibly a larger local model.

### 25.4 Figure and Table Understanding

Extend the PDF processing pipeline to extract embedded figures, tables, and their captions using PyMuPDF's image extraction API. Extracted tables would be formatted as structured context; figures would require a vision-capable local model such as a multimodal variant of Qwen.

### 25.5 Semantic Scholar Integration

Integration with the Semantic Scholar API to provide citation counts, open-access PDF links, author h-index data, and related paper recommendations alongside search results.

### 25.6 arXiv Integration

Direct integration with the arXiv API for immediate access to preprint papers, enabling the system to download and process the latest research before journal publication.

### 25.7 Export to DOCX

Allow users to download the generated literature review as a formatted Microsoft Word document (.docx) suitable for direct inclusion in academic manuscripts, using the `python-docx` library.

### 25.8 Export to LaTeX

Allow users to export the generated literature review and IEEE citation list as LaTeX source (`.tex`), ready for inclusion in IEEE conference and journal submissions.

### 25.9 Streaming LLM Responses

Implement server-sent events (SSE) streaming for LLM generation so users see text appear progressively in real time rather than waiting for complete response generation.

### 25.10 Docker Deployment

Package the complete system — frontend, backend, and pre-downloaded model weights — in Docker containers for single-command deployment, ensuring full reproducibility across diverse hardware environments.

### 25.11 OCR Support for Scanned PDFs

Integrate Tesseract OCR (via `pytesseract`) into the PDF ingestion pipeline to support scanned papers that lack embedded text layers.

---

## 26. Conclusion

This document specifies the complete revised architecture for the **IEEE Research Assistant using Multi-Agent AI** — a locally-deployable, open-source system that automates the academic literature review process.

### Summary of Architecture

The system is a React + FastAPI web application with a multi-agent AI core orchestrated by LangGraph. The architecture distinguishes between four **Core Agents** — Search, Summary, Comparison, and Chat — which combine LLM reasoning with ChromaDB RAG retrieval, and three **Generation Services** — Citation, Research Gap, and Literature Review — which produce structured outputs using deterministic logic or lightweight LLM formatting without RAG overhead.

All AI inference is performed locally using `Qwen/Qwen2.5-1.5B-Instruct` via Hugging Face Transformers, with semantic retrieval powered by `sentence-transformers/all-MiniLM-L6-v2` and ChromaDB. Relational data is persisted in SQLite via SQLAlchemy. All Python dependencies are managed using UV, with `pyproject.toml` and `uv.lock` at the project root for deterministic environment reproduction.

Model optimization strategies — bfloat16 precision, device auto-detection, shared singletons, and optional 4-bit quantization — ensure the system is operational on consumer hardware including CPU-only laptops with 8 GB RAM.

### Feasibility Assessment

The revised architecture is more achievable within 7 days than the previous version. Moving from 3B to 1.5B reduces hardware requirements. Separating agents from services clarifies implementation responsibilities. The tiered MVP scope (Core / Secondary / Future) provides a clear priority ordering that prevents scope creep. The development plan reserves Day 6 entirely for integration testing and Day 7 for polish and documentation.

### Expected Outcomes

Upon completion, the system will:

- Demonstrate a complete, working multi-agent AI pipeline applied to a real academic use case.
- Showcase RAG architecture with ChromaDB and local transformer models.
- Produce genuinely useful academic outputs — paper summaries, IEEE citations, comparisons, and optionally gap analyses and literature reviews.
- Operate entirely on local hardware with zero API cost, full offline capability, and complete data privacy.
- Serve as a technically rigorous engineering mini project demonstrating proficiency in full-stack development, LLM integration, vector databases, RAG systems, and multi-agent orchestration using LangGraph.

### Final Statement

The IEEE Research Assistant represents a principled application of local AI to a real, underserved academic need. By combining multi-agent specialization, RAG-grounded generation, model optimization strategies, and a clean full-stack architecture — all on open-source, locally-run software — the system delivers genuine research value within realistic hardware and timeline constraints. The architecture is honest about its limitations, explicit about its scope, and designed to be extended beyond the initial submission.

---

*End of Architecture Specification Document*

**Document Version:** 2.0  
**Previous Version:** 1.0 (June 2026)  
**Revision Summary:** Model changed to Qwen2.5-1.5B-Instruct; agents redesigned as Core Agents + Generation Services; added Local AI Justification, Model Optimization Strategy, Evaluation Metrics, and Known Limitations sections; MVP scope retiered; pyproject.toml moved to project root; development plan rebalanced toward testing.  
**Prepared By:** Development Team  
**Review Status:** Final  
**Next Review:** Post-MVP Completion
