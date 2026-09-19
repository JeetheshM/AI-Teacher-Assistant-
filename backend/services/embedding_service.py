import os
from typing import List

class EmbeddingError(Exception):
    pass

class EmbeddingService:
    def __init__(self):
        self.model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.model = None
        
    def _lazy_load_model(self):
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
            except ImportError:
                raise EmbeddingError("sentence-transformers not installed")
            except Exception as e:
                raise EmbeddingError(f"Failed to load embedding model: {str(e)}")

    async def embed_text(self, text: str) -> List[float]:
        self._lazy_load_model()
        try:
            vector = self.model.encode(text)
            return vector.tolist()
        except Exception as e:
            raise EmbeddingError(f"Embedding failed: {str(e)}")

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        self._lazy_load_model()
        try:
            vectors = self.model.encode(texts)
            return vectors.tolist()
        except Exception as e:
            raise EmbeddingError(f"Batch embedding failed: {str(e)}")

class MockEmbeddingService(EmbeddingService):
    """Deterministic mock embedding for fast tests without real models."""
    async def embed_text(self, text: str) -> List[float]:
        # Simple deterministic vector based on string length and basic hashing
        base_val = len(text) % 10 / 10.0
        return [base_val] * 384  # Assuming standard dim

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [await self.embed_text(t) for t in texts]

