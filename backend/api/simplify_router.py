"""
FastAPI Router Stub for Content Simplification and Transformations.
TeachMate AI - Person 2 (Lesson Planner + Simplification AI).

This router can be directly mounted by Person 5 in the main FastAPI application:
    app.include_router(create_simplify_router(simplification_service))
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status
from backend.models.lesson_models import (
    ContentTransformationRequest,
    ContentTransformationResponse,
    LessonAIError,
)
from backend.mocks.mock_llm_service import MockLLMService
from backend.services.simplification_service import SimplificationService


def create_simplify_router(service: Optional[SimplificationService] = None) -> APIRouter:
    """
    Factory creating the simplification API router.
    Defaults to an internal MockLLMService if no service is injected (for standalone execution).
    """
    router = APIRouter(prefix="/api/simplify", tags=["Simplification"])
    simplification_service = service or SimplificationService(MockLLMService())

    @router.post(
        "",
        response_model=ContentTransformationResponse,
        status_code=status.HTTP_200_OK,
        summary="Transform educational content (simplify, younger_level, analogy, real_world_example)",
        description="Adapts existing lesson content or explanations according to the chosen transformation mode."
    )
    async def transform_content_endpoint(
        request: ContentTransformationRequest
    ) -> ContentTransformationResponse:
        try:
            return await simplification_service.transform(request)
        except LessonAIError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(err)
            )
        except Exception as err:
            # Prevent leaking system trace / secret details
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to transform content. Please retry."
            )

    return router


# Standalone router instance with default mock for testing
simplify_router = create_simplify_router()
