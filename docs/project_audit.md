# Project Audit – Smart Research Assistant

> **Document Type:** Technical Audit & Recommendations  
> **Date:** June 2026  
> **Scope:** Frontend + Backend static analysis (no automated tooling)

---

> [!NOTE]
> This document provides **recommendations only**. No code changes have been made. All refactoring should be planned as a separate sprint.

---

## 1. Unused / Stub Components

| Component | File | Status | Recommendation |
|---|---|---|---|
| `LibraryPage` | `frontend/src/pages/LibraryPage.jsx` | Stub (empty content) | Implement paper library with saved papers from PaperContext |
| `ReportsPage` | `frontend/src/pages/ReportsPage.jsx` | Stub | Implement report download (PDF/DOCX export using jsPDF or similar) |
| `EmailPage` | `frontend/src/pages/EmailPage.jsx` | Stub | Low priority; implement email digest of research findings |
| `ReportService` | `backend/services/report_service.py` | Unused | Wire to `ReportsPage` for downloadable research reports |

---

## 2. Dead Routes

| Route | Status | Recommendation |
|---|---|---|
| `/library` | Exists in router, page is a stub | Implement or hide from navigation until ready |
| `/reports` | Exists in router, page is a stub | Implement or hide from navigation until ready |
| `/email` | Exists in router, page is a stub | Implement or hide from navigation until ready |

---

## 3. Duplicate API Services

| Issue | Files | Recommendation |
|---|---|---|
| `chatApi.js` makes `POST /agent/chat` but `streamApi.js` also handles `/agent/chat/stream` | `chatApi.js`, `streamApi.js` | ChatPage should use `streamApi` as the primary path; `chatApi` can remain as fallback only |
| `summary`, `comparison` Apis don't report task progress | `summaryApi.js`, `comparisonApi.js` | Wrap these to also initiate task tracking and return a task_id |

---

## 4. Unused CSS

| Class | File | Status | Recommendation |
|---|---|---|---|
| `.agent-gradient-border-wrapper` | `index.css` | Defined but not found in any JSX | Remove or document usage |
| `.agent-left-border` | `index.css` | Used in Sidebar/NavItem | Keep |
| `.markdown-body pre` dark background | `index.css` | Hardcoded `#1E1E1E` ignores light/dark mode | Replace with `var(--bg-card)` tint |

---

## 5. Unused React Pages

| Page | Usage | Recommendation |
|---|---|---|
| `EmailPage.jsx` | Only contains a heading | Implement email digest or disable nav item |
| `LibraryPage.jsx` | Only contains a heading | Connect to `PaperContext.searchResults` to display saved papers |
| `ReportsPage.jsx` | Only contains a heading | Connect to `report_service` to list and download generated reports |

---

## 6. Unused Backend Services

| Service | File | Status | Recommendation |
|---|---|---|---|
| `ReportService` | `backend/services/report_service.py` | Fully implemented but not exposed via any router endpoint | Add `GET /reports` endpoint and wire to `ReportsPage` |
| `coordinator.py` | Backend only exposes per-agent routing, no unified multi-agent pipeline | Could be extended to support multi-step research workflows |

---

## 7. Broken / Risky Imports

| Issue | File | Risk | Recommendation |
|---|---|---|---|
| `from .models import ... FinalReport` is missing from `database.py` `init_db()` import | `backend/database.py` | `FinalReport` table may not be created if not imported | Add `FinalReport` to the `init_db` import |
| `from .database import SessionLocal` creates a new session per request — no pooling | All routers | High concurrency risk with SQLite | Use `scoped_session` or enforce sequential access |
| `ChatPage.jsx` has ~350 lines mixing UI, state, and API dispatch | `frontend/src/pages/ChatPage.jsx` | Maintainability risk | Extract `useAgentDispatch` hook and `useChatMessages` hook |

---

## 8. Slow Queries / Performance Bottlenecks

| Bottleneck | Location | Impact | Recommendation |
|---|---|---|---|
| **LLM inference is synchronous** | `LLMService.generate()` | Blocks the event loop for 60–180s | Move to a dedicated background thread or separate worker process |

| **ChromaDB loaded lazily** | `vector_store.py` | First RAG query is slow | Collection already loaded at startup — maintain this pattern |
| **OpenAlex fetches metadata fields one-by-one** | `paper_search_service.py` | Multiple key accesses on nested dicts | Add safer `.get()` with defaults to prevent KeyErrors |
| **`db.query(Paper).filter(Paper.id.in_(paper_ids))` in streaming endpoints** | `agent.py` | Fine for small lists; no risk at current scale | Add pagination for future scalability |

---

## 9. Database Bottlenecks

| Issue | Impact | Recommendation |
|---|---|---|
| **SQLite single-writer lock** | Parallel requests block each other | Migrate to PostgreSQL for production, or use WAL mode: `PRAGMA journal_mode=WAL` |
| **No migration system (Alembic)** | Schema changes require manual DB deletion | Add Alembic for schema versioning |
| **`research.db` in project root (legacy)** | Two databases may exist | Remove root `research.db` and standardize to `backend/database/research_assistant.db` |
| **`chat_history` grows unbounded** | Could cause slow queries over time | Add a `session_id` TTL or cleanup job |

---

## 10. Security Observations

| Issue | Risk | Recommendation |
|---|---|---|
| No input sanitization on `topic` search queries | Low (no SQL injection with ORM) | Add max length validation on Pydantic schemas |
| CORS allows all methods from `localhost:5173` only | Acceptable for dev | Tighten to specific methods for production |
| PDF uploads stored without scanning | Medium | Add file type validation beyond extension check |
| No rate limiting on any endpoint | Medium | Add `slowapi` rate limiting for production |

---

## Summary Scorecard

| Category | Status | Priority |
|---|---|---|
| Unused Components | 3 stub pages, 1 unused service | Medium |
| Dead Routes | 3 routes serving stub content | Low |
| Duplicate API Logic | Minor chat/stream overlap | Low |
| CSS Debt | 1 unused class, 1 hardcoded color | Low |
| Import Risks | `init_db` missing models | **High** |
| Slow Queries | LLM sync blocking is primary concern | **High** |
| DB Bottlenecks | SQLite WAL mode, no Alembic | Medium |
| Security | Missing rate limiting, file scanning | Medium |
