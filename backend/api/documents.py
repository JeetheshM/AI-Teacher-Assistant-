import os
import uuid
import tempfile
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.services.rag_service import global_rag_service

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    document_id = str(uuid.uuid4())
    
    # Save file to a temporary location
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"{document_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    # Ingest document into RAG
    result = await global_rag_service.ingest_document(
        file_path=file_path, 
        document_id=document_id, 
        filename=file.filename
    )
    
    if result.status == "failed":
        raise HTTPException(status_code=500, detail=f"Document processing failed: {result.error}")
        
    return {
        "message": "Document uploaded and processed successfully",
        "document_id": document_id,
        "filename": file.filename,
        "page_count": getattr(result, 'page_count', 0),
        "chunk_count": getattr(result, 'chunk_count', 0)
    }
