import React from 'react';
import { Server, PlusCircle, ChevronRight } from 'lucide-react';

interface TopBarProps {
  title: string;
  breadcrumb?: string;
  backendHealthy: boolean | null;
  isMockMode: boolean;
  onToggleMockMode: () => void;
  hasLesson: boolean;
  onNewLesson: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({
  title,
  breadcrumb,
  backendHealthy,
  isMockMode,
  onToggleMockMode,
  hasLesson,
  onNewLesson,
}) => {
  return (
    <div className="topbar">
      <div className="topbar-left">
        {breadcrumb && (
          <div className="topbar-breadcrumb">
            <span>{breadcrumb}</span>
            <ChevronRight size={13} />
          </div>
        )}
        <span className="topbar-title">{title}</span>
      </div>

      <div className="topbar-right">
        {/* Backend / Mock status */}
        <button
          onClick={onToggleMockMode}
          className="btn btn-ghost btn-sm"
          title={isMockMode ? 'Switch to live API' : 'Switch to mock mode'}
          style={{ gap: 6 }}
        >
          <span
            className="status-dot"
            style={{
              background: isMockMode ? '#f59e0b' : backendHealthy ? '#10b981' : '#f59e0b',
              boxShadow: !isMockMode && backendHealthy ? '0 0 6px rgba(16,185,129,0.6)' : 'none',
              width: 7, height: 7, borderRadius: '50%', flexShrink: 0
            }}
          />
          <span style={{ fontSize: '0.78rem', color: '#6b7280', fontWeight: 600 }}>
            {isMockMode ? 'Demo Mode' : backendHealthy ? 'API Connected' : 'API Offline'}
          </span>
        </button>

        {hasLesson && (
          <button className="btn btn-secondary btn-sm" onClick={onNewLesson}>
            <PlusCircle size={13} />
            <span>New Lesson</span>
          </button>
        )}

        {/* Teacher Avatar */}
        <div className="avatar-chip">
          <div className="avatar-dot">DT</div>
          <span className="avatar-name">Demo Teacher</span>
        </div>
      </div>
    </div>
  );
};
