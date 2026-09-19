"""
quiz_validator.py
-----------------
Deterministic structural validation for AI-generated quizzes.

IMPORTANT: This validator checks STRUCTURAL and LOGICAL consistency only.
It does NOT verify factual correctness of questions or answers.
Teacher review remains the final safety layer.
"""

from __future__ import annotations

import re
from typing import List

from backend.models.quiz_models import (
    ALLOWED_BLOOM_LEVELS,
    ALLOWED_DIFFICULTIES,
    AnswerKey,
    AnswerKeyEntry,
    Question,
    QuizResponse,
    ValidationChecks,
    ValidationResult,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _normalise(text: str) -> str:
    """Lowercase, strip, and collapse whitespace for duplicate detection."""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)   # strip punctuation
    return text


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class QuizValidator:
    """
    Validates a QuizResponse for structural and logical consistency.

    Usage (by Person 5):
        validator = QuizValidator()
        result = validator.validate(quiz, expected_count=request.question_count)
    """

    def validate(
        self,
        quiz: QuizResponse,
        expected_count: int,
    ) -> ValidationResult:
        checks = ValidationChecks()
        warnings: List[str] = []
        errors: List[str] = []

        questions = quiz.questions

        # ── CHECK 1: Question count ─────────────────────────────────────────
        if len(questions) == expected_count:
            checks.question_count_valid = True
        else:
            checks.question_count_valid = False
            errors.append(
                f"Expected {expected_count} questions, got {len(questions)}."
            )

        # ── CHECK 2: Non-empty question text ────────────────────────────────
        missing_text = [i + 1 for i, q in enumerate(questions) if not q.question.strip()]
        if not missing_text:
            checks.all_questions_have_text = True
        else:
            errors.append(f"Questions with missing text: {missing_text}")

        # ── CHECK 3: Type present and valid ─────────────────────────────────
        invalid_types = [
            (i + 1, q.type) for i, q in enumerate(questions)
            if q.type not in {"mcq", "true_false", "short_answer"}
        ]
        if not invalid_types:
            checks.all_questions_have_type = True
        else:
            errors.append(f"Invalid question types: {invalid_types}")

        # ── CHECK 4: correct_answer present ─────────────────────────────────
        missing_answer = [i + 1 for i, q in enumerate(questions) if not q.correct_answer.strip()]
        if not missing_answer:
            checks.all_questions_have_answers = True
        else:
            errors.append(f"Questions missing correct_answer: {missing_answer}")

        # ── CHECK 5: Explanation present ─────────────────────────────────────
        missing_expl = [i + 1 for i, q in enumerate(questions) if not q.explanation.strip()]
        if not missing_expl:
            checks.all_questions_have_explanations = True
        else:
            errors.append(f"Questions missing explanation: {missing_expl}")

        # ── MCQ-specific checks ──────────────────────────────────────────────
        mcq_questions = [(i + 1, q) for i, q in enumerate(questions) if q.type == "mcq"]

        # CHECK 6: MCQ has options
        mcq_no_options = [num for num, q in mcq_questions if not q.options]
        if mcq_questions:
            if not mcq_no_options:
                checks.mcq_has_options = True
            else:
                errors.append(f"MCQ questions missing options: {mcq_no_options}")
        else:
            checks.mcq_has_options = True  # no MCQ questions — vacuously true

        # CHECK 7: MCQ prefers 4 options
        mcq_not_four = [num for num, q in mcq_questions if len(q.options) != 4]
        if not mcq_not_four:
            checks.mcq_prefers_four_options = True
        else:
            warnings.append(
                f"MCQ questions without exactly 4 options (preferred): {mcq_not_four}"
            )
            # Warning only — not blocking error

        # CHECK 8: MCQ correct_answer in options
        mcq_answer_not_in_options = [
            num for num, q in mcq_questions
            if q.correct_answer not in q.options
        ]
        if not mcq_answer_not_in_options:
            checks.mcq_answers_in_options = True
        else:
            errors.append(
                f"MCQ correct_answer not found in options for questions: "
                f"{mcq_answer_not_in_options}"
            )

        # CHECK 9: No duplicate options within an MCQ
        mcq_dup_options: List[int] = []
        for num, q in mcq_questions:
            seen_opts: set = set()
            for opt in q.options:
                norm = _normalise(opt)
                if norm in seen_opts:
                    mcq_dup_options.append(num)
                    break
                seen_opts.add(norm)
        if not mcq_dup_options:
            checks.no_duplicate_options = True
        else:
            errors.append(f"MCQ questions with duplicate options: {mcq_dup_options}")

        # ── CHECK 10: No duplicate questions ────────────────────────────────
        seen_questions: set = set()
        duplicate_question_ids: List[str] = []
        for q in questions:
            norm = _normalise(q.question)
            if norm in seen_questions:
                duplicate_question_ids.append(q.id)
            else:
                seen_questions.add(norm)

        if not duplicate_question_ids:
            checks.no_duplicate_questions = True
        else:
            errors.append(f"Duplicate questions detected (ids): {duplicate_question_ids}")

        # ── CHECK 11: Difficulty values are valid ────────────────────────────
        invalid_diffs = [
            (i + 1, q.difficulty) for i, q in enumerate(questions)
            if q.difficulty not in ALLOWED_DIFFICULTIES
        ]
        if not invalid_diffs:
            checks.difficulties_valid = True
        else:
            errors.append(f"Invalid difficulty values: {invalid_diffs}")

        # ── CHECK 12: Bloom levels are valid ─────────────────────────────────
        invalid_blooms = [
            (i + 1, q.bloom_level) for i, q in enumerate(questions)
            if q.bloom_level not in ALLOWED_BLOOM_LEVELS
        ]
        if not invalid_blooms:
            checks.bloom_levels_valid = True
        else:
            errors.append(f"Invalid Bloom levels: {invalid_blooms}")

        # ── CHECK 13: True/False answers ─────────────────────────────────────
        tf_questions = [(i + 1, q) for i, q in enumerate(questions) if q.type == "true_false"]
        tf_invalid = [
            num for num, q in tf_questions
            if q.correct_answer not in {"True", "False"}
        ]
        if not tf_invalid:
            checks.true_false_answers_valid = True
        else:
            errors.append(
                f"True/False questions with invalid correct_answer "
                f"(must be 'True' or 'False'): {tf_invalid}"
            )

        # ── Derive overall validity ──────────────────────────────────────────
        is_valid = len(errors) == 0

        return ValidationResult(
            valid=is_valid,
            checks=checks,
            warnings=warnings,
            errors=errors,
        )


# ---------------------------------------------------------------------------
# Answer key helper (no LLM call — extracted from quiz data)
# ---------------------------------------------------------------------------

def generate_answer_key(quiz: QuizResponse) -> AnswerKey:
    """
    Extract the answer key from an already-generated QuizResponse.
    Makes NO additional LLM calls.
    """
    entries = [
        AnswerKeyEntry(
            question_id=q.id,
            answer=q.correct_answer,
            explanation=q.explanation,
        )
        for q in quiz.questions
    ]
    return AnswerKey(quiz_title=quiz.title, entries=entries)
