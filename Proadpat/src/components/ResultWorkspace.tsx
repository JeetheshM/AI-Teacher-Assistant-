import React, { useState } from 'react';
import {
  BookOpen, Sparkles, Users, FileQuestion, Bookmark, FileDown,
  Cpu, ArrowLeft, LayoutDashboard, CheckCircle2
} from 'lucide-react';
import {
  TeachingPackage, LessonPlan, ActivityPlan, QuizPlan,
  TransformationMode, TransformationResult
} from '../types';
import { LessonTab } from './tabs/LessonTab';
import { ExplainTab } from './tabs/ExplainTab';
import { ActivityTab } from './tabs/ActivityTab';
import { QuizTab } from './tabs/QuizTab';
import { SourcesTab } from './tabs/SourcesTab';
import { OverviewTab } from './tabs/OverviewTab';
import { ExportModal } from './ExportModal';
import { AiMetadataDrawer } from './AiMetadataDrawer';

type TabId = 'overview' | 'lesson' | 'explain' | 'activity' | 'quiz' | 'sources';

interface ResultWorkspaceProps {
  packageData: TeachingPackage;
  onUpdateLesson: (l: LessonPlan) => void;
  onUpdateActivity: (a: ActivityPlan) => void;
  onUpdateQuiz: (q: QuizPlan) => void;
  onTransformationCompleted: (mode: TransformationMode, res: TransformationResult) => void;
  onRegenerateAll: () => void;
  isRegenerating: boolean;
  onGoBack: () => void;
}

const TABS: { id: TabId; label: string; icon: React.ReactNode }[] = [
  { id: 'overview',  label: 'Overview',   icon: <LayoutDashboard size={14} /> },
  { id: 'lesson',    label: 'Lesson',     icon: <BookOpen size={14} /> },
  { id: 'explain',   label: 'Explain',    icon: <Sparkles size={14} /> },
  { id: 'activity',  label: 'Activity',   icon: <Users size={14} /> },
  { id: 'quiz',      label: 'Quiz',       icon: <FileQuestion size={14} /> },
  { id: 'sources',   label: 'Sources',    icon: <Bookmark size={14} /> },
];

