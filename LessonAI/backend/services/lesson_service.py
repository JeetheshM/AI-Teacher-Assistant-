"""
Lesson Plan AI Generation Service.
TeachMate AI - Person 2 (Lesson Planner + Simplification AI).

Orchestrates:
Teacher Input -> Prompt Builder -> Shared LLM Service -> Structured Parser -> Validator -> Response
"""

from typing import Optional

from backend.models.lesson_models import (
    ContentTransformationRequest,
    ContentTransformationResponse,
    LessonAIError,
    LessonGenerationError,
    LessonGenerationRequest,
    LessonGenerationResponse,
    LessonPlan,
    LessonValidationError,
    LLMResponseError,
)
from backend.mocks.mock_llm_service import LLMServiceProtocol
from backend.prompts.lesson_prompt import (
    LESSON_PROMPT_VERSION,
    build_lesson_prompt,
)
from backend.services.simplification_service import SimplificationService
from backend.validators.lesson_validator import LessonValidator


class LessonService:
    """
    Core business logic for generating structured classroom lesson plans.
    Uses dependency injection for the LLM service to maintain isolation and testability.
    """

    def __init__(self, llm_service: LLMServiceProtocol):
        self.llm_service = llm_service
        self.simplification_service = SimplificationService(llm_service)

    async def generate_lesson(
        self, request: LessonGenerationRequest
    ) -> LessonGenerationResponse:
        """
        Generates a complete structured lesson plan matching the teacher's requirements
        and grounded in any provided curriculum context.
        """
        # 1. Guard against empty topic or required fields
        if not request.topic or not request.topic.strip():
            raise LessonValidationError("Lesson topic is required and cannot be empty.")
        if not request.subject or not request.subject.strip():
            raise LessonValidationError("Lesson subject is required and cannot be empty.")
        if request.grade <= 0 or request.grade > 12:
            raise LessonValidationError(f"Grade must be between 1 and 12, got {request.grade}.")
        if request.duration_minutes <= 0:
            raise LessonValidationError(
                f"Duration must be a positive integer, got {request.duration_minutes}."
            )

        # 2. Build versioned prompt with prompt injection protection for curriculum text
        prompt = build_lesson_prompt(request)

        # 3. Single structured LLM call
        try:
            lesson_plan: LessonPlan = await self.llm_service.generate_structured(
                prompt=prompt, response_model=LessonPlan
            )
        except Exception as exc:
            if isinstance(exc, LessonAIError):
                raise
            raise LLMResponseError(
                f"Failed to generate structured lesson plan from AI model: {str(exc)}"
            ) from exc

        # 4. Deterministic source reconciliation
        # Ground truth metadata is derived from the supplied curriculum context to prevent hallucination
        reconciled_sources = LessonValidator.reconcile_sources(
            curriculum_context=request.curriculum_context,
            model_sources=lesson_plan.sources_used,
        )
        lesson_plan.sources_used = reconciled_sources

        # 5. Deterministic validation & quality check
        validation_result = LessonValidator.validate(
            lesson=lesson_plan,
            requested_duration_minutes=request.duration_minutes,
            curriculum_context=request.curriculum_context,
        )

        # 6. Composite response for Person 1 / Person 5
        return LessonGenerationResponse(
            lesson=lesson_plan,
            validation=validation_result,
            prompt_version=LESSON_PROMPT_VERSION,
        )

    async def transform_content(
        self, request: ContentTransformationRequest
    ) -> ContentTransformationResponse:
        """
        Delegates content transformation to the integrated SimplificationService.
        """
        return await self.simplification_service.transform(request)
