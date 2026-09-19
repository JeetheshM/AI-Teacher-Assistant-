"""
quizzes.py — generates quiz + saves to Supabase (quizzes + questions tables)
"""
import json
import time
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import Optional

from backend.database.db import get_db
from backend.models.quiz_models import QuizGenerationRequest
from backend.models.core import Quiz, Question
from backend.services.quiz_service import QuizService, InputValidationError, LLMResponseError
from backend.services.gemini_llm_service import GeminiLLMService
from backend.mocks.mock_llm_service import MockLLMService
from backend.services.pdf_extractor import extract_text_from_pdf, extract_text_from_txt
from backend.validators.quiz_validator import QuizValidator, generate_answer_key

router = APIRouter()

try:
    quiz_service = QuizService(GeminiLLMService())
except Exception:
    quiz_service = QuizService(MockLLMService())


def _save_quiz_to_db(db: Session, quiz_result, validation, lesson_id: Optional[str] = None) -> str:
    """Persist quiz + questions to Supabase, return quiz_id."""
    quiz_data = quiz_result.model_dump() if hasattr(quiz_result, "model_dump") else quiz_result

    db_quiz = Quiz(
        lesson_id=lesson_id,
        title=quiz_data.get("title") or f"Quiz – {quiz_data.get('topic', 'General')}",
        difficulty=quiz_data.get("difficulty", "intermediate"),
        question_count=len(quiz_data.get("questions", [])),
        status="generated",
    )
    db.add(db_quiz)
    db.flush()  # get db_quiz.id before adding questions

    for q in quiz_data.get("questions", []):
        options = q.get("options") or q.get("choices") or {}
        db_q = Question(
            quiz_id=db_quiz.id,
            question_text=q.get("question", ""),
            question_type=q.get("question_type", "mcq"),
            difficulty=q.get("difficulty", "intermediate"),
            bloom_level=q.get("bloom_level"),
            options_json=options if isinstance(options, dict) else {"options": options},
            correct_answer=str(q.get("correct_answer", "")),
            explanation=q.get("explanation"),
            validation_status="valid",
        )
        db.add(db_q)

    db.commit()
    db.refresh(db_quiz)
    return db_quiz.id


def _build_response(quiz, validation, answer_key):
    return {
        "quiz": quiz.model_dump(),
        "answer_key": answer_key.model_dump(),
        "validation": validation.model_dump(),
    }


@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_quiz(
    request: QuizGenerationRequest,
    db: Session = Depends(get_db),
):
    try:
        quiz, validation = await quiz_service.generate_quiz(request)
        answer_key = generate_answer_key(quiz)

        # Save to Supabase
        lesson_id = getattr(request, "lesson_id", None)
        quiz_id = _save_quiz_to_db(db, quiz, validation, lesson_id)

        result = _build_response(quiz, validation, answer_key)
        result["quiz_id"] = quiz_id
        return result

    except InputValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except LLMResponseError as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {exc}")


@router.get("/", summary="List all quizzes")
def list_quizzes(db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).order_by(Quiz.created_at.desc()).limit(50).all()
    return [
        {
            "id": q.id,
            "title": q.title,
            "difficulty": q.difficulty,
            "question_count": q.question_count,
            "lesson_id": q.lesson_id,
            "status": q.status,
            "created_at": str(q.created_at),
        }
        for q in quizzes
    ]


@router.get("/{quiz_id}", summary="Get a quiz with its questions")
def get_quiz(quiz_id: str, db: Session = Depends(get_db)):
    q = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quiz not found")
    questions = [
        {
            "id": qu.id,
            "question_text": qu.question_text,
            "question_type": qu.question_type,
            "difficulty": qu.difficulty,
            "bloom_level": qu.bloom_level,
            "options": qu.options_json,
            "correct_answer": qu.correct_answer,
            "explanation": qu.explanation,
        }
        for qu in q.questions
    ]
    return {
        "id": q.id,
        "title": q.title,
        "difficulty": q.difficulty,
        "lesson_id": q.lesson_id,
        "questions": questions,
        "created_at": str(q.created_at),
    }


@router.post("/generate-from-file")
async def generate_quiz_from_file(
    file: UploadFile = File(...),
    subject: str = Form(...),
    topic: str = Form(...),
    grade: int = Form(...),
    difficulty: str = Form("intermediate"),
    question_count: int = Form(5),
    question_types: str = Form("mcq,true_false,short_answer"),
    bloom_levels: str = Form("remember,understand,apply"),
    learning_objective: str = Form(""),
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()
    filename = file.filename or "uploaded_file"
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    fname_lower = filename.lower()
    if fname_lower.endswith(".pdf"):
        curriculum_context = extract_text_from_pdf(file_bytes, filename)
    elif fname_lower.endswith(".txt"):
        curriculum_context = extract_text_from_txt(file_bytes, filename)
    else:
        raise HTTPException(status_code=415, detail="Unsupported file type.")

    req = QuizGenerationRequest(
        subject=subject,
        topic=topic,
        grade=grade,
        difficulty=difficulty,
        question_count=min(question_count, 20),
        question_types=[t.strip() for t in question_types.split(",") if t.strip()],
        learning_objective=learning_objective.strip() or None,
        bloom_levels=[b.strip() for b in bloom_levels.split(",") if b.strip()] or None,
        curriculum_context=curriculum_context,
    )

    quiz, validation = await quiz_service.generate_quiz(req)
    answer_key = generate_answer_key(quiz)
    quiz_id = _save_quiz_to_db(db, quiz, validation)

    res = _build_response(quiz, validation, answer_key)
    res["quiz_id"] = quiz_id
    res["file_info"] = {"filename": filename}
    return res


@router.post("/validate-only")
async def validate_quiz(quiz_data: dict):
    from backend.models.quiz_models import QuizResponse
    try:
        quiz = QuizResponse(**quiz_data)
        result = QuizValidator().validate(quiz, expected_count=quiz.question_count)
        return result.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))
