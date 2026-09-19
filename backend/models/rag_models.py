from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DocumentIngestionRequest(BaseModel):
    file_path: str
    document_id: str
    filename: str

class DocumentIngestionResult(BaseModel):
    document_id: str
    filename: str
    status: str
    page_count: Optional[int] = 0
    chunk_count: Optional[int] = 0
    error: Optional[str] = None

class ChunkMetadata(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page_number: int
    chunk_index: int
    content: str

class RetrievalRequest(BaseModel):
    document_id: Optional[str] = None
    subject: str
    topic: str
    grade: int
    learning_objective: str
    top_k: int = 5

class CurriculumContextItem(BaseModel):
    content: str
    source: str
    page_number: int
    chunk_id: str
    score: Optional[float] = None

class RetrievalResponse(BaseModel):
    success: bool
    grounded: bool
    query: str
    document_id: Optional[str] = None
    chunks: List[CurriculumContextItem]
    source_count: int = 0

