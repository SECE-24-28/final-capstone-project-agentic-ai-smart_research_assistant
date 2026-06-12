# Smart Research Assistant – Project Handover Document

> **Version:** 1.0 | **Date:** June 2026 | **Status:** Production-Ready MVP

---

## 1. Project Overview

The **Smart Research Assistant** is a full-stack, locally-hosted AI application designed to help academic researchers discover, analyze, and synthesize scientific literature. It combines a React frontend with a FastAPI backend powered by a locally-running Qwen2.5 large language model and a ChromaDB vector store.

The system exposes six intelligent agents through a unified chat interface, each specializing in a distinct phase of the academic research workflow.

---

## 2. Problem Statement

Academic researchers face a significant productivity bottleneck when:

- **Discovering** relevant papers across thousands of publications
- **Summarizing** dense academic content under time pressure
- **Comparing** methodologies across multiple papers simultaneously


Existing solutions either require cloud connectivity (privacy risk), are expensive (API costs), or lack a unified multi-agent workflow. This project solves all three issues with a fully local, privacy-first, multi-agent AI assistant.

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────┐
│                     USER BROWSER                     │
│              React + Vite (Port 5173)               │
└────────────────────────┬────────────────────────────┘
                         │ HTTP / SSE
┌────────────────────────▼────────────────────────────┐
│               FASTAPI BACKEND (Port 8000)           │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │  /search    │  │   /agent     │  │  /upload  │  │
│  └─────────────┘  └──────────────┘  └───────────┘  │
│                         │                            │
│  ┌──────────────────────▼─────────────────────────┐ │
│  │          Coordinator Agent                      │ │
│  │  (routes requests to specialized agents)        │ │
│  └──────────────────────┬─────────────────────────┘ │
│     ┌───────┬───────────┼────────────┐               │
│   Search  Summary  Comparison                  │
│             │                                        │
│  ┌──────────▼─────────────────────────────────────┐ │
│  │  Services: LLM (Qwen) │ Embeddings │ ChromaDB  │ │
│  └────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────┐ │
│  │           SQLite Database (research.db)          │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## 4. Agent Architecture

| Agent | Endpoint | Purpose | LLM Used |
|---|---|---|---|
| **Search Agent** | `POST /search/topic` | Discovers papers via OpenAlex API | ❌ (API only) |
| **Summary Agent** | `POST /agent/summary` | Extracts objective, methodology, findings | ✅ Qwen2.5 |
| **Comparison Agent** | `POST /agent/compare` | Compares papers across dimensions | ✅ Qwen2.5 |
| **Chat Agent** | `POST /agent/chat` | RAG-based Q&A over uploaded PDFs | ✅ Qwen2.5 |

| **Citation Agent** | `POST /agent/citation` | Generates APA/MLA/IEEE citations | ❌ (template) |

Each LLM-based agent also has a streaming counterpart (`/stream` suffix) using SSE.

---

## 5. Frontend Architecture

