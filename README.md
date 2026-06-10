# IEEE Research Assistant — Multi-Agent AI

A smart literature review assistant that automates the academic research pipeline using a multi-agent AI architecture. Built as a final year engineering mini project.

---

## What It Does

Researchers and students spend 20–40 hours on a single literature review. This tool cuts that down to under 2 hours by automating every stage of the process:

- **Search** IEEE papers by topic using the IEEE Xplore API
- **Summarize** uploaded PDFs into structured summaries (problem, method, dataset, results, limitations)
- **Compare** 2–5 papers side by side with a generated comparison table and narrative
- **Identify Research Gaps** from cross-paper analysis
- **Generate IEEE Citations** automatically from paper metadata
- **Write a Literature Review Draft** synthesizing all findings
- **Chat with Your Papers** using RAG — ask natural language questions grounded in actual PDF content

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Tailwind CSS, Axios, React Query |
| Backend | FastAPI, Python 3.11, Pydantic, Uvicorn |
| AI / Agents | LangGraph, LangChain, OpenAI GPT-4o-mini |
| Vector DB | ChromaDB (local) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Relational DB | PostgreSQL 15 |
| PDF Processing | PyMuPDF (fitz) |
| ORM | SQLAlchemy + Alembic |
| Containerization | Docker + Docker Compose |

---

## Project Structure

```
ieee-research-assistant/
├── frontend/                  # React application
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # SearchPage, SummarizePage, ComparePage, ReviewPage, ChatPage
│   │   ├── api/               # Axios API client wrappers
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── tailwind.config.js
│
├── backend/
│   ├── api/                   # FastAPI route handlers
│   ├── agents/                # One file per agent + prompts/
│   │   ├── coordinator.py     # LangGraph StateGraph
│   │   ├── search_agent.py
│   │   ├── summarization_agent.py
│   │   ├── comparison_agent.py
│   │   ├── gap_agent.py
│   │   ├── citation_agent.py
│   │   ├── review_agent.py
│   │   ├── chat_agent.py
│   │   └── prompts/
│   ├── services/              # PDF processing, IEEE API client, embeddings
│   ├── database/              # SQLAlchemy models, CRUD, migrations
│   ├── vectorstore/           # ChromaDB client and retriever
│   ├── uploads/               # Uploaded PDFs (gitignored)
│   ├── main.py                # FastAPI entry point
│   ├── config.py              # Environment config
│   └── requirements.txt
│
├── docs/
│   └── architecture.md        # Full architecture document
│
├── docker-compose.yml         # PostgreSQL container
├── .env.example
└── README.md
```

---

## Prerequisites

Make sure the following are installed on your machine before proceeding:

