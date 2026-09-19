# Curriculum RAG Module (Person 4)

## PURPOSE
Curriculum-grounded retrieval. Provides semantic search over uploaded PDFs to ground AI generation in specific educational material.

## PIPELINE
PDF -> extraction -> chunking -> embedding -> vector store -> retrieval -> curriculum_context

## SUPPORTED FILES
- `.pdf` files are supported for the MVP. Scanned PDFs without extractable text are not supported.

## CHUNKING STRATEGY
Word-based chunking with size `600` and overlap `100`. Each chunk is page-bounded (preserves `page_number`).

## EMBEDDING MODEL
Uses `sentence-transformers` locally (`all-MiniLM-L6-v2` by default). Configurable via `EMBEDDING_MODEL` environment variable. A mock embedding service is available for deterministic, fast unit tests without requiring the model.

## VECTOR STORE
Lightweight, in-memory Numpy-based vector store calculating cosine similarity. Fast for MVP, easily replaceable with FAISS/Chroma via the `VectorStore` interface.

## RETRIEVAL
Retrieves `top-k` (default 5) chunks using cosine similarity between the generated query embedding and stored document chunks. Supports filtering by `document_id`.

## SOURCE TRACKING
Preserves `filename`, `page_number`, and a unique `chunk_id` for every retrieved segment. This allows the frontend to correctly cite source pages.

## INTEGRATION
Modules should use `RAGService.get_curriculum_context()` which returns a predictable schema:
```json
[
    {
        "content": "extracted text...",
        "source": "filename.pdf",
        "page_number": 10,
        "chunk_id": "doc123_p10_c1"
    }
]
```
Person 2 (Lesson), Person 3 (Quiz), and Person 6 (Activity) should use this exact schema.

## SECURITY
- Uploaded PDFs are treated as **untrusted reference data**, not system instructions.
- Follows **data minimization**: Only relevant chunks are sent to downstream LLMs, not the entire PDF.
- No API keys are hardcoded.

## LIMITATIONS
- Scanned PDFs without OCR are reported as unreadable.
- RAG grounds the model but does not strictly guarantee 0 hallucinations. Teacher review is always required.
- In-memory vector store resets between restarts.

## RUNNING TESTS
```bash
pip install -r requirements_rag.txt
pytest backend/tests/test_rag.py
```

