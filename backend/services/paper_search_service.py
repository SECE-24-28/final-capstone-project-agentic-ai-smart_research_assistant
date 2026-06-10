import httpx
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PaperSearchService:
    def __init__(self):
        self.base_url = "https://api.openalex.org/works"
        
    def search_topic(self, topic: str, limit: int = 5) -> List[Dict[str, Any]]:
        params = {
            "search": topic,
            "per-page": limit,
            "sort": "relevance_score:desc",
            "filter": "has_abstract:true"
        }
        # Polite pool identifier
        headers = {"User-Agent": "SmartResearchAssistant/1.0 (mailto:test@example.com)"}
        
        try:
            response = httpx.get(self.base_url, params=params, headers=headers, timeout=15.0)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for work in data.get("results", []):
                # Extract Authors
                authors = []
                for authorship in work.get("authorships", []):
                    author_name = authorship.get("author", {}).get("display_name")
                    if author_name:
                        authors.append(author_name)
                        
                # Reconstruct Abstract from Inverted Index
                abstract = ""
                inverted_index = work.get("abstract_inverted_index")
                if inverted_index:
                    max_pos = max([pos for positions in inverted_index.values() for pos in positions], default=-1)
                    if max_pos >= 0:
                        words = [""] * (max_pos + 1)
                        for word, positions in inverted_index.items():
                            for pos in positions:
                                words[pos] = word
                        abstract = " ".join(words).strip()
                    
                result = {
                    "title": work.get("title", "Unknown Title"),
                    "authors": ", ".join(authors),
                    "year": str(work.get("publication_year", "")),
                    "doi": work.get("doi", ""),
                    "abstract": abstract,
                    "url": work.get("id", ""),
                    "citation_count": work.get("cited_by_count", 0),
                    "source": "OpenAlex"
                }
                results.append(result)
            return results
            
        except Exception as e:
            logger.error(f"Error querying OpenAlex: {e}")
            return []

paper_search_service = PaperSearchService()
