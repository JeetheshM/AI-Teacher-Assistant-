// TeachMate AI - Hackathon Demo Scenario Mock Data
// Scenario: Photosynthesis (Grade 8, 45 min, Science, Intermediate, CBSE_Science.pdf grounded)

import {
  LessonPlan,
  QuizPlan,
  ActivityPlan,
  CurriculumSource,
  TransformationResult,
  DocumentUploadResponse,
  GenerationMetadata
} from '../types';

export const MOCK_DOCUMENT: DocumentUploadResponse = {
  document_id: 'doc_cbse_sci_gr8_ch01',
  filename: 'CBSE_Science_Grade8_Ch01.pdf',
  file_type: 'application/pdf',
  page_count: 14,
  status: 'ready',
  message: 'Curriculum document indexed successfully (24 chunks)'
};

export const MOCK_SOURCES: CurriculumSource[] = [
  {
    document_id: 'doc_cbse_sci_gr8_ch01',
    source: 'CBSE_Science_Grade8_Ch01.pdf',
    page_number: 82,
    chunk_id: 'chunk_p82_c01',
    content: 'Green plants prepare their own food through the process of photosynthesis. They utilize solar energy trapped by chlorophyll, absorbed water from root systems, and atmospheric carbon dioxide through stomata.'
  },
  {
    document_id: 'doc_cbse_sci_gr8_ch01',
    source: 'CBSE_Science_Grade8_Ch01.pdf',
    page_number: 84,
    chunk_id: 'chunk_p84_c03',
    content: 'The overall chemical equation of photosynthesis is: 6CO2 + 6H2O + Light Energy -> C6H12O6 (Glucose) + 6O2. Oxygen is released as a vital byproduct into the atmosphere through stomatal pores.'
  },
  {
    document_id: 'doc_cbse_sci_gr8_ch01',
    source: 'CBSE_Science_Grade8_Ch01.pdf',
    page_number: 85,
    chunk_id: 'chunk_p85_c02',
    content: 'Chloroplasts containing chlorophyll pigment are primarily concentrated in the mesophyll cells of plant leaves, acting as microscopic solar-energy converters.'
  }
];

export const MOCK_METADATA: GenerationMetadata = {
  model: 'gemini-1.5-pro / claude-3-5-sonnet',
  prompt_version: 'teachmate_v1.2',
  curriculum_grounded: true,
  retrieved_sources_count: 3,
  validation_status: 'passed',
  latency_ms: 1840,
  input_tokens: 1420,
  output_tokens: 980
};

