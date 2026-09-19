import React, { useState, useRef } from 'react';
import {
  Upload, FileText, CheckCircle2, AlertCircle, X,
  Sparkles, BookOpen, Clock, BarChart2, Target, Zap
} from 'lucide-react';
import { LessonGenerationRequest, Difficulty, DocumentUploadResponse } from '../types';
import { apiClient } from '../services/apiClient';
import { useToast } from './shared/ToastProvider';

interface TeacherFormProps {
  initialValues: LessonGenerationRequest;
  document: DocumentUploadResponse | null;
  onDocumentUploaded: (doc: DocumentUploadResponse | null) => void;
  onSubmit: (req: LessonGenerationRequest) => void;
  isLoading: boolean;
}

export const TeacherForm: React.FC<TeacherFormProps> = ({
  initialValues, document, onDocumentUploaded, onSubmit, isLoading
}) => {
  const [form, setForm] = useState<LessonGenerationRequest>(initialValues);
  const [uploadState, setUploadState] = useState<'idle' | 'uploading' | 'ready' | 'error'>('idle');
  const [uploadError, setUploadError] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isDragOver, setIsDragOver] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const { addToast } = useToast();

  React.useEffect(() => {
    setForm(initialValues);
    if (initialValues.document_id && document) setUploadState('ready');
    else if (!initialValues.document_id) setUploadState('idle');
  }, [initialValues]);

  const set = (field: keyof LessonGenerationRequest, value: string | number) => {
    setForm(p => ({ ...p, [field]: value }));
    if (errors[field]) setErrors(p => { const n = { ...p }; delete n[field]; return n; });
  };

  const handleFile = async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadError('Please upload a PDF file (.pdf)');
      setUploadState('error');
      return;
    }
    setUploadState('uploading');
    setUploadError('');
    try {
      const res = await apiClient.uploadDocument(file);
      onDocumentUploaded(res);
      setForm(p => ({ ...p, document_id: res.document_id }));
      setUploadState('ready');
      addToast(`"${file.name}" processed and ready for grounding`, 'success');
    } catch (e: any) {
      setUploadError(e.message || 'Unable to process PDF. Continue without it, or retry.');
      setUploadState('error');
      addToast('PDF upload failed. You can continue without it.', 'error');
    }
  };

  const removeDoc = () => {
    onDocumentUploaded(null);
    setForm(p => { const n = { ...p }; delete n.document_id; return n; });
    setUploadState('idle');
    if (fileRef.current) fileRef.current.value = '';
  };

  const validate = (): boolean => {
    const e: Record<string, string> = {};
    if (!form.subject.trim()) e.subject = 'Required';
    if (!form.topic.trim()) e.topic = 'Required';
    if (!form.grade || form.grade < 1 || form.grade > 12) e.grade = 'Enter a grade 1–12';
    if (!form.duration_minutes || form.duration_minutes < 1) e.duration_minutes = 'Required';
    if (!form.difficulty) e.difficulty = 'Required';
    if (!form.learning_objective.trim()) e.learning_objective = 'Describe what students should learn';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) { addToast('Please complete the required fields', 'error'); return; }
    onSubmit(form);
  };

  const now = new Date();
  const hour = now.getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  return (
    <div className="fade-slide-up">
      {/* ── Hero ─────────────────────────────────── */}
      <div style={{ marginBottom: 36 }}>
        <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 10 }}>
          TeachMate AI Workspace
        </div>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, letterSpacing: '-0.03em', color: '#111827', marginBottom: 10, lineHeight: 1.15 }}>
          {greeting} 👋 — what are we teaching today?
        </h1>
        <p style={{ fontSize: '0.97rem', color: '#6b7280', maxWidth: 560, lineHeight: 1.6 }}>
          Describe your lesson and TeachMate will build a complete, curriculum-grounded teaching package — lesson plan, activities, quiz, and more.
        </p>
      </div>

      {/* ── Form Card ────────────────────────────── */}
      <form onSubmit={handleSubmit}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 20, alignItems: 'start' }}>

          {/* LEFT: Teaching Details */}
          <div className="card" style={{ padding: '28px 28px 24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 22, paddingBottom: 16, borderBottom: '1px solid #e5e7eb' }}>
              <div style={{ width: 32, height: 32, borderRadius: 8, background: '#eef2ff', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#4f46e5' }}>
                <BookOpen size={16} />
              </div>
              <div>
                <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#111827' }}>Lesson Details</div>
                <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Fill in the teaching requirements</div>
              </div>
            </div>

            {/* Subject + Grade row */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 14, marginBottom: 14 }}>
              <div className="form-group">
                <label className="form-label form-label-required">Subject</label>
                <input
                  type="text"
                  list="subject-list"
                  className={`form-input${errors.subject ? ' error' : ''}`}
                  placeholder="e.g. Science, Maths, English…"
                  value={form.subject}
                  onChange={e => set('subject', e.target.value)}
                />
                <datalist id="subject-list">
                  {['Science','Mathematics','English','Social Science','Computer Science','Environmental Studies','Physics','Chemistry','Biology'].map(s => <option key={s} value={s} />)}
                </datalist>
                {errors.subject && <div className="form-error"><AlertCircle size={12} />{errors.subject}</div>}
              </div>
              <div className="form-group">
                <label className="form-label form-label-required">Grade</label>
                <input
                  type="number" min={1} max={12}
                  className={`form-input${errors.grade ? ' error' : ''}`}
                  placeholder="8"
                  value={form.grade || ''}
                  onChange={e => set('grade', parseInt(e.target.value) || 0)}
                />
                {errors.grade && <div className="form-error"><AlertCircle size={12} />{errors.grade}</div>}
              </div>
            </div>

            {/* Topic */}
            <div className="form-group" style={{ marginBottom: 14 }}>
              <label className="form-label form-label-required">Topic</label>
              <input
                type="text"
                className={`form-input${errors.topic ? ' error' : ''}`}
                placeholder="e.g. Photosynthesis, Pythagorean Theorem…"
                value={form.topic}
                onChange={e => set('topic', e.target.value)}
              />
              {errors.topic && <div className="form-error"><AlertCircle size={12} />{errors.topic}</div>}
            </div>

            {/* Duration + Difficulty */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 14 }}>
              <div className="form-group">
                <label className="form-label form-label-required">
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Clock size={12} />Class Duration</span>
                </label>
                <select
                  className={`form-select${errors.duration_minutes ? ' error' : ''}`}
                  value={form.duration_minutes}
                  onChange={e => set('duration_minutes', parseInt(e.target.value))}
                >
                  <option value={30}>30 minutes</option>
                  <option value={45}>45 minutes</option>
                  <option value={60}>60 minutes</option>
                  <option value={90}>90 minutes</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label form-label-required">
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><BarChart2 size={12} />Difficulty</span>
                </label>
                <select
                  className={`form-select${errors.difficulty ? ' error' : ''}`}
                  value={form.difficulty}
                  onChange={e => set('difficulty', e.target.value as Difficulty)}
                >
                  <option value="easy">Easy — Foundational</option>
                  <option value="intermediate">Intermediate — Grade Benchmark</option>
                  <option value="advanced">Advanced — Extension</option>
                </select>
              </div>
            </div>

            {/* Learning Objective */}
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label form-label-required">
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Target size={12} />Primary Learning Objective</span>
              </label>
              <textarea
                className={`form-textarea${errors.learning_objective ? ' error' : ''}`}
                placeholder="What should students understand or be able to do after this lesson?"
                value={form.learning_objective}
                onChange={e => set('learning_objective', e.target.value)}
              />
              {errors.learning_objective && <div className="form-error"><AlertCircle size={12} />{errors.learning_objective}</div>}
              <div className="form-hint">Be specific — TeachMate will align the entire package to this objective.</div>
            </div>
          </div>

          {/* RIGHT column: Curriculum upload + Generate */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Curriculum card */}
            <div className="card" style={{ padding: '22px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16, paddingBottom: 14, borderBottom: '1px solid #e5e7eb' }}>
                <div style={{ width: 32, height: 32, borderRadius: 8, background: '#ecfdf5', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#059669' }}>
                  <FileText size={16} />
                </div>
                <div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#111827' }}>Curriculum Context</div>
                  <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Upload for grounded generation</div>
                </div>
              </div>

              {/* Upload states */}
              {uploadState === 'idle' || uploadState === 'error' ? (
                <>
                  <div
                    className={`dropzone${isDragOver ? ' dragover' : ''}`}
                    onClick={() => fileRef.current?.click()}
                    onDragOver={e => { e.preventDefault(); setIsDragOver(true); }}
                    onDragLeave={() => setIsDragOver(false)}
                    onDrop={e => { e.preventDefault(); setIsDragOver(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f); }}
                  >
                    <input ref={fileRef} type="file" accept=".pdf" style={{ display: 'none' }}
                      onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f); }} />
                    <div className="dropzone-icon"><Upload size={20} /></div>
                    <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#374151', marginBottom: 4 }}>
                      Upload Curriculum PDF
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#9ca3af', marginBottom: 10 }}>
                      Drop a textbook or syllabus PDF here
                    </div>
                    <button type="button" className="btn btn-secondary btn-sm" onClick={e => { e.stopPropagation(); fileRef.current?.click(); }}>
                      Choose PDF
                    </button>
                    <div style={{ fontSize: '0.68rem', color: '#9ca3af', marginTop: 10 }}>
                      PDF · up to 25 MB · optional but recommended
                    </div>
                  </div>
                  {uploadState === 'error' && (
                    <div className="form-error" style={{ marginTop: 8 }}>
                      <AlertCircle size={13} /> {uploadError}
                    </div>
                  )}
                </>
              ) : uploadState === 'uploading' ? (
                <div style={{ textAlign: 'center', padding: '28px 16px', border: '1px solid #e5e7eb', borderRadius: 12, background: '#f8f9fb' }}>
                  <div style={{ width: 44, height: 44, borderRadius: 22, background: '#eef2ff', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 12px', color: '#4f46e5' }}>
                    <Sparkles size={20} className="spin" />
                  </div>
                  <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#374151', marginBottom: 4 }}>Processing curriculum…</div>
                  <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Extracting, chunking & embedding text</div>
                </div>
              ) : (
                <div className="dropzone-ready">
                  <div style={{ width: 38, height: 38, borderRadius: 10, background: '#ecfdf5', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#059669', flexShrink: 0 }}>
                    <CheckCircle2 size={20} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 700, fontSize: '0.84rem', color: '#111827', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {document?.filename}
                    </div>
                    <div style={{ fontSize: '0.72rem', color: '#059669', fontWeight: 600, marginTop: 2 }}>
                      ✓ Curriculum indexed · Grounding enabled
                    </div>
                    {document?.page_count && (
                      <div style={{ fontSize: '0.7rem', color: '#9ca3af' }}>{document.page_count} pages ready</div>
                    )}
                  </div>
                  <button type="button" className="btn btn-ghost btn-xs" onClick={removeDoc} title="Remove">
                    <X size={14} />
                  </button>
                </div>
              )}
            </div>

            {/* Generate CTA */}
            <button
              type="submit"
              className="btn btn-cta"
              disabled={isLoading}
              style={{ width: '100%', justifyContent: 'center' }}
            >
              {isLoading ? (
                <>
                  <Sparkles size={18} className="spin" />
                  <span>Generating…</span>
                </>
              ) : (
                <>
                  <span style={{ fontSize: '1.1em' }}>✦</span>
                  <span>Generate Teaching Package</span>
                </>
              )}
            </button>

            {/* Hint */}
            <div style={{ fontSize: '0.72rem', color: '#9ca3af', textAlign: 'center', lineHeight: 1.5 }}>
              AI generates a draft · You review, edit and export.<br />
              Full teacher control at every step.
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};
