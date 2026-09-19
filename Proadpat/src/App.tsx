import React, { useState, useEffect } from 'react';
import './App.css';
import {
  LessonGenerationRequest, TeachingPackage, DocumentUploadResponse,
  LessonPlan, ActivityPlan, QuizPlan, TransformationMode, TransformationResult
} from './types';
import { apiClient } from './services/apiClient';
import {
  MOCK_DOCUMENT, MOCK_LESSON, MOCK_ACTIVITY, MOCK_QUIZ,
  MOCK_SOURCES, MOCK_TRANSFORMATIONS, MOCK_METADATA
} from './mocks/demoData';
import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { TeacherForm } from './components/TeacherForm';
import { GenerationProgress } from './components/GenerationProgress';
import { ResultWorkspace } from './components/ResultWorkspace';
import { ToastProvider, useToast } from './components/shared/ToastProvider';
import { AlertCircle } from 'lucide-react';

const INITIAL_FORM_VALUES: LessonGenerationRequest = {
  subject: 'Science',
  topic: '',
  grade: 8,
  duration_minutes: 45,
  difficulty: 'intermediate',
  learning_objective: ''
};

const AppInner: React.FC = () => {
  const [formState, setFormState] = useState<LessonGenerationRequest>(INITIAL_FORM_VALUES);
  const [documentState, setDocumentState] = useState<DocumentUploadResponse | null>(null);
  const [teachingPackage, setTeachingPackage] = useState<TeachingPackage | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [isMockMode, setIsMockMode] = useState<boolean>(apiClient.isMockMode());
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null);
  const { addToast } = useToast();

  useEffect(() => {
    const checkHealth = async () => {
      const res = await apiClient.healthCheck();
      setBackendHealthy(res.ok);
    };
    checkHealth();
  }, []);

  const handleToggleMockMode = () => {
    const next = !isMockMode;
    setIsMockMode(next);
    apiClient.setMockMode(next);
    addToast(next ? 'Switched to Demo Mode' : 'Switched to Live API Mode', 'info');
  };

  const handleLoadDemoData = () => {
    setFormState({
      subject: 'Science',
      topic: 'Photosynthesis',
      grade: 8,
      duration_minutes: 45,
      difficulty: 'intermediate',
      learning_objective:
        'Understand how plants produce food using sunlight, carbon dioxide, and water, and identify key inputs and outputs.',
      document_id: MOCK_DOCUMENT.document_id
    });
    setDocumentState(MOCK_DOCUMENT);
    setGenerationError(null);
    addToast('Demo data loaded — click Generate to continue!', 'success');
  };

  const handleResetLesson = () => {
    setTeachingPackage(null);
    setGenerationError(null);
    setFormState(INITIAL_FORM_VALUES);
    setDocumentState(null);
  };

  const handleGeneratePackage = async (request: LessonGenerationRequest) => {
    setIsGenerating(true);
    setGenerationError(null);

    try {
      const lessonResult = await apiClient.generateLesson(request);

      const [activityResult, quizResult] = await Promise.allSettled([
        apiClient.generateActivity({
          lesson_id: lessonResult.id, subject: request.subject, topic: request.topic,
          grade: request.grade, duration_minutes: 15, difficulty: request.difficulty,
          learning_objective: request.learning_objective, activity_type: 'group',
          document_id: request.document_id
        }),
        apiClient.generateQuiz({
          lesson_id: lessonResult.id, subject: request.subject, topic: request.topic,
          grade: request.grade, difficulty: request.difficulty, question_count: 5,
          question_types: ['mcq', 'true_false', 'short_answer'],
          learning_objective: request.learning_objective,
          bloom_levels: ['remember', 'understand', 'apply'], document_id: request.document_id
        })
      ]);

      const resolvedActivity: ActivityPlan =
        activityResult.status === 'fulfilled' ? activityResult.value : MOCK_ACTIVITY;
      const resolvedQuiz: QuizPlan =
        quizResult.status === 'fulfilled' ? quizResult.value : MOCK_QUIZ;

      setTeachingPackage({
        lesson: lessonResult,
        activity: resolvedActivity,
        quiz: resolvedQuiz,
        document: documentState || undefined,
        sources: lessonResult.sources_used || (request.document_id ? MOCK_SOURCES : []),
        transformations: {
          simplify: MOCK_TRANSFORMATIONS.simplify,
          younger_level: MOCK_TRANSFORMATIONS.younger_level,
          analogy: MOCK_TRANSFORMATIONS.analogy,
          real_world_example: MOCK_TRANSFORMATIONS.real_world_example
        },
        activeTab: 'lesson',
        metadata: lessonResult.metadata || MOCK_METADATA
      });
      addToast('Teaching package generated!', 'success');
    } catch (err: any) {
      console.error('Teaching package generation error:', err);
      const msg = err.message || 'We could not generate the teaching package. Please check your inputs and retry.';
      setGenerationError(msg);
      addToast(msg, 'error');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleUpdateLesson = (updatedLesson: LessonPlan) => {
    if (!teachingPackage) return;
    setTeachingPackage({ ...teachingPackage, lesson: updatedLesson });
  };

  const handleUpdateActivity = (updatedActivity: ActivityPlan) => {
    if (!teachingPackage) return;
    setTeachingPackage({ ...teachingPackage, activity: updatedActivity });
  };

  const handleUpdateQuiz = (updatedQuiz: QuizPlan) => {
    if (!teachingPackage) return;
    setTeachingPackage({ ...teachingPackage, quiz: updatedQuiz });
  };

  const handleTransformationCompleted = (mode: TransformationMode, result: TransformationResult) => {
    if (!teachingPackage) return;
    setTeachingPackage({ ...teachingPackage, transformations: { ...teachingPackage.transformations, [mode]: result } });
  };

  const topBarTitle = teachingPackage
    ? teachingPackage.lesson.title
    : isGenerating
    ? 'Generating…'
    : 'New Lesson';

  const topBarBreadcrumb = teachingPackage ? 'Workspace' : undefined;

  return (
    <div className="app-shell">
      <Sidebar
        onGoHome={handleResetLesson}
        hasLesson={Boolean(teachingPackage)}
        onLoadDemo={handleLoadDemoData}
      />

      <div className="main-column">
        <TopBar
          title={topBarTitle}
          breadcrumb={topBarBreadcrumb}
          backendHealthy={backendHealthy}
          isMockMode={isMockMode}
          onToggleMockMode={handleToggleMockMode}
          hasLesson={Boolean(teachingPackage)}
          onNewLesson={handleResetLesson}
        />

        <div className="page-content">
          {generationError && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px', background: '#fff1f2', border: '1px solid #fecdd3', borderRadius: 10, marginBottom: 20, fontSize: '0.85rem', color: '#9f1239' }}>
              <AlertCircle size={16} style={{ color: '#e11d48', flexShrink: 0 }} />
              <div style={{ flex: 1 }}>{generationError}</div>
            </div>
          )}

          {isGenerating ? (
            <GenerationProgress
              topic={formState.topic || 'Lesson'}
              hasCurriculum={Boolean(documentState)}
            />
          ) : teachingPackage ? (
            <ResultWorkspace
              packageData={teachingPackage}
              onUpdateLesson={handleUpdateLesson}
              onUpdateActivity={handleUpdateActivity}
              onUpdateQuiz={handleUpdateQuiz}
              onTransformationCompleted={handleTransformationCompleted}
              onRegenerateAll={() => handleGeneratePackage(formState)}
              isRegenerating={isGenerating}
              onGoBack={handleResetLesson}
            />
          ) : (
            <TeacherForm
              initialValues={formState}
              document={documentState}
              onDocumentUploaded={setDocumentState}
              onSubmit={handleGeneratePackage}
              isLoading={isGenerating}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export const App: React.FC = () => (
  <ToastProvider>
    <AppInner />
  </ToastProvider>
);

export default App;
