"""
Activity Models for TeachMate AI (Person 6)

Shared Data Contracts:
- subject: str
- topic: str
- grade: int
- duration_minutes: int
- difficulty: str
- class_size: Optional[int]
- learning_objective: Optional[str]
- activity_type: Optional[str]
- curriculum_context: Optional[List[CurriculumChunk]]
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class CurriculumChunk(BaseModel):
    """Curriculum chunk supplied by Person 4 RAG service."""
    content: str
    source: str
    page_number: Optional[int] = None
    chunk_id: Optional[str] = None


class SourceReference(BaseModel):
    """Source reference citation for UI and PDF."""
    source: str
    page_number: Optional[int] = None


class ActivityGenerationRequest(BaseModel):
    """Incoming request for classroom activity generation."""
    subject: str = Field(..., description="Subject area, e.g. Science, Math, History")
    topic: str = Field(..., description="Lesson topic, e.g. Photosynthesis")
    grade: int = Field(..., ge=1, le=12, description="Grade level (1-12)")
    duration_minutes: int = Field(default=15, gt=0, le=120, description="Target activity duration in minutes")
    difficulty: str = Field(default="intermediate", description="Difficulty: easy, intermediate, advanced")
    class_size: Optional[int] = Field(default=30, ge=1, le=100, description="Expected number of students")
    learning_objective: Optional[str] = Field(default=None, description="Primary learning objective")
    activity_type: Optional[str] = Field(
        default="group",
        description="Suggested activity type: group, individual, discussion, experiment, problem_solving, creative"
    )
    curriculum_context: Optional[List[CurriculumChunk]] = Field(
        default=None,
        description="Curriculum chunks provided by RAG service"
    )

    @field_validator("subject", "topic")
    @classmethod
    def check_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field must not be empty or whitespace only")
        return v.strip()


class ActivityResponse(BaseModel):
    """Structured classroom activity response."""
    title: str = Field(..., description="Creative, engaging title for the activity")
    activity_type: str = Field(..., description="Type of activity: group, individual, discussion, experiment, problem_solving, creative")
    objective: str = Field(..., description="Clear instructional goal of the activity")
    duration_minutes: int = Field(..., description="Estimated completion duration in minutes")
    group_size: Optional[int] = Field(default=None, description="Recommended students per group if group activity")
    materials: List[str] = Field(default_factory=list, description="Common, low-cost classroom materials required")
    setup: str = Field(..., description="Preparation and classroom arrangement instructions for the teacher")
    instructions: List[str] = Field(default_factory=list, description="Step-by-step classroom action steps")
    teacher_role: str = Field(..., description="Teacher facilitation, monitoring, and guidance instructions")
    student_role: str = Field(..., description="Student participation and collaboration responsibilities")
    expected_outcome: str = Field(..., description="Observable learning evidence and artifact")
    assessment_method: str = Field(..., description="Formative assessment method to verify understanding")
    safety_notes: List[str] = Field(default_factory=list, description="Safety precautions if relevant")
    adaptations: List[str] = Field(default_factory=list, description="Differentiated learning adaptations")
    sources_used: List[SourceReference] = Field(default_factory=list, description="Curriculum source references used")


class ActivityValidationResult(BaseModel):
    """Validation report for activity structure and quality."""
    valid: bool
    checks: Dict[str, bool]
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
