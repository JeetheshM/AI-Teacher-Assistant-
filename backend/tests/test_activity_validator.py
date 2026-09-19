"""
Unit Tests for Activity Validator (Person 6)
"""

import pytest
from backend.models.activity_models import (
    ActivityGenerationRequest,
    ActivityResponse,
    CurriculumChunk,
    SourceReference,
)
from backend.validators.activity_validator import ActivityValidator


def test_valid_request_passes():
    req = ActivityGenerationRequest(
        subject="Science",
        topic="Photosynthesis",
        grade=8,
        duration_minutes=15,
        difficulty="intermediate",
        class_size=30,
        learning_objective="Understand how plants make food",
    )
    result = ActivityValidator.validate_request(req)
    assert result.valid is True
    assert len(result.errors) == 0


def test_empty_topic_rejected():
    with pytest.raises(ValueError):
        ActivityGenerationRequest(
            subject="Science",
            topic="   ",
            grade=8,
            duration_minutes=15,
        )


def test_invalid_grade_rejected():
    with pytest.raises(ValueError):
        ActivityGenerationRequest(
            subject="Science",
            topic="Photosynthesis",
            grade=0,
            duration_minutes=15,
        )


def test_valid_activity_response_passes():
    activity = ActivityResponse(
        title="Photosynthesis Recipe Challenge",
        activity_type="group",
        objective="Identify the inputs and outputs of photosynthesis",
        duration_minutes=15,
        group_size=4,
        materials=["Paper", "Markers"],
        setup="Arrange desks in clusters of 4",
        instructions=["Draw leaf", "Label inputs and outputs", "Explain to class"],
        teacher_role="Facilitate groups and guide misconceptions",
        student_role="Collaborate and draw diagrams",
        expected_outcome="Annotated diagram of inputs and outputs",
        assessment_method="30-second group explanation",
        safety_notes=[],
        adaptations=["Provide leaf outline for support"],
        sources_used=[SourceReference(source="Science.pdf", page_number=82)],
    )
    result = ActivityValidator.validate_activity(activity)
    assert result.valid is True
    assert result.checks["title_present"] is True
    assert result.checks["instructions_present"] is True
    assert result.checks["duration_positive"] is True


def test_missing_title_fails():
    activity = ActivityResponse(
        title="   ",
        activity_type="group",
        objective="Identify inputs",
        duration_minutes=15,
        setup="Arrange desks",
        instructions=["Step 1", "Step 2"],
        teacher_role="Guide",
        student_role="Build",
        expected_outcome="Diagram",
        assessment_method="Exit ticket",
    )
    result = ActivityValidator.validate_activity(activity)
    assert result.valid is False
    assert any("title" in err.lower() for err in result.errors)


def test_missing_instructions_fails():
    activity = ActivityResponse(
        title="Plant Model",
        activity_type="individual",
        objective="Identify inputs",
        duration_minutes=10,
        setup="Distribute worksheets",
        instructions=[],
        teacher_role="Monitor",
        student_role="Write",
        expected_outcome="Completed worksheet",
        assessment_method="Check sheet",
    )
    result = ActivityValidator.validate_activity(activity)
    assert result.valid is False
    assert any("instructions" in err.lower() for err in result.errors)


def test_duration_discrepancy_warning():
    req = ActivityGenerationRequest(
        subject="Science",
        topic="Photosynthesis",
        grade=8,
        duration_minutes=15,
    )
    activity = ActivityResponse(
        title="Long Lab",
        activity_type="experiment",
        objective="Analyze rate of photosynthesis",
        duration_minutes=60,
        setup="Setup beakers",
        instructions=["Step 1", "Step 2"],
        teacher_role="Guide",
        student_role="Measure",
        expected_outcome="Chart",
        assessment_method="Report",
    )
    result = ActivityValidator.validate_activity(activity, req)
    # Remains valid structurally but produces a warning
    assert result.valid is True
    assert len(result.warnings) > 0
    assert any("duration" in w.lower() for w in result.warnings)


def test_source_deduplication():
    req = ActivityGenerationRequest(
        subject="Science",
        topic="Photosynthesis",
        grade=8,
        duration_minutes=15,
        curriculum_context=[
            CurriculumChunk(content="Chunk 1", source="Textbook.pdf", page_number=82, chunk_id="c1"),
            CurriculumChunk(content="Chunk 2", source="Textbook.pdf", page_number=82, chunk_id="c2"),
            CurriculumChunk(content="Chunk 3", source="Textbook.pdf", page_number=84, chunk_id="c3"),
        ],
    )
    sources = ActivityValidator.extract_and_deduplicate_sources(req)
    assert len(sources) == 2
    assert sources[0].source == "Textbook.pdf" and sources[0].page_number == 82
    assert sources[1].source == "Textbook.pdf" and sources[1].page_number == 84
