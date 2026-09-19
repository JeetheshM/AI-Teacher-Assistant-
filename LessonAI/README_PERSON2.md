# TeachMate AI - Module 2: Lesson Planner + Simplification AI

**Owner:** PERSON 2 (Lesson Planner + Simplification AI Developer)  
**Status:** Complete & Tested (24/24 unit tests passing)

---

## 1. Module Overview & Purpose
This module is the core pedagogical intelligence layer of **TeachMate AI**. It transforms teacher inputs (subject, topic, grade, duration, difficulty, learning objective) and optional retrieved curriculum context into a classroom-ready, structured teaching package. It also provides 4 on-demand content transformations:
- **`simplify`**: Reduces vocabulary and sentence complexity for the same grade.
- **`younger_level`**: Explains the concept intuitively for younger learners (~2-3 grades lower).
- **`analogy`**: Generates a vivid, concrete, relatable physical metaphor.
- **`real_world_example`**: Provides an authentic, everyday observation or practical application.

---

## 2. Directory Structure

```
backend/
├── models/
│   ├── __init__.py
│   └── lesson_models.py          # Strict Pydantic v2 schemas preserving all shared field names
├── prompts/
│   ├── __init__.py
│   ├── lesson_prompt.py          # LESSON_PROMPT_VERSION = "lesson_v1" with prompt safety guards
│   └── simplify_prompt.py        # SIMPLIFY_PROMPT_VERSION = "simplify_v1" for multi-mode transformations
├── validators/
│   ├── __init__.py
│   └── lesson_validator.py       # Deterministic structural, duration tolerance, and source checks
├── services/
│   ├── __init__.py
│   ├── lesson_service.py         # LessonService orchestrating prompt -> LLM -> validator -> response
│   └── simplification_service.py # SimplificationService for the 4 transformation modes
├── mocks/
│   ├── __init__.py
│   └── mock_llm_service.py       # Production-quality offline Mock LLM simulating Photosynthesis Gr 8
├── api/
│   ├── __init__.py
│   ├── lessons_router.py         # FastAPI APIRouter stub for POST /api/lessons/generate
│   └── simplify_router.py        # FastAPI APIRouter stub for POST /api/simplify
└── tests/
    ├── __init__.py
    ├── test_lesson_service.py    # Unit tests for lesson generation, transformations, and error handling
    ├── test_lesson_validator.py  # Unit tests for duration tolerance, missing fields, duplicate removal
    └── test_api_routers.py       # Integration tests for FastAPI endpoints
```

---

## 3. Shared Data Contracts

### 3.1 Input: LessonGenerationRequest
```json
{
  "subject": "Science",
  "topic": "Photosynthesis",
  "grade": 8,
  "duration_minutes": 45,
  "difficulty": "intermediate",
  "learning_objective": "Understand how plants make food using sunlight, carbon dioxide and water",
  "curriculum_context": [
    {
      "content": "Green plants prepare their own food using carbon dioxide and water in the presence of sunlight and chlorophyll. Oxygen is released during this process.",
      "source": "CBSE_Science.pdf",
      "page_number": 82
    }
  ]
}
```

### 3.2 Output: LessonPlan
```json
{
  "title": "Understanding Photosynthesis: How Plants Make Food",
  "subject": "Science",
  "grade": 8,
  "difficulty": "intermediate",
  "total_duration_minutes": 45,
  "objectives": [
    "Explain the basic chemical equation and biological process of photosynthesis.",
    "Identify the essential inputs (sunlight, carbon dioxide, water) and outputs (glucose, oxygen)."
  ],
  "prerequisites": [
    "Basic knowledge of plant cell structures (chloroplasts)."
  ],
  "introduction": {
    "duration_minutes": 5,
    "content": "Hold up a fresh green leaf. Ask: 'Where does a giant tree's mass come from if it never eats food?'"
  },
  "explanation": {
    "duration_minutes": 25,
    "content": "Core instructional breakdown of light absorption, chlorophyll, stomata gas exchange, and glucose storage."
  },
  "examples": [
    {
      "title": "The Solar Kitchen Analogy",
      "description": "Leaves act as tiny solar kitchens where sunlight powers the stove to turn water and CO2 into sugar."
    }
  ],
  "key_points": [
    "Inputs: Water, carbon dioxide, sunlight.",
    "Outputs: Glucose, oxygen.",
    "Chlorophyll captures light energy inside chloroplasts."
  ],
  "common_misconceptions": [
    {
      "misconception": "Plants absorb their food directly from the soil.",
      "correction": "Soil provides water and minerals; plants manufacture their organic food (glucose) from sunlight and air."
    }
  ],
  "recap": {
    "duration_minutes": 15,
    "content": "Quick check for understanding questions and whiteboard input/output drill."
  },
  "teacher_tips": [
    "Use a leaf diagram on the board showing arrows for CO2 entering and O2 exiting."
  ],
  "sources_used": [
    {
      "source": "CBSE_Science.pdf",
      "page_number": 82
    }
  ]
}
```

### 3.3 Quality Validation: LessonValidationResult
```json
{
  "valid": true,
  "checks": {
    "has_title": true,
    "has_subject": true,
    "has_valid_grade": true,
    "has_objectives": true,
    "has_introduction": true,
    "has_explanation": true,
    "has_recap": true,
    "has_key_points": true,
    "durations_positive": true,
    "duration_reasonable": true,
    "sources_grounded": true
  },
  "warnings": [],
  "disclaimer": "Structural and duration validation only. Does not guarantee factual correctness; teacher review required."
}
```

