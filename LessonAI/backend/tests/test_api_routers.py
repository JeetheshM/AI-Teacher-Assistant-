"""
Unit tests for FastAPI router stubs.
TeachMate AI - Person 2 (Lesson Planner + Simplification AI).
"""

import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.lessons_router import create_lessons_router
from backend.api.simplify_router import create_simplify_router
from backend.mocks.mock_llm_service import MockLLMService
from backend.services.lesson_service import LessonService
from backend.services.simplification_service import SimplificationService


class TestApiRouters(unittest.TestCase):
    """Tests that endpoints expose correct routes, schemas, and status codes."""

    def setUp(self):
        self.app = FastAPI(title="TeachMate AI Test App")
        mock_llm = MockLLMService()
        lesson_service = LessonService(mock_llm)
        simplification_service = SimplificationService(mock_llm)

        self.app.include_router(create_lessons_router(lesson_service))
        self.app.include_router(create_simplify_router(simplification_service))
        self.client = TestClient(self.app)

    def test_post_lessons_generate(self):
        """Verify POST /api/lessons/generate endpoint."""
        payload = {
            "subject": "Science",
            "topic": "Photosynthesis",
            "grade": 8,
            "duration_minutes": 45,
            "difficulty": "intermediate",
            "learning_objective": "Understand how plants make food",
            "curriculum_context": [
                {
                    "content": "Green plants make food using sunlight and chlorophyll.",
                    "source": "CBSE_Science.pdf",
                    "page_number": 82
                }
            ]
        }
        response = self.client.post("/api/lessons/generate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("lesson", data)
        self.assertIn("validation", data)
        self.assertEqual(data["lesson"]["subject"], "Science")
        self.assertEqual(data["lesson"]["grade"], 8)
        self.assertEqual(len(data["lesson"]["sources_used"]), 1)
        self.assertEqual(data["lesson"]["sources_used"][0]["source"], "CBSE_Science.pdf")
        self.assertTrue(data["validation"]["valid"])

    def test_post_simplify_modes(self):
        """Verify POST /api/simplify endpoint for all 4 modes."""
        modes = ["simplify", "younger_level", "analogy", "real_world_example"]
        for mode in modes:
            payload = {
                "content": "Photosynthesis converts light into chemical energy.",
                "subject": "Science",
                "topic": "Photosynthesis",
                "grade": 8,
                "mode": mode
            }
            response = self.client.post("/api/simplify", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["mode"], mode)
            self.assertGreater(len(data["transformed_content"]), 10)

    def test_invalid_request_returns_422_or_400(self):
        """Verify bad request payload returns client error."""
        # Missing required field 'topic'
        payload = {
            "subject": "Science",
            "grade": 8,
            "duration_minutes": 45,
            "difficulty": "intermediate",
            "learning_objective": "Learn stuff"
        }
        response = self.client.post("/api/lessons/generate", json=payload)
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
