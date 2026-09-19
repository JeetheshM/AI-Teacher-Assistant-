import React from 'react';
import {
  GraduationCap, LayoutDashboard, BookOpen, Library,
  FolderOpen, Settings, ChevronRight, Server, Zap, PlusCircle
} from 'lucide-react';

interface SidebarProps {
  onGoHome: () => void;
  hasLesson: boolean;
  onLoadDemo: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onGoHome, hasLesson, onLoadDemo }) => {
  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand" onClick={onGoHome}>
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
        <button className="sidebar-nav-item" style={{ opacity: 0.65, cursor: 'pointer' }} onClick={onLoadDemo}>
          <Library size={15} className="sidebar-nav-icon" />
          <span>Lesson Library</span>
          <span style={{ marginLeft: 'auto', fontSize: '0.65rem', color: '#6b7280', fontWeight: 600 }}>Demo</span>
        </button>
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
