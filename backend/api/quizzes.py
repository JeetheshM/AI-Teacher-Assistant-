from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.db import get_db

router = APIRouter()

@router.post("/generate")
def generate_quiz(db: Session = Depends(get_db)):
    # Person 3 (Quiz AI) will implement this.
    return {"message": "Quiz generation stub"}