export const ResultWorkspace: React.FC<ResultWorkspaceProps> = ({
  packageData, onUpdateLesson, onUpdateActivity, onUpdateQuiz,
  onTransformationCompleted, onRegenerateAll, isRegenerating, onGoBack
}) => {
  const [tab, setTab] = useState<TabId>('overview');
  const [showExport, setShowExport] = useState(false);
  const [showAi, setShowAi] = useState(false);

  const { lesson, activity, quiz, document: doc, sources, transformations, metadata } = packageData;
  const isGrounded = Boolean(lesson.document_id || doc?.document_id);

  const handleApplyExplanation = (c: string) =>
    onUpdateLesson({ ...lesson, explanation: { ...lesson.explanation, content: c } });

  const handleAddAnalogy = (text: string) =>
    onUpdateLesson({ ...lesson, examples: [...(lesson.examples || []), text] });

  return (
    <div className="fade-in">
      {/* ── Result Header ─────────────────────────── */}
      <div className="result-header">
        <div>
          {/* Back link */}
          <button className="btn btn-ghost btn-xs" onClick={onGoBack} style={{ marginBottom: 10, color: '#6b7280' }}>
            <ArrowLeft size={13} /> <span>Workspace</span>
          </button>

          <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#6b7280', marginBottom: 4 }}>
            Teaching Package
          </div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800, letterSpacing: '-0.025em', color: '#111827', marginBottom: 10 }}>
            {lesson.title}
          </h1>
          <div className="result-header-meta">
            <span className="tag">{lesson.subject || 'Science'}</span>
            <span className="tag">Grade {lesson.grade || 8}</span>
            <span className="time-badge">{lesson.total_duration_minutes || 45} min</span>
            <span className="tag" style={{ textTransform: 'capitalize' }}>{lesson.difficulty || 'Intermediate'}</span>
            {isGrounded ? (
              <span className="pill pill-grounded">
                <CheckCircle2 size={11} />
                <span>Curriculum Grounded · {doc?.filename || 'Textbook'}</span>
              </span>
            ) : (
              <span className="pill pill-ungrounded">General AI Generation</span>
            )}
          </div>
        </div>

        {/* Header actions */}
        <div className="result-header-actions">
          <button className="btn btn-ghost btn-sm" onClick={() => setShowAi(true)}>
            <Cpu size={14} /> <span>AI Details</span>
          </button>
          <button className="btn btn-secondary btn-sm" onClick={onRegenerateAll} disabled={isRegenerating}>
            <span>{isRegenerating ? 'Regenerating…' : 'Regenerate'}</span>
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => setShowExport(true)}>
            <FileDown size={14} /> <span>Export Package</span>
          </button>
        </div>
      </div>

      {/* ── Package completion summary bar ─────────── */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
        {[
          { label: 'Lesson Plan', done: true },
          { label: 'Explanation', done: true },
          { label: 'Activity', done: Boolean(activity) },
          { label: 'Quiz', done: Boolean(quiz) },
          { label: 'Answer Key', done: Boolean(quiz) },
          { label: `Sources (${sources.length})`, done: sources.length > 0 },
        ].map(({ label, done }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 5, padding: '4px 10px', borderRadius: 999, border: '1px solid', borderColor: done ? '#a7f3d0' : '#e5e7eb', background: done ? '#ecfdf5' : '#f8f9fb', fontSize: '0.73rem', fontWeight: 600, color: done ? '#065f46' : '#9ca3af' }}>
            {done ? <CheckCircle2 size={12} style={{ color: '#10b981' }} /> : <div style={{ width: 12, height: 12, border: '1.5px solid #d1d5db', borderRadius: '50%' }} />}
            <span>{label}</span>
          </div>
        ))}
      </div>

      {/* ── Tab Bar ──────────────────────────────── */}
      <div className="tabs-bar">
        {TABS.map(t => (
          <button key={t.id} className={`tab-btn${tab === t.id ? ' active' : ''}`} onClick={() => setTab(t.id)}>
            {t.icon}
            <span>{t.label}</span>
            {t.id === 'sources' && sources.length > 0 && (
              <span style={{ background: tab === t.id ? '#e0e7ff' : '#e5e7eb', color: tab === t.id ? '#4338ca' : '#6b7280', borderRadius: 9999, padding: '0 5px', fontSize: '0.65rem', fontWeight: 700, lineHeight: '16px' }}>
                {sources.length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* ── Tab Content ──────────────────────────── */}
      {tab === 'overview' && (
        <OverviewTab packageData={packageData} onNavigate={setTab} />
      )}
      {tab === 'lesson' && (
        <LessonTab lesson={lesson} onUpdateLesson={onUpdateLesson} onRegenerate={onRegenerateAll} isRegenerating={isRegenerating} />
      )}
      {tab === 'explain' && (
        <ExplainTab lesson={lesson} transformations={transformations} onTransformationCompleted={onTransformationCompleted} onApplyExplanation={handleApplyExplanation} onAddAnalogyToLesson={handleAddAnalogy} />
      )}
      {tab === 'activity' && (
        <ActivityTab activity={activity || null} lesson={lesson} onActivityUpdated={onUpdateActivity} />
      )}
      {tab === 'quiz' && (
        <QuizTab quiz={quiz || null} lesson={lesson} onQuizUpdated={onUpdateQuiz} />
      )}
      {tab === 'sources' && (
        <SourcesTab sources={sources} document={doc || null} isGrounded={isGrounded} />
      )}

      {showExport && <ExportModal teachingPackage={packageData} onClose={() => setShowExport(false)} />}
      {showAi     && <AiMetadataDrawer metadata={metadata} onClose={() => setShowAi(false)} />}
    </div>
  );
};
