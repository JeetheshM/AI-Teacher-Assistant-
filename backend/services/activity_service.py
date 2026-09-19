"""
Classroom Activity Service (Person 6)

Core orchestration for classroom activity generation.
Performs single LLM call, parses structured JSON, applies safety constraints,
preserves curriculum context metadata, and executes deterministic validation.
"""

import json
import re
from typing import Protocol, Any, Dict, Optional, runtime_checkable
from backend.models.activity_models import (
    ActivityGenerationRequest,
    ActivityResponse,
    ActivityValidationResult,
)
from backend.prompts.activity_prompt import (
    ACTIVITY_PROMPT_VERSION,
    build_activity_prompt,
)
from backend.validators.activity_validator import ActivityValidator


@runtime_checkable
class LLMServiceInterface(Protocol):
    """
    Protocol matching Person 5's shared LLM service contract.
    Allows easy injection of real or mock LLM providers.
    """
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        ...


class ActivityService:
    """
    Service responsible for generating classroom activities.
    """

    def __init__(self, llm_service: Optional[LLMServiceInterface] = None):
        self.llm_service = llm_service
        self.prompt_version = ACTIVITY_PROMPT_VERSION

    @staticmethod
    def _extract_json_payload(raw_text: str) -> str:
        """
        Extracts JSON substring from raw model output, stripping markdown fences if present.
        """
        text = raw_text.strip()
        # Match ```json ... ``` or ``` ... ```
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if fence_match:
            return fence_match.group(1).strip()
        
        # Match between first '{' and last '}'
        brace_match = re.search(r"(\{[\s\S]*\})", text)
        if brace_match:
            return brace_match.group(1).strip()
            
        return text

    async def generate_activity(
        self,
        request: ActivityGenerationRequest,
    ) -> ActivityResponse:
        """
        Generates a structured, curriculum-grounded classroom activity.
        Performs ONE LLM call and returns validated ActivityResponse.
        """
        # Step 1: Validate input request
        req_val = ActivityValidator.validate_request(request)
        if not req_val.valid:
            raise ValueError(f"Invalid ActivityGenerationRequest: {'; '.join(req_val.errors)}")

        # Step 2: Build prompt
        prompt = build_activity_prompt(request)

        # Step 3: Call LLM
        if self.llm_service is None:
            raise RuntimeError("LLM service is not configured on ActivityService.")

        try:
            raw_response = await self.llm_service.generate(prompt=prompt)
        except Exception as e:
            raise RuntimeError(f"Activity generation failed at LLM layer: {str(e)}") from e

        # Step 4: Extract and parse JSON
        cleaned_json = self._extract_json_payload(raw_response)
        try:
            data = json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM returned malformed JSON for activity: {str(e)}") from e

        # Step 5: Derive trusted curriculum sources directly from context
        trusted_sources = ActivityValidator.extract_and_deduplicate_sources(request)
        data["sources_used"] = [s.model_dump() for s in trusted_sources]

        # Ensure requested duration or fallback if omitted
        if "duration_minutes" not in data or not data["duration_minutes"]:
            data["duration_minutes"] = request.duration_minutes

        # Ensure activity type matches or defaults
        if "activity_type" not in data or not data["activity_type"]:
            data["activity_type"] = request.activity_type or "group"

        # Step 6: Validate against Pydantic schema
        try:
            activity = ActivityResponse(**data)
        except Exception as e:
            raise ValueError(f"Generated activity does not conform to ActivityResponse schema: {str(e)}") from e

        # Step 7: Perform deterministic structural validation
        val_result = ActivityValidator.validate_activity(activity, request)
        if not val_result.valid:
            raise ValueError(f"Generated activity failed structural validation: {'; '.join(val_result.errors)}")

        return activity

    def validate_activity_object(
        self,
        activity: ActivityResponse,
        request: Optional[ActivityGenerationRequest] = None,
    ) -> ActivityValidationResult:
        """Helper to validate an existing activity object."""
        return ActivityValidator.validate_activity(activity, request)
