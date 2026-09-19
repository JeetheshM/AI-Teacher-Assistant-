"""
Unit Tests for Activity Service (Person 6)
"""

import asyncio
import json
import pytest
from backend.models.activity_models import (
    ActivityGenerationRequest,
    CurriculumChunk,
)
from backend.services.activity_service import ActivityService


class MockLLMService:
    """Mock LLM implementation for tests without API charges."""

    def __init__(self, response_text: str = "", fail: bool = False):
        self.response_text = response_text
        self.fail = fail
        self.last_prompt = None

    async def generate(self, prompt: str, **kwargs) -> str:
        self.last_prompt = prompt
        if self.fail:
            raise RuntimeError("API connection timeout")
        return self.response_text


def test_generate_activity_success():
    sample_payload = {
        "title": "Photosynthesis Recipe Challenge",
        "activity_type": "group",
        "objective": "Identify the inputs and outputs of photosynthesis.",
        "duration_minutes": 15,
        "group_size": 4,
        "materials": ["Paper", "Markers"],
        "setup": "Arrange tables in groups of 4.",
        "instructions": [
            "Draw a leaf in the center.",
            "Draw yellow arrows for sunlight and blue for water.",
            "Draw red arrows for glucose output.",
            "Share with the class."
        ],
        "teacher_role": "Circulate and guide students.",
        "student_role": "Collaborate on the diagram.",
        "expected_outcome": "Finished leaf diagram.",
        "assessment_method": "Quick group share.",
        "safety_notes": [],
        "adaptations": ["Provide outline template."],
        "sources_used": []
    }
    
    # Wrap in markdown code fence to verify extraction
    raw_response = f"```json\n{json.dumps(sample_payload)}\n```"
    mock_llm = MockLLMService(response_text=raw_response)
    service = ActivityService(llm_service=mock_llm)

    req = ActivityGenerationRequest(
        subject="Science",
        topic="Photosynthesis",
        grade=8,
        duration_minutes=15,
        difficulty="intermediate",
        curriculum_context=[
            CurriculumChunk(
                content="Chlorophyll absorbs sunlight in chloroplasts.",
                source="CBSE_Science.pdf",
                page_number=82,
                chunk_id="chunk_1"
            )
        ]
    )

    activity = asyncio.run(service.generate_activity(req))

    assert activity.title == "Photosynthesis Recipe Challenge"
    assert activity.duration_minutes == 15
    assert len(activity.instructions) == 4
    # Check that trusted sources from context were attached
    assert len(activity.sources_used) == 1
    assert activity.sources_used[0].source == "CBSE_Science.pdf"
    assert activity.sources_used[0].page_number == 82
    # Check prompt injection security tag in generated prompt
    assert "<CURRICULUM_REFERENCE>" in mock_llm.last_prompt


def test_generate_activity_malformed_json_handled():
    mock_llm = MockLLMService(response_text="Sorry, I cannot format this as JSON.")
    service = ActivityService(llm_service=mock_llm)

    req = ActivityGenerationRequest(
        subject="Science",
        topic="Photosynthesis",
        grade=8,
        duration_minutes=15,
    )

    with pytest.raises(ValueError) as excinfo:
        asyncio.run(service.generate_activity(req))
    assert "malformed JSON" in str(excinfo.value)


def test_generate_activity_llm_failure_handled():
    mock_llm = MockLLMService(fail=True)
    service = ActivityService(llm_service=mock_llm)

    req = ActivityGenerationRequest(
        subject="Science",
        topic="Photosynthesis",
        grade=8,
        duration_minutes=15,
    )

    with pytest.raises(RuntimeError) as excinfo:
        asyncio.run(service.generate_activity(req))
    assert "LLM layer" in str(excinfo.value)
