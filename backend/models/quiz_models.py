"""
quiz_models.py
--------------
Pydantic models for the TeachMate AI Quiz / Assessment module.

These are the canonical shared schemas that Person 1 (frontend contract),
Person 4 (RAG context), and Person 5 (persistence + routes) integrate with.
"""

from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_DIFFICULTIES = {"easy", "intermediate", "hard"}
ALLOWED_QUESTION_TYPES = {"mcq", "true_false", "short_answer"}
ALLOWED_BLOOM_LEVELS = {"remember", "understand", "apply", "analyze"}

QuestionType = Literal["mcq", "true_false", "short_answer"]
DifficultyLevel = Literal["easy", "intermediate", "hard"]
BloomLevel = Literal["remember", "understand", "apply", "analyze"]


# ---------------------------------------------------------------------------
# Curriculum context (provided by Person 4 / RAG)
# ---------------------------------------------------------------------------

class CurriculumContext(BaseModel):
    """A single retrieved chunk from Person 4's RAG pipeline."""

    content: str = Field(..., description="Extracted text from the curriculum document.")
    source: str = Field(..., description="Source document filename, e.g. CBSE_Science.pdf")
    page_number: Optional[int] = Field(None, description="Page number the chunk was retrieved from.")


# ---------------------------------------------------------------------------
# Request schema
# ---------------------------------------------------------------------------

class QuizGenerationRequest(BaseModel):
    """
    Input to QuizService.generate_quiz().

    IMPORTANT: field names are canonical — do not rename them.
    """

    subject: str = Field(..., min_length=1, description="e.g. Science, Mathematics")
    topic: str = Field(..., min_length=1, description="e.g. Photosynthesis")
    grade: int = Field(..., ge=1, le=12, description="School grade, 1–12")
    difficulty: DifficultyLevel = Field(..., description="easy | intermediate | hard")
    question_count: int = Field(..., ge=1, le=50, description="Total questions to generate")
    question_types: List[QuestionType] = Field(
        ..., min_length=1, description="List of: mcq | true_false | short_answer"
    )
    learning_objective: Optional[str] = Field(
        None, description="Optional learning objective to align questions with."
    )
    bloom_levels: Optional[List[BloomLevel]] = Field(
        None, description="Subset of: remember | understand | apply | analyze"
    )
    curriculum_context: Optional[List[CurriculumContext]] = Field(
        None,
        description="Retrieved curriculum chunks from Person 4's RAG pipeline. "
                    "Used to ground generation; NOT trusted as instructions.",
    )

    @field_validator("topic")
    @classmethod
    def topic_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("topic must not be blank.")
        return v.strip()

    @field_validator("question_types")
    @classmethod
    def dedup_question_types(cls, v: List[str]) -> List[str]:
        seen: list = []
        for qt in v:
            if qt not in seen:
                seen.append(qt)
        return seen


# ---------------------------------------------------------------------------
# Question model
# ---------------------------------------------------------------------------

class Question(BaseModel):
    """
    A single assessment question with answer and explanation.

    IDs are assigned by application code (q1, q2, …) after LLM generation.
    """

    id: str = Field(default="", description="Deterministic ID: q1, q2, …")
    question: str = Field(..., description="The question text.")
    type: QuestionType
    difficulty: DifficultyLevel
    bloom_level: BloomLevel
    options: List[str] = Field(
        default_factory=list,
        description="Answer choices for MCQ/True-False. Empty for short_answer.",
    )
    correct_answer: str = Field(..., description="Correct answer string.")
    explanation: str = Field(..., description="Concise explanation of the correct answer.")


# ---------------------------------------------------------------------------
# Source metadata (derived from curriculum_context, not LLM output)
# ---------------------------------------------------------------------------

class SourceReference(BaseModel):
    source: str
    page_number: Optional[int] = None

    def __hash__(self):
        return hash((self.source, self.page_number))

    def __eq__(self, other):
        if not isinstance(other, SourceReference):
            return False
        return self.source == other.source and self.page_number == other.page_number


# ---------------------------------------------------------------------------
# Quiz response schema (returned by QuizService)
# ---------------------------------------------------------------------------

class QuizResponse(BaseModel):
    """
    Complete quiz output consumed by Person 1 (frontend) and Person 5 (persistence).
    """

    title: str
    subject: str
    topic: str
    grade: int
    difficulty: DifficultyLevel
    question_count: int
    questions: List[Question]
    sources_used: List[SourceReference] = Field(default_factory=list)

    @model_validator(mode="after")
    def assign_question_ids(self) -> "QuizResponse":
        for idx, q in enumerate(self.questions, start=1):
            if not q.id:
                q.id = f"q{idx}"
        return self


# ---------------------------------------------------------------------------
# Answer key helper type
# ---------------------------------------------------------------------------

class AnswerKeyEntry(BaseModel):
    question_id: str
    answer: str
    explanation: str


class AnswerKey(BaseModel):
    quiz_title: str
    entries: List[AnswerKeyEntry]


# ---------------------------------------------------------------------------
# Validation result schema (for Person 1 quality display)
# ---------------------------------------------------------------------------

class ValidationChecks(BaseModel):
    question_count_valid: bool = False
    all_questions_have_text: bool = False
    all_questions_have_type: bool = False
    all_questions_have_answers: bool = False
    all_questions_have_explanations: bool = False
    mcq_has_options: bool = False
    mcq_prefers_four_options: bool = False
    mcq_answers_in_options: bool = False
    no_duplicate_options: bool = False
    no_duplicate_questions: bool = False
    difficulties_valid: bool = False
    bloom_levels_valid: bool = False
    true_false_answers_valid: bool = False


class ValidationResult(BaseModel):
    """
    Structural quality check result — does NOT verify factual correctness.
    Teacher review remains the final safety layer.
    """

    valid: bool
    checks: ValidationChecks
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