export const MOCK_LESSON: LessonPlan = {
  id: 101,
  title: 'Photosynthesis: How Plants Harness Solar Energy',
  subject: 'Science',
  grade: 8,
  duration_minutes: 45,
  difficulty: 'intermediate',
  learning_objective: 'Understand how plants produce food using sunlight, carbon dioxide, and water, and identify key inputs and outputs.',
  document_id: 'doc_cbse_sci_gr8_ch01',
  objectives: [
    'Define photosynthesis and state its fundamental chemical equation.',
    'Identify the three essential inputs (water, carbon dioxide, sunlight) and two outputs (glucose, oxygen).',
    'Explain the crucial role of chlorophyll and chloroplasts in light absorption.',
    'Differentiate between plant autotrophic nutrition and human heterotrophic nutrition.'
  ],
  prerequisites: [
    'Basic knowledge of plant structures (roots, stems, leaves, stomata).',
    'Introductory familiarity with atoms, molecules (CO2, H2O, O2), and solar radiation.'
  ],
  introduction: {
    duration_minutes: 5,
    content: 'Hook the class by asking: "If animals must hunt or forage for every meal, how do giant trees stay nourished without moving an inch?" Introduce the term autotrophs and reveal that leaves function as biological solar-powered kitchens.'
  },
  explanation: {
    duration_minutes: 20,
    content: `Photosynthesis is the biochemical process whereby green plants convert light energy into chemical energy stored in glucose molecules. 

1. Raw Materials Intake:
   • Carbon Dioxide (CO2): Absorbed from atmospheric air via microscopic pores on leaf undersides called stomata.
   • Water (H2O): Taken up by root hair cells through osmosis and conducted upward to leaves via xylem vessels.
   • Sunlight: Solar photons are trapped by the green pigment chlorophyll housed in cellular organelles called chloroplasts.

2. The Transformation:
   Inside the chloroplasts, solar photons split water molecules and recombine carbon with hydrogen to synthesize glucose (C6H12O6), synthesizing the chemical bonds of sugar.

3. The Byproducts:
   Oxygen (O2) is produced during water photolysis and released back into the atmosphere through stomata, sustaining aerobic planetary life.`
  },
  examples: [
    'Aquatic Elodea plants bubbling oxygen beads when exposed to bright lamps in a laboratory beaker.',
    'Variegated leaves (like Coleus or Pothos) where only the green sections containing chlorophyll produce starch when tested with iodine solution.'
  ],
  key_points: [
    'Equation: 6CO2 + 6H2O + Sunlight -> C6H12O6 + 6O2.',
    'Chlorophyll is essential for capturing radiant photon energy.',
    'Glucose is used for plant respiration, cellular growth, or stored as insoluble starch.',
    'Oxygen released supports almost all multicellular life on Earth.'
  ],
  common_misconceptions: [
    {
      misconception: 'Plants absorb their "food" directly from the soil through roots.',
      correction: 'Soil provides water and dissolved trace minerals only. True biochemical food (sugars) is manufactured exclusively in leaves via photosynthesis.'
    },
    {
      misconception: 'Photosynthesis replaces cellular respiration in plants.',
      correction: 'Plants photosynthesize to create glucose when light is present, but they continually perform cellular respiration day and night to release energy.'
    }
  ],
  recap: {
    duration_minutes: 5,
    content: 'Quick 60-second summary: Inputs = Sun + Water + CO2. Location = Chloroplasts in leaves. Outputs = Glucose (stored energy) + Oxygen (breathable air).'
  },
  total_duration_minutes: 45,
  teacher_tips: [
    'Keep an actual potted plant or freshly plucked leaf on the demonstration desk for physical context.',
    'Use the "Solar Kitchen" analogy for students struggling with the chemical formula abstraction.'
  ],
  sources_used: MOCK_SOURCES,
  validation: {
    learning_objectives_present: true,
    explanation_generated: true,
    duration_aligned: true,
    key_points_included: true,
    curriculum_grounded: true,
    notes: 'Structural verification passed. 4 learning objectives aligned with Grade 8 curriculum benchmark.'
  },
  metadata: MOCK_METADATA
};

