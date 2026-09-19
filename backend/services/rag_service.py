import os
from typing import List

from backend.models.rag_models import (
    DocumentIngestionRequest,
    DocumentIngestionResult,
    RetrievalRequest,
    RetrievalResponse,
    CurriculumContextItem
)
from backend.utils.pdf_parser import PDFParser
from backend.utils.text_chunker import TextChunker
from backend.services.embedding_service import EmbeddingService
from backend.vector_store.vector_store import VectorStore, VectorStoreError

class DocumentProcessingError(Exception):
    pass

class UnsupportedDocumentError(Exception):
    pass

class RAGService:
    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStore):
        self.pdf_parser = PDFParser()
        self.text_chunker = TextChunker()
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    async def ingest_document(self, file_path: str, document_id: str, filename: str) -> DocumentIngestionResult:
        if not filename.lower().endswith(".pdf"):
            return DocumentIngestionResult(
                document_id=document_id,
                filename=filename,
                status="failed",
                error="Unsupported file extension. Only .pdf is supported for MVP."
            )
            
        if not os.path.exists(file_path):
            return DocumentIngestionResult(
                document_id=document_id,
                filename=filename,
                status="failed",
                error="File does not exist."
            )

        try:
            # 1. Parse pages
            pages = self.pdf_parser.extract_pages(file_path)
            
            # 2. Chunk text
            chunks = self.text_chunker.chunk_pages(pages, document_id, filename)
            
            if not chunks:
                return DocumentIngestionResult(
                    document_id=document_id,
                    filename=filename,
                    status="failed",
                    error="No valid chunks could be created from the document."
                )

            # 3. Embed chunks
            texts = [c.content for c in chunks]
            embeddings = await self.embedding_service.embed_texts(texts)
            
            # 4. Store vectors
            self.vector_store.add_chunks(chunks, embeddings)
            
            return DocumentIngestionResult(
                document_id=document_id,
                filename=filename,
                status="processed",
                page_count=len(pages),
                chunk_count=len(chunks)
            )
            
        except Exception as e:
            return DocumentIngestionResult(
                document_id=document_id,
                filename=filename,
                status="failed",
                error=str(e)
            )

    def _build_query(self, request: RetrievalRequest) -> str:
        return f"{request.subject} Grade {request.grade} {request.topic}: {request.learning_objective}"

    async def retrieve(self, request: RetrievalRequest) -> RetrievalResponse:
        query_text = self._build_query(request)
        
        try:
            query_embedding = await self.embedding_service.embed_text(query_text)
            results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=request.top_k,
                document_id=request.document_id
            )
            
            context_items = []
            for res in results:
                chunk = res["chunk"]
                context_items.append(CurriculumContextItem(
                    content=chunk.content,
                    source=chunk.filename,
                    page_number=chunk.page_number,
                    chunk_id=chunk.chunk_id,
                    score=res["score"]
                ))
                
            return RetrievalResponse(
                success=True,
                grounded=len(context_items) > 0,
                query=query_text,
                document_id=request.document_id,
                chunks=context_items,
                source_count=len(set(c.page_number for c in context_items))  # count unique pages roughly
            )
        except Exception as e:
            # Log error properly in real app
            return RetrievalResponse(
                success=False,
                grounded=False,
                query=query_text,
                document_id=request.document_id,
                chunks=[]
            )

    async def get_curriculum_context(self, request: RetrievalRequest) -> List[dict]:
        """Returns the shared dictionary schema expected by other modules."""
        response = await self.retrieve(request)
        
        return [
            {
                "content": item.content,
                "source": item.source,
                "page_number": item.page_number,
                "chunk_id": item.chunk_id
            }
            for item in response.chunks
        ]

