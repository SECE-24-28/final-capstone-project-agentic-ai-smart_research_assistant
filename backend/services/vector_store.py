import logging
from pathlib import Path
from ..config import settings, VECTOR_DIR

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
except ImportError:
    chromadb = None
    ChromaSettings = None

logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self):
        self.collection_name = settings.chroma_collection_name
        self.store = None
        self.collection = None
        self.persist_directory = VECTOR_DIR

    def initialize(self):
        if chromadb is None or ChromaSettings is None:
            raise RuntimeError("chromadb is required for VectorStoreService")

        self.persist_directory.mkdir(parents=True, exist_ok=True)
        logger.info("Initializing ChromaDB vector store at %s", self.persist_directory)
        self.store = chromadb.PersistentClient(path=str(self.persist_directory))
        if self.collection_name in [c.name for c in self.store.list_collections()]:
            self.collection = self.store.get_collection(self.collection_name)
        else:
            self.collection = self.store.create_collection(name=self.collection_name)

    def add_documents(self, ids, texts, metadatas, embeddings):
        if self.collection is None:
            self.initialize()
        self.collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)

    def query(self, query_embeddings, n_results=5, where=None):
        if self.collection is None:
            self.initialize()
        return self.collection.query(query_embeddings=query_embeddings, n_results=n_results, where=where)

vector_store = VectorStoreService()
# Trigger uvicorn reload after installing chromadb
