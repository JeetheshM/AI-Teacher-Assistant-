"""
Lesson and Content Transformation Data Models.
Shared data contracts for TeachMate AI - Person 2 (Lesson Planner + Simplification AI).
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


# =====================================================================
# Curriculum Context Contract (Received from Person 4 - RAG Module)
# =====================================================================

class CurriculumChunk(BaseModel):
    """Chunk of reference curriculum text provided by RAG retrieval."""
    content: str = Field(..., description="Text content extracted from curriculum document")
    source: str = Field(..., description="Document filename, e.g. CBSE_Science.pdf")
    page_number: Optional[int] = Field(None, description="Page number if available")


# =====================================================================
# Request Contract (Initiated by Person 1 - Frontend / Person 5 - API)
# =====================================================================

class LessonGenerationRequest(BaseModel):
    """
    Standard request payload for generating a lesson plan.
    Strictly follows shared naming conventions from Section 8 & 29 of Master Spec.
    """
    subject: str = Field(..., min_length=1, description="Subject name (e.g., Science)")
    topic: str = Field(..., min_length=1, description="Lesson topic (e.g., Photosynthesis)")
    grade: int = Field(..., gt=0, le=12, description="Target student grade level (1-12)")
    duration_minutes: int = Field(..., gt=0, le=300, description="Target duration in minutes (e.g., 45)")
    difficulty: str = Field(default="intermediate", description="Difficulty level: easy, intermediate, advanced")
    learning_objective: str = Field(..., min_length=1, description="Core learning objective")
    curriculum_context: Optional[List[CurriculumChunk]] = Field(
        default_factory=list,
        description="Optional list of retrieved curriculum excerpts from RAG"
    )

    @field_validator("subject", "topic", "learning_objective")
    @classmethod
    def validate_non_empty_strings(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(f"Field '{info.field_name}' must not be empty or whitespace only.")
        return v.strip()

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        normalized = v.strip().lower()
        allowed = {"easy", "intermediate", "advanced"}
        if normalized not in allowed:
            raise ValueError(f"Difficulty must be one of {allowed}, got '{v}'")
        return normalized


# =====================================================================
# Lesson Plan Output Structure (Consumed by Person 1 - UI & Person 5 - DB)
# =====================================================================

class TimedContent(BaseModel):
    """Section of a lesson plan with allocated duration and content."""
    duration_minutes: int = Field(..., ge=0, description="Allocated duration in minutes")
    content: str = Field(..., min_length=1, description="Actionable instructional content")


class ExampleItem(BaseModel):
    """Teaching example or illustration."""
    title: str = Field(..., min_length=1, description="Example headline")
    description: str = Field(..., min_length=1, description="Detailed explanation of the example")


class MisconceptionItem(BaseModel):
    """Common student misconception and corresponding pedagogical correction."""
    misconception: str = Field(..., min_length=1, description="Common false assumption by students")
    correction: str = Field(..., min_length=1, description="Accurate scientific/factual clarification")


class SourceUsed(BaseModel):
    """Document citation preserved from RAG retrieval context."""
    source: str = Field(..., description="Document source filename")
    page_number: Optional[int] = Field(None, description="Page number if available")


class LessonPlan(BaseModel):
    """
    Complete classroom-ready structured lesson plan.
    Strictly matches output specification in Section 7 & 9 of Master Spec.
    """
    title: str = Field(..., min_length=1, description="Lesson title")
    subject: str = Field(..., min_length=1, description="Subject area")
    grade: int = Field(..., gt=0, le=12, description="Target grade")
    difficulty: str = Field(..., description="Difficulty level: easy, intermediate, advanced")
    total_duration_minutes: int = Field(..., gt=0, description="Overall duration in minutes")
    objectives: List[str] = Field(..., min_length=1, description="List of learning objectives")
    prerequisites: List[str] = Field(default_factory=list, description="Prior knowledge required")
    introduction: TimedContent = Field(..., description="Hook and introduction section with timing")
    explanation: TimedContent = Field(..., description="Core teaching explanation and concept delivery")
    examples: List[ExampleItem] = Field(default_factory=list, description="Instructive examples")
    key_points: List[str] = Field(..., min_length=1, description="Summary of key takeaway points")
    common_misconceptions: List[MisconceptionItem] = Field(
        default_factory=list,
        description="Known misconceptions and corrections"
    )
    recap: TimedContent = Field(..., description="Wrap-up, check for understanding, and recap")
    teacher_tips: List[str] = Field(default_factory=list, description="Practical tips for class management")
    sources_used: List[SourceUsed] = Field(
        default_factory=list,
        description="Preserved sources from curriculum context"
    )


# =====================================================================
# Content Transformation Models (Simplification, Analogy, Real-world)
# =====================================================================

class TransformationMode(str, Enum):
    SIMPLIFY = "simplify"
    YOUNGER_LEVEL = "younger_level"
    ANALOGY = "analogy"
    REAL_WORLD_EXAMPLE = "real_world_example"


class ContentTransformationRequest(BaseModel):
    """Request payload for transforming an explanation or concept block."""
    content: str = Field(..., min_length=1, description="Original text to transform")
    subject: str = Field(..., min_length=1, description="Subject context")
    topic: str = Field(..., min_length=1, description="Topic context")
    grade: int = Field(..., gt=0, le=12, description="Student grade")
    mode: TransformationMode = Field(..., description="Transformation type")

    @field_validator("content", "subject", "topic")
    @classmethod
    def validate_non_empty(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(f"Field '{info.field_name}' must not be empty or whitespace only.")
        return v.strip()


class ContentTransformationResponse(BaseModel):
    """Structured response containing original and transformed content."""
    mode: TransformationMode = Field(..., description="Applied transformation mode")
    original_content: str = Field(..., description="Original input content")
    transformed_content: str = Field(..., description="Transformed output content")
    grade: int = Field(..., description="Target grade")


# =====================================================================
# Validation and Composite Response Models
# =====================================================================

class LessonValidationResult(BaseModel):
    """Result of deterministic quality and structural checks."""
    valid: bool = Field(..., description="True if all critical checks passed")
    checks: Dict[str, bool] = Field(..., description="Individual boolean check results")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warning messages")
    disclaimer: str = Field(
        default="Structural and duration validation only. Does not guarantee factual correctness; teacher review required.",
        description="Quality disclaimer for judging and UI transparency"
    )


class LessonGenerationResponse(BaseModel):
    """Full generation response delivered to API / Frontend."""
    lesson: LessonPlan
    validation: LessonValidationResult
    prompt_version: str = Field(default="lesson_v1", description="Traceability prompt version")


# =====================================================================
# Exceptions
# =====================================================================

class LessonAIError(Exception):
    """Base exception for Lesson AI module."""
    pass


class LessonGenerationError(LessonAIError):
    """Raised when lesson generation fails."""
    pass


class LessonValidationError(LessonAIError):
    """Raised when deterministic validation fails critically."""
    pass


class LLMResponseError(LessonAIError):
    """Raised when LLM returns invalid, unparseable, or timed out response."""
    pass
