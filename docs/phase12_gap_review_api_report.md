# Phase 12: Gap and Literature Review API Endpoints Report

## Objective
Expose the existing `GapAgent` and `LiteratureReviewAgent` intelligence through FastAPI routes, making them production-ready for frontend consumption via structured markdown.

## 1. New API Routes Created
Two new public endpoints were successfully added to the `agent.py` router:
- `POST /agent/gap`
- `POST /agent/review`

Both endpoints are now active and visible in the auto-generated Swagger UI at `http://localhost:8000/docs`.

## 2. Schemas Added
The following Pydantic V2 schemas were added to `backend/schemas.py`:

### Gap Analysis
**`GapAnalysisRequest`**
- `topic`: str
- `paper_ids`: List[int]

**`GapAnalysisResponse`**
- `id`: int
- `paper_ids`: str
- `unexplored_areas`: Optional[str]
- `contradictions`: Optional[str]
- `opportunities`: Optional[str]
- `raw_text`: str

### Literature Review
**`LiteratureReviewRequest`**
- `topic`: str
- `paper_ids`: List[int]

**`LiteratureReviewResponse`**
- `id`: int
- `paper_ids`: str
- `review_text`: str

## 3. Markdown Parsing Implementation
To adhere strictly to the rule of not modifying core business logic or database schemas, a lightweight Markdown parser was implemented directly inside the FastAPI router (`/agent/gap`). 

The parser successfully scans the `GapAgent`'s generated string and maps the content under specific Markdown headings (e.g., `## Unexplored Areas`) to their respective fields in the `GapAnalysisResponse` schema, allowing the React frontend to consume structured data effortlessly while preserving the full output in `raw_text`.

## 4. Testing & Validation
Pytest files were added and executed for both endpoints:
- `tests/test_gap_endpoint.py`
- `tests/test_review_endpoint.py`

**Executed Scenarios (9/9 Passed):**
- Valid request generation
- **Caching behavior verification** (Subsequent requests for identical `topic` and `paper_ids` return cached database results without triggering the LLM)
- Invalid paper IDs handling
- Empty list handling
- Duplicate ID tolerance

## Example Usage

### Gap Analysis

**Request:**
```http
POST /agent/gap
{
  "topic": "Federated Learning Security",
  "paper_ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "id": 4,
  "paper_ids": "1,2,3",
  "unexplored_areas": "There is a notable lack of datasets testing...",
  "contradictions": "While Paper 1 asserts X, Paper 2 demonstrates Y...",
  "opportunities": "Future work should investigate...",
  "raw_text": "## Research Gaps\n..."
}
```

### Literature Review

**Request:**
```http
POST /agent/review
{
  "topic": "Federated Learning Security",
  "paper_ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "id": 2,
  "paper_ids": "1,2,3",
  "review_text": "## Introduction\nFederated Learning has emerged...\n## Related Work\n..."
}
```
