"""
simplify_router.py — transforms content AND saves result to Supabase materials table.
"""
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.models.lesson_models import (
    ContentTransformationRequest,
    ContentTransformationResponse,
    LessonAIError,
)
from backend.models.core import Material
from backend.mocks.mock_llm_service import MockLLMService
from backend.services.gemini_llm_service import GeminiLLMService
from backend.services.simplification_service import SimplificationService


router = APIRouter(prefix="/api/simplify", tags=["Simplification"])

try:
    _simplification_service = SimplificationService(GeminiLLMService())
except Exception:
    _simplification_service = SimplificationService(MockLLMService())


@router.post(
    "",
    response_model=ContentTransformationResponse,
    status_code=status.HTTP_200_OK,
    summary="Transform educational content and save to Supabase",
)
async def transform_content_endpoint(
    request: ContentTransformationRequest,
    db: Session = Depends(get_db),
) -> ContentTransformationResponse:
    try:
        result: ContentTransformationResponse = await _simplification_service.transform(request)
    except LessonAIError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content transformation failed: {str(err)}",
        )

    # Save result to materials table (linked to lesson if lesson_id provided)
    lesson_id: Optional[str] = getattr(request, "lesson_id", None)
    mat_type = str(getattr(request, "mode", "simplified_explanation"))

    mat = Material(
        lesson_id=lesson_id,
        type=mat_type,
        title=f"Simplified: {getattr(request, 'topic', 'Content')}",
        content=result.transformed_content if hasattr(result, "transformed_content") else str(result),
    )
    db.add(mat)
    db.commit()

    return result


# Backwards-compat alias used by main.py
simplify_router = router
