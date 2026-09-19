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
                from google import genai
                import os
                api_key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
                if not api_key:
                    raise EmbeddingError("No GEMINI_API_KEY found")
                self.model = genai.Client(api_key=api_key)
                # use text-embedding-004 for text embeddings
                self.model_name = "text-embedding-004"
            except ImportError:
                raise EmbeddingError("google-genai not installed")
            except Exception as e:
                raise EmbeddingError(f"Failed to initialize google-genai: {str(e)}")

    async def embed_text(self, text: str) -> List[float]:
        self._lazy_load_model()
        import asyncio
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                lambda: self.model.models.embed_content(
                    model=self.model_name, contents=text
                )
            )
            return response.embeddings[0].values
        except Exception as e:
            raise EmbeddingError(f"Embedding failed: {str(e)}")

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        self._lazy_load_model()
        import asyncio
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                lambda: self.model.models.embed_content(
                    model=self.model_name, contents=texts
                )
            )
            return [emb.values for emb in response.embeddings]
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

