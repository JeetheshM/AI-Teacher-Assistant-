import React from 'react';
import {
  BookOpen, Users, FileQuestion, Bookmark, Sparkles,
  Clock, BarChart2, Target, ChevronRight, CheckCircle2, FileCheck2
} from 'lucide-react';
import { TeachingPackage } from '../../types';

type TabId = 'overview' | 'lesson' | 'explain' | 'activity' | 'quiz' | 'sources';

interface OverviewTabProps {
  packageData: TeachingPackage;
  onNavigate: (tab: TabId) => void;
}

export const OverviewTab: React.FC<OverviewTabProps> = ({ packageData, onNavigate }) => {
  const { lesson, activity, quiz, sources } = packageData;

  const quickActions: { label: string; desc: string; tab: TabId; icon: React.ReactNode; color: string }[] = [
    { label: 'Read Lesson Plan', desc: 'Timeline, key points & misconceptions', tab: 'lesson', icon: <BookOpen size={16} />, color: '#eef2ff' },
    { label: 'Adapt Explanation', desc: 'Simplify, add analogy, younger level', tab: 'explain', icon: <Sparkles size={16} />, color: '#fffbeb' },
    { label: 'View Activity', desc: `${activity?.duration_minutes || 15}-min group investigation`, tab: 'activity', icon: <Users size={16} />, color: '#ecfdf5' },
    { label: 'Open Assessment', desc: `${quiz?.questions.length || 5} questions with answer key`, tab: 'quiz', icon: <FileQuestion size={16} />, color: '#fff1f2' },
    { label: 'Curriculum Sources', desc: `${sources.length} textbook references cited`, tab: 'sources', icon: <Bookmark size={16} />, color: '#f0fdf4' },
  ];

  const packageItems = [
    { label: 'Lesson Plan', value: 'Complete · ' + (lesson.total_duration_minutes || 45) + ' min', done: true },
    { label: 'Teaching Explanation', value: `${lesson.key_points?.length || 0} key points`, done: true },
    { label: 'Classroom Activity', value: activity ? `${activity.duration_minutes} min group activity` : 'Not yet generated', done: Boolean(activity) },
    { label: 'Assessment (Quiz)', value: quiz ? `${quiz.questions.length} questions` : 'Not yet generated', done: Boolean(quiz) },
    { label: 'Answer Key', value: quiz ? 'All answers included' : '—', done: Boolean(quiz) },
    { label: 'Curriculum Sources', value: sources.length > 0 ? `${sources.length} references` : 'No document uploaded', done: sources.length > 0 },
  ];

  return (
    <div className="fade-in" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
      {/* Left column */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {/* Stats row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12 }}>
          {[
            { label: 'Duration', value: `${lesson.total_duration_minutes || 45}m`, icon: <Clock size={14} />, color: '#4f46e5' },
            { label: 'Grade', value: `G${lesson.grade || 8}`, icon: <BarChart2 size={14} />, color: '#059669' },
            { label: 'Objectives', value: `${lesson.objectives?.length || 0}`, icon: <Target size={14} />, color: '#d97706' },
          ].map(s => (
            <div key={s.label} className="card" style={{ padding: '14px 16px' }}>
              <div style={{ width: 28, height: 28, borderRadius: 8, background: `${s.color}1a`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: s.color, marginBottom: 8 }}>
                {s.icon}
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#111827', fontFamily: 'var(--font-display)', lineHeight: 1 }}>{s.value}</div>
              <div style={{ fontSize: '0.72rem', color: '#9ca3af', fontWeight: 600, marginTop: 3, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* Objectives */}
        <div className="card" style={{ padding: '18px 20px' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#9ca3af', marginBottom: 12 }}>
            Learning Objectives
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {(lesson.objectives || []).map((obj, i) => (
              <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start', fontSize: '0.85rem', color: '#374151' }}>
                <div style={{ width: 22, height: 22, borderRadius: '50%', background: '#eef2ff', color: '#4f46e5', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '0.7rem', flexShrink: 0 }}>
                  {String(i + 1).padStart(2, '0')}
                </div>
                <span style={{ lineHeight: 1.5, paddingTop: 2 }}>{obj}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right column */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {/* Teaching Package checklist */}
        <div className="card" style={{ padding: '18px 20px' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#9ca3af', marginBottom: 12 }}>
            Teaching Package
          </div>
          <div className="package-checklist">
            {packageItems.map(item => (
              <div key={item.label} className={`package-check-item${item.done ? ' done' : ''}`}>
                {item.done
                  ? <CheckCircle2 size={15} className="package-check-icon-done" />
                  : <div style={{ width: 15, height: 15, border: '1.5px solid #d1d5db', borderRadius: '50%', flexShrink: 0 }} />
                }
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: '0.84rem' }}>{item.label}</div>
                  <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>{item.value}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card" style={{ padding: '18px 20px' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#9ca3af', marginBottom: 12 }}>
            Quick Navigation
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {quickActions.map(a => (
              <button
                key={a.tab}
                onClick={() => onNavigate(a.tab)}
                style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 10px', borderRadius: 8, border: 'none', background: 'transparent', cursor: 'pointer', textAlign: 'left', width: '100%', transition: 'background 150ms' }}
                onMouseEnter={e => (e.currentTarget.style.background = '#f6f7f9')}
                onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
              >
                <div style={{ width: 32, height: 32, borderRadius: 8, background: a.color, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  {a.icon}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: '0.83rem', fontWeight: 600, color: '#111827' }}>{a.label}</div>
                  <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>{a.desc}</div>
                </div>
                <ChevronRight size={14} style={{ color: '#d1d5db', flexShrink: 0 }} />
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
