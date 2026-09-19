# TeachMate AI — Quiz / Assessment Module

**Module Owner: Person 3**
**Prompt Version:** `quiz_v1`

> **Important:** Validation checks structural and logical consistency of the generated quiz.
> It does **not** guarantee factual correctness of questions or answers.
> Teacher review remains the final safety layer.

---

## Purpose

AI-powered assessment generation for school educators. Given a subject, topic,
grade, difficulty, and optional curriculum context, the service generates a
complete quiz with:

- Questions (MCQ, True/False, Short Answer)
- Correct answers
- Explanations
- Bloom's Taxonomy levels
- Structural quality validation report
- Answer key (extracted — no extra LLM call)
- Source metadata (preserved from RAG, not hallucinated)

---

## Supported Question Types

| Type | Description |
|---|---|
| `mcq` | Multiple choice, 4 options, 1 correct answer |
| `true_false` | Two options: `"True"` / `"False"` |
| `short_answer` | Open-ended, model answer provided |

---

## Supported Difficulties

| Difficulty | Focus |
|---|---|
| `easy` | Recall, definitions, identification |
| `intermediate` | Understanding, explanation, basic application |
| `hard` | Analysis, multi-step reasoning, misconceptions |

---

## Supported Bloom Levels

| Level | Description |
|---|---|
| `remember` | Recall facts |
| `understand` | Explain concepts |
| `apply` | Use knowledge in a new context |
| `analyze` | Compare, infer, examine relationships |

---

## File Structure

```
backend/
├── models/
│   └── quiz_models.py          # Pydantic schemas (request, response, validation)
├── prompts/
│   └── quiz_prompt.py          # Prompt builder + QUIZ_PROMPT_VERSION
├── services/
│   └── quiz_service.py         # QuizService (core generation logic)
├── validators/
│   └── quiz_validator.py       # Deterministic structural validator
├── mocks/
│   └── mock_llm_service.py     # MockLLMService + fixture JSON for tests
└── tests/
    └── test_quiz.py            # 46 unit tests (no real LLM calls)
```

---

## Input Schema — `QuizGenerationRequest`

```json
{
  "subject": "Science",
  "topic": "Photosynthesis",
  "grade": 8,
  "difficulty": "intermediate",
  "question_count": 5,
  "question_types": ["mcq", "true_false", "short_answer"],
  "learning_objective": "Understand how plants make food",
  "bloom_levels": ["remember", "understand", "apply"],
  "curriculum_context": [
    {
      "content": "Green plants prepare food using CO2, water and sunlight...",
      "source": "CBSE_Science.pdf",
      "page_number": 82
    }
  ]
}
```

> All field names are canonical. Do **not** rename them.

---

## Output Schema — `QuizResponse`

```json
{
  "title": "Photosynthesis Assessment",
  "subject": "Science",
  "topic": "Photosynthesis",
  "grade": 8,
  "difficulty": "intermediate",
  "question_count": 5,
  "questions": [
    {
      "id": "q1",
      "question": "Which pigment helps plants absorb light energy?",
      "type": "mcq",
      "difficulty": "easy",
      "bloom_level": "remember",
      "options": ["Chlorophyll", "Hemoglobin", "Keratin", "Melanin"],
      "correct_answer": "Chlorophyll",
      "explanation": "Chlorophyll absorbs light energy used during photosynthesis."
    }
  ],
  "sources_used": [
    { "source": "CBSE_Science.pdf", "page_number": 82 }
  ]
}
```

---

## Validation Report — `ValidationResult`

```json
{
  "valid": true,
  "checks": {
    "question_count_valid": true,
    "all_questions_have_text": true,
    "all_questions_have_type": true,
    "all_questions_have_answers": true,
    "all_questions_have_explanations": true,
    "mcq_has_options": true,
    "mcq_prefers_four_options": true,
    "mcq_answers_in_options": true,
    "no_duplicate_options": true,
    "no_duplicate_questions": true,
    "difficulties_valid": true,
    "bloom_levels_valid": true,
    "true_false_answers_valid": true
  },
  "warnings": [],
  "errors": []
}
```

