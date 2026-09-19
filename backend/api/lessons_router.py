"""
FastAPI Router Stub for Lesson Generation.
TeachMate AI - Person 2 (Lesson Planner + Simplification AI).

This router can be directly mounted by Person 5 in the main FastAPI application:
    app.include_router(create_lessons_router(lesson_service))
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status
from backend.models.lesson_models import (
    LessonAIError,
    LessonGenerationRequest,
    LessonGenerationResponse,
)
from backend.mocks.mock_llm_service import MockLLMService
from backend.services.lesson_service import LessonService


def create_lessons_router(service: Optional[LessonService] = None) -> APIRouter:
    """
    Factory creating the lessons API router.
    Defaults to an internal MockLLMService if no service is injected (for standalone execution).
    """
    router = APIRouter(prefix="/api/lessons", tags=["Lessons"])
    lesson_service = service or LessonService(MockLLMService())

    @router.post(
        "/generate",
        response_model=LessonGenerationResponse,
        status_code=status.HTTP_200_OK,
        summary="Generate a structured, classroom-ready lesson plan",
        description="Receives teacher requirements and optional curriculum context, generating a validated lesson plan."
    )
    async def generate_lesson_endpoint(request: LessonGenerationRequest) -> LessonGenerationResponse:
        try:
            return await lesson_service.generate_lesson(request)
        except LessonAIError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(err)
            )
        except Exception as err:
            # Prevent leaking system trace / secret details
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to generate lesson plan. Please retry."
            )

    return router


# Standalone router instance with default mock for testing
lessons_router = create_lessons_router()