export const MOCK_TRANSFORMATIONS: Record<string, TransformationResult> = {
  simplify: {
    mode: 'simplify',
    title: 'Simplified Explanation',
    tagline: 'Direct, clear, jargon-reduced concept breakdown',
    transformed_content: `Think of a plant as a tiny solar-powered kitchen! 

Instead of going to the grocery store, green leaves use three simple ingredients to cook their own food:
1. Sunlight: The heat and light from the sun acts as the oven's power switch.
2. Water: Drawn up from the roots like drinking through a tiny straw.
3. Air (Carbon Dioxide): Breathed in through tiny invisible mouth-pores under the leaf called stomata.

The plant mixes these together to make sugar for itself to grow big and strong, and as a thank-you gift, it breathes out fresh clean oxygen for all of us!`
  },
  younger_level: {
    mode: 'younger_level',
    title: 'Explained for Younger Learners (Grades 4-6)',
    tagline: 'Friendly, vivid, story-driven explanation',
    transformed_content: `Did you know trees have green superpowers? 

Inside every green leaf lives a friendly green superhero called "Chlorophyll". Whenever the sun shines, Chlorophyll reaches up its arms and catches sunlight like a baseball.

Then the leaf drinks a sip of water from underground, catches a whisper of air, and bakes sweet plant-sugar! 

And the coolest part? When plants finish baking their sweet lunch, they exhale the clean oxygen that you and I breathe right now!`
  },
  analogy: {
    mode: 'analogy',
    title: 'Intuitive Analogy: The Solar Bakery',
    tagline: 'Memorable conceptual metaphor',
    transformed_content: `A leaf is like an ultra-modern rooftop bakery:

• The Solar Panels: Chlorophyll acts as rooftop solar panels, capturing clean electric energy from rays of sunshine.
• The Ingredients: Water is piped into the kitchen from the plumbing (roots), and Carbon Dioxide is drafted in through the ventilation vents (stomata).
• The Master Chef: Chloroplasts mix the water and carbon together using solar power.
• The Baked Goods: Fresh warm loaves of bread (Glucose) that feed the household.
• The Pleasant Aroma: Extra fresh oxygen released out the window into the neighborhood for everyone to breathe.`
  },
  real_world_example: {
    mode: 'real_world_example',
    title: 'Real-World Connection: Window Sill Plants & Global Forests',
    tagline: 'Tangible application connecting theory to everyday experience',
    transformed_content: `Have you ever noticed a houseplant placed near a window bending toward the glass? 

That is called phototropism! The plant is physically angling its leaf surfaces to maximize the solar energy hitting its chloroplasts. 

On a planetary scale, the Amazon Rainforest produces about 20% of Earth's land-based photosynthetic oxygen. This is why preserving old-growth forests and planting trees in cities acts as our planet's natural carbon scrubber—locking away industrial carbon dioxide into wood while pumping out cool, fresh air.`
  }
};

export const MOCK_ACTIVITY: ActivityPlan = {
  id: 301,
  title: 'Photosynthesis Recipe Challenge & Leaf Diagramming',
  activity_type: 'Collaborative Group Investigation',
  objective: 'Students will physically map the biochemical flow of photosynthesis by creating an interactive visual recipe diagram in small teams.',
  duration_minutes: 15,
  group_size: 4,
  materials: [
    'Chart paper or whiteboard sheets (1 per group)',
    'Set of colored markers (Green, Yellow, Blue, Red)',
    'Cut-out symbol cards (Sun, H2O drop, CO2 cloud, Glucose cube, O2 bubble)',
    'Glue stick or tape'
  ],
  setup: 'Divide students into balanced teams of 4. Distribute one chart paper and marker set to each table.',
  instructions: [
    'Step 1 (3 min): Draw a large cross-section of a green leaf in the center of your chart using the green marker.',
    'Step 2 (4 min): Position and label the 3 INGREDIENTS (Sunlight entering from top, Water entering through stem/vein, CO2 entering through stomata on underside).',
    'Step 3 (4 min): Position and label the 2 PRODUCTS (Glucose stored in the leaf tissue, Oxygen exiting into the air).',
    'Step 4 (4 min): Team Lightning Round: One student from each team acts as the "Chloroplast Chef" and gives a 30-second presentation explaining their diagram to a neighboring table.'
  ],
  teacher_role: 'Circulate among tables. Probe with guiding questions: "Where did this oxygen molecule come from?" and verify stomata are placed on leaf undersides.',
  student_role: 'Collaborate actively: 1 Illustrator, 1 Chemical Scribe, 1 Timekeeper, 1 Presenter.',
  expected_outcome: 'Every group finishes an accurate, color-coded diagram clearly distinguishing biochemical inputs from metabolic outputs.',
  assessment_method: 'Quick visual rubric check: Correct input placement (2 pts), Correct output placement (2 pts), Accurate verbal explanation (1 pt).',
  safety_notes: 'Standard classroom etiquette with marker caps and paper scissors.',
  adaptations: [
    'For advanced learners: Require students to write the balanced chemical coefficients (6CO2 + 6H2O).',
    'For students needing support: Provide pre-printed leaf templates with dotted arrow outlines.'
  ]
};

