// TeachMate AI - Shared Data Contracts & TypeScript Definitions
// Strictly adhering to Hackathon Master Context & Person 1/2/3/4/5/6 contracts

export type Difficulty = 'easy' | 'intermediate' | 'advanced';

export type QuestionType = 'mcq' | 'true_false' | 'short_answer';

export type BloomLevel = 'remember' | 'understand' | 'apply' | 'analyze';

export type TransformationMode = 'simplify' | 'younger_level' | 'analogy' | 'real_world_example';

// 1. Shared Request Model for Lesson Generation
export interface LessonGenerationRequest {
  subject: string;
  topic: string;
  grade: number;
  duration_minutes: number;
  difficulty: Difficulty;
  learning_objective: string;
  document_id?: string;
}

// Structured Misconception Pair
export interface Misconception {
  misconception: string;
  correction: string;
}

// 2. Structured Lesson Response (Person 2)
export interface LessonPlan {
  id?: number | string;
  title: string;
  subject?: string;
  grade?: number;
  duration_minutes?: number;
  difficulty?: Difficulty;
  learning_objective?: string;
  document_id?: string;
  objectives: string[];
  prerequisites: string[];
  introduction: {
    duration_minutes: number;
    content: string;
  };
  explanation: {
    duration_minutes: number;
    content: string;
  };
  examples: string[];
  key_points: string[];
  common_misconceptions: Misconception[];
  recap: {
    duration_minutes: number;
    content: string;
  } | string;
  total_duration_minutes: number;
  teacher_tips?: string[];
  sources_used?: CurriculumSource[];
  validation?: LessonQualityValidation;
  metadata?: GenerationMetadata;
}

export interface LessonQualityValidation {
  learning_objectives_present: boolean;
  explanation_generated: boolean;
  duration_aligned: boolean;
  key_points_included: boolean;
  curriculum_grounded: boolean;
  notes?: string;
}

// 3. Transformation / Simplification (Person 2)
export interface TransformationRequest {
  content: string;
  subject: string;
  topic: string;
  grade: number;
  mode: TransformationMode;
}

export interface TransformationResult {
  mode: TransformationMode;
  title: string;
  transformed_content: string;
  tagline?: string;
  created_at?: string;
}

// 4. Activity Generation (Person 6)
export interface ActivityRequest {
  lesson_id?: number | string;
  subject: string;
  topic: string;
  grade: number;
  duration_minutes: number;
  difficulty: Difficulty;
  class_size?: number;
  learning_objective: string;
  activity_type?: string;
  document_id?: string;
}

export interface ActivityPlan {
  id?: number | string;
  title: string;
  activity_type: string;
  objective: string;
  duration_minutes: number;
  group_size: number;
  materials: string[];
  setup?: string;
  instructions: string[];
  teacher_role: string;
  student_role?: string;
  expected_outcome: string;
  assessment_method: string;
  safety_notes?: string;
  adaptations?: string[];
}

// 5. Quiz Generation (Person 3)
export interface QuizRequest {
  lesson_id?: number | string;
  subject: string;
  topic: string;
  grade: number;
  difficulty: Difficulty;
  question_count: number;
  question_types: QuestionType[];
  learning_objective: string;
  bloom_levels: BloomLevel[];
  document_id?: string;
}

export interface QuizQuestion {
  id?: string | number;
  question: string;
  type: QuestionType;
  difficulty: string;
  bloom_level: BloomLevel;
  options?: string[];
  correct_answer: string;
  explanation: string;
}

export interface QuizQualityValidation {
  passed: boolean;
  checks: Array<{
    label: string;
    passed: boolean;
    description?: string;
  }>;
  question_count_satisfied: boolean;
  answers_present: boolean;
  options_valid: boolean;
  no_duplicates: boolean;
  bloom_levels_assigned: boolean;
}

export interface QuizPlan {
  id?: number | string;
  title: string;
  difficulty: string;
  questions: QuizQuestion[];
  validation?: QuizQualityValidation;
}

// 6. Curriculum Grounding / RAG (Person 4)
export interface CurriculumSource {
  document_id?: string;
  source: string; // e.g., "CBSE_Science.pdf"
  page_number?: number;
  chunk_id?: string;
  content: string;
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  file_type?: string;
  page_count?: number;
  status: 'processing' | 'ready' | 'error';
  message?: string;
}

// 7. Observability & AI Generation Metadata
export interface GenerationMetadata {
  model: string;
  prompt_version: string;
  curriculum_grounded: boolean;
  retrieved_sources_count: number;
  validation_status: 'passed' | 'warning' | 'failed';
  latency_ms: number;
  input_tokens?: number;
  output_tokens?: number;
}

// 8. Overall Teaching Package
export interface TeachingPackage {
  lesson: LessonPlan;
  activity?: ActivityPlan;
  quiz?: QuizPlan;
  document?: DocumentUploadResponse;
  sources: CurriculumSource[];
  transformations: Record<TransformationMode, TransformationResult | null>;
  activeTab: 'lesson' | 'explain' | 'activity' | 'quiz' | 'sources';
  metadata?: GenerationMetadata;
}
