"""
Content Transformation Prompts (Simplification, Younger-Level, Analogy, Real-World Example).
TeachMate AI - Person 2 (Lesson Planner + Simplification AI).
"""

from backend.models.lesson_models import (
    ContentTransformationRequest,
    TransformationMode,
)

SIMPLIFY_PROMPT_VERSION = "simplify_v1"


def get_mode_instructions(request: ContentTransformationRequest) -> str:
    """Returns specialized prompt instructions based on the requested transformation mode."""
    target_younger_grade = max(1, request.grade - 3)

    if request.mode == TransformationMode.SIMPLIFY:
        return f"""MODE: SIMPLIFY (Same Grade Level)
- Target Audience: Grade {request.grade} students.
- Goal: Reduce vocabulary complexity and break down long, convoluted sentences.
- Constraints:
  * Maintain all underlying scientific, mathematical, or factual accuracy.
  * Do NOT dumb down the essential concepts—make them crystal clear.
  * Use active voice and intuitive phrasing."""

    elif request.mode == TransformationMode.YOUNGER_LEVEL:
        return f"""MODE: YOUNGER LEVEL EXPLANATION
- Target Audience: Approximate Grade {target_younger_grade} students (younger learners).
- Goal: Explain the core essence of this concept so a Grade {target_younger_grade} student can understand.
- Constraints:
  * Use everyday, friendly vocabulary and relatable scenarios.
  * Avoid technical jargon unless immediately explained with simple words.
  * Keep the explanation warm, engaging, and easy to follow.
  * Do NOT distort scientific/factual truth."""

    elif request.mode == TransformationMode.ANALOGY:
        return f"""MODE: ANALOGY GENERATION
- Target Audience: Grade {request.grade} students.
- Goal: Produce a vivid, memorable, and concrete real-world analogy.
- Example: Photosynthesis can be compared to a solar-powered kitchen where sunlight is electricity, water and CO2 are recipe ingredients, glucose is the prepared meal, and oxygen is clean steam released.
- Constraints:
  * Clearly map the key components of the analogy to the conceptual components.
  * Ensure the analogy does NOT introduce scientifically misleading or contradictory relationships.
  * Make it visually intuitive and immediately relatable for Grade {request.grade}."""

    elif request.mode == TransformationMode.REAL_WORLD_EXAMPLE:
        return f"""MODE: REAL-WORLD EXAMPLE
- Target Audience: Grade {request.grade} students.
- Goal: Provide an authentic, observable real-world example or practical modern application.
- Example: For friction, how bicycle brake pads clamp onto wheels to safely stop a cyclist.
- Constraints:
  * Must be an everyday situation, modern technology, or natural phenomenon students recognize.
  * Keep it concise, age-appropriate, and directly illustrative of the concept."""

    else:
        return f"Transform the text appropriately for Grade {request.grade}."


def build_transformation_prompt(request: ContentTransformationRequest) -> str:
    """
    Constructs the prompt for transforming an existing content block.
    """
    mode_instructions = get_mode_instructions(request)

    prompt = f"""=== ROLE ===
You are an expert pedagogical communicator and master teacher known for making complex ideas accessible, intuitive, and engaging.

=== CONTEXT ===
- Subject: {request.subject}
- Topic: {request.topic}
- Student Grade: Grade {request.grade}
- Requested Mode: {request.mode.value}

=== ORIGINAL CONTENT TO TRANSFORM ===
\"\"\"
{request.content}
\"\"\"

=== INSTRUCTIONS ===
{mode_instructions}

=== OUTPUT FORMAT ===
Return ONLY a valid JSON object matching the schema below. Do NOT include markdown code fences, comments, or backticks.

{{
    "mode": "{request.mode.value}",
    "transformed_content": "Your complete transformed text here."
}}
"""
    return prompt
