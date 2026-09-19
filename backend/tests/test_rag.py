import pytest
import os
import tempfile
import fitz
import asyncio

from backend.models.rag_models import RetrievalRequest
from backend.services.rag_service import RAGService
from backend.services.embedding_service import MockEmbeddingService
from backend.vector_store.vector_store import VectorStore
from backend.utils.pdf_parser import PDFParser
from backend.utils.text_chunker import TextChunker

@pytest.fixture
def rag_service():
    embed_service = MockEmbeddingService()
    vector_store = VectorStore()
    return RAGService(embed_service, vector_store)

def create_mock_pdf(path: str, pages_text: list):
    doc = fitz.open()
    for text in pages_text:
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), text)
    doc.save(path)
    doc.close()

@pytest.mark.asyncio
async def test_pdf_extraction_and_chunking(rag_service):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name
    
    try:
        # TEST 1 & 2: PDF extraction preserves page numbers, ignores empty
        create_mock_pdf(path, ["Page 1 content here", "", "Page 3 content about photosynthesis sunlight carbon dioxide"])
        
        result = await rag_service.ingest_document(path, "doc_123", "test.pdf")
        assert result.status == "processed"
        assert result.page_count == 2  # one empty page ignored
        
        # TEST 3, 5, 6, 7: Chunking produces chunks with valid metadata
        assert result.chunk_count > 0
        
        # TEST 8, 9, 11: Retrieval
        req = RetrievalRequest(
            document_id="doc_123",
            subject="Science",
            topic="Photosynthesis",
            grade=8,
            learning_objective="Understand how plants make food using sunlight"
        )
        
        resp = await rag_service.retrieve(req)
        assert resp.success
        assert resp.grounded
        assert len(resp.chunks) > 0
        assert resp.chunks[0].source == "test.pdf"
        assert resp.chunks[0].chunk_id.startswith("doc_123_p")
        
        # Shared Context format test
        context = await rag_service.get_curriculum_context(req)
        assert len(context) > 0
        assert "content" in context[0]
        assert "source" in context[0]
        assert "page_number" in context[0]
        assert "chunk_id" in context[0]
        
    finally:
        os.remove(path)

@pytest.mark.asyncio
async def test_unsupported_file(rag_service):
    # TEST 12: Unsupported file
    result = await rag_service.ingest_document("test.txt", "doc_123", "test.txt")
    assert result.status == "failed"
    assert "Unsupported file extension" in result.error

@pytest.mark.asyncio
async def test_empty_or_unreadable_pdf(rag_service):
    # TEST 13: Empty / unreadable handled
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name
    try:
        create_mock_pdf(path, [" "])
        result = await rag_service.ingest_document(path, "doc_123", "test.pdf")
        assert result.status == "failed"
        assert "No readable text" in result.error or "No valid chunks" in result.error
    finally:
        os.remove(path)

@pytest.mark.asyncio
async def test_no_retrieval_results():
    embed_service = MockEmbeddingService()
    vector_store = VectorStore()
    service = RAGService(embed_service, vector_store)
    
    # TEST 10: No result handled
    req = RetrievalRequest(
        document_id="doc_xyz",
        subject="Math",
        topic="Algebra",
        grade=8,
        learning_objective="x+y"
    )
    resp = await service.retrieve(req)
    assert not resp.grounded
    assert len(resp.chunks) == 0

