"""
Deterministic Lesson Plan Validator.
TeachMate AI - Person 2 (Lesson Planner + Simplification AI).

CRITICAL PRINCIPLE:
This validator performs deterministic structural, completeness, and duration checks.
It does NOT claim to verify factual correctness. Factual grounding is supported
by RAG curriculum context, and final verification rests with the educator.
"""

from typing import List, Optional, Set, Tuple
from backend.models.lesson_models import (
    CurriculumChunk,
    LessonPlan,
    LessonValidationResult,
    SourceUsed,
)


class LessonValidator:
    """
    Validates generated LessonPlan structures deterministically.
    """

    DEFAULT_TOLERANCE_MINUTES = 10
    DEFAULT_TOLERANCE_PERCENT = 0.25

    @classmethod
    def reconcile_sources(
        cls,
        curriculum_context: Optional[List[CurriculumChunk]] = None,
        model_sources: Optional[List[SourceUsed]] = None,
    ) -> List[SourceUsed]:
        """
        Deduplicates and reconciles source references.
        Prioritizes verified sources from the retrieved curriculum context
        to prevent LLM hallucination of citations/page numbers.
        """
        seen_keys: Set[Tuple[str, Optional[int]]] = set()
        reconciled: List[SourceUsed] = []

        # 1. Primary ground truth: curriculum context chunks supplied by RAG
        if curriculum_context:
            for chunk in curriculum_context:
                key = (chunk.source.strip(), chunk.page_number)
                if key not in seen_keys and chunk.source.strip():
                    seen_keys.add(key)
                    reconciled.append(
                        SourceUsed(source=chunk.source.strip(), page_number=chunk.page_number)
                    )

        # 2. Secondary fallback: if model supplied valid sources not already seen
        if model_sources:
            for src in model_sources:
                key = (src.source.strip(), src.page_number)
                if key not in seen_keys and src.source.strip():
                    seen_keys.add(key)
                    reconciled.append(
                        SourceUsed(source=src.source.strip(), page_number=src.page_number)
                    )

        return reconciled

    @classmethod
    def validate(
        cls,
        lesson: LessonPlan,
        requested_duration_minutes: int,
        curriculum_context: Optional[List[CurriculumChunk]] = None,
    ) -> LessonValidationResult:
        """
        Runs comprehensive deterministic checks on a LessonPlan.
        """
        checks = {}
        warnings: List[str] = []

        # Check 1: Title
        checks["has_title"] = bool(lesson.title and lesson.title.strip())

        # Check 2: Subject & Grade
        checks["has_subject"] = bool(lesson.subject and lesson.subject.strip())
        checks["has_valid_grade"] = 1 <= lesson.grade <= 12

        # Check 3: Objectives
        valid_objectives = [o.strip() for o in lesson.objectives if o and o.strip()]
        checks["has_objectives"] = len(valid_objectives) > 0
        if len(valid_objectives) == 0:
            warnings.append("No valid learning objectives found.")

        # Check 4: Major content sections
        checks["has_introduction"] = bool(lesson.introduction and lesson.introduction.content.strip())
        checks["has_explanation"] = bool(lesson.explanation and lesson.explanation.content.strip())
        checks["has_recap"] = bool(lesson.recap and lesson.recap.content.strip())

        if not checks["has_introduction"]:
            warnings.append("Introduction section is missing or empty.")
        if not checks["has_explanation"]:
            warnings.append("Core explanation section is missing or empty.")
        if not checks["has_recap"]:
            warnings.append("Recap section is missing or empty.")

        # Check 5: Key points
        valid_key_points = [k.strip() for k in lesson.key_points if k and k.strip()]
        checks["has_key_points"] = len(valid_key_points) > 0
        if len(valid_key_points) == 0:
            warnings.append("No key summary points provided.")

        # Check 6: Section Durations are positive
        intro_dur = lesson.introduction.duration_minutes if lesson.introduction else 0
        exp_dur = lesson.explanation.duration_minutes if lesson.explanation else 0
        recap_dur = lesson.recap.duration_minutes if lesson.recap else 0
        total_dur = lesson.total_duration_minutes

        checks["durations_positive"] = (
            intro_dur > 0 and exp_dur > 0 and recap_dur > 0 and total_dur > 0
        )
        if not checks["durations_positive"]:
            warnings.append("One or more section durations are zero or negative.")

        # Check 7: Duration Consistency & Tolerance
        section_sum = intro_dur + exp_dur + recap_dur
        allowed_tolerance = max(
            cls.DEFAULT_TOLERANCE_MINUTES,
            int(requested_duration_minutes * cls.DEFAULT_TOLERANCE_PERCENT)
        )
        duration_diff = abs(section_sum - requested_duration_minutes)
        checks["duration_reasonable"] = duration_diff <= allowed_tolerance

        if not checks["duration_reasonable"]:
            warnings.append(
                f"Planned section timings total {section_sum} min, which differs from requested "
                f"{requested_duration_minutes} min by {duration_diff} min (exceeding tolerance of ±{allowed_tolerance} min)."
            )

        # Check 8: Curriculum Context & Sources
        has_context_input = bool(curriculum_context and len(curriculum_context) > 0)
        has_sources_output = bool(lesson.sources_used and len(lesson.sources_used) > 0)

        if has_context_input:
            checks["sources_grounded"] = has_sources_output
            if not has_sources_output:
                warnings.append("Curriculum context was provided but no sources are cited.")
        else:
            checks["sources_grounded"] = True  # Not applicable if no context provided

        # Critical failure conditions for valid flag:
        # Title, subject, grade, objectives, explanation, and positive durations are required.
        critical_passes = (
            checks["has_title"]
            and checks["has_subject"]
            and checks["has_valid_grade"]
            and checks["has_objectives"]
            and checks["has_explanation"]
            and checks["durations_positive"]
        )

        return LessonValidationResult(
            valid=critical_passes,
            checks=checks,
            warnings=warnings,
            disclaimer="Structural and duration validation only. Does not guarantee factual correctness; teacher review required."
        )
