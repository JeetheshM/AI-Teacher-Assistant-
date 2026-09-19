import React from 'react';
import { Cpu, CheckCircle2, X } from 'lucide-react';
import { GenerationMetadata } from '../types';

interface AiMetadataDrawerProps { metadata?: GenerationMetadata; onClose: () => void; }

export const AiMetadataDrawer: React.FC<AiMetadataDrawerProps> = ({ metadata, onClose }) => {
  if (!metadata) return null;

  const rows = [
    { label: 'Underlying Model', value: metadata.model, mono: true },
    { label: 'Prompt Template Version', value: metadata.prompt_version, mono: true },
    { label: 'Curriculum RAG Grounding', value: metadata.curriculum_grounded ? '✓ Active & Enforced' : 'Unbounded', color: metadata.curriculum_grounded ? '#059669' : '#f59e0b' },
    { label: 'Retrieved Context Passages', value: `${metadata.retrieved_sources_count} Chunks`, mono: true },
    { label: 'Structural Validation', value: metadata.validation_status, color: '#059669' },
    { label: 'End-to-End Latency', value: `${(metadata.latency_ms / 1000).toFixed(2)}s (${metadata.latency_ms}ms)`, mono: true },
  ];

  return (
    <div className="modal-overlay no-print" onClick={onClose}>
      <div className="modal" style={{ maxWidth: 480 }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 34, height: 34, borderRadius: 9, background: '#eef2ff', color: '#4f46e5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Cpu size={17} />
            </div>
            <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#111827' }}>AI Generation Observability</h3>
          </div>
          <button type="button" className="btn btn-ghost btn-xs" onClick={onClose}><X size={16} /></button>
        </div>

        <div className="modal-body">
          <p style={{ fontSize: '0.78rem', color: '#9ca3af', marginBottom: 16, lineHeight: 1.55 }}>
            Inspection telemetry for hackathon judges detailing orchestration latency, grounding integrity, and prompt traceability.
          </p>
          <div style={{ background: '#f8f9fb', border: '1px solid #e5e7eb', borderRadius: 10, overflow: 'hidden' }}>
            {rows.map((row, i) => (
              <div key={row.label} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 16px', borderBottom: i < rows.length - 1 ? '1px solid #e5e7eb' : 'none', gap: 12 }}>
                <span style={{ fontSize: '0.78rem', color: '#6b7280', fontWeight: 500 }}>{row.label}</span>
                <span style={{ fontSize: '0.78rem', fontWeight: 700, color: row.color || '#111827', fontFamily: row.mono ? 'var(--font-mono)' : undefined }}>
                  {row.value}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" className="btn btn-secondary btn-sm" onClick={onClose}>Close Inspector</button>
        </div>
      </div>
    </div>
  );
};
