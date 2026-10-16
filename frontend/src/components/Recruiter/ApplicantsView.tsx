import React, { useState } from 'react';
import { recruiterService } from '../../services/api';
import { RecruiterApplication, Internship, Interview } from '../../types';
import { X, Calendar, FileText, Download, ExternalLink, MapPin, GraduationCap, Link as LinkIcon, MessageSquare } from 'lucide-react';

interface Props {
  applicants: RecruiterApplication[];
  internships: Internship[];
  interviews: Interview[];
  onRefresh: () => void;
  onMessage?: (studentUserId: number) => void;
}

const STATUSES = ['Applied', 'Under Review', 'Shortlisted', 'Interview Scheduled', 'Accepted', 'Rejected'] as const;
type Status = (typeof STATUSES)[number];

const STATUS_STYLE: Record<Status, { bg: string; color: string }> = {
  Applied: { bg: 'var(--primary-soft)', color: 'var(--primary)' },
  'Under Review': { bg: 'var(--warning-soft)', color: 'var(--warning)' },
  Shortlisted: { bg: 'color-mix(in srgb, #8b5cf6 14%, transparent)', color: '#7c3aed' },
  'Interview Scheduled': { bg: 'color-mix(in srgb, #f97316 14%, transparent)', color: '#ea580c' },
  Accepted: { bg: 'var(--success-soft)', color: 'var(--success)' },
  Rejected: { bg: 'var(--danger-soft)', color: 'var(--danger)' },
};

const COLUMN_META: Record<Status, { icon: string; border: string }> = {
  Applied: { icon: '📥', border: 'var(--primary)' },
  'Under Review': { icon: '🔍', border: 'var(--warning)' },
  Shortlisted: { icon: '⭐', border: '#8b5cf6' },
  'Interview Scheduled': { icon: '📅', border: '#f97316' },
  Accepted: { icon: '✅', border: 'var(--success)' },
  Rejected: { icon: '❌', border: 'var(--danger)' },
};

const ScheduleModal: React.FC<{ app: RecruiterApplication; onSchedule: (data: any) => void; onClose: () => void }> = ({ app, onSchedule, onClose }) => {
  const [form, setForm] = useState({ scheduled_at: '', duration_minutes: '30', interview_type: 'Video Call', meeting_link: '', notes: '' });
  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => setForm((f) => ({ ...f, [k]: e.target.value }));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in" style={{ background: 'rgba(15,23,42,0.6)', backdropFilter: 'blur(6px)' }} onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="w-full max-w-md rounded-3xl p-6 animate-scale-in" style={{ background: 'var(--surface)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-lg)' }}>
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'var(--primary-soft)', color: 'var(--primary)' }}><Calendar className="w-4 h-4" /></div>
            <h3 className="font-bold">Schedule interview</h3>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-lg flex items-center justify-center transition" style={{ color: 'var(--muted)' }} onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-3)'; }}><X className="w-4 h-4" /></button>
        </div>
        <p className="text-xs mb-4 p-2.5 rounded-lg" style={{ background: 'var(--surface-2)', color: 'var(--muted)' }}>Candidate: <strong style={{ color: 'var(--text)' }}>{app.student_name}</strong> · {app.internship_title}</p>
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>Date & time <span style={{ color: 'var(--danger)' }}>*</span></label>
            <input type="datetime-local" value={form.scheduled_at} onChange={set('scheduled_at')} required className="input" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>Duration</label>
              <select value={form.duration_minutes} onChange={set('duration_minutes')} className="select"><option value="30">30 min</option><option value="45">45 min</option><option value="60">60 min</option><option value="90">90 min</option></select>
            </div>
            <div>
              <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>Type</label>
              <select value={form.interview_type} onChange={set('interview_type')} className="select"><option>Video Call</option><option>Phone Call</option><option>In-Person</option><option>Technical Test</option></select>
            </div>
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>Meeting link</label>
            <input type="url" value={form.meeting_link} onChange={set('meeting_link')} placeholder="https://meet.google.com/…" className="input" />
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>Notes</label>
            <textarea rows={2} value={form.notes} onChange={set('notes')} placeholder="Technical round — bring examples of your work…" className="textarea" />
          </div>
        </div>
        <div className="flex gap-2 mt-5">
          <button onClick={onClose} className="btn btn-ghost flex-1">Cancel</button>
          <button onClick={() => onSchedule({ ...form, application_id: app.id, internship_id: app.internship_id, duration_minutes: parseInt(form.duration_minutes) })} disabled={!form.scheduled_at} className="btn btn-primary flex-1 disabled:opacity-50">Schedule</button>
        </div>
      </div>
    </div>
  );
};

