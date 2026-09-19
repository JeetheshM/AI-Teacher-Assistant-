"""
lessons_router.py — TeachMate AI
Saves generated lesson + materials to Supabase PostgreSQL via SQLAlchemy.
"""
import json
import time
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.models.lesson_models import (
    LessonAIError,
    LessonGenerationRequest,
    LessonGenerationResponse,
)
from backend.models.core import Lesson, Material, GenerationLog
from backend.mocks.mock_llm_service import MockLLMService
from backend.services.gemini_llm_service import GeminiLLMService
from backend.services.lesson_service import LessonService

router = APIRouter(prefix="/api/lessons", tags=["Lessons"])

try:
    lesson_service = LessonService(GeminiLLMService())
except Exception:
    lesson_service = LessonService(MockLLMService())



@router.post(
    "/generate",
    status_code=status.HTTP_200_OK,
    summary="Generate a structured lesson plan and save to Supabase",
)
async def generate_lesson_endpoint(
    request: LessonGenerationRequest,
    db: Session = Depends(get_db),
):
    start = time.time()
    try:
        if getattr(request, "document_id", None):
            from backend.models.rag_models import RetrievalRequest
            from backend.services.rag_service import global_rag_service
            
            retrieval_req = RetrievalRequest(
                document_id=request.document_id,
                subject=request.subject,
                topic=request.topic,
                grade=request.grade,
                learning_objective=request.learning_objective
            )
            # Fetch context from vector store
            context = await global_rag_service.get_curriculum_context(retrieval_req)
            if context:
                from backend.models.lesson_models import CurriculumChunk
                request.curriculum_context = [
                    CurriculumChunk(**c) for c in context
                ]

        result: LessonGenerationResponse = await lesson_service.generate_lesson(request)
    except LessonAIError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lesson generation failed: {str(err)}",
        )

    latency_ms = int((time.time() - start) * 1000)
    lesson_plan = result.lesson

    # ── Save lesson metadata to Supabase ────────────────────────────────────
    db_lesson = Lesson(
        title=lesson_plan.title,
        subject=lesson_plan.subject,
        topic=request.topic,
        grade=lesson_plan.grade,
        duration_minutes=lesson_plan.total_duration_minutes or request.duration_minutes,
        difficulty=lesson_plan.difficulty,
        learning_objective=request.learning_objective,
        status="generated",
    )
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)

    # ── Save lesson content as materials ────────────────────────────────────
    def save_material(mat_type: str, title: str, content):
        if not content:
            return
        text = content if isinstance(content, str) else json.dumps(content, default=str)
        mat = Material(
            lesson_id=db_lesson.id,
            type=mat_type,
            title=title,
            content=text,
        )
        db.add(mat)

    save_material("introduction", "Introduction & Hook",
                  getattr(lesson_plan.introduction, "content", str(lesson_plan.introduction)))
    save_material("explanation", "Core Concept Explanation",
                  getattr(lesson_plan.explanation, "content", str(lesson_plan.explanation)))
    save_material("key_points", "Key Takeaways",
                  json.dumps(lesson_plan.key_points))
    save_material("recap", "Class Recap & Synthesis",
                  getattr(lesson_plan.recap, "content", str(lesson_plan.recap)))
    if lesson_plan.examples:
        save_material("examples", "Concrete Examples",
                      json.dumps([e.model_dump() if hasattr(e, "model_dump") else e for e in lesson_plan.examples]))
    if lesson_plan.common_misconceptions:
        save_material("misconceptions", "Common Misconceptions & Corrections",
                      json.dumps([m.model_dump() if hasattr(m, "model_dump") else m for m in lesson_plan.common_misconceptions]))

    # ── Save generation log ─────────────────────────────────────────────────
    log = GenerationLog(
        lesson_id=db_lesson.id,
        feature="lesson_generation",
        model=os.getenv("LLM_MODEL", "mock"),
        prompt_version="lesson_v1",
        status="success",
        latency_ms=latency_ms,
    )
    db.add(log)
    db.commit()

    # ── Return full response with DB lesson id injected ─────────────────────
    response_dict = result.model_dump()
    response_dict["id"] = db_lesson.id
    response_dict["lesson"]["id"] = db_lesson.id
    return response_dict


@router.get("/{lesson_id}", summary="Fetch a lesson by ID from Supabase")
def get_lesson(lesson_id: str, db: Session = Depends(get_db)):
    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    materials = {m.type: m.content for m in db_lesson.materials}

    def parse_json_field(key):
        raw = materials.get(key, "[]")
        try:
            return json.loads(raw)
        except Exception:
            return []

    return {
        "id": db_lesson.id,
        "title": db_lesson.title,
        "subject": db_lesson.subject,
        "topic": db_lesson.topic,
        "grade": db_lesson.grade,
        "duration_minutes": db_lesson.duration_minutes,
        "difficulty": db_lesson.difficulty,
        "learning_objective": db_lesson.learning_objective,
        "status": db_lesson.status,
        "created_at": str(db_lesson.created_at),
        "introduction": {"duration_minutes": 5, "content": materials.get("introduction", "")},
        "explanation": {"duration_minutes": 20, "content": materials.get("explanation", "")},
        "key_points": parse_json_field("key_points"),
        "recap": {"duration_minutes": 5, "content": materials.get("recap", "")},
        "examples": parse_json_field("examples"),
        "common_misconceptions": parse_json_field("misconceptions"),
    }


@router.get("/", summary="List all lessons from Supabase")
def list_lessons(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    lessons = db.query(Lesson).order_by(Lesson.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": l.id,
            "title": l.title,
            "subject": l.subject,
            "topic": l.topic,
            "grade": l.grade,
            "difficulty": l.difficulty,
            "status": l.status,
            "created_at": str(l.created_at),
        }
        for l in lessons
    ]


@router.get("/{lesson_id}/sources", summary="Get sources for a lesson")
def get_lesson_sources(lesson_id: str, db: Session = Depends(get_db)):
    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    sources = [
        {"filename": doc.filename, "file_type": doc.file_type, "status": doc.status}
        for doc in db_lesson.documents
    ]
    return {"lesson_id": lesson_id, "sources": sources}


@router.post("/{lesson_id}/export")
def export_lesson(lesson_id: str, db: Session = Depends(get_db)):
    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return {"message": "PDF export triggered", "lesson_id": lesson_id, "title": db_lesson.title}


# Keep backwards compat alias
lessons_router = router
