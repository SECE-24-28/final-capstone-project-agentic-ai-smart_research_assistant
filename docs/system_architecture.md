# System Architecture – Smart Research Assistant

> **Document Type:** Technical Architecture Reference  
> **Date:** June 2026

---

## 1. High-Level System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                           USER (Browser)                             │
│                     http://localhost:5173                            │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │ HTTP REST + SSE (EventSource)
                                 │
┌────────────────────────────────▼─────────────────────────────────────┐
│                    REACT FRONTEND (Vite / Port 5173)                 │
│                                                                      │
│  ┌──────────────┐  ┌──────────────────┐  ┌────────────────────────┐ │
│  │  AgentContext │  │   PaperContext   │  │    ThemeContext         │ │
│  │  (selector)   │  │  (global papers) │  │  (dark/light mode)     │ │
│  └──────────────┘  └──────────────────┘  └────────────────────────┘ │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                        ChatPage.jsx                             │ │
│  │   ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐   │ │
│  │   │  WelcomeSection│ │  ChatMessage  │  │   ChatInput      │   │ │
│  │   │  (hero + cards)│ │  (markdown)   │  │  (gradient box)  │   │ │
│  │   └──────────────┘  └───────────────┘  └──────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                      API Service Layer                          │ │
│  │  searchApi │ summaryApi │ comparisonApi │ chatApi             │ │
│  │  citationApi │ streamApi (SSE)                                  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │ Axios HTTP (port 8000)
                                 │
┌────────────────────────────────▼─────────────────────────────────────┐
│                   FASTAPI BACKEND (Uvicorn / Port 8000)              │
│                                                                      │
│  ┌──────────┐  ┌───────────────────────────┐  ┌──────────────────┐ │
│  │ /search  │  │         /agent            │  │    /upload       │ │
│  │  router  │  │ (summary, compare, chat,  │  │   (PDF ingestion │ │
│  │          │  │  citation,                │  │    + chunking)   │ │
│  └──────────┘  │  task status, streaming)  │  └──────────────────┘ │
│                └───────────────┬───────────┘                        │
│                                │                                     │
│  ┌─────────────────────────────▼───────────────────────────────────┐ │
│  │                    CoordinatorAgent                             │ │
│  │   Routes: summary → SummaryAgent                                │ │
│  │           comparison → ComparisonAgent                          │ │
│  │           chat → ChatAgent                                      │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                       Service Layer                             │ │
│  │  LLMService │ EmbeddingService │ VectorStore │ PaperSearch      │ │
│  │  PDFService │ CitationService  │ ReportService │ TaskService    │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌──────────────────────┐  ┌──────────────────────────────────────┐ │
│  │    SQLite Database   │  │         ChromaDB Vector Store        │ │
│  │  (structured data)   │  │    (PDF chunk embeddings for RAG)    │ │
│  └──────────────────────┘  └──────────────────────────────────────┘ │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
         ┌───────────────────────┼────────────────────┐
         │                       │                    │
┌────────▼─────────┐  ┌──────────▼────────┐  ┌───────▼────────────┐
│   Qwen2.5-1.5B   │  │  MiniLM-L6-v2     │  │    OpenAlex API    │
│  (Local LLM,     │  │  (Local embedding  │  │  (External paper   │
│   HuggingFace)   │  │   model, 384-dim)  │  │   discovery API)   │
└──────────────────┘  └────────────────────┘  └────────────────────┘
```

---

## 2. Frontend Flow

### Request Lifecycle

```
User types query in ChatInput
          │
          ▼
ChatPage.jsx handleSend()
          │
          ├──► agent === 'search'  ──► searchApi.search(topic)
          │                               │
          │                               ▼
          │                        POST /search/topic
          │                               │
          │                               ▼
          │                        PaperCards render
          │
          ├──► agent === 'summary' ──► summaryApi.summarize(paper_id)
          │                               │
          │                               ▼
          │                        POST /agent/summary
          │                               │
          │                               ▼
          │                        SummaryResponse rendered as Markdown
          │
          ├──► agent === 'chat'    ──► streamApi.streamChat(question, paper_ids)
          │                               │
          │                               ▼
          │                        POST /agent/chat/stream (SSE)
          │                               │
          │                               ▼
          │                        Tokens streamed live to ChatMessage
          │
          └──► agent === 'comparison'
                                   ──► comparisonApi
                                               │
                                               ▼
                                    POST /agent/{type}
                                               │
                                               ▼
                                    TaskProgress polls GET /agent/task/{id}
                                    Progress bar updates until complete
