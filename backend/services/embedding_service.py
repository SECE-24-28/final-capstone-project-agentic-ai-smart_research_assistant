import logging
from .config import settings

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.model_name = settings.embedding_model_name
        self.model = None

    def load(self):
        if SentenceTransformer is None:
            raise RuntimeError("sentence-transformers is required for EmbeddingService")
        logger.info("Loading embedding model: %s", self.model_name)
        self.model = SentenceTransformer(self.model_name)

    def embed_texts(self, texts):
        if self.model is None:
            self.load()
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

embedding_service = EmbeddingService()
