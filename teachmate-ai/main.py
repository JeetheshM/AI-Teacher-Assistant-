"""
main.py
-------
TeachMate AI — Quiz Module API Server

Endpoints:
    GET  /                          Health check
    GET  /health                    Health check
    POST /api/quizzes/generate      Generate quiz from JSON request
    POST /api/quizzes/generate-from-file   Upload a PDF/TXT + quiz params -> quiz
    POST /api/quizzes/validate-only Validate an existing quiz JSON

Run:
    python -m uvicorn main:app --port 8080
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from backend.models.quiz_models import QuizGenerationRequest
from backend.services.gemini_llm_service import GeminiLLMService
from backend.services.pdf_extractor import extract_text_from_pdf, extract_text_from_txt
from backend.services.quiz_service import (
    InputValidationError,
    LLMResponseError,
    QuizService,
)
from backend.validators.quiz_validator import QuizValidator, generate_answer_key

# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------

quiz_service: QuizService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global quiz_service
    quiz_service = QuizService(GeminiLLMService())
    yield


app = FastAPI(
    title="TeachMate AI — Quiz Module",
    description=(
        "AI-powered assessment generation. "
        "Upload any PDF or text file and get a full quiz with answers and quality check."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _build_response(quiz, validation, answer_key):
    return {
        "quiz": quiz.model_dump(),
        "answer_key": answer_key.model_dump(),
        "validation": validation.model_dump(),
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "TeachMate AI Quiz Module"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


# ── Endpoint 1: Generate from JSON (no file) ───────────────────────────────

@app.post("/api/quizzes/generate", tags=["Quiz"])
async def generate_quiz(request: QuizGenerationRequest):
    """
    Generate a quiz from a structured JSON request.
    Optionally pass `curriculum_context` to ground the quiz in your own material.
    """
    try:
        quiz, validation = await quiz_service.generate_quiz(request)
    except InputValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except LLMResponseError as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}")

    return _build_response(quiz, validation, generate_answer_key(quiz))


# ── Endpoint 2: Generate from uploaded file ────────────────────────────────

@app.post("/api/quizzes/generate-from-file", tags=["Quiz"])
async def generate_quiz_from_file(
    file: UploadFile = File(..., description="Upload a PDF or .txt file"),
    subject: str = Form(..., description="e.g. Science"),
    topic: str = Form(..., description="e.g. Photosynthesis"),
    grade: int = Form(..., description="School grade 1-12"),
    difficulty: str = Form("intermediate", description="easy | intermediate | hard"),
    question_count: int = Form(5, description="Number of questions (1-20)"),
    question_types: str = Form(
        "mcq,true_false,short_answer",
        description="Comma-separated: mcq,true_false,short_answer"
    ),
    bloom_levels: str = Form(
        "remember,understand,apply",
        description="Comma-separated bloom levels"
    ),
    learning_objective: str = Form("", description="Optional learning objective"),
):
    """
    Upload a PDF or TXT file → extract text → generate a quiz grounded in that content.

    **How to use in Swagger UI:**
    1. Click 'Try it out'
    2. Click 'Choose File' and upload your PDF
    3. Fill in subject, topic, grade etc.
    4. Click Execute
    """

    # ── Read file bytes ─────────────────────────────────────────────────────
    file_bytes = await file.read()
    filename = file.filename or "uploaded_file"

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # ── Extract text from file ──────────────────────────────────────────────
    fname_lower = filename.lower()
    try:
        if fname_lower.endswith(".pdf"):
            curriculum_context = extract_text_from_pdf(file_bytes, filename)
        elif fname_lower.endswith(".txt"):
            curriculum_context = extract_text_from_txt(file_bytes, filename)
        else:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type '{filename}'. Upload a .pdf or .txt file."
            )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not read file: {exc}")

    if not curriculum_context:
        raise HTTPException(
            status_code=422,
            detail="No readable text found in the uploaded file. "
                   "Make sure the PDF contains actual text (not just scanned images)."
        )

    # ── Parse form fields ───────────────────────────────────────────────────
    types_list = [t.strip() for t in question_types.split(",") if t.strip()]
    bloom_list = [b.strip() for b in bloom_levels.split(",") if b.strip()] or None
    objective = learning_objective.strip() or None

    # ── Build request ───────────────────────────────────────────────────────
    try:
        request = QuizGenerationRequest(
            subject=subject,
            topic=topic,
            grade=grade,
            difficulty=difficulty,
            question_count=min(question_count, 20),
            question_types=types_list,
            learning_objective=objective,
            bloom_levels=bloom_list,
            curriculum_context=curriculum_context,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid parameters: {exc}")

    # ── Generate quiz ───────────────────────────────────────────────────────
    try:
        quiz, validation = await quiz_service.generate_quiz(request)
    except InputValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except LLMResponseError as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}")

    response = _build_response(quiz, validation, generate_answer_key(quiz))

    # Add info about extracted content
    response["file_info"] = {
        "filename": filename,
        "pages_extracted": len(curriculum_context),
        "total_chars": sum(len(c.content) for c in curriculum_context),
    }

    return response


# ── Endpoint 3: Validate only ──────────────────────────────────────────────

@app.post("/api/quizzes/validate-only", tags=["Quiz"])
async def validate_quiz(quiz_data: dict):
    """
    Run structural validation on an existing quiz JSON.
    Useful for testing the validator independently.
    """
    from backend.models.quiz_models import QuizResponse
    try:
        quiz = QuizResponse(**quiz_data)
        result = QuizValidator().validate(quiz, expected_count=quiz.question_count)
        return result.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))
