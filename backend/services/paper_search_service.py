import httpx
import logging
import numpy as np
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two 1-D numpy vectors."""
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


class PaperSearchService:
    def __init__(self):
        self.base_url = "https://api.openalex.org/works"

    def search_topic(self, topic: str, limit: int = 5) -> List[Dict[str, Any]]:
        logger.info(f"START search_topic: query='{topic}', limit={limit}")
        # Sanitize query to prevent 400 Bad Request from OpenAlex wildcards
        clean_topic = topic.replace("?", "").replace("*", "").replace("!", "")

        # Heuristic: if it's a natural language question, filter stopwords
        lower_topic = clean_topic.lower()
        stopwords = ["how", "do", "i", "can", "you", "find", "some", "research",
                     "papers", "based", "on", "show", "me", "what", "is", "about",
                     "a", "good", "the", "for"]

        if len(clean_topic.split()) > 3 and any(sw in lower_topic.split() for sw in ["how", "can", "find", "show", "what"]):
            words = [w for w in clean_topic.split() if w.lower() not in stopwords]
            if words:
                clean_topic = " ".join(words)

        params = {
            "search": clean_topic,
            "per-page": min(limit * 3, 30),   # fetch 3× more so cosine re-rank has candidates
            "sort": "relevance_score:desc",
            "filter": "has_abstract:true"
        }
        headers = {"User-Agent": "SmartResearchAssistant/1.0 (mailto:test@example.com)"}

        try:
            response = httpx.get(self.base_url, params=params, headers=headers, timeout=15.0)
            response.raise_for_status()
            data = response.json()
            works = data.get("results", [])
            logger.info(f"OpenAlex returned {len(works)} papers_found")

            raw_results = []
            for work in works:
                # Extract authors
                authors = []
                for authorship in work.get("authorships", []):
                    author_name = authorship.get("author", {}).get("display_name")
                    if author_name:
                        authors.append(author_name)

                # Reconstruct abstract from inverted index
                abstract = ""
                inverted_index = work.get("abstract_inverted_index")
                if inverted_index:
                    max_pos = max(
                        [pos for positions in inverted_index.values() for pos in positions],
                        default=-1
                    )
                    if max_pos >= 0:
                        words_arr = [""] * (max_pos + 1)
                        for word, positions in inverted_index.items():
                            for pos in positions:
                                words_arr[pos] = word
                        abstract = " ".join(words_arr).strip()

                raw_results.append({
                    "title": work.get("title", "Unknown Title"),
                    "authors": ", ".join(authors),
                    "year": str(work.get("publication_year", "")),
                    "doi": work.get("doi", "") or "",
                    "abstract": abstract,
                    "url": work.get("id", ""),
                    "citation_count": work.get("cited_by_count", 0),
                    "source": "OpenAlex",
                    "similarity_score": 0.0,
                })

            # ── Cosine Similarity Re-Ranking ─────────────────────────────────
            if raw_results:
                try:
                    from ..services.embedding_service import embedding_service

                    # Build corpus: title + abstract for each paper
                    corpus = [
                        f"{r['title']}. {r['abstract'][:500]}"
                        for r in raw_results
                    ]

                    # Embed query and corpus in one batch call
                    all_texts = [topic] + corpus
                    all_vecs = embedding_service.embed_texts(all_texts)
                    query_vec = all_vecs[0]
                    paper_vecs = all_vecs[1:]

                    # Compute cosine similarity for each paper
                    for i, result in enumerate(raw_results):
                        score = _cosine_similarity(query_vec, paper_vecs[i])
                        result["similarity_score"] = round(score, 4)

                    # Re-rank by cosine similarity descending
                    raw_results.sort(key=lambda r: r["similarity_score"], reverse=True)
                    logger.info(
                        f"Cosine re-rank complete. Top score: {raw_results[0]['similarity_score']:.4f}, "
                        f"Bottom: {raw_results[-1]['similarity_score']:.4f}"
                    )
                except Exception as embed_err:
                    logger.warning(f"Cosine re-ranking failed (fallback to OpenAlex order): {embed_err}")

            # Return top-N after re-ranking
            results = raw_results[:limit]
            logger.info(f"COMPLETE search_topic: {len(results)} papers_returned (cosine re-ranked)")
            return results

        except Exception as e:
            logger.error(f"ERROR querying OpenAlex: {e}", exc_info=True)
            return []


paper_search_service = PaperSearchService()

