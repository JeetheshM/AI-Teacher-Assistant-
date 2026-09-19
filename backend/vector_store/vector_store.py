import numpy as np
from typing import List, Dict, Any, Optional
from backend.models.rag_models import ChunkMetadata

class VectorStoreError(Exception):
    pass

class VectorStore:
    def __init__(self):
        # Maps chunk_id to ChunkMetadata
        self.chunks: Dict[str, ChunkMetadata] = {}
        # Stores embeddings as numpy array
        self.embeddings: List[List[float]] = []
        # Stores chunk_ids corresponding to the embeddings list index
        self.chunk_ids: List[str] = []

    def add_chunks(self, chunks: List[ChunkMetadata], embeddings: List[List[float]]):
        if len(chunks) != len(embeddings):
            raise VectorStoreError("Chunks and embeddings length mismatch")
            
        for chunk, emb in zip(chunks, embeddings):
            # deduplication (simple override)
            if chunk.chunk_id not in self.chunks:
                self.chunks[chunk.chunk_id] = chunk
                self.chunk_ids.append(chunk.chunk_id)
                self.embeddings.append(emb)

    def search(self, query_embedding: List[float], top_k: int = 5, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.embeddings:
            return []
            
        query_vec = np.array(query_embedding)
        
        # Calculate cosine similarities
        corpus_vecs = np.array(self.embeddings)
        
        # Normalize vectors for cosine similarity
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return []
        query_vec = query_vec / query_norm
        
        corpus_norms = np.linalg.norm(corpus_vecs, axis=1, keepdims=True)
        # Avoid division by zero
        corpus_norms[corpus_norms == 0] = 1.0
        corpus_vecs = corpus_vecs / corpus_norms
        
        similarities = np.dot(corpus_vecs, query_vec)
        
        # Filter and rank
        results = []
        for idx, score in enumerate(similarities):
            chunk_id = self.chunk_ids[idx]
            chunk = self.chunks[chunk_id]
            
            if document_id and chunk.document_id != document_id:
                continue
                
            results.append({
                "chunk": chunk,
                "score": float(score)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_k]

