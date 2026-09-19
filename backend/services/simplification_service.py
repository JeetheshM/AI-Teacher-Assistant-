"""
Content Simplification and Transformation Service.
TeachMate AI - Person 2 (Lesson Planner + Simplification AI).

Provides multi-mode pedagogical content transformations:
1. simplify: reduces syntactic & vocabulary complexity for the same grade.
2. younger_level: explains concepts for a student 2-3 grades younger.
3. analogy: generates an intuitive, concrete real-world analogy.
4. real_world_example: creates an observable, everyday example or application.
"""

from typing import Optional
from pydantic import BaseModel, Field

from backend.models.lesson_models import (
    ContentTransformationRequest,
    ContentTransformationResponse,
    LLMResponseError,
    LessonAIError,
    TransformationMode,
)
from backend.mocks.mock_llm_service import LLMServiceProtocol
from backend.prompts.simplify_prompt import (
    SIMPLIFY_PROMPT_VERSION,
    build_transformation_prompt,
)


class RawTransformationOutput(BaseModel):
    """Internal model for parsing LLM structured response."""
    mode: str = Field(..., description="The transformation mode applied")
    transformed_content: str = Field(..., description="The transformed explanation text")


class SimplificationService:
    """
    Handles pedagogical content transformations.
    Integrates with shared LLM service via dependency injection.
    """

    def __init__(self, llm_service: LLMServiceProtocol):
        self.llm_service = llm_service

    async def transform(
        self, request: ContentTransformationRequest
    ) -> ContentTransformationResponse:
        """
        Executes a pedagogical transformation on the provided content block.
        """
        if not request.content or not request.content.strip():
            raise LessonAIError("Input content to transform must not be empty.")

        # Construct versioned transformation prompt
        prompt = build_transformation_prompt(request)

        try:
            # Single structured generation call
            raw_result = await self.llm_service.generate_structured(
                prompt=prompt,
                response_model=RawTransformationOutput
            )
            transformed_text = raw_result.transformed_content.strip()
        except Exception as exc:
            # Graceful error wrap preventing raw stack trace exposure
            if isinstance(exc, LessonAIError):
                raise
            raise LLMResponseError(
                f"Failed to transform content using mode '{request.mode.value}': {str(exc)}"
            ) from exc

        return ContentTransformationResponse(
            mode=request.mode,
            original_content=request.content.strip(),
            transformed_content=transformed_text,
            grade=request.grade,
        )

    # Convenience helper methods for specific modes
    async def simplify(
        self, content: str, subject: str, topic: str, grade: int
    ) -> ContentTransformationResponse:
        return await self.transform(
            ContentTransformationRequest(
                content=content,
                subject=subject,
                topic=topic,
                grade=grade,
                mode=TransformationMode.SIMPLIFY,
            )
        )

    async def younger_level(
        self, content: str, subject: str, topic: str, grade: int
    ) -> ContentTransformationResponse:
        return await self.transform(
            ContentTransformationRequest(
                content=content,
                subject=subject,
                topic=topic,
                grade=grade,
                mode=TransformationMode.YOUNGER_LEVEL,
            )
        )

    async def analogy(
        self, content: str, subject: str, topic: str, grade: int
    ) -> ContentTransformationResponse:
        return await self.transform(
            ContentTransformationRequest(
                content=content,
                subject=subject,
                topic=topic,
                grade=grade,
                mode=TransformationMode.ANALOGY,
            )
        )

    async def real_world_example(
        self, content: str, subject: str, topic: str, grade: int
    ) -> ContentTransformationResponse:
        return await self.transform(
            ContentTransformationRequest(
                content=content,
                subject=subject,
                topic=topic,
                grade=grade,
                mode=TransformationMode.REAL_WORLD_EXAMPLE,
            )
        )
