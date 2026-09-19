import React, { useState } from 'react';
import {
  Users, Clock, CheckSquare, Package, ListOrdered,
  UserCheck, Award, Sliders, RotateCcw, Sparkles, Edit3, Save
} from 'lucide-react';
import { ActivityPlan, LessonPlan } from '../../types';
import { apiClient } from '../../services/apiClient';
import { useToast } from '../shared/ToastProvider';

interface ActivityTabProps {
  activity: ActivityPlan | null;
  lesson: LessonPlan;
  onActivityUpdated: (activity: ActivityPlan) => void;
}

export const ActivityTab: React.FC<ActivityTabProps> = ({ activity, lesson, onActivityUpdated }) => {
  const [loading, setLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedActivity, setEditedActivity] = useState<ActivityPlan | null>(activity);
  const { addToast } = useToast();

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await apiClient.generateActivity({
        lesson_id: lesson.id,
        subject: lesson.subject || 'Science',
        topic: lesson.title,
        grade: lesson.grade || 8,
        duration_minutes: 15,
        difficulty: lesson.difficulty || 'intermediate',
        learning_objective: lesson.learning_objective || '',
        activity_type: 'group',
        document_id: lesson.document_id
      });
      onActivityUpdated(res);
      setEditedActivity(res);
      addToast('Classroom activity generated!', 'success');
    } catch (err) {
      addToast('Activity generation failed. Check your API connection.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = () => {
    if (editedActivity) { onActivityUpdated(editedActivity); setIsEditing(false); addToast('Activity saved!', 'success'); }
  };

  if (!activity) {
    return (
      <div className="fade-in" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 300 }}>
        <div className="card" style={{ padding: '48px 40px', maxWidth: 480, width: '100%', textAlign: 'center' }}>
          <div style={{ width: 52, height: 52, borderRadius: 26, background: '#eef2ff', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', color: '#4f46e5' }}>
            <Users size={26} />
          </div>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#111827', marginBottom: 6 }}>No Activity Generated Yet</h3>
          <p style={{ fontSize: '0.85rem', color: '#9ca3af', maxWidth: 340, margin: '0 auto 24px', lineHeight: 1.6 }}>
            Generate an active, hands-on classroom investigation aligned with the current learning objectives and group dynamics.
          </p>
          <button type="button" className="btn btn-cta" onClick={handleGenerate} disabled={loading}>
            <Sparkles size={18} className={loading ? 'spin' : ''} />
            <span>{loading ? 'Designing Activity…' : 'Generate 15-min Group Activity'}</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      {/* Banner */}
      <div className="teacher-banner">
        <div className="teacher-banner-msg">
          <Users size={14} />
          <span><strong>Classroom Activity:</strong> Structured for collaborative active learning with minimal preparation materials.</span>
        </div>
        <div className="teacher-banner-actions">
          {isEditing ? (
            <button type="button" className="btn btn-success btn-sm" onClick={handleSave}>
              <Save size={14} /> Save
            </button>
          ) : (
            <button type="button" className="btn btn-secondary btn-sm" onClick={() => setIsEditing(true)}>
              <Edit3 size={14} /> Edit
            </button>
          )}
          <button type="button" className="btn btn-ghost btn-sm" onClick={handleGenerate} disabled={loading}>
            <RotateCcw size={13} className={loading ? 'spin' : ''} />
            <span>{loading ? 'Regenerating…' : 'Regenerate'}</span>
          </button>
        </div>
      </div>

      <div className="card" style={{ padding: '24px 28px' }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', paddingBottom: 16, marginBottom: 20, borderBottom: '1px solid #e5e7eb', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#4f46e5', marginBottom: 4 }}>
              {activity.activity_type || 'Collaborative Group Investigation'}
            </div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#111827', letterSpacing: '-0.02em' }}>{activity.title}</h2>
          </div>
          <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
            <span className="time-badge"><Clock size={12} /> {activity.duration_minutes || 15} min</span>
            <span className="tag"><Users size={12} /> Teams of {activity.group_size || 4}</span>
          </div>
        </div>

        {/* Objective */}
        <div style={{ background: '#f0f9ff', border: '1px solid #bae6fd', borderRadius: 10, padding: '12px 16px', marginBottom: 20, display: 'flex', gap: 10 }}>
          <CheckSquare size={16} style={{ color: '#0284c7', flexShrink: 0, marginTop: 2 }} />
          <div>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#0284c7', marginBottom: 3 }}>Activity Objective</div>
            <div style={{ fontSize: '0.87rem', color: '#0c4a6e', fontWeight: 600, lineHeight: 1.5 }}>{activity.objective}</div>
          </div>
        </div>

        {/* Materials + Setup row */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 20 }}>
          <div style={{ border: '1px solid #e5e7eb', borderRadius: 10, padding: '14px 16px', background: 'white' }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#6b7280', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 5 }}>
              <Package size={12} /> Required Materials
            </div>
            <div className="material-chips">
              {activity.materials.map((mat, i) => (
                <span key={i} className="material-chip">{mat}</span>
              ))}
            </div>
          </div>
          {activity.setup && (
            <div style={{ border: '1px solid #e5e7eb', borderRadius: 10, padding: '14px 16px', background: 'white' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#6b7280', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 5 }}>
                <Sliders size={12} /> Classroom Setup
              </div>
              <div style={{ fontSize: '0.84rem', color: '#374151', lineHeight: 1.55 }}>{activity.setup}</div>
            </div>
          )}
        </div>

        {/* Instructions */}
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#111827', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
            <ListOrdered size={15} style={{ color: '#4f46e5' }} /> Step-by-Step Instructions
          </div>
          <div className="activity-steps">
            {activity.instructions.map((step, i) => (
              <div key={i} className="activity-step">
                <div className="activity-step-num">{i + 1}</div>
                <div className="activity-step-content">{step}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Teacher + Student Roles */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 20 }}>
          <div style={{ background: '#eef2ff', border: '1px solid #c7d2fe', borderRadius: 10, padding: '14px 16px' }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#4338ca', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 5 }}>
              <UserCheck size={12} /> Teacher Facilitation Role
            </div>
            <div style={{ fontSize: '0.84rem', color: '#3730a3', lineHeight: 1.6 }}>{activity.teacher_role}</div>
          </div>
          {activity.student_role && (
            <div style={{ background: '#f8f9fb', border: '1px solid #e5e7eb', borderRadius: 10, padding: '14px 16px' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#6b7280', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 5 }}>
                <Users size={12} /> Student Team Roles
              </div>
              <div style={{ fontSize: '0.84rem', color: '#374151', lineHeight: 1.6 }}>{activity.student_role}</div>
            </div>
          )}
        </div>

        {/* Assessment Method */}
        <div style={{ background: '#ecfdf5', border: '1px solid #a7f3d0', borderRadius: 10, padding: '14px 16px', marginBottom: activity.adaptations?.length ? 16 : 0 }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#059669', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 5 }}>
            <Award size={12} /> Quick Assessment & Rubric
          </div>
          <div style={{ fontSize: '0.86rem', color: '#065f46', lineHeight: 1.55 }}>{activity.assessment_method}</div>
        </div>

        {/* Adaptations */}
        {activity.adaptations && activity.adaptations.length > 0 && (
          <div style={{ background: '#f8f9fb', border: '1px solid #e5e7eb', borderRadius: 10, padding: '12px 16px' }}>
            <div style={{ fontWeight: 700, fontSize: '0.75rem', color: '#374151', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Differentiated Adaptations</div>
            <ul style={{ paddingLeft: 16, display: 'flex', flexDirection: 'column', gap: 4 }}>
              {activity.adaptations.map((ad, i) => (
                <li key={i} style={{ fontSize: '0.83rem', color: '#6b7280', lineHeight: 1.5 }}>{ad}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