```
frontend/src/
├── App.jsx                   # Root component, provider wrapping, routing
├── main.jsx                  # Vite entry point
├── index.css                 # Global CSS + CSS Custom Properties (agent theming)
├── contexts/
│   ├── AgentContext.jsx      # Active agent state, AGENTS config list
│   ├── PaperContext.jsx      # Selected papers, search results global state
│   └── ThemeContext.jsx      # Dark/Light mode toggle
├── pages/
│   ├── ChatPage.jsx          # Main interface: agent dispatch, streaming
│   ├── LibraryPage.jsx       # Paper library (stub)
│   ├── ReportsPage.jsx       # Reports page (stub)
│   ├── EmailPage.jsx         # Email page (stub)
│   └── SettingsPage.jsx      # Theme/settings
├── components/
│   ├── layout/
│   │   ├── MainLayout.jsx    # Sidebar + content layout, background glows
│   │   ├── Sidebar.jsx       # Navigation, recent chats, user profile
│   │   └── TopBar.jsx        # Agent selector header
│   ├── chat/
│   │   ├── ChatPage.jsx      # Message dispatch logic
│   │   ├── ChatInput.jsx     # Gradient-border textarea + send/stop
│   │   ├── ChatMessage.jsx   # Message renderer (markdown + streaming cursor)
│   │   ├── AIThinking.jsx    # Animated loading indicator
│   │   └── WelcomeSection.jsx # Hero screen with spotlight glow
│   ├── papers/
│   │   ├── PaperCard.jsx     # Paper selection card with gradient selected state
│   │   └── CitationCard.jsx  # Citation display card
│   ├── AgentSelector.jsx     # Dropdown with gradient dot, Framer Motion
│   └── ThemeToggle.jsx       # Sun/moon toggle
└── services/
    ├── api.js                # Base Axios instance (http://localhost:8000)
    ├── searchApi.js          # POST /search/topic
    ├── summaryApi.js         # POST /agent/summary
    ├── comparisonApi.js      # POST /agent/compare
    ├── chatApi.js            # POST /agent/chat
    ├── citationApi.js        # POST /agent/citation

    └── streamApi.js          # ReadableStream SSE consumer
```

**State Management:** React Context API (no Redux/Zustand).  
**Styling:** Tailwind CSS with CSS Custom Properties for agent-specific theming.  
**Animation:** Framer Motion for page transitions, dropdown, and loading states.

---

## 6. Backend Architecture

```
backend/
├── main.py               # FastAPI app, CORS, router registration, startup events
├── config.py             # Path constants, Pydantic settings
├── database.py           # SQLAlchemy engine, SessionLocal, init_db()
├── models.py             # ORM models (Paper, Summary, Comparison, etc.)
├── schemas.py            # Pydantic request/response schemas
├── agents/
│   ├── coordinator.py    # Routes requests to specialized agents
│   ├── search_agent.py   # OpenAlex paper discovery
│   ├── summary_agent.py  # PDF + abstract summarization
│   ├── comparison_agent.py # Cross-paper comparison

│   └── chat_agent.py     # RAG Q&A
├── routers/
│   ├── search.py         # /search/topic endpoint
│   ├── upload.py         # /upload/pdf endpoint
│   └── agent.py          # All /agent/* endpoints incl. streaming
└── services/
    ├── llm_service.py    # Qwen2.5 wrapper (generate + stream_generate)
    ├── embedding_service.py # sentence-transformers MiniLM
    ├── vector_store.py   # ChromaDB collection management
    ├── paper_search_service.py # OpenAlex API client
    ├── pdf_service.py    # PDF text extraction (PyMuPDF)
    ├── citation_service.py # Citation generation
    └── report_service.py # Final report compilation
```

---

## 7. Database Schema

**Database:** SQLite at `backend/database/research_assistant.db`

| Table | Key Columns |
|---|---|
| `papers` | `id, title, authors, abstract, year, doi, journal, source, file_path` |
| `summaries` | `id, paper_id (FK), objective, methodology, findings, limitations, contributions` |
| `comparisons` | `id, name, paper_ids, result` |

| `final_reports` | `id, topic, paper_ids, content` |
| `citations` | `id, paper_id (FK), citation_type, citation_text` |
| `chat_history` | `id, paper_id (FK), session_id, user_question, assistant_answer, source_references` |
| `agent_tasks` | `id, task_type, status, progress, current_step, created_at, completed_at, result` |

---

## 8. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/search/topic` | Search papers by topic (OpenAlex) |
| `POST` | `/upload/pdf` | Upload PDF for RAG indexing |
| `POST` | `/agent/summary?paper_id=N` | Generate paper summary |
| `POST` | `/agent/compare` | Compare multiple papers |
| `POST` | `/agent/chat` | Chat Q&A over papers |
| `POST` | `/agent/citation` | Generate citation |

| `GET` | `/agent/task/{task_id}` | Poll task progress |
| `POST` | `/agent/chat/stream` | Streaming chat (SSE) |
| `POST` | `/agent/summary/stream` | Streaming summary (SSE) |
| `POST` | `/agent/compare/stream` | Streaming comparison (SSE) |