export const MOCK_QUIZ: QuizPlan = {
  id: 401,
  title: 'Photosynthesis Mastery & Concept Assessment',
  difficulty: 'intermediate',
  questions: [
    {
      id: 1,
      question: 'Which specialized plant pigment is responsible for absorbing sunlight to power photosynthesis?',
      type: 'mcq',
      difficulty: 'easy',
      bloom_level: 'remember',
      options: ['Chlorophyll', 'Hemoglobin', 'Keratin', 'Melanin'],
      correct_answer: 'Chlorophyll',
      explanation: 'Chlorophyll is the green pigment located inside chloroplasts that traps light photon energy needed to initiate the photosynthesis reaction.'
    },
    {
      id: 2,
      question: 'True or False: Oxygen generated by plants during photosynthesis originates directly from the split of carbon dioxide (CO2) molecules.',
      type: 'true_false',
      difficulty: 'intermediate',
      bloom_level: 'understand',
      options: ['True', 'False'],
      correct_answer: 'False',
      explanation: 'False. Photolysis splits water molecules (H2O), releasing oxygen (O2) as a byproduct. The carbon from CO2 is incorporated into glucose.'
    },
    {
      id: 3,
      question: 'What are the microscopic openings typically found on the undersides of leaves that regulate gas exchange called?',
      type: 'short_answer',
      difficulty: 'easy',
      bloom_level: 'remember',
      correct_answer: 'Stomata (singular: stoma)',
      explanation: 'Stomata are microscopic pores flanked by guard cells that open and close to permit CO2 intake and oxygen/water vapor release.'
    },
    {
      id: 4,
      question: 'A gardener places a plant inside a sealed glass dome with plenty of water and bright sunlight, but completely removes all carbon dioxide from the air. What will happen to the rate of photosynthesis?',
      type: 'mcq',
      difficulty: 'intermediate',
      bloom_level: 'apply',
      options: [
        'Photosynthesis will completely stop because carbon atoms are necessary to build glucose.',
        'Photosynthesis will speed up because excess oxygen fills the dome.',
        'The plant will switch to absorbing nitrogen to produce sugar.',
        'The rate will remain unchanged because light and water are the only limiting factors.'
      ],
      correct_answer: 'Photosynthesis will completely stop because carbon atoms are necessary to build glucose.',
      explanation: 'Carbon dioxide is an indispensable reactant. Without CO2 molecules, the plant lacks the carbon and oxygen backbone necessary to synthesize glucose (C6H12O6).'
    },
    {
      id: 5,
      question: 'Why do most plant leaves appear bright green under white sunlight rather than blue or red?',
      type: 'mcq',
      difficulty: 'intermediate',
      bloom_level: 'understand',
      options: [
        'Chlorophyll absorbs blue and red wavelengths of light and reflects green light back to our eyes.',
        'Leaves reflect ultraviolet light which our human eyes register as green.',
        'Chlorophyll only absorbs green light and rejects all other wavelengths.',
        'Water inside the leaf turns green when heated by solar rays.'
      ],
      correct_answer: 'Chlorophyll absorbs blue and red wavelengths of light and reflects green light back to our eyes.',
      explanation: 'Chlorophyll pigments efficiently absorb high-energy blue and red light for photochemical reactions, reflecting green wavelengths, which is what enters our eyes.'
    }
  ],
  validation: {
    passed: true,
    question_count_satisfied: true,
    answers_present: true,
    options_valid: true,
    no_duplicates: true,
    bloom_levels_assigned: true,
    checks: [
      { label: 'Requested 5 questions generated', passed: true },
      { label: 'All questions have complete answers and explanations', passed: true },
      { label: 'MCQ options contain exact matching correct answers', passed: true },
      { label: 'Zero duplicate questions detected', passed: true },
      { label: "Bloom's taxonomy levels (Remember, Understand, Apply) validated", passed: true }
    ]
  }
};
