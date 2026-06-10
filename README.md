# IEEE Research Assistant — Multi-Agent AI

> A locally-running, privacy-preserving AI research assistant that automates the literature review pipeline for students and researchers. Zero cloud APIs. Zero cost.

---

## What It Does

Literature reviews are slow, repetitive, and error-prone. This tool automates the entire pipeline:

- **Search** for research papers by keyword (CrossRef API)
- **Upload PDFs** and process them with AI
- **Summarize** papers into structured academic summaries
- **Compare** multiple papers side-by-side
- **Chat** with your uploaded papers using RAG
- **Generate IEEE citations** automatically from paper metadata
- **Identify research gaps** across a set of papers
- **Generate literature reviews** from your collected papers

Everything runs locally on your machine. No OpenAI. No Gemini. No Claude API. No subscriptions.

---

## Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| React + Vite | UI framework and build tool |
| Tailwind CSS | Utility-first styling |
| React Query | Server state and caching |
| Axios | HTTP client |

### Backend
| Technology | Purpose |
|---|---|
| FastAPI | REST API framework |
| LangGraph | Multi-agent orchestration |
| LangChain | RAG utilities and text splitting |
| SQLAlchemy | ORM for SQLite |
| Pydantic | Request/response validation |
| PyMuPDF | PDF text extraction |

### Local AI
| Technology | Purpose |
|---|---|
| Qwen/Qwen2.5-1.5B-Instruct | Local LLM for text generation |
| sentence-transformers/all-MiniLM-L6-v2 | Sentence embeddings |
| ChromaDB | Local vector database |
| Hugging Face Transformers | Model inference |

### Infrastructure
| Technology | Purpose |
|---|---|
| SQLite | Relational data storage |
| UV | Python package manager |

---

## Architecture Overview

The system uses a **Coordinator Agent** (via LangGraph) to route requests to specialized components:

```
User Request
     |
     v
Coordinator Agent (LangGraph)
     |
     +---> Search Agent          (CrossRef API + SQLite)
     +---> Summary Agent         (ChromaDB RAG + Qwen LLM)
     +---> Comparison Agent      (SQLite summaries + Qwen LLM)
     +---> Chat Agent            (ChromaDB RAG + Qwen LLM)
     +---> Citation Service      (deterministic IEEE formatter)
     +---> Research Gap Service  (LLM synthesis)
     +---> Literature Review     (LLM generation)
          Service
```

**Core Agents** use Retrieval Augmented Generation (RAG) — they retrieve relevant chunks from ChromaDB before calling the LLM, grounding all outputs in your actual documents.

**Generation Services** (Citation, Gap, Review) either use deterministic formatting (Citation) or lightweight LLM calls over stored summaries.

---

## Hardware Requirements

| Configuration | RAM | GPU | Inference Speed |
|---|---|---|---|
| Minimum | 8 GB | None (CPU only) | 30–60 sec / task |
| Recommended | 12 GB | Any NVIDIA 4+ GB VRAM | 3–8 sec / task |
| Optimal | 16 GB | NVIDIA 6+ GB VRAM | 2–5 sec / task |

The model loads in `bfloat16` precision (~3.5 GB RAM). Optional 4-bit quantization is available for machines with only 8 GB RAM — enable it in `backend/config.py`.

