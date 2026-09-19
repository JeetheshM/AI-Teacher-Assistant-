import React, { useState } from 'react';
import {
  Sparkles, Baby, Lightbulb, Globe,
  RotateCcw, Check, Plus, ArrowRight
} from 'lucide-react';
import { TransformationMode, TransformationResult, LessonPlan } from '../../types';
import { apiClient } from '../../services/apiClient';
import { useToast } from '../shared/ToastProvider';

interface ExplainTabProps {
  lesson: LessonPlan;
  transformations: Record<TransformationMode, TransformationResult | null>;
  onTransformationCompleted: (mode: TransformationMode, result: TransformationResult) => void;
  onApplyExplanation: (newContent: string) => void;
  onAddAnalogyToLesson: (analogy: string) => void;
}

const STRATEGIES: { mode: TransformationMode; label: string; desc: string; icon: React.ReactNode; color: string; bg: string }[] = [
  { mode: 'simplify',          label: 'Simplify',    desc: 'Reduce complexity, keep accuracy',   icon: <Sparkles size={16} />, color: '#4f46e5', bg: '#eef2ff' },
  { mode: 'younger_level',     label: 'Younger',     desc: 'Adapt for a lower grade level',       icon: <Baby size={16} />,     color: '#0284c7', bg: '#e0f2fe' },
  { mode: 'analogy',           label: 'Analogy',     desc: 'Relatable conceptual bridge',         icon: <Lightbulb size={16} />,color: '#d97706', bg: '#fffbeb' },
  { mode: 'real_world_example',label: 'Real-World',  desc: 'Connect to everyday life',            icon: <Globe size={16} />,    color: '#059669', bg: '#ecfdf5' },
];

export const ExplainTab: React.FC<ExplainTabProps> = ({
  lesson, transformations, onTransformationCompleted, onApplyExplanation, onAddAnalogyToLesson
}) => {
  const [activeMode, setActiveMode] = useState<TransformationMode>('simplify');
  const [loadingMode, setLoadingMode] = useState<TransformationMode | null>(null);
  const { addToast } = useToast();

  const handleTransform = async (mode: TransformationMode) => {
    setActiveMode(mode);
    setLoadingMode(mode);
    try {
      const result = await apiClient.transformContent({
        content: lesson.explanation.content,
        subject: lesson.subject || 'Science',
        topic: lesson.title,
        grade: lesson.grade || 8,
        mode
      });
      onTransformationCompleted(mode, result);
    } catch (err) {
      console.error('Transformation error:', err);
      addToast('Transformation failed. Check your API connection.', 'error');
    } finally {
      setLoadingMode(null);
    }
  };

  const handleApplyToLesson = (content: string, typeName: string) => {
    onApplyExplanation(content);
    addToast(`Lesson explanation updated with ${typeName}`, 'success');
  };

  const handleAddAnalogy = (text: string) => {
    onAddAnalogyToLesson(text);
    addToast('Analogy added as a concrete demonstration', 'success');
  };

  const currentResult = transformations[activeMode];
  const activeStrategy = STRATEGIES.find(s => s.mode === activeMode)!;

  return (
    <div className="fade-in">
      {/* Banner */}
      <div className="teacher-banner" style={{ marginBottom: 20 }}>
        <div className="teacher-banner-msg">
          <Sparkles size={14} />
          <span><strong>Adaptive Teaching Copilot:</strong> Transform explanations dynamically for diverse student comprehension levels. Your original is preserved until you explicitly adopt an alternative.</span>
        </div>
      </div>

      {/* Strategy selector */}
      <div className="transform-grid" style={{ marginBottom: 20 }}>
        {STRATEGIES.map(s => (
          <button
            key={s.mode}
            type="button"
            className={`transform-card${activeMode === s.mode ? ' active' : ''}`}
            onClick={() => handleTransform(s.mode)}
            disabled={loadingMode !== null}
          >
            <div className="transform-card-icon" style={{ background: s.bg, color: s.color }}>
              {s.icon}
            </div>
            <div className="transform-card-body">
              <div className="transform-card-title">{s.label}</div>
              <div className="transform-card-desc">{s.desc}</div>
            </div>
            {loadingMode === s.mode && <Sparkles size={14} className="spin" style={{ color: s.color, flexShrink: 0 }} />}
            {activeMode === s.mode && !loadingMode && <ArrowRight size={14} style={{ color: s.color, flexShrink: 0 }} />}
          </button>
        ))}
      </div>

      {/* Comparison workspace */}
      <div className="comparison-grid">
        {/* Original */}
        <div className="version-panel">
          <div className="version-panel-header">
            <span className="version-label version-label-original">Original Explanation</span>
            <span className="time-badge">{lesson.explanation.duration_minutes || 20} min · Grade {lesson.grade || 8}</span>
          </div>
          <div className="version-content">{lesson.explanation.content}</div>
          <div style={{ padding: '10px 16px', borderTop: '1px solid #e5e7eb', fontSize: '0.72rem', color: '#9ca3af' }}>
            Standard curriculum baseline · read-only
          </div>
        </div>

        {/* Transformed */}
        <div className={`version-panel${currentResult && !loadingMode ? ' highlighted' : ''}`}>
          <div className="version-panel-header">
            <span className="version-label version-label-transform" style={{ color: activeStrategy.color }}>
              {currentResult ? currentResult.title : `${activeStrategy.label} Adaptation`}
            </span>
            <button type="button" className="btn btn-ghost btn-xs" onClick={() => handleTransform(activeMode)} disabled={loadingMode !== null}>
              <RotateCcw size={12} className={loadingMode === activeMode ? 'spin' : ''} />
              <span>Refresh</span>
            </button>
          </div>

          <div className="version-content">
            {loadingMode === activeMode ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 180, gap: 10, color: '#6b7280' }}>
                <Sparkles size={26} className="spin" style={{ color: activeStrategy.color }} />
                <span style={{ fontSize: '0.82rem', fontWeight: 600 }}>Reframing concept…</span>
              </div>
            ) : currentResult ? (
              <>
                {currentResult.tagline && (
                  <div style={{ fontSize: '0.76rem', color: '#9ca3af', fontStyle: 'italic', marginBottom: 10, paddingBottom: 10, borderBottom: '1px dashed #e5e7eb' }}>
                    {currentResult.tagline}
                  </div>
                )}
                {currentResult.transformed_content}
              </>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 180, gap: 8, color: '#9ca3af' }}>
                <Lightbulb size={24} />
                <span style={{ fontSize: '0.78rem' }}>Click a strategy above to generate an adaptation</span>
              </div>
            )}
          </div>

          {currentResult && !loadingMode && (
            <div className="version-footer">
              {(activeMode === 'analogy' || activeMode === 'real_world_example') && (
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => handleAddAnalogy(currentResult.transformed_content)}>
                  <Plus size={13} /> Add as Example
                </button>
              )}
              <button type="button" className="btn btn-success btn-sm" onClick={() => handleApplyToLesson(currentResult.transformed_content, currentResult.title)}>
                <Check size={13} /> Use in Lesson
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
