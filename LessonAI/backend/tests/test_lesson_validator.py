"""
Unit tests for deterministic LessonValidator.
TeachMate AI - Person 2 (Lesson Planner + Simplification AI).
"""

import unittest
from backend.models.lesson_models import (
    CurriculumChunk,
    ExampleItem,
    LessonPlan,
    MisconceptionItem,
    SourceUsed,
    TimedContent,
)
from backend.validators.lesson_validator import LessonValidator


class TestLessonValidator(unittest.TestCase):
    """Tests for deterministic validation, duration tolerance, and source reconciliation."""

    def setUp(self):
        self.sample_lesson = LessonPlan(
            title="Understanding Photosynthesis",
            subject="Science",
            grade=8,
            difficulty="intermediate",
            total_duration_minutes=45,
            objectives=["Understand inputs and outputs of photosynthesis."],
            prerequisites=["Basic plant cell structures."],
            introduction=TimedContent(duration_minutes=5, content="Hook question."),
            explanation=TimedContent(duration_minutes=25, content="Detailed explanation."),
            examples=[ExampleItem(title="Kitchen Analogy", description="Sunlight as power.")],
            key_points=["Chlorophyll absorbs light.", "Glucose is stored food."],
            common_misconceptions=[
                MisconceptionItem(
                    misconception="Plants eat soil.",
                    correction="Plants make food from CO2 and water."
                )
            ],
            recap=TimedContent(duration_minutes=15, content="Quick recap quiz."),
            teacher_tips=["Draw on board."],
            sources_used=[SourceUsed(source="CBSE_Science.pdf", page_number=82)]
        )

    def test_valid_lesson_passes_validation(self):
        """Verify that a well-structured lesson plan passes all deterministic checks."""
        result = LessonValidator.validate(
            lesson=self.sample_lesson,
            requested_duration_minutes=45,
            curriculum_context=[
                CurriculumChunk(content="Text", source="CBSE_Science.pdf", page_number=82)
            ]
        )
        self.assertTrue(result.valid)
        self.assertTrue(result.checks["has_title"])
        self.assertTrue(result.checks["has_objectives"])
        self.assertTrue(result.checks["has_explanation"])
        self.assertTrue(result.checks["duration_reasonable"])
        self.assertTrue(result.checks["sources_grounded"])
        self.assertEqual(len(result.warnings), 0)

    def test_missing_objectives_fails_validation(self):
        """TEST 3: Lesson with no objectives fails validation."""
        lesson_no_objs = self.sample_lesson.model_copy(deep=True)
        lesson_no_objs.objectives = []

        result = LessonValidator.validate(
            lesson=lesson_no_objs,
            requested_duration_minutes=45
        )
        self.assertFalse(result.valid)
        self.assertFalse(result.checks["has_objectives"])
        self.assertIn("No valid learning objectives found.", result.warnings)

    def test_duration_mismatch_creates_warning(self):
        """TEST 4: Duration mismatch creates warning according to chosen tolerance."""
        lesson_long = self.sample_lesson.model_copy(deep=True)
        # 5 + 60 + 15 = 80 min (requested 45 min -> diff is 35 min, > max(10, 11 min))
        lesson_long.explanation.duration_minutes = 60

        result = LessonValidator.validate(
            lesson=lesson_long,
            requested_duration_minutes=45
        )
        self.assertFalse(result.checks["duration_reasonable"])
        self.assertTrue(any("differs from requested 45 min" in w for w in result.warnings))

    def test_duration_within_tolerance_passes(self):
        """Verify that reasonable duration deviation within tolerance passes without warning."""
        lesson_close = self.sample_lesson.model_copy(deep=True)
        # 5 + 23 + 14 = 42 min (requested 45 min -> diff is 3 min, well within ±10 min)
        lesson_close.explanation.duration_minutes = 23
        lesson_close.recap.duration_minutes = 14

        result = LessonValidator.validate(
            lesson=lesson_close,
            requested_duration_minutes=45
        )
        self.assertTrue(result.checks["duration_reasonable"])

    def test_negative_or_zero_duration_fails(self):
        """Verify that zero or negative section durations fail validation."""
        lesson_zero = self.sample_lesson.model_copy(deep=True)
        lesson_zero.introduction.duration_minutes = 0

        result = LessonValidator.validate(
            lesson=lesson_zero,
            requested_duration_minutes=45
        )
        self.assertFalse(result.valid)
        self.assertFalse(result.checks["durations_positive"])
        self.assertIn("One or more section durations are zero or negative.", result.warnings)

    def test_duplicate_sources_reconciled(self):
        """TEST 10: Duplicate source metadata removed."""
        chunks = [
            CurriculumChunk(content="Text 1", source="CBSE_Science.pdf", page_number=82),
            CurriculumChunk(content="Text 2", source="CBSE_Science.pdf", page_number=82),
            CurriculumChunk(content="Text 3", source="CBSE_Science.pdf", page_number=84),
            CurriculumChunk(content="Text 4", source="NCERT_Biology.pdf", page_number=12),
        ]
        reconciled = LessonValidator.reconcile_sources(curriculum_context=chunks)
        self.assertEqual(len(reconciled), 3)
        sources_pages = [(s.source, s.page_number) for s in reconciled]
        self.assertEqual(
            sources_pages,
            [
                ("CBSE_Science.pdf", 82),
                ("CBSE_Science.pdf", 84),
                ("NCERT_Biology.pdf", 12),
            ]
        )

    def test_sources_preserved_from_curriculum_context(self):
        """TEST 9: Curriculum source metadata preserved."""
        chunks = [
            CurriculumChunk(content="Chapter 4 text", source="Grade8_Science.pdf", page_number=45)
        ]
        reconciled = LessonValidator.reconcile_sources(curriculum_context=chunks)
        self.assertEqual(len(reconciled), 1)
        self.assertEqual(reconciled[0].source, "Grade8_Science.pdf")
        self.assertEqual(reconciled[0].page_number, 45)

    def test_disclaimer_present(self):
        """Verify that factual correctness is NOT claimed and disclaimer is provided."""
        result = LessonValidator.validate(self.sample_lesson, 45)
        self.assertIn("Structural and duration validation only", result.disclaimer)
        self.assertIn("teacher review required", result.disclaimer)


if __name__ == "__main__":
    unittest.main()