---

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- [UV](https://docs.astral.sh/uv/) — Python package manager
- Git
- (Optional) NVIDIA GPU with CUDA 11.8+ for faster inference

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/SECE-24-28/final-capstone-project-agentic-ai-smart_research_assistant
cd final-capstone-project-agentic-ai-smart_research_assistant
```

### 2. Install Python Dependencies with UV

UV manages all Python dependencies from the project root.

```bash
# Install UV if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all backend dependencies from the lockfile
uv sync
```

### 3. Download the AI Models

The models are downloaded automatically the first time the backend starts. To pre-download manually:

```bash
uv run python -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
AutoTokenizer.from_pretrained('Qwen/Qwen2.5-1.5B-Instruct')
AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-1.5B-Instruct')
"

uv run python -c "
from sentence_transformers import SentenceTransformer
SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
"
```

> This requires an internet connection and approximately 3.5 GB of disk space. After download, the system runs fully offline.

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

---

## Running the Application

### Start the Backend

```bash
uv run uvicorn backend.main:app --reload --port 8000
```

The backend will:
- Load the Qwen2.5-1.5B-Instruct model into memory (allow 15–30 seconds on first start)
- Load the all-MiniLM-L6-v2 embedding model
- Initialize the SQLite database at `backend/database/research_assistant.db`
- Initialize ChromaDB at `backend/vectorstore/chroma_db/`

API documentation is available at `http://localhost:8000/docs` once running.

### Start the Frontend

Open a second terminal:

```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:5173`.

---

## Quick Start Workflow

1. **Search** — Enter a keyword (e.g., "transformer attention NLP") to find papers. Results are stored in the current session.

2. **Upload** — Upload one or more PDF papers. Each PDF is extracted, chunked, and embedded into ChromaDB automatically.

3. **Summarize** — Click "Summarize" on any uploaded paper to generate a structured summary covering objective, methodology, findings, limitations, and contributions.

4. **Cite** — Click "Generate Citation" on any paper to produce an IEEE-formatted citation string.

5. **Compare** — Select two or more papers and click "Compare" for a structured side-by-side analysis.

6. **Chat** — Open the Chat interface, select a paper (or all papers), and ask any natural-language question. Answers are grounded in the document text with source references.

7. **Gap Analysis** — Select three or more papers and run "Research Gaps" to identify unexplored directions in the field.

8. **Literature Review** — Select all relevant papers and run "Generate Review" to produce a structured academic literature review section.

---

## Configuration

Key settings are in `backend/config.py`:

| Setting | Default | Description |
|---|---|---|
| `LLM_MODEL_ID` | `Qwen/Qwen2.5-1.5B-Instruct` | Hugging Face model ID |
| `EMBEDDING_MODEL_ID` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `USE_4BIT_QUANTIZATION` | `False` | Enable for 8 GB RAM machines |
| `MAX_CHUNK_SIZE` | `500` | Token size per text chunk |
| `CHUNK_OVERLAP` | `50` | Overlap tokens between chunks |
| `TOP_K_CHUNKS` | `5` | Retrieved chunks per RAG query |
| `DB_PATH` | `backend/database/research_assistant.db` | SQLite database path |
| `UPLOAD_DIR` | `backend/uploads/` | PDF storage directory |
| `CHROMA_DIR` | `backend/vectorstore/chroma_db/` | ChromaDB storage path |

---

## Project Structure

```
ieee-research-assistant/
|
+-- pyproject.toml          # UV project config + all Python dependencies
+-- uv.lock                 # UV lockfile (deterministic installs)
+-- README.md               # This file
|
+-- frontend/               # React + Vite application
|   +-- src/
|   |   +-- components/     # Reusable UI components
|   |   +-- pages/          # Route-level page components
|   |   +-- hooks/          # React Query data hooks
|   |   +-- api/            # Axios client config
|   +-- package.json
|
+-- backend/                # FastAPI application
|   +-- main.py             # App entry point
|   +-- config.py           # Configuration constants
|   +-- routers/            # FastAPI route handlers
|   +-- agents/             # LangGraph core agents
|   +-- services/           # Generation services + LLM/embedding singletons
|   +-- database/           # SQLAlchemy models + SQLite
|   +-- vectorstore/        # ChromaDB client + storage
|   +-- schemas/            # Pydantic request/response models
|   +-- uploads/            # Uploaded PDF files
|
+-- docs/
    +-- architecture.md     # Full system architecture document
    +-- api_reference.md    # API endpoint reference
    +-- setup_guide.md      # Detailed setup instructions
```

---

## API Endpoints

All endpoints are prefixed with `/api`. Interactive docs at `http://localhost:8000/docs`.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/search` | Search for papers by keyword |
| POST | `/api/upload` | Upload and process a PDF |
| POST | `/api/agent/summarize` | Generate a structured paper summary |
| POST | `/api/agent/compare` | Compare multiple papers |
| POST | `/api/agent/cite` | Generate an IEEE citation |
| POST | `/api/agent/gaps` | Generate research gap analysis |
| POST | `/api/agent/review` | Generate a literature review |
| POST | `/api/chat` | Ask a question about uploaded papers |
| GET | `/api/report/{session_id}` | Get all outputs for a session |

---

## Why Local AI?

This project uses local models instead of cloud APIs for principled reasons:

- **Zero cost** — No per-token charges, no subscriptions, no surprises.
- **Offline capable** — Works without internet after the initial model download.
- **Data privacy** — Your research papers and questions never leave your machine.
- **No vendor lock-in** — Swap models by changing a single config value.
- **Academic reproducibility** — No dependency on external API availability or versioning.

The tradeoff is inference speed and output quality compared to large cloud models. The RAG architecture compensates by grounding all outputs in your actual documents rather than relying solely on the model's parametric knowledge.

---

## Known Limitations

- **Scanned PDFs are not supported.** Only text-based PDFs (e.g., from arXiv or IEEE Xplore) work with the current pipeline. Scanned image PDFs will return an extraction error.
- **Inference is slow on CPU.** Without a GPU, each LLM task takes 30–60 seconds. This is expected behavior for local 1.5B model inference.
- **Output quality is limited by model size.** The 1.5B model produces good structured outputs for focused tasks but may produce shallow results for complex multi-document synthesis. Treat all generated text as a draft requiring human review.
- **Single-user design.** The MVP has no authentication or concurrent session isolation. It is designed for individual local use.

---

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run a specific test file
uv run pytest backend/tests/test_citation_service.py
```

---

## Contributing

This is an engineering mini project. If you wish to extend it:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Install dependencies: `uv sync`
4. Make your changes and add tests.
5. Run the test suite: `uv run pytest`
6. Open a pull request with a clear description of your changes.

See `docs/architecture.md` for the full system design before making structural changes.

---

## Documentation

| Document | Location | Description |
|---|---|---|
| Architecture Spec | `docs/architecture.md` | Complete system design (26 sections) |
| API Reference | `docs/api_reference.md` | All endpoint request/response schemas |
| Setup Guide | `docs/setup_guide.md` | Detailed installation walkthrough |

---

## License

This project is built for academic use. All dependencies are open-source:

- Qwen/Qwen2.5-1.5B-Instruct — Apache 2.0
- Hugging Face Transformers — Apache 2.0
- sentence-transformers — Apache 2.0
- ChromaDB — Apache 2.0
- FastAPI, LangGraph, LangChain — MIT
- React, Vite, Tailwind CSS — MIT
- SQLite — Public Domain
- UV — MIT

---