---

## 9. Agent Workflow

```
User Query
    │
    ▼
Search Agent ──────────► OpenAlex API ──────────► PaperCards displayed
    │
    │ (user selects papers)
    ▼
Summary Agent ─────────► Qwen2.5 + RAG ─────────► Structured summary
    │
Comparison Agent ──────► Qwen2.5 ────────────────► Comparison table

    │
Citation Agent ────────► Template engine ──────────► APA/MLA/IEEE
```

---

## 10. Folder Structure

```
final-capstone-project-agentic-ai-smart_research_assistant/
├── backend/              # FastAPI Python backend
├── frontend/             # React + Vite frontend
├── docs/                 # Documentation
├── tests/                # Test suite
├── research.db           # Root-level SQLite (legacy, use backend/database/)
├── pyproject.toml        # Python project config (uv)
└── README.md
```

---

## 11. Technologies Used

| Category | Technology | Version |
|---|---|---|
| **Frontend Framework** | React | 18.x |
| **Build Tool** | Vite | 5.x |
| **Styling** | Tailwind CSS | 3.x |
| **Animation** | Framer Motion | 11.x |
| **HTTP Client** | Axios | 1.x |
| **Markdown Renderer** | react-markdown | 9.x |
| **Backend Framework** | FastAPI | 0.115.x |
| **ORM** | SQLAlchemy | 2.x |
| **Database** | SQLite | (built-in) |
| **LLM** | Qwen2.5-1.5B-Instruct | — |
| **LLM Runtime** | HuggingFace Transformers | 4.x |
| **Embeddings** | sentence-transformers (MiniLM-L6-v2) | — |
| **Vector Store** | ChromaDB | 0.5.x |
| **PDF Processing** | PyMuPDF (fitz) | — |
| **Paper Discovery** | OpenAlex API | (free, no auth) |
| **Package Manager (PY)** | uv | — |
| **Package Manager (JS)** | npm | — |

---

## 12. Current Limitations

| Limitation | Impact | Priority |
|---|---|---|
| LLM is CPU-only (Qwen 1.5B) | 60–180s per generation | High |
| SQLite single-writer | Concurrency issues with parallel requests | Medium |
| No user authentication | Single-user only | Medium |
| ChromaDB in-memory fallback | RAG fails if collection not loaded | Medium |
| Stub pages (Library, Reports, Email) | Incomplete workflows | Low |
| No persistent chat sessions | History resets on page reload | Low |
| OpenAlex rate limiting | Occasional slow search results | Low |

---

## 13. Performance Metrics

| Operation | Observed Time |
|---|---|
| Paper Search (OpenAlex) | 1–3 seconds |
| PDF Upload + Indexing | 2–5 seconds |
| Summary Generation (no cache) | 60–120 seconds |
| Summary Generation (cached) | < 1 second |
| Comparison Generation | 60–120 seconds |

| Chat Response | 30–60 seconds |
| Citation Generation | < 1 second |

---

## 14. Future Roadmap

### Short-Term (1–2 months)
- [ ] GPU support for LLM inference (10–50x speedup)
- [ ] WebSocket or full SSE streaming for all agents
- [ ] Fix SQLAlchemy concurrency with `scoped_session`
- [ ] Implement Library page (saved papers)
- [ ] Implement Reports page (download reports)

### Medium-Term (3–6 months)
- [ ] User authentication (JWT)
- [ ] Multi-user support with isolated sessions
- [ ] Cloud deployment (Docker + Nginx)
- [ ] Larger LLM model (Qwen 7B or Llama 3.1)
- [ ] Agent memory and long-term context

### Long-Term (6–12 months)
- [ ] Citation graph visualization
- [ ] Automated systematic review pipeline
- [ ] Integration with Zotero / Mendeley
- [ ] Email digest of research findings
- [ ] Multi-modal support (images, tables in PDFs)
