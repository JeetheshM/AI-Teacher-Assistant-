"""
mock_llm_service.py
-------------------
MockLLMService for unit tests.

Allows Person 3's quiz module to be tested independently of the real LLM service
(owned by Person 5) and without making any paid API calls.

Usage:
    mock_llm = MockLLMService(response=VALID_QUIZ_JSON)
    quiz_service = QuizService(mock_llm)
    result, validation = await quiz_service.generate_quiz(request)
"""

from __future__ import annotations

import json
from typing import Any, Optional


class MockLLMService:
    """
    A test double for Person 5's shared LLM service.

    Attributes:
        response     : The raw string the mock will return (should be valid JSON).
        raise_error  : If set, generate_text() raises this exception instead.
        call_count   : Tracks how many times generate_text() was called.
    """

    def __init__(
        self,
        response: str = "",
        raise_error: Optional[Exception] = None,
    ) -> None:
        self.response = response
        self.raise_error = raise_error
        self.call_count = 0
        self._prompts_received: list[str] = []

    async def generate_text(self, prompt: str) -> str:
        self.call_count += 1
        self._prompts_received.append(prompt)
        if self.raise_error is not None:
            raise self.raise_error
        return self.response

    async def generate_structured(self, prompt: str, response_model: Any = None) -> Any:
        raw = await self.generate_text(prompt)
        return json.loads(raw)

    @property
    def last_prompt(self) -> Optional[str]:
        return self._prompts_received[-1] if self._prompts_received else None


# ---------------------------------------------------------------------------
# Fixture quiz JSON strings for tests
# ---------------------------------------------------------------------------

VALID_QUIZ_JSON = json.dumps({
    "questions": [
        {
            "question": "Which pigment helps plants absorb light energy?",
            "type": "mcq",
            "difficulty": "easy",
            "bloom_level": "remember",
            "options": ["Chlorophyll", "Hemoglobin", "Keratin", "Melanin"],
            "correct_answer": "Chlorophyll",
            "explanation": "Chlorophyll absorbs light energy used during photosynthesis.",
        },
        {
            "question": "Plants use carbon dioxide during photosynthesis.",
            "type": "true_false",
            "difficulty": "easy",
            "bloom_level": "remember",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "Carbon dioxide is one of the raw materials for photosynthesis.",
        },
        {
            "question": "Why does reducing light availability affect photosynthesis?",
            "type": "short_answer",
            "difficulty": "intermediate",
            "bloom_level": "understand",
            "options": [],
            "correct_answer": "Light provides energy required for photosynthesis, so less light reduces its rate.",
            "explanation": "Photosynthesis depends on light energy to convert CO2 and water into glucose.",
        },
    ]
})

MCQ_MISSING_OPTIONS_JSON = json.dumps({
    "questions": [
        {
            "question": "Which pigment helps plants absorb light?",
            "type": "mcq",
            "difficulty": "easy",
            "bloom_level": "remember",
            "options": [],  # ← invalid: MCQ with no options
            "correct_answer": "Chlorophyll",
            "explanation": "Chlorophyll absorbs light.",
        }
    ]
})

MCQ_ANSWER_NOT_IN_OPTIONS_JSON = json.dumps({
    "questions": [
        {
            "question": "Which pigment helps plants absorb light?",
            "type": "mcq",
            "difficulty": "easy",
            "bloom_level": "remember",
            "options": ["Hemoglobin", "Keratin", "Melanin", "Carotene"],
            "correct_answer": "Chlorophyll",  # ← not in options
            "explanation": "Chlorophyll absorbs light.",
        }
    ]
})

DUPLICATE_OPTIONS_JSON = json.dumps({
    "questions": [
        {
            "question": "Which pigment helps plants absorb light?",
            "type": "mcq",
            "difficulty": "easy",
            "bloom_level": "remember",
            "options": ["Chlorophyll", "Chlorophyll", "Keratin", "Melanin"],  # duplicate
            "correct_answer": "Chlorophyll",
            "explanation": "Chlorophyll absorbs light.",
        }
    ]
})

DUPLICATE_QUESTIONS_JSON = json.dumps({
    "questions": [
        {
            "question": "What is photosynthesis?",
            "type": "short_answer",
            "difficulty": "easy",
            "bloom_level": "remember",
            "options": [],
            "correct_answer": "A process by which plants make food.",
            "explanation": "Plants use light to make food.",
        },
        {
            "question": "  what is photosynthesis?  ",  # duplicate (normalised)
            "type": "short_answer",
            "difficulty": "easy",
            "bloom_level": "remember",
            "options": [],
            "correct_answer": "A process by which plants make food.",
            "explanation": "Plants use light to make food.",
        },
    ]
})

MISSING_ANSWER_JSON = json.dumps({
    "questions": [
        {
            "question": "What is chlorophyll?",
            "type": "short_answer",
            "difficulty": "easy",
            "bloom_level": "remember",
            "options": [],
            "correct_answer": "",  # ← missing
            "explanation": "Chlorophyll is a green pigment.",
        }
    ]
})

MISSING_EXPLANATION_JSON = json.dumps({
    "questions": [
        {
            "question": "What is chlorophyll?",
            "type": "short_answer",
            "difficulty": "easy",
            "bloom_level": "remember",
            "options": [],
            "correct_answer": "A green pigment in plants.",
            "explanation": "",  # ← missing
        }
    ]
})

INVALID_TRUE_FALSE_JSON = json.dumps({
    "questions": [
        {
            "question": "Plants release oxygen during photosynthesis.",
            "type": "true_false",
            "difficulty": "easy",
            "bloom_level": "remember",
            "options": ["True", "False"],
            "correct_answer": "Maybe",  # ← invalid
            "explanation": "Oxygen is released.",
        }
    ]
})

INVALID_BLOOM_JSON = json.dumps({
    "questions": [
        {
            "question": "What is photosynthesis?",
            "type": "short_answer",
            "difficulty": "easy",
            "bloom_level": "evaluate",  # ← not in supported set
            "options": [],
            "correct_answer": "A food-making process.",
            "explanation": "Plants make food.",
        }
    ]
})

INVALID_DIFFICULTY_JSON = json.dumps({
    "questions": [
        {
            "question": "What is photosynthesis?",
            "type": "short_answer",
            "difficulty": "expert",  # ← invalid
            "bloom_level": "remember",
            "options": [],
            "correct_answer": "A food-making process.",
            "explanation": "Plants make food.",
        }
    ]
})

MALFORMED_JSON = "{ this is not valid json }"

WITH_CURRICULUM_JSON = json.dumps({
    "questions": [
        {
            "question": "According to CBSE curriculum, what do green plants use to prepare food?",
            "type": "mcq",
            "difficulty": "easy",
            "bloom_level": "remember",
            "options": ["CO2, water, sunlight", "Oxygen, glucose, light", "Water, minerals, heat", "Nitrogen, CO2, water"],
            "correct_answer": "CO2, water, sunlight",
            "explanation": "Green plants use CO2, water and sunlight in the presence of chlorophyll.",
        }
    ]
})
