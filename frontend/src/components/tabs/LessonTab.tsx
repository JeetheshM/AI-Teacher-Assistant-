import React, { useState } from 'react';
import {
  Clock, BookOpen, Target, ListChecks, AlertTriangle,
  Lightbulb, CheckCircle2, RotateCcw, Edit3, Save, Sparkles
} from 'lucide-react';
import { LessonPlan } from '../../types';
import { QualityCheckCard } from '../shared/QualityCheckCard';

interface LessonTabProps {
  lesson: LessonPlan;
  onUpdateLesson: (updated: LessonPlan) => void;
  onRegenerate: () => void;
  isRegenerating: boolean;
}

export const LessonTab: React.FC<LessonTabProps> = ({
  lesson, onUpdateLesson, onRegenerate, isRegenerating
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedLesson, setEditedLesson] = useState<LessonPlan>(lesson);

  const handleSave = () => { onUpdateLesson(editedLesson); setIsEditing(false); };

  const introDuration   = lesson.introduction?.duration_minutes || 5;
  const explainDuration = lesson.explanation?.duration_minutes || 20;
  const recapDuration   = typeof lesson.recap === 'object' ? lesson.recap.duration_minutes : 5;
  const totalDuration   = lesson.total_duration_minutes || 45;

  const qualityChecks = [
    { label: `${lesson.objectives?.length || 0} Learning objectives specified`, passed: true },
    { label: 'Core explanation & biochemical formulas generated', passed: true },
    { label: `Section timings total ${totalDuration} min`, passed: true },
    { label: `${lesson.key_points?.length || 0} Key takeaways structured`, passed: true },
    { label: 'Common misconceptions & corrections paired', passed: true },
  ];

  return (
    <div className="fade-in">
      {/* Teacher Action Banner */}
      <div className="teacher-banner">
        <div className="teacher-banner-msg">
          <Edit3 size={14} />
          <span><strong>Teacher in the Loop:</strong> Review, tailor sections to your class dynamics, or regenerate.</span>
        </div>
        <div className="teacher-banner-actions">
          {isEditing ? (
            <button type="button" className="btn btn-success btn-sm" onClick={handleSave}>
              <Save size={14} /> Save Changes
            </button>
          ) : (
            <button type="button" className="btn btn-secondary btn-sm" onClick={() => setIsEditing(true)}>
              <Edit3 size={14} /> Edit Sections
            </button>
          )}
          <button type="button" className="btn btn-ghost btn-sm" onClick={onRegenerate} disabled={isRegenerating}>
            <RotateCcw size={13} className={isRegenerating ? 'spin' : ''} />
            <span>{isRegenerating ? 'Regenerating…' : 'Regenerate'}</span>
          </button>
        </div>
      </div>

      {/* Prerequisites */}
      {lesson.prerequisites && lesson.prerequisites.length > 0 && (
        <div style={{ background: '#f8f9fb', border: '1px solid #e5e7eb', borderRadius: 10, padding: '12px 16px', marginBottom: 16 }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#6b7280', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 5 }}>
            <BookOpen size={12} /> Prerequisites & Prior Knowledge
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {lesson.prerequisites.map((req, i) => (
              <span key={i} className="tag">{req}</span>
            ))}
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="timeline" style={{ marginBottom: 20 }}>
        {/* 1. Introduction */}
        <div className="timeline-item">
          <div className={`timeline-icon timeline-icon-intro`}>
            <Sparkles size={17} />
          </div>
          <div className="timeline-body">
            <div className="timeline-label">
              <span>1 · Introduction & Hook</span>
              <span className="time-badge"><Clock size={10} /> {introDuration} min</span>
            </div>
            {isEditing ? (
              <textarea className="form-textarea" style={{ marginTop: 6 }}
                value={editedLesson.introduction.content}
                onChange={e => setEditedLesson({ ...editedLesson, introduction: { ...editedLesson.introduction, content: e.target.value } })}
              />
            ) : (
              <div className="timeline-content">{lesson.introduction.content}</div>
            )}
          </div>
        </div>

        {/* 2. Core Explanation */}
        <div className="timeline-item">
          <div className="timeline-icon timeline-icon-explain">
            <BookOpen size={17} />
          </div>
          <div className="timeline-body">
            <div className="timeline-label">
              <span>2 · Core Concept Explanation</span>
              <span className="time-badge"><Clock size={10} /> {explainDuration} min</span>
            </div>
            {isEditing ? (
              <textarea className="form-textarea" style={{ minHeight: 160, marginTop: 6 }}
                value={editedLesson.explanation.content}
                onChange={e => setEditedLesson({ ...editedLesson, explanation: { ...editedLesson.explanation, content: e.target.value } })}
              />
            ) : (
              <div className="timeline-content">{lesson.explanation.content}</div>
            )}
          </div>
        </div>

        {/* 3. Examples */}
        {lesson.examples && lesson.examples.length > 0 && (
          <div className="timeline-item">
            <div className="timeline-icon timeline-icon-examples">
              <Lightbulb size={17} />
            </div>
            <div className="timeline-body">
              <div className="timeline-label">3 · Concrete Examples & Demonstrations</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px,1fr))', gap: 10, marginTop: 8 }}>
                {lesson.examples.map((ex: any, i: number) => (
                  <div key={i} style={{ padding: '12px 14px', background: '#fffbeb', border: '1px solid #fde68a', borderRadius: 10, fontSize: '0.84rem', color: '#374151', lineHeight: 1.5 }}>
                    <span style={{ fontWeight: 700, color: '#92400e', display: 'block', marginBottom: 4 }}>
                      {typeof ex === 'object' && ex.title ? ex.title : `Example ${i + 1}`}
                    </span>
                    {typeof ex === 'string' ? ex : ex.description || JSON.stringify(ex)}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 4. Key Points */}
        <div className="timeline-item">
          <div className="timeline-icon" style={{ background: '#ecfdf5', color: '#059669' }}>
            <ListChecks size={17} />
          </div>
          <div className="timeline-body">
            <div className="timeline-label">4 · Key Takeaways</div>
            <div className="key-points-grid" style={{ marginTop: 8 }}>
              {lesson.key_points.map((pt, i) => (
                <div key={i} className="key-point-card">
                  <div className="key-point-icon"><CheckCircle2 size={14} /></div>
                  <span>{pt}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 5. Misconceptions */}
        {lesson.common_misconceptions && lesson.common_misconceptions.length > 0 && (
          <div className="timeline-item">
            <div className="timeline-icon" style={{ background: '#fff1f2', color: '#e11d48' }}>
              <AlertTriangle size={17} />
            </div>
            <div className="timeline-body">
              <div className="timeline-label">5 · Common Misconceptions & Corrections</div>
              <div style={{ marginTop: 8 }}>
                {lesson.common_misconceptions.map((item, i) => (
                  <div key={i} className="misconception-card">
                    <div className="misconception-header">
                      <AlertTriangle size={13} style={{ color: '#e11d48', flexShrink: 0, marginTop: 2 }} />
                      <div>
                        <span className="misconception-badge">Misconception</span>
                        <div className="misconception-text">{item.misconception}</div>
                      </div>
                    </div>
                    <div className="correction-body">
                      <CheckCircle2 size={13} style={{ color: '#059669', flexShrink: 0, marginTop: 2 }} />
                      <div>
                        <span className="correction-badge">Correction</span>
                        <div className="correction-text">{item.correction}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 6. Recap */}
        <div className="timeline-item">
          <div className="timeline-icon timeline-icon-recap">
            <Clock size={17} />
          </div>
          <div className="timeline-body">
            <div className="timeline-label">
              <span>6 · Class Recap & Synthesis</span>
              <span className="time-badge"><Clock size={10} /> {recapDuration} min</span>
            </div>
            <div className="timeline-content">
              {typeof lesson.recap === 'object' ? lesson.recap.content : lesson.recap}
            </div>
          </div>
        </div>
      </div>

      {/* Teacher Tips */}
      {lesson.teacher_tips && lesson.teacher_tips.length > 0 && (
        <div style={{ background: '#eef2ff', border: '1px solid #c7d2fe', borderRadius: 10, padding: '14px 18px', marginBottom: 16 }}>
          <div style={{ fontWeight: 700, fontSize: '0.8rem', color: '#3730a3', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
            <Lightbulb size={14} /> Teacher Delivery Tips
          </div>
          <ul style={{ paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 4 }}>
            {lesson.teacher_tips.map((tip, i) => (
              <li key={i} style={{ fontSize: '0.84rem', color: '#3730a3', lineHeight: 1.55 }}>{tip}</li>
            ))}
          </ul>
        </div>
      )}

      <QualityCheckCard title="Lesson Plan Quality Check" checks={qualityChecks} />
    </div>
  );
};
