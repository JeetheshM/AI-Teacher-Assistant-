"""
demo_test.py  -  TeachMate AI Quiz Module Demo
Runs the full quiz generation pipeline and prints results.

Usage:
    python demo_test.py
"""

import asyncio
import json
import os
import sys

# Force UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

from backend.models.quiz_models import CurriculumContext, QuizGenerationRequest
from backend.services.gemini_llm_service import GeminiLLMService
from backend.services.quiz_service import QuizService
from backend.validators.quiz_validator import generate_answer_key


async def main():
    SEP  = "=" * 60
    LINE = "-" * 60

    print(SEP)
    print("  TeachMate AI -- Quiz Module Demo")
    print(SEP)

    request = QuizGenerationRequest(
        subject="Science",
        topic="Photosynthesis",
        grade=8,
        difficulty="intermediate",
        question_count=5,
        question_types=["mcq", "true_false", "short_answer"],
        learning_objective="Understand how plants make food using sunlight, CO2 and water",
        bloom_levels=["remember", "understand", "apply"],
        curriculum_context=[
            CurriculumContext(
                content=(
                    "Green plants prepare their own food using carbon dioxide "
                    "and water in the presence of sunlight and chlorophyll. "
                    "This process is called photosynthesis. Oxygen is released "
                    "as a by-product."
                ),
                source="CBSE_Science.pdf",
                page_number=82,
            )
        ],
    )

    print(f"\n[REQUEST] Topic: {request.topic} | Grade: {request.grade} | Difficulty: {request.difficulty}")
    print(f"  Types : {request.question_types}")
    print(f"  Bloom : {request.bloom_levels}")
    print(f"  Count : {request.question_count} questions")
    print(f"\n  Calling Gemini... (takes ~10 seconds)\n")

    llm = GeminiLLMService()
    svc = QuizService(llm)

    quiz, validation = await svc.generate_quiz(request)
    answer_key = generate_answer_key(quiz)

    # ── Quiz ──────────────────────────────────────────────────────────
    print(SEP)
    print(f"  {quiz.title.upper()}")
    print(f"  Subject: {quiz.subject}  |  Grade: {quiz.grade}  |  Difficulty: {quiz.difficulty}")
    print(SEP)

    for q in quiz.questions:
        print(f"\n{q.id.upper()}.  {q.question}")
        print(f"    Type: {q.type}  |  Bloom: {q.bloom_level}  |  Difficulty: {q.difficulty}")
        if q.options:
            for i, opt in enumerate(q.options, 1):
                print(f"      {chr(64+i)}) {opt}")

    # ── Answer Key ────────────────────────────────────────────────────
    print(f"\n{LINE}")
    print("  ANSWER KEY")
    print(LINE)
    for entry in answer_key.entries:
        print(f"\n  {entry.question_id.upper()}.  Answer : {entry.answer}")
        print(f"       Explain: {entry.explanation}")

    # ── Validation ────────────────────────────────────────────────────
    print(f"\n{LINE}")
    overall = "PASSED" if validation.valid else "FAILED"
    print(f"  QUALITY CHECK -- {overall}")
    print(LINE)
    for check, passed in validation.checks.model_dump().items():
        icon = "[OK]" if passed else "[!!]"
        label = check.replace("_", " ").title()
        print(f"  {icon}  {label}")

    if validation.warnings:
        print("\n  Warnings:")
        for w in validation.warnings:
            print(f"    - {w}")
    if validation.errors:
        print("\n  Errors:")
        for e in validation.errors:
            print(f"    - {e}")

    # ── Sources ───────────────────────────────────────────────────────
    if quiz.sources_used:
        print(f"\n{LINE}")
        print("  SOURCES USED")
        for s in quiz.sources_used:
            page = f"p.{s.page_number}" if s.page_number else ""
            print(f"  [PDF]  {s.source}  {page}")

    # ── Save JSON ─────────────────────────────────────────────────────
    output = {
        "quiz": quiz.model_dump(),
        "answer_key": answer_key.model_dump(),
        "validation": validation.model_dump(),
    }
    with open("quiz_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n{SEP}")
    print("  Done! Full JSON saved to: quiz_output.json")
    print(SEP)


if __name__ == "__main__":
    asyncio.run(main())