### 3.4 Content Transformation: ContentTransformationRequest & Response
**Request (`POST /api/simplify`):**
```json
{
  "content": "Photosynthesis converts light energy into chemical energy through complex biochemical pathways in the chloroplasts.",
  "subject": "Science",
  "topic": "Photosynthesis",
  "grade": 8,
  "mode": "analogy"
}
```
*Supported modes:* `"simplify"`, `"younger_level"`, `"analogy"`, `"real_world_example"`.

**Response:**
```json
{
  "mode": "analogy",
  "original_content": "Photosynthesis converts light energy into chemical energy through complex biochemical pathways in the chloroplasts.",
  "transformed_content": "Think of a plant like a solar-powered kitchen! Sunlight provides the electricity, water and air are the ingredients, and the leaf bakes sugar meals while puffing out fresh oxygen.",
  "grade": 8
}
```

---

## 4. Team Integration Guide

### 4.1 For Person 4 (RAG / Curriculum Context Developer)
- You pass retrieved chunks to the lesson generator via `curriculum_context`.
- Each chunk should conform to:
  ```python
  CurriculumChunk(
      content="...",      # Retrieved excerpt
      source="CBSE.pdf",  # Filename
      page_number=82      # Optional integer page number
  )
  ```
- **Security Guardrail:** Lesson generation wraps your chunks inside `<curriculum_context>` with strict system instructions that they are informational reference material only, preventing prompt injection attacks from malicious PDF contents.
- **Source Preservation:** The validator deterministically reconciles unique `(source, page_number)` pairs directly from your input chunks, preventing LLM citation hallucination.

### 4.2 For Person 5 (Backend / Database / Shared LLM Service Developer)
- **Dependency Injection:** `LessonService` accepts any LLM service satisfying the `LLMServiceProtocol`:
  ```python
  class LLMServiceProtocol(Protocol):
      async def generate_structured(self, prompt: str, response_model: Type[T]) -> T:
          ...
  ```
- **Mounting FastAPI Routers:** You can mount our pre-built routers directly in `main.py`:
  ```python
  from backend.api.lessons_router import create_lessons_router
  from backend.api.simplify_router import create_simplify_router
  from backend.services.lesson_service import LessonService
  from backend.services.simplification_service import SimplificationService

  # Inject your shared LLM service instance:
  lesson_svc = LessonService(shared_llm_service)
  simplify_svc = SimplificationService(shared_llm_service)

  app.include_router(create_lessons_router(lesson_svc))
  app.include_router(create_simplify_router(simplify_svc))
  ```
- **Observability Metadata:**
  - `prompt_version`: `"lesson_v1"` and `"simplify_v1"` are exposed in every response and as module constants (`LESSON_PROMPT_VERSION`, `SIMPLIFY_PROMPT_VERSION`) for logging into `GENERATION_LOGS`.

### 4.3 For Person 1 (Frontend Developer)
- **Endpoints Exposed:**
  - `POST /api/lessons/generate`: Returns `{ "lesson": {...}, "validation": {...}, "prompt_version": "lesson_v1" }`
  - `POST /api/simplify`: Returns `{ "mode": "...", "original_content": "...", "transformed_content": "...", "grade": 8 }`
- **UI Tabs Supported:**
  - **[Lesson]**: Render `title`, `objectives`, `introduction`, `explanation`, `key_points`, `recap`, `teacher_tips`.
  - **[Explain] / Transformations**: When teacher clicks "Simplify", "Younger Learner", "Analogy", or "Real-world Example", call `POST /api/simplify` with the selected section's content.
  - **[Sources]**: Render `sources_used` (e.g. `CBSE_Science.pdf - Page 82`).
  - **AI Quality Check Indicator**: Render `validation.checks` with green checks (e.g. ✓ Objectives present, ✓ Timing aligned, ✓ Grounded in curriculum).

---

## 5. How to Run Tests

All unit tests run completely offline with **zero paid LLM calls** using `MockLLMService`:

```bash
# Using standard Python unittest
py -3 -m unittest discover -s backend/tests -p "test_*.py" -v
```

### Test Coverage (24/24 Passed):
1. `test_valid_lesson_request_produces_structured_lesson` (P0: Structured JSON output)
2. `test_empty_topic_rejected` (Validation error)
3. `test_empty_subject_rejected`
4. `test_invalid_grade_rejected`
5. `test_invalid_difficulty_rejected`
6. `test_missing_objectives_fails_validation`
7. `test_duration_mismatch_creates_warning` (Tolerance checking)
8. `test_duration_within_tolerance_passes`
9. `test_negative_or_zero_duration_fails`
10. `test_simplification_mode_works` (P0: Simplify)
11. `test_younger_level_mode_works` (P2: Younger level)
12. `test_analogy_mode_works` (P1: Analogy)
13. `test_real_world_example_mode_works` (P1: Real-world example)
14. `test_malformed_llm_response_handled_gracefully` (Error wrap, no system crashes)
15. `test_curriculum_source_metadata_preserved_and_deduplicated`
16. `test_no_curriculum_context_generates_clean_fallback`
17. `test_prompt_version_constants`
18. `test_disclaimer_present` (No false claims of factual verification)
19. `test_post_lessons_generate` (FastAPI router)
20. `test_post_simplify_modes` (FastAPI router)
21. `test_invalid_request_returns_422_or_400` (HTTP error handling)

---

## 6. Known Limitations & Judging Transparency
1. **Teacher in Control:** Deterministic validation checks structural integrity, completeness, and timing consistency. It does NOT guarantee factual infallibility; the teacher remains the final editor and authority.
2. **Grounding Quality:** Grounding fidelity depends on relevant chunk retrieval from the RAG service (Person 4). When no curriculum context is supplied, the module gracefully falls back to standard curriculum standards without falsifying citations.
