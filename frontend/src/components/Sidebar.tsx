import React, { useEffect, useState } from 'react';
import {
  GraduationCap, LayoutDashboard, BookOpen, Library,
  FolderOpen, Zap, RefreshCw, BookMarked, Clock
} from 'lucide-react';
import { apiClient } from '../services/apiClient';

interface SavedLesson {
  id: string;
  title: string;
  subject: string;
  topic: string;
  grade: number;
  difficulty: string;
  status: string;
  created_at: string;
}

interface SidebarProps {
  onGoHome: () => void;
  hasLesson: boolean;
  onLoadDemo: () => void;
  onLoadLesson?: (lessonId: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onGoHome, hasLesson, onLoadDemo, onLoadLesson }) => {
  const [lessons, setLessons] = useState<SavedLesson[]>([]);
  const [loading, setLoading] = useState(false);
  const [showLibrary, setShowLibrary] = useState(false);

  const fetchLessons = async () => {
    setLoading(true);
    try {
      const data = await apiClient.getLessons();
      setLessons(data);
    } catch {
      setLessons([]);
    } finally {
      setLoading(false);
    }
  };

  const handleLibraryClick = () => {
    setShowLibrary(prev => !prev);
    if (!showLibrary) fetchLessons();
  };

  const timeAgo = (dateStr: string) => {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
  };

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand" onClick={onGoHome} style={{ cursor: 'pointer' }}>
        <div className="sidebar-brand-icon">
          <GraduationCap size={18} strokeWidth={2.5} />
        </div>
        <div className="sidebar-brand-text">
          <span className="sidebar-brand-title">TeachMate AI</span>
          <span className="sidebar-brand-sub">AI Teaching Copilot</span>
        </div>
      </div>

      {/* Primary Nav */}
      <div className="sidebar-section">
        <div className="sidebar-section-label">Workspace</div>
        <button className={`sidebar-nav-item ${!hasLesson ? 'active' : ''}`} onClick={onGoHome}>
          <LayoutDashboard size={15} className="sidebar-nav-icon" />
          <span>New Lesson</span>
        </button>

        {/* Lesson Library — fetches from Supabase */}
        <button
          className={`sidebar-nav-item ${showLibrary ? 'active' : ''}`}
          onClick={handleLibraryClick}
        >
          <Library size={15} className="sidebar-nav-icon" />
          <span>Lesson Library</span>
          {lessons.length > 0 && (
            <span style={{ marginLeft: 'auto', fontSize: '0.65rem', background: '#6366f1', color: '#fff', borderRadius: 8, padding: '1px 6px', fontWeight: 700 }}>
              {lessons.length}
            </span>
          )}
        </button>

        {/* Lesson Library panel */}
        {showLibrary && (
          <div style={{ marginLeft: 8, marginTop: 4, marginBottom: 4 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '4px 6px' }}>
              <span style={{ fontSize: '0.7rem', color: '#9ca3af', fontWeight: 600 }}>SAVED LESSONS</span>
              <button
                onClick={fetchLessons}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#6b7280', padding: 2 }}
                title="Refresh"
              >
                <RefreshCw size={11} />
              </button>
            </div>

            {loading && (
              <div style={{ padding: '8px 6px', fontSize: '0.72rem', color: '#9ca3af' }}>Loading from Supabase…</div>
            )}

            {!loading && lessons.length === 0 && (
              <div style={{ padding: '8px 6px', fontSize: '0.72rem', color: '#9ca3af', fontStyle: 'italic' }}>
                No saved lessons yet. Generate one!
              </div>
            )}

            {!loading && lessons.map(lesson => (
              <button
                key={lesson.id}
                onClick={() => onLoadLesson && onLoadLesson(lesson.id)}
                style={{
                  display: 'flex', flexDirection: 'column', alignItems: 'flex-start',
                  width: '100%', background: '#f9fafb', border: '1px solid #e5e7eb',
                  borderRadius: 8, padding: '6px 8px', marginBottom: 4,
                  cursor: 'pointer', textAlign: 'left',
                  transition: 'background 0.15s',
                }}
                onMouseEnter={e => (e.currentTarget.style.background = '#eef2ff')}
                onMouseLeave={e => (e.currentTarget.style.background = '#f9fafb')}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 5, width: '100%' }}>
                  <BookMarked size={11} color="#6366f1" />
                  <span style={{ fontSize: '0.72rem', fontWeight: 600, color: '#1f2937', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {lesson.title || lesson.topic}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 2 }}>
                  <span style={{ fontSize: '0.62rem', color: '#6b7280' }}>Grade {lesson.grade} · {lesson.subject}</span>
                  <span style={{ fontSize: '0.6rem', color: '#9ca3af', marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Clock size={9} />
                    {timeAgo(lesson.created_at)}
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}

        <button className="sidebar-nav-item" style={{ opacity: 0.65, cursor: 'pointer' }} onClick={onLoadDemo}>
          <FolderOpen size={15} className="sidebar-nav-icon" />
          <span>Curriculum Files</span>
          <span style={{ marginLeft: 'auto', fontSize: '0.65rem', color: '#6b7280', fontWeight: 600 }}>Demo</span>
        </button>
      </div>

      {/* Quick Demo */}
      <div className="sidebar-section">
        <div className="sidebar-section-label">Quick Start</div>
        <button className="sidebar-nav-item" onClick={onLoadDemo} style={{ background: '#fffbeb', border: '1px solid #fde68a', color: '#92400e' }}>
          <Zap size={15} className="sidebar-nav-icon" style={{ color: '#d97706' }} />
          <span>Demo: Grade 8 Science</span>
        </button>
      </div>

      {/* Footer */}
      <div className="sidebar-footer">
        <div
          style={{
            padding: '10px 10px',
            borderRadius: '10px',
            background: '#f6f7f9',
            fontSize: '0.75rem',
            color: '#6b7280',
          }}
        >
          <div style={{ fontWeight: 700, color: '#374151', marginBottom: 3 }}>TeachMate AI v1.0</div>
          <div>Hackathon Build · 2026</div>
        </div>
      </div>
    </aside>
  );
};