```

### State Architecture

```
ThemeProvider
    └── AgentProvider
            └── PaperProvider
                    └── Router
                            └── MainLayout
                                    ├── Sidebar (agent-themed glow)
                                    └── ChatPage
                                            ├── TopBar (AgentSelector)
                                            ├── Messages (ChatMessage list)
                                            ├── PaperPanel (PaperCard grid)
                                            ├── TaskProgress (polling bar)
                                            └── ChatInput (gradient border)
```

---

## 3. Backend Flow

### Agent Dispatch

```
POST /agent/summary?paper_id=N
    │
    ├── CoordinatorAgent.route_summary(paper_id)
    │       │
    │       ├── Check Summary cache (DB lookup)
    │       │       └── Hit? Return cached → skip LLM
    │       │
    │       └── Miss? → SummaryAgent.summarize(paper)
    │               │
    │               ├── Build RAG query
    │               ├── EmbeddingService.embed_texts([query])
    │               ├── VectorStore.query(embeddings, n_results=5)
    │               ├── Build LLM prompt (context + instructions)
    │               ├── LLMService.generate(prompt, max_tokens=1024)
    │               └── Parse sections → DB.save(Summary)
    │
    └── Return SummaryResponse



### Streaming Flow (SSE)

```
POST /agent/chat/stream
    │
    ├── Build RAG context (VectorStore query)
    ├── LLMService.stream_generate(prompt)
    │       │
    │       └── TextIteratorStreamer (HuggingFace)
    │               └── background Thread generates tokens
    │
    └── StreamingResponse(generator, media_type="text/event-stream")
            │
            └── _sse_token_generator formats: "data: <token>\n\n"
                    │
                    └── Frontend ReadableStream reads tokens
                            └── tokens appended to message state live
```

---

## 4. Database Layer

```
SQLite (research_assistant.db)
│
├── papers           ← Master paper records (from OpenAlex or PDF upload)
├── summaries        ← Cached summaries per paper (prevents re-generation)
├── comparisons      ← Cached comparison results (by paper_id set)
├── citations        ← Generated citations per paper per type
├── chat_history     ← Conversation logs per session
├── final_reports    ← Compiled multi-agent reports
└── agent_tasks      ← Long-running task progress tracking
```

**Caching Strategy:**  
Before calling the LLM, every agent checks if a result already exists in the database for the given `paper_ids`. If found, it is returned immediately (sub-second). This is critical for UX since LLM inference takes 60–180s.

---

## 5. Vector Store (ChromaDB)

```
ChromaDB Collection: "research_chunks"
│
├── Documents: text chunks from uploaded PDFs (max 2000 chars each)
├── Embeddings: 384-dimensional MiniLM vectors
└── Metadata: { "paper_id": N, "chunk_index": N }

Query Flow:
  User question → embed_texts([question]) → 384-dim vector
      └─► VectorStore.query(vector, n_results=5, where={"paper_id": N})
              └─► Returns top-5 most semantically similar chunks
                      └─► Injected as context into LLM prompt
```

---

## 6. LLM Layer

```
LLMService (Qwen2.5-1.5B-Instruct)
│
├── load()           ← Called at startup in background thread
├── generate()       ← Synchronous full-text generation
└── stream_generate() ← Token-by-token via TextIteratorStreamer

Architecture:
  AutoTokenizer + AutoModelForCausalLM
  Device: CPU (float32 precision)
  Max tokens: 384 (chat) – 2048 (literature review)
  Inference time: 60–180 seconds (CPU-bound)
```

---

## 7. Paper Discovery (OpenAlex)

```
OpenAlex API (https://api.openalex.org)
│
├── Endpoint: /works?search={topic}&per_page={limit}
├── Fields: title, authors, year, doi, abstract, primary_location
├── Rate limit: ~10 req/second (no auth required)
└── Response: parsed → PaperResponse → stored in SQLite papers table
```

---

## 8. Task Tracking System

```
Long-Running Task Flow:
    │
    ▼
POST /agent/compare (or /summary)
    │
    ├── TaskService.create_task(task_type)
    │       └── Returns task_id (UUID)
    │
    ├── Background Thread starts:
    │       ├── TaskService.update(task_id, status="running", progress=0, step="Initializing")
    │       ├── ... agent executes ...
    │       ├── TaskService.update(task_id, progress=50, step="Generating analysis")
    │       └── TaskService.update(task_id, status="done", progress=100)
    │
    └── Frontend polls: GET /agent/task/{task_id} every 2 seconds
            │
            └── TaskProgress.jsx renders animated progress bar
```
