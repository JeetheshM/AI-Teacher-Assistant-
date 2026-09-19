"""
Mock LLM Service for testing and offline development.
TeachMate AI - Person 2 (Lesson Planner + Simplification AI).
"""

import json
import re
from typing import Any, Dict, Optional, Protocol, Type, TypeVar
from pydantic import BaseModel
from backend.models.lesson_models import (
    ExampleItem,
    LessonPlan,
    MisconceptionItem,
    SourceUsed,
    TimedContent,
    TransformationMode,
)

T = TypeVar("T", bound=BaseModel)


class LLMServiceProtocol(Protocol):
    """Protocol for shared LLM service owned by Person 5."""

    async def generate_structured(self, prompt: str, response_model: Type[T]) -> T:
        """Generate and parse structured Pydantic response from the given prompt."""
        ...


class MockLLMService:
    """High-fidelity Mock LLM service implementing LLMServiceProtocol."""

    def __init__(
        self,
        force_error: Optional[Exception] = None,
        custom_lesson: Optional[LessonPlan] = None,
        custom_transformations: Optional[Dict[str, str]] = None,
    ):
        self.force_error = force_error
        self.custom_lesson = custom_lesson
        self.custom_transformations = custom_transformations or {}
        self.call_count = 0
        self.last_prompt: Optional[str] = None

    async def generate_structured(self, prompt: str, response_model: Type[T]) -> T:
        self.call_count += 1
        self.last_prompt = prompt

        if self.force_error is not None:
            raise self.force_error

        if response_model is LessonPlan:
            if self.custom_lesson:
                return self.custom_lesson

            default_lesson = LessonPlan(
                title="Understanding Photosynthesis: How Plants Make Food",
                subject="Science",
                grade=8,
                difficulty="intermediate",
                total_duration_minutes=45,
                objectives=[
                    "Explain the basic chemical equation and biological process of photosynthesis.",
                    "Identify the essential inputs (sunlight, carbon dioxide, water) and outputs (glucose, oxygen).",
                    "Describe the functional role of chlorophyll and chloroplasts in plant cells.",
                ],
                prerequisites=[
                    "Basic knowledge of plant cell structures (cell wall, nucleus, chloroplasts).",
                    "Basic understanding that living things require energy to survive.",
                ],
                introduction=TimedContent(
                    duration_minutes=5,
                    content=(
                        "Teacher Hook: Hold up a fresh green leaf or show an image of a lush forest. "
                        "Ask the class: 'If plants never eat food like animals do, where does all their mass come from?' "
                        "Collect 2-3 student hypotheses, then introduce today's objective: discovering how leaves function as solar-powered food factories."
                    ),
                ),
                explanation=TimedContent(
                    duration_minutes=25,
                    content=(
                        "1. Overview of Photosynthesis: Plants are autotrophs that convert light energy into chemical energy.\n"
                        "2. The Chemical Equation: Carbon Dioxide (from air) + Water (from soil) + Light Energy -> Glucose (sugar/food) + Oxygen (released).\n"
                        "3. Role of Chlorophyll: Chlorophyll is the green pigment in chloroplasts that absorbs light wavelengths (mainly blue and red).\n"
                        "4. Stomata & Roots: Explain how stomata on leaves regulate CO2 intake and O2 release, while root hairs absorb water from soil."
                    ),
                ),
                examples=[
                    ExampleItem(
                        title="The Solar Kitchen Analogy",
                        description=(
                            "Explain that chloroplasts are tiny kitchens, chlorophyll acts like solar panels catching energy, "
                            "water and CO2 are raw ingredients from the pantry, glucose is the baked loaf of bread, and oxygen is the clean steam released."
                        ),
                    ),
                    ExampleItem(
                        title="Underwater Bubbles Demonstration",
                        description=(
                            "Describe an aquatic plant (like Elodea) placed in bright light producing visible oxygen bubbles, "
                            "demonstrating gas production during active photosynthesis."
                        ),
                    ),
                ],
                key_points=[
                    "Photosynthesis converts light energy into stored chemical energy (glucose).",
                    "Inputs: Carbon dioxide (absorbed via stomata), water (absorbed via roots), sunlight (captured by chlorophyll).",
                    "Outputs: Glucose (stored food for growth) and oxygen (released into the atmosphere).",
                    "Occurs primarily inside chloroplasts in green plant leaves.",
                ],
                common_misconceptions=[
                    MisconceptionItem(
                        misconception="Plants get all their food and nutrients directly from soil.",
                        correction="Soil provides minerals and water, but plants synthesize their actual organic food (sugars) from air and sunlight.",
                    ),
                    MisconceptionItem(
                        misconception="Plants only perform photosynthesis, not respiration.",
                        correction="Plants respire continuously, taking in oxygen to release energy from glucose, just like other organisms.",
                    ),
                ],
                recap=TimedContent(
                    duration_minutes=10,
                    content=(
                        "Quick Formative Check:\n"
                        "1. Ask students to write down the 3 inputs and 2 outputs on personal whiteboards.\n"
                        "2. Cold-call two students to explain why leaves are usually green.\n"
                        "3. Summary recap: emphasize the interdependence of plants and oxygen-breathing organisms on Earth."
                    ),
                ),
                teacher_tips=[
                    "Sketch the leaf cross-section with arrows for CO2 entering and O2 exiting on the board.",
                    "If students struggle with chemical equations, use word cards before introducing chemical formulas.",
                ],
                sources_used=[SourceUsed(source="CBSE_Science.pdf", page_number=82)],
            )
            return default_lesson

        prompt_lower = prompt.lower()
        if "mode: simplify" in prompt_lower or '"mode": "simplify"' in prompt_lower:
            mode = TransformationMode.SIMPLIFY
            content = self.custom_transformations.get(
                "simplify",
                "Plants make their own food using sunlight. They take water from the soil and carbon dioxide from the air, turn them into sugar for energy, and give off oxygen.",
            )
        elif "mode: younger_level" in prompt_lower or '"mode": "younger_level"' in prompt_lower:
            mode = TransformationMode.YOUNGER_LEVEL
            content = self.custom_transformations.get(
                "younger_level",
                "Think of a plant like a sun chef! Green leaves catch warm sunshine and mix it with water and air to bake tasty plant treats.",
            )
        elif "mode: analogy" in prompt_lower or '"mode": "analogy"' in prompt_lower:
            mode = TransformationMode.ANALOGY
            content = self.custom_transformations.get(
                "analogy",
                "Think of a leaf as a miniature solar-powered kitchen. Sunlight is the electricity, water and carbon dioxide are ingredients, and glucose is the meal the plant makes.",
            )
        elif "mode: real_world_example" in prompt_lower or '"mode": "real_world_example"' in prompt_lower:
            mode = TransformationMode.REAL_WORLD_EXAMPLE
            content = self.custom_transformations.get(
                "real_world_example",
                "Ever notice tiny bubbles on pond plants on a sunny afternoon? Those bubbles are oxygen being released while the plant makes food.",
            )
        else:
            mode = TransformationMode.SIMPLIFY
            content = "Transformed pedagogical content for students."

        try:
            return response_model(
                mode=mode,
                original_content="Original text",
                transformed_content=content,
                grade=8,
            )
        except Exception:
            return response_model.model_validate({
                "mode": mode.value if hasattr(mode, "value") else str(mode),
                "transformed_content": content,
            })

    async def generate_text(self, prompt: str) -> str:
        """Return a compact quiz payload for offline/demo execution."""
        topic = "the lesson topic"
        lower_prompt = prompt.lower()
        if "photosynthesis" in lower_prompt:
            topic = "Photosynthesis"
        elif "ecosystem" in lower_prompt:
            topic = "Ecosystems"
        elif "fractions" in lower_prompt:
            topic = "Fractions"

        count_match = re.search(r"generate exactly (\d+)", lower_prompt)
        question_count = int(count_match.group(1)) if count_match else 2
        question_templates = [
            (
                f"Which statement best describes {topic}?",
                "mcq",
                "It is the main process being studied in this lesson.",
                [
                    "It is the main process being studied in this lesson.",
                    "It is unrelated to the topic.",
                    "Only the teacher should know it.",
                    "It is a random fact with no learning value.",
                ],
                "understand",
            ),
            (
                f"What is one key idea students should remember about {topic}?",
                "short_answer",
                "The main idea is the core concept or process being taught.",
                [],
                "remember",
            ),
            (
                f"Which input is important when learning about {topic}?",
                "mcq",
                "The conditions and materials involved in the process.",
                [
                    "The conditions and materials involved in the process.",
                    "An unrelated classroom rule.",
                    "A random number with no context.",
                    "A topic from a different subject.",
                ],
                "understand",
            ),
            (
                f"How can students apply their understanding of {topic}?",
                "short_answer",
                "Students can explain the process using a relevant example.",
                [],
                "apply",
            ),
            (
                f"What should students compare when studying {topic}?",
                "mcq",
                "The key inputs, steps, and outcomes of the process.",
                [
                    "The key inputs, steps, and outcomes of the process.",
                    "Only the page number of the textbook.",
                    "Unrelated facts from another lesson.",
                    "The classroom seating arrangement.",
                ],
                "analyze",
            ),
        ]
        questions = []
        for question, question_type, correct_answer, options, bloom_level in question_templates[:question_count]:
            questions.append({
                "question": question,
                "type": question_type,
                "difficulty": "intermediate",
                "bloom_level": bloom_level,
                "options": options,
                "correct_answer": correct_answer,
                "explanation": f"This checks understanding of {topic}.",
            })

        return json.dumps({
            "questions": questions
        })
