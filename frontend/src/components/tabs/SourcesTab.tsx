import React from 'react';
import { BookOpen, FileCheck2, Bookmark, Hash, ShieldCheck, Info } from 'lucide-react';
import { CurriculumSource, DocumentUploadResponse } from '../../types';

interface SourcesTabProps {
  sources: CurriculumSource[];
  document: DocumentUploadResponse | null;
  isGrounded: boolean;
}

export const SourcesTab: React.FC<SourcesTabProps> = ({ sources, document, isGrounded }) => {
  return (
    <div className="fade-in">
      {/* Grounding Status */}
      <div className="card" style={{ padding: '18px 22px', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
        <div style={{ width: 44, height: 44, borderRadius: 12, background: isGrounded ? '#ecfdf5' : '#f0f2f5', display: 'flex', alignItems: 'center', justifyContent: 'center', color: isGrounded ? '#059669' : '#6b7280', flexShrink: 0 }}>
          {isGrounded ? <FileCheck2 size={22} /> : <BookOpen size={22} />}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 3 }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 800, color: '#111827' }}>
              {isGrounded ? 'Curriculum-Grounded Synthesis' : 'Standard Pedagogical Synthesis'}
            </h3>
            <span className={`pill ${isGrounded ? 'pill-grounded' : 'pill-ungrounded'}`}>
              {isGrounded ? '✓ Curriculum Grounded' : 'General AI Generation'}
            </span>
          </div>
          <p style={{ fontSize: '0.8rem', color: '#9ca3af' }}>
            {isGrounded
              ? `Teaching content was grounded in verified excerpts from "${document?.filename || 'Curriculum PDF'}"`
              : 'No custom curriculum document was provided; generated using foundational grade-level standards.'}
          </p>
        </div>
      </div>

      {/* How Grounding Works */}
      <div style={{ background: '#ecfdf5', border: '1px solid #a7f3d0', borderRadius: 10, padding: '14px 18px', marginBottom: 20, display: 'flex', gap: 12 }}>
        <ShieldCheck size={18} style={{ color: '#059669', flexShrink: 0, marginTop: 2 }} />
        <div>
          <div style={{ fontWeight: 700, fontSize: '0.8rem', color: '#065f46', marginBottom: 4 }}>How Curriculum Grounding Eliminates Hallucination</div>
          <p style={{ fontSize: '0.8rem', color: '#047857', lineHeight: 1.6 }}>
            Instead of querying an ungrounded LLM, TeachMate AI extracts syllabus text from your textbook, chunks the concepts into vector embeddings, and retrieves strictly relevant passages to ground the lesson plan, activities, and quiz questions.
          </p>
        </div>
      </div>

      {/* Sources list */}
      {sources && sources.length > 0 ? (
        <>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: '#9ca3af', marginBottom: 10 }}>
            Retrieved Textbook Passages · {sources.length} sources cited
          </div>
          {sources.map((src, i) => (
            <div key={i} className="source-card">
              <div className="source-card-header">
                <div className="source-citation">
                  <Bookmark size={14} style={{ color: '#059669' }} />
                  <span>{src.source}</span>
                  {src.page_number && <span className="time-badge">Page {src.page_number}</span>}
                </div>
                {src.chunk_id && (
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7rem', color: '#9ca3af', display: 'flex', alignItems: 'center', gap: 4 }}>
                    <Hash size={11} /> {src.chunk_id}
                  </span>
                )}
              </div>
              <div className="source-snippet">"{src.content}"</div>
            </div>
          ))}
        </>
      ) : (
        <div className="card" style={{ padding: '40px 24px', textAlign: 'center' }}>
          <Info size={28} style={{ color: '#d1d5db', margin: '0 auto 12px' }} />
          <p style={{ fontSize: '0.85rem', color: '#9ca3af' }}>No specific curriculum document citations associated with this lesson.</p>
        </div>
      )}
    </div>
  );
};
