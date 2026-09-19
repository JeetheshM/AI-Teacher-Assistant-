"""
Unit Tests for Export Service (Person 6)
"""

import os
import tempfile
import pytest
from backend.services.export_service import ExportService


@pytest.fixture
def export_service():
    return ExportService()


@pytest.fixture
def sample_package():
    return {
        "subject": "Science",
        "topic": "Photosynthesis",
        "grade": 8,
        "duration_minutes": 45,
        "difficulty": "intermediate",
        "learning_objective": "Understand how plants convert sunlight to food",
        "lesson": {
            "title": "Photosynthesis Masterclass",
            "subject": "Science",
            "topic": "Photosynthesis",
            "grade": 8,
            "objectives": ["Identify inputs and outputs", "Explain chlorophyll role"],
            "introduction": {"duration_minutes": 5, "content": "Ask students how plants eat."},
            "explanation": {"duration_minutes": 15, "content": "Photosynthesis takes CO2 and water to make glucose."},
            "key_points": ["Chlorophyll traps light", "Glucose is food"],
            "examples": ["Leaf is a kitchen"],
            "common_misconceptions": ["Plants get food from soil (false)"],
            "recap": "Photosynthesis powers the biosphere.",
        },
        "materials": {
            "activity": {
                "title": "Photosynthesis Recipe Challenge",
                "activity_type": "group",
                "duration_minutes": 15,
                "group_size": 4,
                "objective": "Map inputs and outputs",
                "materials": ["Paper", "Markers"],
                "setup": "Cluster desks",
                "instructions": ["Draw plant", "Label sunlight, CO2, H2O", "Label glucose, O2"],
                "teacher_role": "Guide students",
                "student_role": "Collaborate",
                "expected_outcome": "Poster",
                "assessment_method": "30s share",
                "safety_notes": [],
                "adaptations": ["Provide outline"],
            }
        },
        "quiz": {
            "title": "Photosynthesis Formative Quiz",
            "questions": [
                {
                    "question": "Which pigment absorbs sunlight?",
                    "type": "mcq",
                    "bloom_level": "remember",
                    "options": ["Chlorophyll", "Hemoglobin", "Melanin"],
                    "correct_answer": "Chlorophyll",
                    "explanation": "Chlorophyll absorbs light in chloroplasts."
                },
                {
                    "question": "Oxygen is produced during photosynthesis.",
                    "type": "true_false",
                    "bloom_level": "understand",
                    "options": ["True", "False"],
                    "correct_answer": "True",
                    "explanation": "Oxygen is a product released into the atmosphere."
                }
            ]
        },
        "sources": [
            {"source": "CBSE_Science.pdf", "page_number": 82},
            {"source": "CBSE_Science.pdf", "page_number": 84}
        ]
    }


def test_export_full_package(export_service, sample_package):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        temp_pdf = tmp.name

    try:
        out_path = export_service.generate_pdf(sample_package, output_path=temp_pdf)
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 1000
    finally:
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)


def test_export_partial_package_without_quiz(export_service, sample_package):
    pkg = dict(sample_package)
    del pkg["quiz"]

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        temp_pdf = tmp.name

    try:
        out_path = export_service.generate_pdf(pkg, output_path=temp_pdf)
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 500
    finally:
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)


def test_export_partial_package_without_activity(export_service, sample_package):
    pkg = dict(sample_package)
    del pkg["materials"]

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        temp_pdf = tmp.name

    try:
        out_path = export_service.generate_pdf(pkg, output_path=temp_pdf)
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 500
    finally:
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)


def test_export_partial_package_without_sources(export_service, sample_package):
    pkg = dict(sample_package)
    del pkg["sources"]

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        temp_pdf = tmp.name

    try:
        out_path = export_service.generate_pdf(pkg, output_path=temp_pdf)
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 500
    finally:
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)


def test_sanitize_filename(export_service):
    raw_name = "../../etc/passwd..photosynthesis//grade8"
    sanitized = export_service.sanitize_filename(raw_name)
    assert "/" not in sanitized
    assert ".." not in sanitized
