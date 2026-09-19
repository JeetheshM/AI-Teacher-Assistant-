"""
quiz_service.py
---------------
Core quiz generation service for TeachMate AI.

Person 5 instantiates QuizService with the shared LLMService.
Person 4 passes curriculum_context inside QuizGenerationRequest.
Person 1 consumes the returned QuizResponse.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from backend.models.quiz_models import (
    CurriculumContext,
    Question,
    QuizGenerationRequest,
    QuizResponse,
    SourceReference,
    ValidationResult,
)
from backend.prompts.quiz_prompt import QUIZ_PROMPT_VERSION, build_quiz_prompt
from backend.validators.quiz_validator import QuizValidator, generate_answer_key

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class InputValidationError(ValueError):
    """Raised when the QuizGenerationRequest contains invalid input."""


class LLMResponseError(RuntimeError):
    """Raised when the LLM returns an unusable response."""


class QuizGenerationError(RuntimeError):
    """General quiz generation failure."""


class QuizValidationError(RuntimeError):
    """Raised when the generated quiz fails structural validation."""


# ---------------------------------------------------------------------------
# LLM Service protocol (Person 5 provides the real implementation)
# ---------------------------------------------------------------------------

class LLMServiceProtocol:
    """
    Structural duck-type protocol for Person 5's shared LLM service.

    The real implementation lives in backend/services/llm_service.py (Person 5).
    MockLLMService in tests/mocks/mock_llm_service.py implements this for testing.
    """

    async def generate_text(self, prompt: str) -> str:  # pragma: no cover
        raise NotImplementedError

    async def generate_structured(
        self, prompt: str, response_model: Any = None
    ) -> Any:  # pragma: no cover
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Quiz Service
# ---------------------------------------------------------------------------

class QuizService:
    """
    Generates and validates AI-powered assessments.

    Architecture:
        QuizGenerationRequest
            -> build_quiz_prompt()
            -> LLMService.generate_text()   (ONE call)
            -> _parse_llm_response()
            -> _build_quiz_response()
            -> QuizValidator.validate()
            -> Optional single repair attempt
            -> Return QuizResponse + ValidationResult

    Usage (Person 5):
        quiz_service = QuizService(llm_service)
        result, validation = await quiz_service.generate_quiz(request)
        answer_key = generate_answer_key(result)

    prompt_version is exposed for Person 5's GenerationLog.
    """

    prompt_version: str = QUIZ_PROMPT_VERSION

    def __init__(self, llm_service: LLMServiceProtocol) -> None:
        self._llm = llm_service
        self._validator = QuizValidator()

    # ── Public entry point ──────────────────────────────────────────────────

    async def generate_quiz(
        self,
        request: QuizGenerationRequest,
        attempt_repair: bool = True,
    ) -> tuple[QuizResponse, ValidationResult]:
        """
        Generate a complete quiz for the given request.

        Returns:
            (QuizResponse, ValidationResult)

        Raises:
            InputValidationError  — bad request parameters
            LLMResponseError      — LLM returned unusable output
            QuizGenerationError   — unexpected generation failure
        """
        self._validate_request(request)

        # ── Step 1: build prompt ────────────────────────────────────────────
        prompt = build_quiz_prompt(request)
        logger.info(
            "Generating quiz | topic=%s grade=%s difficulty=%s count=%d prompt_version=%s",
            request.topic,
            request.grade,
            request.difficulty,
            request.question_count,
            self.prompt_version,
        )

        # ── Step 2: ONE LLM call ────────────────────────────────────────────
        try:
            raw = await self._llm.generate_text(prompt)
        except Exception as exc:
            raise LLMResponseError(f"LLM call failed: {exc}") from exc

        # ── Step 3: parse + assemble ────────────────────────────────────────
        quiz = self._build_quiz_response(raw, request)

        # ── Step 4: validate ────────────────────────────────────────────────
        validation = self._validator.validate(quiz, expected_count=request.question_count)

        # ── Step 5: optional single repair attempt ──────────────────────────
        if not validation.valid and attempt_repair:
            logger.warning("Quiz failed validation — attempting single repair.")
            quiz, validation = await self._attempt_repair(quiz, request, validation)

        if not validation.valid:
            logger.warning(
                "Quiz validation failed after generation. Errors: %s", validation.errors
            )

        return quiz, validation

    # ── Private helpers ─────────────────────────────────────────────────────

    def _validate_request(self, request: QuizGenerationRequest) -> None:
        if not request.topic.strip():
            raise InputValidationError("topic must not be blank.")
        if request.question_count < 1:
            raise InputValidationError("question_count must be at least 1.")
        unsupported = set(request.question_types) - {"mcq", "true_false", "short_answer"}
        if unsupported:
            raise InputValidationError(
                f"Unsupported question_types: {unsupported}. "
                "Allowed: mcq, true_false, short_answer"
            )

    def _parse_llm_response(self, raw: str) -> Dict[str, Any]:
        """
        Parse LLM output to a Python dict.
        Handles common LLM formatting artefacts (e.g., ```json fences).
        """
        text = raw.strip()

        # Strip markdown code fences if present
        if text.startswith("```"):
            lines = text.splitlines()
            # Remove opening fence (```json or ```)
            lines = lines[1:] if lines[0].startswith("```") else lines
            # Remove closing fence
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise LLMResponseError(
                f"LLM returned malformed JSON: {exc}\n\nRaw output (first 500 chars):\n{raw[:500]}"
            ) from exc

    def _build_quiz_response(
        self,
        raw: str,
        request: QuizGenerationRequest,
    ) -> QuizResponse:
        """Parse raw LLM output and assemble a QuizResponse."""
        data = self._parse_llm_response(raw)

        raw_questions: List[Dict[str, Any]] = data.get("questions", [])

        questions: List[Question] = []
        for i, item in enumerate(raw_questions):
            try:
                q = Question(
                    id=f"q{i + 1}",
                    question=item.get("question", ""),
                    type=item.get("type", "mcq"),
                    difficulty=item.get("difficulty", request.difficulty),
                    bloom_level=item.get("bloom_level", "remember"),
                    options=item.get("options", []),
                    correct_answer=item.get("correct_answer", ""),
                    explanation=item.get("explanation", ""),
                )
                questions.append(q)
            except Exception as exc:
                logger.warning("Skipping malformed question %d: %s", i + 1, exc)

        sources_used = self._derive_sources(request.curriculum_context)

        title = f"{request.topic} Assessment"

        return QuizResponse(
            title=title,
            subject=request.subject,
            topic=request.topic,
            grade=request.grade,
            difficulty=request.difficulty,
            question_count=len(questions),
            questions=questions,
            sources_used=sources_used,
        )

    def _derive_sources(
        self,
        curriculum_context: Optional[List[CurriculumContext]],
    ) -> List[SourceReference]:
        """
        Derive sources directly from curriculum_context (not from LLM output).
        Deduplicates entries.
        """
        if not curriculum_context:
            return []

        seen: set = set()
        sources: List[SourceReference] = []
        for ctx in curriculum_context:
            ref = SourceReference(source=ctx.source, page_number=ctx.page_number)
            key = (ctx.source, ctx.page_number)
            if key not in seen:
                seen.add(key)
                sources.append(ref)
        return sources

    async def _attempt_repair(
        self,
        quiz: QuizResponse,
        request: QuizGenerationRequest,
        validation: ValidationResult,
    ) -> tuple[QuizResponse, ValidationResult]:
        """
        Single repair attempt when initial validation fails.

        Only attempted for simple issues (e.g., question count mismatch).
        Returns original quiz + validation if repair is not warranted.
        """
        # Only repair if count mismatch is the sole issue
        count_issue = not validation.checks.question_count_valid
        other_issues = any(
            v
            for k, v in validation.checks.model_dump().items()
            if k != "question_count_valid" and not v
        )

        if not count_issue or other_issues:
            # Too many issues — don't attempt repair; return as-is with warning
            return quiz, validation

        missing = request.question_count - len(quiz.questions)
        if missing <= 0:
            return quiz, validation

        logger.info("Repair: requesting %d additional question(s).", missing)

        repair_prompt = (
            f"The previous quiz on '{request.topic}' (Grade {request.grade}) was missing "
            f"{missing} question(s). Generate exactly {missing} additional question(s) "
            f"of the same style, difficulty ({request.difficulty}), and Bloom level(s) "
            f"({request.bloom_levels or 'any'}). "
            f"Return ONLY a JSON object with a single key 'questions' containing an array."
        )

        try:
            raw = await self._llm.generate_text(repair_prompt)
            extra_data = self._parse_llm_response(raw)
            extra_raw = extra_data.get("questions", [])
            start_idx = len(quiz.questions) + 1
            for j, item in enumerate(extra_raw[:missing]):
                try:
                    q = Question(
                        id=f"q{start_idx + j}",
                        question=item.get("question", ""),
                        type=item.get("type", request.question_types[0]),
                        difficulty=item.get("difficulty", request.difficulty),
                        bloom_level=item.get("bloom_level", "remember"),
                        options=item.get("options", []),
                        correct_answer=item.get("correct_answer", ""),
                        explanation=item.get("explanation", ""),
                    )
                    quiz.questions.append(q)
                except Exception as exc:
                    logger.warning("Repair: skipping malformed question: %s", exc)

            quiz.question_count = len(quiz.questions)
        except Exception as exc:
            logger.warning("Repair attempt failed: %s", exc)

        final_validation = self._validator.validate(quiz, expected_count=request.question_count)
        return quiz, final_validation
