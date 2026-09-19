from typing import List, Dict, Any
from backend.models.rag_models import ChunkMetadata

class TextChunker:
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        # We use simple word-based chunking for MVP
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(self, pages: List[Dict[str, Any]], document_id: str, filename: str) -> List[ChunkMetadata]:
        chunks = []
        for page in pages:
            page_num = page["page_number"]
            text = page["text"]
            
            words = text.split()
            if not words:
                continue
                
            chunk_index = 1
            start = 0
            
            while start < len(words):
                end = min(start + self.chunk_size, len(words))
                chunk_words = words[start:end]
                chunk_text = " ".join(chunk_words)
                
                chunk_id = f"{document_id}_p{page_num}_c{chunk_index}"
                
                chunks.append(ChunkMetadata(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    filename=filename,
                    page_number=page_num,
                    chunk_index=chunk_index,
                    content=chunk_text
                ))
                
                chunk_index += 1
                start += (self.chunk_size - self.chunk_overlap)
                
        return chunks

