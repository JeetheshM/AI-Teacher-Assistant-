"""
Classroom Activity Validator (Person 6)

Deterministic structural, completeness, and constraint validation for activities.
Ensures consistency with request parameters and safety guidelines.
"""

from typing import Optional, List
from backend.models.activity_models import (
    ActivityGenerationRequest,
    ActivityResponse,
    ActivityValidationResult,
    SourceReference,
)


class ActivityValidator:
    """
    Deterministic validator for classroom activities.
    Checks structural completeness, instruction clarity, duration consistency,
    and material reasonableness.
    """

    @staticmethod
    def validate_request(request: ActivityGenerationRequest) -> ActivityValidationResult:
        """Validates incoming teacher activity generation request."""
        checks = {
            "subject_valid": bool(request.subject and request.subject.strip()),
            "topic_valid": bool(request.topic and request.topic.strip()),
            "grade_valid": 1 <= request.grade <= 12,
            "duration_valid": 1 <= request.duration_minutes <= 120,
            "class_size_valid": request.class_size is None or (1 <= request.class_size <= 100),
        }
        errors = []
        warnings = []

        if not checks["subject_valid"]:
            errors.append("Subject is required and cannot be blank.")
        if not checks["topic_valid"]:
            errors.append("Topic is required and cannot be blank.")
        if not checks["grade_valid"]:
            errors.append(f"Grade {request.grade} is out of valid range (1-12).")
        if not checks["duration_valid"]:
            errors.append(f"Duration {request.duration_minutes} minutes must be between 1 and 120 minutes.")
        if not checks["class_size_valid"]:
            warnings.append(f"Class size {request.class_size} is unusual; standard range is 1-100.")

        is_valid = len(errors) == 0
        return ActivityValidationResult(
            valid=is_valid,
            checks=checks,
            warnings=warnings,
            errors=errors,
        )

    @staticmethod
    def validate_activity(
        activity: ActivityResponse,
        request: Optional[ActivityGenerationRequest] = None,
    ) -> ActivityValidationResult:
        """
        Performs deterministic quality and structural checks on generated ActivityResponse.
        """
        checks = {}
        errors = []
        warnings = []

        # 1. Title validation
        checks["title_present"] = bool(activity.title and activity.title.strip())
        if not checks["title_present"]:
            errors.append("Activity title is missing or empty.")

        # 2. Objective validation
        checks["objective_present"] = bool(activity.objective and activity.objective.strip())
        if not checks["objective_present"]:
            errors.append("Activity objective is missing or empty.")

        # 3. Instructions validation
        has_instructions = isinstance(activity.instructions, list) and len(activity.instructions) > 0
        checks["instructions_present"] = has_instructions
        if not has_instructions:
            errors.append("Step-by-step instructions are missing or empty.")
        elif len(activity.instructions) < 2:
            warnings.append("Activity has fewer than 2 instruction steps; more detail is recommended.")

        # 4. Duration validation
        duration_positive = activity.duration_minutes > 0
        checks["duration_positive"] = duration_positive
        if not duration_positive:
            errors.append(f"Activity duration must be greater than 0, got {activity.duration_minutes}.")

        if request is not None:
            # Check duration variance: within ±50% or ±10 minutes
            duration_diff = abs(activity.duration_minutes - request.duration_minutes)
            checks["duration_reasonable"] = duration_diff <= max(10, request.duration_minutes * 0.5)
            if not checks["duration_reasonable"]:
                warnings.append(
                    f"Generated duration ({activity.duration_minutes}m) differs significantly from requested ({request.duration_minutes}m)."
                )
        else:
            checks["duration_reasonable"] = duration_positive

        # 5. Assessment method validation
        checks["assessment_present"] = bool(activity.assessment_method and activity.assessment_method.strip())
        if not checks["assessment_present"]:
            warnings.append("Formative assessment method is missing.")

        # 6. Expected outcome validation
        checks["expected_outcome_present"] = bool(activity.expected_outcome and activity.expected_outcome.strip())
        if not checks["expected_outcome_present"]:
            warnings.append("Expected learning outcome is missing.")

        # 7. Materials check
        checks["materials_valid"] = isinstance(activity.materials, list)
        if not checks["materials_valid"]:
            errors.append("Materials must be a list of items.")

        # 8. Setup and Roles
        checks["setup_present"] = bool(activity.setup and activity.setup.strip())
        checks["teacher_role_present"] = bool(activity.teacher_role and activity.teacher_role.strip())
        checks["student_role_present"] = bool(activity.student_role and activity.student_role.strip())

        # 9. Group size check
        if activity.activity_type == "group":
            if activity.group_size is not None and activity.group_size < 2:
                warnings.append("Group activity has group_size < 2; typically 3-5 students is ideal.")
        
        is_valid = len(errors) == 0
        return ActivityValidationResult(
            valid=is_valid,
            checks=checks,
            warnings=warnings,
            errors=errors,
        )

    @staticmethod
    def extract_and_deduplicate_sources(request: ActivityGenerationRequest) -> List[SourceReference]:
        """
        Derives trusted source metadata directly from Person 4's curriculum_context.
        Deduplicates sources by (source, page_number).
        """
        if not request.curriculum_context:
            return []

        seen = set()
        sources: List[SourceReference] = []

        for chunk in request.curriculum_context:
            key = (chunk.source, chunk.page_number)
            if key not in seen:
                seen.add(key)
                sources.append(
                    SourceReference(
                        source=chunk.source,
                        page_number=chunk.page_number,
                    )
                )

        return sources
