from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.db import get_db

router = APIRouter()

@router.post("/generate")
def generate_activity(db: Session = Depends(get_db)):
    # Person 6 (Classroom Activities) will implement this.
    return {"message": "Activity generation stub"}
