import React from 'react';
import {
  GraduationCap,
  Sparkles,
  Server,
  Zap,
  PlusCircle
} from 'lucide-react';

interface NavbarProps {
  isMockMode: boolean;
  onToggleMockMode: () => void;
  backendHealthy: boolean | null;
  onLoadDemoData: () => void;
  onResetLesson: () => void;
  hasLesson: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  isMockMode,
  onToggleMockMode,
  backendHealthy,
  onLoadDemoData,
  onResetLesson,
  hasLesson
}) => {
  return (
    <header className="navbar">
      <div className="navbar-inner">
        <div className="brand-wrapper" onClick={onResetLesson}>
          <div className="brand-icon">
            <GraduationCap size={22} />
          </div>
          <div>
            <div className="brand-title">TeachMate AI</div>
            <div className="brand-tagline">AI Teaching Copilot</div>
          </div>
        </div>

        <div className="nav-actions">
          {/* Quick Demo Preset Button */}
          <button
            type="button"
            className="btn btn-ghost btn-sm"
            onClick={onLoadDemoData}
            title="Load Photosynthesis Grade 8 Demo Scenario"
          >
            <Zap size={14} className="text-amber-500" />
            <span>Load Demo (Grade 8 Science)</span>
          </button>

          {/* New Lesson button if currently viewing a generated package */}
          {hasLesson && (
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={onResetLesson}
            >
              <PlusCircle size={14} />
              <span>New Lesson</span>
            </button>
          )}

          {/* Backend Status Indicator */}
          <div
            className="status-pill un-grounded"
            title={
              backendHealthy === true
                ? 'Backend connected (http://localhost:8000/api)'
                : 'Live backend offline. Automatic mock fallback active.'
            }
          >
            <span
              className={`status-dot ${
                backendHealthy === true ? 'online' : 'offline'
              }`}
            />
            <span>
              {backendHealthy === true ? 'API Connected' : 'API Offline'}
            </span>
          </div>

          {/* Standalone / Mock Toggle for Hackathon Safety */}
          <button
            type="button"
            className={`btn btn-sm ${isMockMode ? 'status-pill mock-mode' : 'btn-ghost'}`}
            onClick={onToggleMockMode}
            title="Toggle between Live FastAPI Backend and Built-in Mock Service"
          >
            <Server size={13} />
            <span>{isMockMode ? 'Mock Mode (Active)' : 'Live API Mode'}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