export const ApplicantsView: React.FC<Props> = ({ applicants, internships, onRefresh, onMessage }) => {
  const [filter, setFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState<string>('All');
  const [updating, setUpdating] = useState<number | null>(null);
  const [scheduleFor, setScheduleFor] = useState<RecruiterApplication | null>(null);
  const [detailApp, setDetailApp] = useState<RecruiterApplication | null>(null);
  const [view, setView] = useState<'kanban' | 'table'>('table');

  const internshipOptions = ['All', ...internships.map((i) => i.title)];
  const filtered = applicants.filter((a) => {
    const inMatch = filter === 'All' || a.internship_title === filter;
    const stMatch = statusFilter === 'All' || a.status === statusFilter;
    return inMatch && stMatch;
  });

  const handleStatusChange = async (id: number, status: string) => {
    setUpdating(id);
    try { await recruiterService.updateApplicationStatus(id, status); onRefresh(); }
    catch { alert('Failed to update status.'); }
    finally { setUpdating(null); }
  };

  const handleSchedule = async (data: any) => {
    try { await recruiterService.scheduleInterview(data); setScheduleFor(null); onRefresh(); }
    catch { alert('Failed to schedule interview.'); }
  };

  const handleViewResume = async (app: RecruiterApplication) => {
    try {
      const res = await recruiterService.getResume(app.id);
      if (res.url) { window.open(res.url, '_blank'); return; }
      if (res.data && res.data.startsWith('data:')) {
        // Open the data URI in a new tab (renders PDFs inline in the browser).
        const w = window.open();
        if (w) {
          w.document.write(`<title>${res.file_name}</title><iframe src="${res.data}" style="width:100%;height:100%;border:0;" frameborder="0"></iframe>`);
          w.document.close();
        }
      } else {
        alert('No resume attached to this application.');
      }
    } catch (e) { console.error(e); alert('Could not load resume.'); }
  };

  const FALLBACK_AVATAR = 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=120&q=80';

  // Rich applicant detail modal (#7)
  const ApplicantDetail: React.FC<{ app: RecruiterApplication }> = ({ app }) => {
    const st = STATUS_STYLE[app.status as Status] || STATUS_STYLE['Applied'];
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in" style={{ background: 'rgba(15,23,42,0.6)', backdropFilter: 'blur(6px)' }} onClick={(e) => { if (e.target === e.currentTarget) setDetailApp(null); }}>
        <div className="w-full max-w-2xl rounded-3xl overflow-hidden animate-scale-in flex flex-col" style={{ background: 'var(--surface)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-lg)', maxHeight: '92vh' }}>
          {/* Header */}
          <div className="p-6 relative" style={{ borderBottom: '1px solid var(--border)', background: 'var(--surface-2)' }}>
            <button onClick={() => setDetailApp(null)} className="absolute top-4 right-4 w-8 h-8 rounded-lg flex items-center justify-center transition" style={{ color: 'var(--muted)' }}><X className="w-4 h-4" /></button>
            <div className="flex items-start gap-4">
              <img src={app.student_avatar || FALLBACK_AVATAR} alt="" className="w-16 h-16 rounded-2xl object-cover" style={{ border: '1px solid var(--border)' }} />
              <div className="min-w-0 flex-1">
                <h2 className="text-lg font-extrabold">{app.student_name}</h2>
                <p className="text-xs" style={{ color: 'var(--muted)' }}>{app.student_email}{app.student_phone ? ` · ${app.student_phone}` : ''}</p>
                <div className="flex flex-wrap items-center gap-1.5 mt-2">
                  <span className="badge" style={st}>{app.status}</span>
                  <span className="badge" style={{ background: 'var(--surface-3)', color: 'var(--muted)' }}>{app.internship_title}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Body */}
          <div className="p-6 overflow-y-auto space-y-4">
            {/* Quick facts */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[[GraduationCap, app.student_university || '—', 'University'],
                 [MapPin, app.student_location || '—', 'Location'],
                 [LinkIcon, app.student_cgpa ? `GPA ${app.student_cgpa}` : '—', 'CGPA'],
                 [FileText, new Date(app.applied_at).toLocaleDateString(), 'Applied']].map(([Icon, val, label]: any, i) => (
                <div key={i} className="p-3 rounded-xl" style={{ background: 'var(--surface-2)', border: '1px solid var(--border)' }}>
                  <Icon className="w-4 h-4 mb-1.5" style={{ color: 'var(--primary)' }} />
                  <p className="text-xs font-bold truncate">{val}</p>
                  <p className="text-[10px]" style={{ color: 'var(--muted)' }}>{label}</p>
                </div>
              ))}
            </div>

            {/* Bio */}
            {app.student_bio && (
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider mb-1.5" style={{ color: 'var(--muted)' }}>About</h3>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--text-soft)' }}>{app.student_bio}</p>
              </div>
            )}

            {/* Skills */}
            {app.student_skills && (
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider mb-2" style={{ color: 'var(--muted)' }}>Skills</h3>
                <div className="flex flex-wrap gap-1.5">
                  {app.student_skills.split(',').map((s, i) => <span key={i} className="chip" style={{ background: 'var(--primary-soft)', color: 'var(--primary)', borderColor: 'transparent' }}>{s.trim()}</span>)}
                </div>
              </div>
            )}

            {/* Cover letter */}
            {app.cover_letter && (
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider mb-1.5" style={{ color: 'var(--muted)' }}>Cover letter</h3>
                <div className="text-sm leading-relaxed p-4 rounded-xl italic" style={{ background: 'var(--surface-2)', color: 'var(--text-soft)', border: '1px solid var(--border)' }}>"{app.cover_letter}"</div>
              </div>
            )}

            {app.recruiter_notes && (
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider mb-1.5" style={{ color: 'var(--muted)' }}>Your notes</h3>
                <div className="text-sm p-3 rounded-xl" style={{ background: 'var(--warning-soft)', color: 'var(--text-soft)' }}>{app.recruiter_notes}</div>
              </div>
            )}
          </div>

          {/* Footer actions */}
          <div className="p-4 flex flex-wrap items-center gap-2" style={{ borderTop: '1px solid var(--border)', background: 'var(--surface-2)' }}>
            <select value={app.status} onChange={(e) => handleStatusChange(app.id, e.target.value)} disabled={updating === app.id} className="select text-xs flex-1 min-w-[160px]" style={{ background: st.bg, color: st.color, borderColor: 'transparent', fontWeight: 600 }}>
              {STATUSES.map((s) => <option key={s} value={s} style={{ background: 'var(--surface)', color: 'var(--text)' }}>{s}</option>)}
            </select>
            <button onClick={() => handleViewResume(app)} disabled={!app.has_resume && !app.resume_url} className="btn btn-soft text-xs disabled:opacity-40">
              <FileText className="w-3.5 h-3.5" /> {app.has_resume ? app.resume_filename || 'Resume' : 'Resume link'}
            </button>
            {onMessage && app.student_user_id && (
              <button onClick={() => { setDetailApp(null); onMessage(app.student_user_id!); }} className="btn btn-soft text-xs">
                <MessageSquare className="w-3.5 h-3.5" /> Message
              </button>
            )}
            <button onClick={() => { setDetailApp(null); setScheduleFor(app); }} className="btn btn-primary text-xs">
              <Calendar className="w-3.5 h-3.5" /> Schedule
            </button>
          </div>
        </div>
      </div>
    );
  };

  const ApplicantCard: React.FC<{ app: RecruiterApplication }> = ({ app }) => {
    const st = STATUS_STYLE[app.status as Status] || STATUS_STYLE['Applied'];
    return (
      <div className="p-3 rounded-xl transition cursor-pointer" style={{ background: 'var(--surface-2)', border: '1px solid var(--border)' }} onClick={() => setDetailApp(app)} onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'color-mix(in srgb, var(--primary) 30%, var(--border))'; }} onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border)'; }}>
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 min-w-0">
            <img src={app.student_avatar || FALLBACK_AVATAR} alt="" className="w-9 h-9 rounded-lg object-cover flex-shrink-0" />
            <div className="min-w-0">
              <p className="text-sm font-bold leading-none truncate">{app.student_name}</p>
              <p className="text-[11px] mt-0.5 truncate" style={{ color: 'var(--muted)' }}>{app.student_university || app.student_email}</p>
            </div>
          </div>
          {app.student_cgpa && <span className="badge flex-shrink-0" style={{ background: 'var(--surface-3)', color: 'var(--muted)' }}>GPA {app.student_cgpa}</span>}
        </div>
        <p className="text-xs mb-2 truncate" style={{ color: 'var(--muted)' }}>{app.internship_title}</p>
        <div className="flex gap-1.5" onClick={(e) => e.stopPropagation()}>
          <select value={app.status} onChange={(e) => handleStatusChange(app.id, e.target.value)} disabled={updating === app.id} className="select text-xs py-1.5 flex-1 disabled:opacity-60" style={{ background: st.bg, color: st.color, borderColor: 'transparent', fontWeight: 600 }}>
            {STATUSES.map((s) => <option key={s} value={s} style={{ background: 'var(--surface)', color: 'var(--text)' }}>{s}</option>)}
          </select>
          {(app.has_resume || app.resume_url) && <button onClick={() => handleViewResume(app)} className="btn btn-soft text-xs px-2.5 py-1.5" title="View resume"><FileText className="w-3.5 h-3.5" /></button>}
          {onMessage && app.student_user_id && <button onClick={() => onMessage(app.student_user_id!)} className="btn btn-soft text-xs px-2.5 py-1.5" title="Message candidate"><MessageSquare className="w-3.5 h-3.5" /></button>}
          <button onClick={() => setScheduleFor(app)} className="btn btn-soft text-xs px-2.5 py-1.5"><Calendar className="w-3.5 h-3.5" /></button>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-5 max-w-7xl">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-2">
        <div className="flex gap-1.5 p-1 rounded-xl" style={{ background: 'var(--surface-2)' }}>
          {(['table', 'kanban'] as const).map((v) => (
            <button key={v} onClick={() => setView(v)} className="px-4 py-1.5 rounded-lg text-xs font-semibold transition capitalize" style={view === v ? { background: 'var(--surface)', color: 'var(--primary)', boxShadow: 'var(--shadow-sm)' } : { color: 'var(--muted)' }}>
              {v === 'kanban' ? '🗂️ Kanban' : '📋 Table'}
            </button>
          ))}
        </div>
        <select value={filter} onChange={(e) => setFilter(e.target.value)} className="select" style={{ width: 'auto' }}>{internshipOptions.map((o) => <option key={o}>{o}</option>)}</select>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="select" style={{ width: 'auto' }}>
          <option>All</option>{STATUSES.map((s) => <option key={s}>{s}</option>)}
        </select>
        <span className="text-xs ml-auto" style={{ color: 'var(--muted)' }}>{filtered.length} applicant{filtered.length !== 1 ? 's' : ''}</span>
      </div>

      {/* Kanban */}
      {view === 'kanban' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
          {STATUSES.map((status) => {
            const group = filtered.filter((a) => a.status === status);
            const meta = COLUMN_META[status];
            return (
              <div key={status} className="rounded-2xl min-h-[200px] flex flex-col" style={{ background: 'var(--surface-2)', borderTop: `3px solid ${meta.border}` }}>
                <div className="px-3 py-2.5 flex items-center gap-2">
                  <span className="text-sm">{meta.icon}</span>
                  <span className="text-xs font-bold">{status}</span>
                  <span className="ml-auto text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center" style={{ background: 'var(--surface-3)', color: 'var(--muted)' }}>{group.length}</span>
                </div>
                <div className="p-2 space-y-2 flex-1 overflow-y-auto">
                  {group.map((app) => <ApplicantCard key={app.id} app={app} />)}
                  {group.length === 0 && <p className="text-center text-xs pt-4" style={{ color: 'var(--muted-2)' }}>None</p>}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Table */}
      {view === 'table' && (
        <div className="space-y-3 stagger">
          {filtered.length === 0 ? (
            <div className="card p-12 text-center" style={{ color: 'var(--muted)' }}>No applicants match these filters.</div>
          ) : (
            filtered.map((app) => {
              const st = STATUS_STYLE[app.status as Status] || STATUS_STYLE['Applied'];
              return (
                <div key={app.id} className="card p-5 cursor-pointer transition" onClick={() => setDetailApp(app)} onMouseEnter={(e) => { e.currentTarget.style.boxShadow = 'var(--shadow-md)'; e.currentTarget.style.transform = 'translateY(-2px)'; }} onMouseLeave={(e) => { e.currentTarget.style.boxShadow = ''; e.currentTarget.style.transform = ''; }}>
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div className="flex items-center gap-4 min-w-0 flex-1">
                      <img src={app.student_avatar || FALLBACK_AVATAR} alt="" className="w-12 h-12 rounded-2xl object-cover flex-shrink-0" style={{ border: '1px solid var(--border)' }} />
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h4 className="font-bold text-sm">{app.student_name}</h4>
                          <span className="badge" style={st}>{app.status}</span>
                          {(app.has_resume || app.resume_url) && <span className="badge" style={{ background: 'var(--success-soft)', color: 'var(--success)' }}><FileText className="w-3 h-3" /> Resume</span>}
                        </div>
                        <p className="text-xs mt-0.5 truncate" style={{ color: 'var(--muted)' }}>
                          {app.student_email}{app.student_university ? ` · ${app.student_university}` : ''}{app.student_cgpa ? ` · GPA ${app.student_cgpa}` : ''} · {app.internship_title}
                        </p>
                        {app.student_skills && <p className="text-[11px] mt-1 truncate" style={{ color: 'var(--muted-2)' }}>Skills: {app.student_skills}</p>}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
                      <select value={app.status} onChange={(e) => handleStatusChange(app.id, e.target.value)} disabled={updating === app.id} className="select text-xs py-1.5 w-40 disabled:opacity-60" style={{ background: st.bg, color: st.color, borderColor: 'transparent', fontWeight: 600 }}>
                        {STATUSES.map((s) => <option key={s} value={s} style={{ background: 'var(--surface)', color: 'var(--text)' }}>{s}</option>)}
                      </select>
                      {(app.has_resume || app.resume_url) && (
                        <button onClick={() => handleViewResume(app)} className="btn btn-soft text-xs px-3 py-1.5" title="View resume">
                          {app.has_resume ? <><Download className="w-3.5 h-3.5" /> Resume</> : <><ExternalLink className="w-3.5 h-3.5" /> Link</>}
                        </button>
                      )}
                      {onMessage && app.student_user_id && (
                        <button onClick={() => onMessage(app.student_user_id!)} className="btn btn-soft text-xs px-3 py-1.5" title="Message candidate">
                          <MessageSquare className="w-3.5 h-3.5" /> Message
                        </button>
                      )}
                      <button onClick={() => setScheduleFor(app)} className="btn btn-soft text-xs px-3 py-1.5"><Calendar className="w-3.5 h-3.5" /></button>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {scheduleFor && <ScheduleModal app={scheduleFor} onSchedule={handleSchedule} onClose={() => setScheduleFor(null)} />}
      {detailApp && <ApplicantDetail app={detailApp} />}
    </div>
  );
};
