from sqlalchemy.orm import Session
from backend.models.core import Lesson, Document, Material, Quiz, Question, GenerationLog

class DBService:
    @staticmethod
    def get_lesson(db: Session, lesson_id: str):
        return db.query(Lesson).filter(Lesson.id == lesson_id).first()

    @staticmethod
    def create_material(db: Session, lesson_id: str, mat_type: str, title: str, content: str):
        new_material = Material(
            lesson_id=lesson_id,
            type=mat_type,
            title=title,
            content=content
        )
        db.add(new_material)
        db.commit()
        db.refresh(new_material)
        return new_material
        
    @staticmethod
    def log_generation(db: Session, lesson_id: str, feature: str, model: str, latency: int, status: str = "success"):
        log = GenerationLog(
            lesson_id=lesson_id,
            feature=feature,
            model=model,
            latency_ms=latency,
            status=status
        )
        db.add(log)
        db.commit()
        return log
