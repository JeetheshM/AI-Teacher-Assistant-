from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.db import get_db

router = APIRouter()

class SimplifyRequest(BaseModel):
    content: str
    subject: str = "Science"
    topic: str = "General"
    grade: int = 8
    mode: str = "simplify"

class SimplifyResponse(BaseModel):
    original_text: str
    simplified_text: str
    subject: str
    topic: str
    grade: int
    mode: str

@router.post("/", response_model=SimplifyResponse)
def simplify_content(request: SimplifyRequest, db: Session = Depends(get_db)):
    content = request.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    simplified = content
    return {
        "original_text": request.content,
        "simplified_text": simplified,
        "subject": request.subject,
        "topic": request.topic,
        "grade": request.grade,
        "mode": request.mode,
    }
