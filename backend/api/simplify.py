from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.db import get_db

router = APIRouter()

@router.post("/")
def simplify_content(db: Session = Depends(get_db)):
    # Person 2 (Simplification AI) will implement this.
    return {"message": "Simplification stub"}
