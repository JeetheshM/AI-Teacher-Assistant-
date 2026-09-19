"""
gemini_llm_service.py
---------------------
Real LLM service backed by google-genai (new SDK).
Set GEMINI_API_KEY in your .env file before starting the server.
"""

from __future__ import annotations
import os

try:
    from google import genai
    from google.genai import types as genai_types
    _USING_NEW_SDK = True
except ImportError:
    _USING_NEW_SDK = False
    try:
        import google.generativeai as genai_legacy  # type: ignore
    except ImportError:
        genai_legacy = None


class GeminiLLMService:
    """Wraps google-genai for use with QuizService."""

    def __init__(self, model_name: str = "gemini-1.5-flash") -> None:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set. Add it to your .env file."
            )

        self._model_name = model_name

        if _USING_NEW_SDK:
            self._client = genai.Client(api_key=api_key)
        else:
            if genai_legacy is None:
                raise RuntimeError("Neither google-genai nor google-generativeai is installed.")
            genai_legacy.configure(api_key=api_key)
            self._model = genai_legacy.GenerativeModel(
                model_name=model_name,
                generation_config=genai_legacy.types.GenerationConfig(
                    temperature=0.4,
                    response_mime_type="application/json",
                ),
            )

    async def generate_text(self, prompt: str) -> str:
        import asyncio
        loop = asyncio.get_event_loop()

        if _USING_NEW_SDK:
            response = await loop.run_in_executor(
                None,
                lambda: self._client.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        temperature=0.4,
                        response_mime_type="application/json",
                    ),
                ),
            )
            return response.text
        else:
            response = await loop.run_in_executor(
                None,
                lambda: self._model.generate_content(prompt)
            )
            return response.text