- [Node.js](https://nodejs.org/) v18 or higher
- [Python](https://www.python.org/) 3.11 or higher
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for PostgreSQL)
- [Git](https://git-scm.com/)

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ieee-research-assistant.git
cd ieee-research-assistant
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in the required values:

```env
# LLM Provider — get from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-...

# Gemini fallback — get from https://aistudio.google.com/app/apikey
GEMINI_API_KEY=AI...

# IEEE Xplore API — get from https://developer.ieee.org
IEEE_API_KEY=...

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ieee_research_db

# Set to true to use mock paper data instead of real IEEE API
USE_MOCK=false

# File upload directory
UPLOAD_DIR=./uploads
```

> **Note:** If you don't have an IEEE API key yet, set `USE_MOCK=true` to use the included sample paper dataset during development.

### 3. Start PostgreSQL

```bash
docker-compose up -d
```

This starts a PostgreSQL 15 container on port 5432 with the default credentials. Verify it's running:

```bash
docker ps
```

### 4. Set Up the Backend

```bash
cd backend
python -m venv venv

# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate

pip install -r requirements.txt
```

Run database migrations:

```bash
alembic upgrade head
```

Start the FastAPI server:

```bash
uvicorn main:app --reload --port 8000
```

The backend is now running at `http://localhost:8000`.
API docs are available at `http://localhost:8000/docs`.

### 5. Set Up the Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend is now running at `http://localhost:3000`.

---

## Usage Guide

### Step 1 — Search for Papers

Go to the **Search** tab. Enter your research topic (e.g., `"transformer models for medical image segmentation"`) and click Search. Select the papers you want to work with.

### Step 2 — Upload PDFs

For any selected paper, upload its PDF using the upload button on the paper card. Text is automatically extracted and stored for RAG.

### Step 3 — Summarize

Go to the **Summarize** tab. Click "Summarize All" or summarize individual papers. Each paper gets a structured breakdown: problem, method, dataset, results, limitations, future work.

### Step 4 — Compare

Go to the **Compare** tab. Select 2 or more papers and click Compare. A comparison table and narrative are generated.

### Step 5 — Generate Literature Review

Go to the **Review** tab. Click "Generate Review". The system synthesizes all summaries, comparisons, and gap findings into a 600–1000 word draft. The draft is editable directly in the browser.

### Step 6 — Chat with Your Papers

Go to the **Chat** tab. Ask any question about your uploaded papers in natural language. Answers are grounded in actual PDF content with source references.

---

## API Reference

All endpoints are documented interactively at `http://localhost:8000/docs` when the backend is running.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/search` | Search IEEE papers by topic |
| POST | `/api/upload-pdf` | Upload and extract text from a PDF |
| POST | `/api/summarize` | Generate structured summary for a paper |
| POST | `/api/compare` | Compare 2 or more papers |
| POST | `/api/gap` | Identify research gaps from session papers |
| POST | `/api/cite` | Generate IEEE citation for a paper |
| POST | `/api/review` | Generate literature review draft |
| POST | `/api/chat` | RAG-powered Q&A with uploaded papers |
| GET | `/api/session/{id}/report` | Get full compiled session report |

---

## Multi-Agent Architecture

```
User
 |
 v
Coordinator Agent (LangGraph)
 |
 +---> Search Agent          — IEEE Xplore API queries
 |
 +---> Summarization Agent   — LLM-powered structured summaries
 |
 +---> Comparison Agent      — Cross-paper comparison tables
 |
 +---> Research Gap Agent    — Gap identification from synthesis
 |
 +---> Citation Agent        — IEEE citation formatting
 |
 +---> Literature Review Agent — Full review draft generation
 |
 +---> AI Chat Agent         — RAG over uploaded PDFs
 |
 v
Final Report
```

Each agent has a single focused responsibility. The Coordinator manages state and routes outputs between agents using LangGraph's `StateGraph`.

---

## RAG Pipeline

```
PDF Upload
  → PyMuPDF text extraction
  → RecursiveCharacterTextSplitter (500 tokens, 50 overlap)
  → all-MiniLM-L6-v2 embeddings (local, no API cost)
  → ChromaDB vector storage (per-session collections)

At query time:
  User question → embed → ChromaDB similarity search → top 5 chunks
  → GPT-4o-mini with grounding prompt → answer + source references
```

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

Tests cover:
- Agent output parsing (unit tests with mocked LLM responses)
- PDF text extraction with sample files
- Citation formatting against known inputs
- Database CRUD operations
- RAG retrieval recall (10 known Q&A pairs)

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI API key for LLM calls |
| `GEMINI_API_KEY` | No | Gemini Flash fallback key |
| `IEEE_API_KEY` | No* | IEEE Xplore API key |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `USE_MOCK` | No | `true` to use mock paper data (default: `false`) |
| `UPLOAD_DIR` | No | PDF upload directory (default: `./uploads`) |
| `CHROMA_PERSIST_DIR` | No | ChromaDB storage path (default: `./vectorstore/chroma`) |

*If `USE_MOCK=true`, IEEE API key is not required.

---

## Known Limitations (MVP)

- Scanned PDFs (image-based) are not supported — text extraction requires text-based PDFs.
- The comparison feature supports a maximum of 5 papers at once.
- No user authentication — all sessions are anonymous in the MVP.
- IEEE Xplore API only returns paper metadata, not full text. Full PDFs must be uploaded manually.
- ChromaDB runs locally — not suitable for concurrent multi-user production deployment.

---

## Future Enhancements

- [ ] arXiv and Semantic Scholar integration
- [ ] Trend Analysis Agent (year-over-year methodology shifts)
- [ ] Paper Recommendation Agent (semantic similarity)
- [ ] Multi-modal understanding of paper figures and tables
- [ ] LaTeX export with BibTeX citations
- [ ] Research roadmap generation
- [ ] User accounts and persistent session history
- [ ] Multi-document deep reasoning across 15+ papers

---

## Contributing

This is a final year mini project. External contributions are welcome after the academic submission.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add your feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## Team

Built by a 2-person team as a Final Year Engineering Mini Project at Sri Eshwar College of Engineering (B.E. Computer Science & Engineering, Batch 2024–2028).

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgements

- [IEEE Xplore Developer Portal](https://developer.ieee.org) for the metadata API
- [LangChain](https://langchain.com) and [LangGraph](https://langchain-ai.github.io/langgraph/) for the agent framework
- [ChromaDB](https://www.trychroma.com/) for local vector storage
- [sentence-transformers](https://www.sbert.net/) for free local embeddings
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF text extraction
