"""
End-to-End Demo Smoke Test (Person 6)

Verifies that all fallback demo datasets (lesson, quiz, activity, full package)
are valid, loadable, pass validation, and can be exported directly to PDF.
"""

import os
import json
import tempfile
import pytest
from backend.models.activity_models import ActivityResponse, ActivityGenerationRequest
from backend.validators.activity_validator import ActivityValidator
from backend.services.export_service import ExportService


def test_fallback_activity_is_valid():
    filepath = os.path.join(os.getcwd(), "demo", "fallback_activity.json")
    assert os.path.exists(filepath), f"Missing {filepath}"

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    activity = ActivityResponse(**data)
    req = ActivityGenerationRequest(
        subject="Science",
        topic="Photosynthesis",
        grade=8,
        duration_minutes=15,
        difficulty="intermediate",
    )
    result = ActivityValidator.validate_activity(activity, req)
    assert result.valid is True
    assert len(result.errors) == 0


def test_fallback_lesson_structure():
    filepath = os.path.join(os.getcwd(), "demo", "fallback_lesson.json")
    assert os.path.exists(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["topic"] == "Photosynthesis"
    assert data["grade"] == 8
    assert "introduction" in data
    assert "explanation" in data
    assert "key_points" in data
    assert "common_misconceptions" in data


def test_fallback_quiz_structure():
    filepath = os.path.join(os.getcwd(), "demo", "fallback_quiz.json")
    assert os.path.exists(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "questions" in data
    assert len(data["questions"]) == 5
    for q in data["questions"]:
        assert "question" in q
        assert "correct_answer" in q
        assert "explanation" in q
        if q["type"] == "mcq":
            assert q["correct_answer"] in q["options"]


def test_fallback_teaching_package_export():
    filepath = os.path.join(os.getcwd(), "demo", "fallback_teaching_package.json")
    assert os.path.exists(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        package = json.load(f)

    export_service = ExportService()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        temp_pdf = tmp.name

    try:
        out_path = export_service.generate_pdf(package, output_path=temp_pdf)
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 2000
    finally:
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)
