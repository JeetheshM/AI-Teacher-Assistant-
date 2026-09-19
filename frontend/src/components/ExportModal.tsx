import React, { useState } from 'react';
import { FileDown, Printer, CheckCircle2, X, Layers, Sparkles } from 'lucide-react';
import { TeachingPackage } from '../types';
import { apiClient } from '../services/apiClient';
import { useToast } from './shared/ToastProvider';

interface ExportModalProps { teachingPackage: TeachingPackage; onClose: () => void; }

export const ExportModal: React.FC<ExportModalProps> = ({ teachingPackage, onClose }) => {
  const [exporting, setExporting] = useState(false);
  const [done, setDone] = useState(false);
  const { addToast } = useToast();

  const handleExportPdf = async () => {
    setExporting(true);
    try {
      const res = await apiClient.exportLessonPdf(teachingPackage.lesson.id || 'current', teachingPackage.lesson);
      if (res.blob) {
        const url = window.URL.createObjectURL(res.blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${teachingPackage.lesson.title.replace(/\s+/g, '_')}_Package.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        window.print();
      }
      setDone(true);
      addToast('Teaching package exported successfully!', 'success');
    } catch {
      window.print();
      addToast('PDF export unavailable. Opening print dialog instead.', 'info');
    } finally {
      setExporting(false);
    }
  };

  const items = [
    { label: 'Lesson Plan', detail: `${teachingPackage.lesson.title} · ${teachingPackage.lesson.total_duration_minutes || 45} min` },
    { label: 'Adaptive Explanations', detail: 'Core content & conceptual analogies' },
    { label: 'Classroom Activity', detail: teachingPackage.activity?.title || 'Interactive Team Activity' },
    { label: 'Assessment & Answer Key', detail: `${teachingPackage.quiz?.questions.length || 5} questions with Bloom-level tags` },
    { label: 'Curriculum Citations', detail: `${teachingPackage.sources.length} verified textbook references` },
  ];

  return (
    <div className="modal-overlay no-print" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 34, height: 34, borderRadius: 9, background: '#eef2ff', color: '#4f46e5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FileDown size={17} />
            </div>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#111827' }}>Export Teaching Package</h3>
              <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Print-ready classroom teaching packet</div>
            </div>
          </div>
          <button type="button" className="btn btn-ghost btn-xs" onClick={onClose}><X size={16} /></button>
        </div>

        <div className="modal-body">
          {/* Bundle contents */}
          <div style={{ background: '#f8f9fb', border: '1px solid #e5e7eb', borderRadius: 10, padding: '14px 18px', marginBottom: 16 }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#6b7280', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 5 }}>
              <Layers size={12} style={{ color: '#4f46e5' }} /> Included Materials
            </div>
            {items.map(item => (
              <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '7px 0', borderBottom: '1px solid #f0f2f5' }}>
                <CheckCircle2 size={14} style={{ color: '#059669', flexShrink: 0 }} />
                <div>
                  <span style={{ fontWeight: 700, fontSize: '0.83rem', color: '#111827' }}>{item.label}</span>
                  <span style={{ fontSize: '0.78rem', color: '#9ca3af' }}> — {item.detail}</span>
                </div>
              </div>
            ))}
          </div>

          {done && (
            <div style={{ background: '#ecfdf5', border: '1px solid #a7f3d0', borderRadius: 8, padding: '10px 14px', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.82rem', color: '#065f46', fontWeight: 600 }}>
              <CheckCircle2 size={15} style={{ color: '#059669' }} />
              Teaching package compiled successfully! Check your downloads or print dialog.
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button type="button" className="btn btn-secondary" onClick={() => window.print()}>
            <Printer size={15} /> Print Layout
          </button>
          <button type="button" className="btn btn-primary" onClick={handleExportPdf} disabled={exporting}>
            {exporting ? <Sparkles size={15} className="spin" /> : <FileDown size={15} />}
            <span>{exporting ? 'Compiling PDF…' : 'Download PDF Package'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
