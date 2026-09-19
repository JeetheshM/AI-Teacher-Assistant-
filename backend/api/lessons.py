from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database.schemas import LessonCreate, LessonResponse
from backend.models.core import Lesson

router = APIRouter()

@router.post("/generate", response_model=LessonResponse)
def generate_lesson(request: LessonCreate, db: Session = Depends(get_db)):
    # Person 2 (Lesson Planner) will integrate LLM logic here.
    # DB stub creation for now.
    new_lesson = Lesson(
        title=f"{request.topic} Lesson",
        subject=request.subject,
        topic=request.topic,
        grade=request.grade,
        duration_minutes=request.duration_minutes,
        difficulty=request.difficulty,
        learning_objective=request.learning_objective
    )
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    
    return new_lesson

@router.get("/{lesson_id}", response_model=LessonResponse)
def get_lesson(lesson_id: str, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson

@router.get("/{lesson_id}/sources")
def get_lesson_sources(lesson_id: str, db: Session = Depends(get_db)):
    # Person 4 (RAG) will implement this.
    return {"sources": []}

@router.post("/{lesson_id}/export")
def export_lesson(lesson_id: str, db: Session = Depends(get_db)):
    # Person 6 (Export) will implement this.
    return {"message": "PDF exported successfully"}
