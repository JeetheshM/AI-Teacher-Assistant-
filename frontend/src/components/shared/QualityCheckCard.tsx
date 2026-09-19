import React from 'react';
import { ShieldCheck, CheckCircle2, AlertCircle } from 'lucide-react';

interface CheckItem { label: string; passed: boolean; description?: string; }
interface QualityCheckCardProps { title: string; checks: CheckItem[]; disclaimer?: string; }

export const QualityCheckCard: React.FC<QualityCheckCardProps> = ({
  title, checks,
  disclaimer = 'Deterministic structural check verifies completeness, timings, and schema contracts. Always review before teaching.'
}) => {
  const passCount = checks.filter(c => c.passed).length;
  return (
    <div className="quality-panel">
      <div className="quality-panel-header">
        <div className="quality-panel-title">
          <ShieldCheck size={15} />
          {title}
        </div>
        <span className="pill pill-grounded">
          <CheckCircle2 size={11} /> {passCount}/{checks.length} Checks Passed
        </span>
      </div>
      <ul className="quality-checks-list">
        {checks.map((item, i) => (
          <li key={i} className="quality-check-item">
            {item.passed
              ? <CheckCircle2 size={14} className="quality-check-icon" />
              : <AlertCircle size={14} style={{ color: '#f59e0b', flexShrink: 0 }} />
            }
            <span>{item.label}</span>
          </li>
        ))}
      </ul>
      <div className="quality-disclaimer">{disclaimer}</div>
    </div>
  );
};
