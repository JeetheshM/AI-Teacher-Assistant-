"""
gemini_llm_service.py
---------------------
Real LLM service backed by google-generativeai (Gemini).

This is the concrete implementation that replaces MockLLMService in production.
Person 5 can replace this with their own shared LLM abstraction.

Set GEMINI_API_KEY in your .env file or environment before starting the server.
"""

from __future__ import annotations

import os
import google.generativeai as genai


class GeminiLLMService:
    """
    Wraps google-generativeai for use with QuizService.

    Usage:
        llm = GeminiLLMService()
        text = await llm.generate_text(prompt)
    """

    def __init__(self, model_name: str = "gemini-3.6-flash") -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set. "
                "Add it to your .env file."
            )
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,          # lower = more deterministic/factual
                response_mime_type="application/json",  # ask Gemini for JSON
            ),
        )

    async def generate_text(self, prompt: str) -> str:
        # google-generativeai is synchronous; run in executor for async compat
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._model.generate_content(prompt)
        )
        return response.text