### Validation Rules

| # | Check | Type |
|---|---|---|
| 1 | Question count matches requested count | Error |
| 2 | All questions have non-empty text | Error |
| 3 | All questions have a valid type | Error |
| 4 | All questions have a correct_answer | Error |
| 5 | All questions have an explanation | Error |
| 6 | MCQ questions have options | Error |
| 7 | MCQ questions have exactly 4 options | **Warning** |
| 8 | MCQ correct_answer exists in options | Error |
| 9 | No duplicate options within any MCQ | Error |
| 10 | No exact duplicate questions (normalised) | Error |
| 11 | Difficulty values are in allowed set | Error |
| 12 | Bloom level values are in allowed set | Error |
| 13 | True/False answers are "True" or "False" | Error |

---

## Answer Key

```python
from backend.validators.quiz_validator import generate_answer_key

key = generate_answer_key(quiz)
# key.entries: [{ question_id, answer, explanation }, ...]
```

No additional LLM call is made.

---

## How Person 4 Passes RAG Context

```python
curriculum_context = [
    {
        "content": "Green plants prepare their own food...",
        "source": "CBSE_Science.pdf",
        "page_number": 82
    }
]
request = QuizGenerationRequest(
    ...,
    curriculum_context=curriculum_context
)
```

Sources are preserved verbatim in `sources_used` — the LLM never invents citations.

---

## How Person 5 Integrates QuizService

```python
from backend.services.quiz_service import QuizService
from backend.validators.quiz_validator import generate_answer_key

quiz_service = QuizService(llm_service)          # inject Person 5's LLM service

quiz, validation = await quiz_service.generate_quiz(request)
answer_key = generate_answer_key(quiz)

# Persist quiz, questions, validation, answer_key via Person 5's DB layer
# Log: feature="quiz_generation", prompt_version=quiz_service.prompt_version
```

---

## How Person 1 Consumes the Result

```json
quiz.questions[i]:
  id           → "q1"
  question     → display text
  type         → "mcq" | "true_false" | "short_answer"
  options      → list for MCQ/T-F, [] for short_answer
  correct_answer → show on "Show Answer" click
  explanation  → show below answer
  bloom_level  → badge display
  difficulty   → badge display

validation.checks → Quality Check UI (✓ / ✗)
validation.warnings → optional display
```

---

## Running Tests

```bash
# From teachmate-ai/ root
pip install pydantic pytest pytest-asyncio
pytest backend/tests/ -v
```

**46 tests, 0 real LLM calls, 0 API costs.**

---

## Environment Variables Required

| Variable | Used By | Notes |
|---|---|---|
| `GEMINI_API_KEY` or `OPENAI_API_KEY` | Person 5's LLMService | **Not** used in this module |

This module never reads API keys. All LLM access is injected via `LLMServiceProtocol`.

---

## Dependencies

```
pydantic>=2.0,<3.0
pytest>=7.0
pytest-asyncio>=0.23
```

---

## Known Limitations

1. **Factual accuracy** is not verified. Curriculum grounding reduces hallucination risk; teacher review is required.
2. Bloom distribution is **approximate** — exact mathematical splitting is intentionally not enforced.
3. Duplicate detection uses **lexical normalisation** (not semantic embeddings) — near-duplicates with different wording may not be caught.
4. The optional repair attempt covers only **question-count mismatch**; other structural failures return validation errors for the caller to handle.
5. LLM output quality depends on the model version used (owned by Person 5).

---

## Git Commit Suggestion

```
feat: add AI quiz generation and assessment validation

- QuizGenerationRequest + QuizResponse Pydantic models
- MCQ, True/False, Short Answer generation
- Difficulty (easy/intermediate/hard) and Bloom's Taxonomy support
- Dedicated quiz prompt with curriculum injection + prompt injection protection
- Deterministic QuizValidator with 13 structural checks
- Answer key extraction (no extra LLM call)
- MockLLMService for isolated unit testing
- 46 unit tests, 0 real LLM calls
- QUIZ_PROMPT_VERSION = "quiz_v1" for generation logging
```
