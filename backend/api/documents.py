from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.db import get_db

router = APIRouter()

@router.post("/upload")
def upload_document(db: Session = Depends(get_db)):
    # Person 4 (RAG) will implement PDF upload and chunking here.
    return {"message": "Document uploaded successfully"}
