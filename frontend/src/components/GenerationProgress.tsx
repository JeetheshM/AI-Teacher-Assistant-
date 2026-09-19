import React, { useEffect, useState } from 'react';
import { CheckCircle2, Loader2, Sparkles } from 'lucide-react';

interface GenerationProgressProps {
  topic: string;
  hasCurriculum: boolean;
}

interface Step { label: string; detail: string; }

export const GenerationProgress: React.FC<GenerationProgressProps> = ({ topic, hasCurriculum }) => {
  const steps: Step[] = [
    { label: 'Analyzing lesson requirements', detail: `Grade standards and objectives for "${topic}"` },
    {
      label: hasCurriculum ? 'Retrieving curriculum context' : 'Curating pedagogical references',
      detail: hasCurriculum ? 'Running semantic search over uploaded textbook' : 'Aligning with grade-level benchmarks'
    },
    { label: 'Structuring lesson plan', detail: 'Timings, explanations, key points, misconceptions' },
    { label: 'Designing classroom activity', detail: 'Collaborative hands-on investigation & rubric' },
    { label: 'Building assessment', detail: 'Bloom-tagged questions with answer keys & quality checks' },
  ];

  const [idx, setIdx] = useState(0);

  useEffect(() => {
    if (idx >= steps.length - 1) return;
    const t = setTimeout(() => setIdx(i => i + 1), 480);
    return () => clearTimeout(t);
  }, [idx]);

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
      <div className="card fade-in" style={{ padding: '40px 48px', maxWidth: 560, width: '100%', textAlign: 'center' }}>
        {/* Animated spark */}
        <div style={{ width: 60, height: 60, borderRadius: 30, background: 'linear-gradient(135deg,#eef2ff,#e0e7ff)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px', color: '#4f46e5' }}>
          <Sparkles size={28} className="spin" />
        </div>

        <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#111827', marginBottom: 8, letterSpacing: '-0.02em' }}>
          Building your teaching package…
        </h2>
        <p style={{ fontSize: '0.84rem', color: '#9ca3af', marginBottom: 32 }}>
          TeachMate is preparing a {topic} lesson for Grade {hasCurriculum ? 'with curriculum grounding' : ''}.
        </p>

        <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', gap: 14 }}>
          {steps.map((step, i) => {
            const done = i < idx;
            const active = i === idx;
            return (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <div style={{ flexShrink: 0, marginTop: 2 }}>
                  {done ? (
                    <CheckCircle2 size={18} style={{ color: '#059669' }} />
                  ) : active ? (
                    <Loader2 size={18} style={{ color: '#4f46e5' }} className="spin" />
                  ) : (
                    <div style={{ width: 18, height: 18, borderRadius: '50%', border: '2px solid #e5e7eb' }} />
                  )}
                </div>
                <div>
                  <div style={{ fontSize: '0.87rem', fontWeight: done || active ? 600 : 400, color: done ? '#059669' : active ? '#111827' : '#9ca3af' }}>
                    {step.label}
                  </div>
                  {(done || active) && (
                    <div style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: 1 }}>{step.detail}</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
