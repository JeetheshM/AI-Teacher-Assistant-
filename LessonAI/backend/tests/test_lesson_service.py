"""
Unit tests for LessonService and SimplificationService.
TeachMate AI - Person 2 (Lesson Planner + Simplification AI).

Tests run entirely offline using MockLLMService with zero paid API calls.
"""

import asyncio
import unittest
from backend.models.lesson_models import (
    ContentTransformationRequest,
    CurriculumChunk,
    LessonAIError,
    LessonGenerationRequest,
    LessonValidationError,
    LLMResponseError,
    TransformationMode,
)
from backend.mocks.mock_llm_service import MockLLMService
from backend.prompts.lesson_prompt import LESSON_PROMPT_VERSION
from backend.prompts.simplify_prompt import SIMPLIFY_PROMPT_VERSION
from backend.services.lesson_service import LessonService
from backend.services.simplification_service import SimplificationService


class TestLessonService(unittest.TestCase):
    """Test suite covering lesson generation, prompt versioning, fallbacks, and transformations."""

    def setUp(self):
        self.mock_llm = MockLLMService()
        self.lesson_service = LessonService(self.mock_llm)
        self.simplification_service = SimplificationService(self.mock_llm)

    def test_valid_lesson_request_produces_structured_lesson(self):
        """TEST 1: Valid lesson request produces valid structured lesson."""
        request = LessonGenerationRequest(
            subject="Science",
            topic="Photosynthesis",
            grade=8,
            duration_minutes=45,
            difficulty="intermediate",
            learning_objective="Understand how plants make food using sunlight, carbon dioxide and water.",
            curriculum_context=[
                CurriculumChunk(
                    content="Green plants prepare their own food using carbon dioxide and water in the presence of sunlight and chlorophyll.",
                    source="CBSE_Science.pdf",
                    page_number=82
                )
            ]
        )

        response = asyncio.run(self.lesson_service.generate_lesson(request))

        self.assertIsNotNone(response.lesson)
        self.assertEqual(response.lesson.subject, "Science")
        self.assertEqual(response.lesson.grade, 8)
        self.assertEqual(response.lesson.difficulty, "intermediate")
        self.assertEqual(response.lesson.total_duration_minutes, 45)
        self.assertGreater(len(response.lesson.objectives), 0)
        self.assertIsNotNone(response.lesson.introduction.content)
        self.assertIsNotNone(response.lesson.explanation.content)
        self.assertIsNotNone(response.lesson.recap.content)
        self.assertGreater(len(response.lesson.key_points), 0)
        self.assertGreater(len(response.lesson.common_misconceptions), 0)
        self.assertTrue(response.validation.valid)
        self.assertEqual(response.prompt_version, LESSON_PROMPT_VERSION)

    def test_empty_topic_rejected(self):
        """TEST 2: Empty topic rejected."""
        # Pydantic validation error or service validation error
        with self.assertRaises((ValueError, LessonValidationError)):
            LessonGenerationRequest(
                subject="Science",
                topic="   ",
                grade=8,
                duration_minutes=45,
                difficulty="intermediate",
                learning_objective="Learn stuff"
            )

    def test_empty_subject_rejected(self):
        """Empty subject rejected."""
        with self.assertRaises((ValueError, LessonValidationError)):
            LessonGenerationRequest(
                subject="",
                topic="Photosynthesis",
                grade=8,
                duration_minutes=45,
                difficulty="intermediate",
                learning_objective="Learn stuff"
            )

    def test_invalid_grade_rejected(self):
        """Invalid grade outside 1-12 rejected."""
        with self.assertRaises(ValueError):
            LessonGenerationRequest(
                subject="Science",
                topic="Photosynthesis",
                grade=0,  # Invalid
                duration_minutes=45,
                difficulty="intermediate",
                learning_objective="Learn stuff"
            )

    def test_invalid_difficulty_rejected(self):
        """Unrecognized difficulty level rejected."""
        with self.assertRaises(ValueError):
            LessonGenerationRequest(
                subject="Science",
                topic="Photosynthesis",
                grade=8,
                duration_minutes=45,
                difficulty="impossible",  # Invalid
                learning_objective="Learn stuff"
            )

    def test_simplification_mode_works(self):
        """TEST 5: Simplification mode works."""
        req = ContentTransformationRequest(
            content="Photosynthesis converts light energy into chemical energy through biochemical reactions.",
            subject="Science",
            topic="Photosynthesis",
            grade=8,
            mode=TransformationMode.SIMPLIFY
        )
        response = asyncio.run(self.simplification_service.transform(req))

        self.assertEqual(response.mode, TransformationMode.SIMPLIFY)
        self.assertIn("Plants make their own food", response.transformed_content)
        self.assertEqual(response.grade, 8)

    def test_younger_level_mode_works(self):
        """TEST 11: Younger-level transformation mode works."""
        req = ContentTransformationRequest(
            content="Photosynthesis converts light energy into chemical energy through biochemical reactions.",
            subject="Science",
            topic="Photosynthesis",
            grade=8,
            mode=TransformationMode.YOUNGER_LEVEL
        )
        response = asyncio.run(self.simplification_service.transform(req))

        self.assertEqual(response.mode, TransformationMode.YOUNGER_LEVEL)
        self.assertIn("sun chef", response.transformed_content.lower())

    def test_analogy_mode_works(self):
        """TEST 6: Analogy mode works."""
        req = ContentTransformationRequest(
            content="Photosynthesis converts light energy into chemical energy through biochemical reactions.",
            subject="Science",
            topic="Photosynthesis",
            grade=8,
            mode=TransformationMode.ANALOGY
        )
        response = asyncio.run(self.simplification_service.transform(req))

        self.assertEqual(response.mode, TransformationMode.ANALOGY)
        self.assertIn("kitchen", response.transformed_content.lower())
        self.assertIn("ingredients", response.transformed_content.lower())

    def test_real_world_example_mode_works(self):
        """TEST 7: Real-world example mode works."""
        req = ContentTransformationRequest(
            content="Photosynthesis releases oxygen gas into the environment.",
            subject="Science",
            topic="Photosynthesis",
            grade=8,
            mode=TransformationMode.REAL_WORLD_EXAMPLE
        )
        response = asyncio.run(self.simplification_service.transform(req))

        self.assertEqual(response.mode, TransformationMode.REAL_WORLD_EXAMPLE)
        self.assertIn("bubbles", response.transformed_content.lower())

    def test_malformed_llm_response_handled_gracefully(self):
        """TEST 8: Malformed LLM response handled gracefully without unhandled crashes."""
        error_llm = MockLLMService(force_error=RuntimeError("JSON Decode error: Unterminated string"))
        failing_service = LessonService(error_llm)

        request = LessonGenerationRequest(
            subject="Science",
            topic="Photosynthesis",
            grade=8,
            duration_minutes=45,
            difficulty="intermediate",
            learning_objective="Understand photosynthesis."
        )

        with self.assertRaises(LLMResponseError) as ctx:
            asyncio.run(failing_service.generate_lesson(request))

        self.assertIn("Failed to generate structured lesson plan", str(ctx.exception))

    def test_curriculum_source_metadata_preserved_and_deduplicated(self):
        """TEST 9 & 10: Curriculum source metadata preserved and duplicate sources removed."""
        request = LessonGenerationRequest(
            subject="Science",
            topic="Photosynthesis",
            grade=8,
            duration_minutes=45,
            difficulty="intermediate",
            learning_objective="Understand how plants make food.",
            curriculum_context=[
                CurriculumChunk(content="Text 1", source="CBSE_Science.pdf", page_number=82),
                CurriculumChunk(content="Text 2 (Duplicate)", source="CBSE_Science.pdf", page_number=82),
                CurriculumChunk(content="Text 3 (Different page)", source="CBSE_Science.pdf", page_number=84),
            ]
        )

        response = asyncio.run(self.lesson_service.generate_lesson(request))

        # Check preserved sources
        sources = response.lesson.sources_used
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0].source, "CBSE_Science.pdf")
        self.assertEqual(sources[0].page_number, 82)
        self.assertEqual(sources[1].source, "CBSE_Science.pdf")
        self.assertEqual(sources[1].page_number, 84)

    def test_no_curriculum_context_generates_clean_fallback(self):
        """TEST 12: Lesson generation with no curriculum context functions properly."""
        request = LessonGenerationRequest(
            subject="History",
            topic="Industrial Revolution",
            grade=9,
            duration_minutes=40,
            difficulty="intermediate",
            learning_objective="Understand major technological shifts in 18th century Britain."
        )

        response = asyncio.run(self.lesson_service.generate_lesson(request))
        self.assertTrue(response.validation.valid)
        self.assertEqual(response.lesson.subject, "Science")  # mock returns default
        self.assertEqual(response.prompt_version, "lesson_v1")

    def test_prompt_version_constants(self):
        """Verify prompt version constants for observability traceability."""
        self.assertEqual(LESSON_PROMPT_VERSION, "lesson_v1")
        self.assertEqual(SIMPLIFY_PROMPT_VERSION, "simplify_v1")


if __name__ == "__main__":
    unittest.main()
