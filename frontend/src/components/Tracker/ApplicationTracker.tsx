/*
 * Submitted applications view. Server statuses drive the badge and stage
 * indicator. Withdrawal calls the delete endpoint and removes the successful
 * result from local state; it is separate from removing a saved bookmark.
 */

import React, { useEffect, useState } from 'react';
import { applicationService } from '../../services/api';
import { Application } from '../../types';
import { Bookmark, Trash2, Send, CheckCircle2, ChevronRight } from 'lucide-react';

// The stepper shows five progressive stages; Rejected has its own badge
// and is absent from this list, so it does not highlight a successful stage.
const STAGES = ['Applied', 'Under Review', 'Shortlisted', 'Interview Scheduled', 'Accepted'] as const;
const STAGE_LABELS = ['Submitted', 'Under Review', 'Shortlisted', 'Interview', 'Offer'];

const STATUS_BADGE: Record<string, { bg: string; color: string }> = {
  Applied: { bg: 'var(--primary-soft)', color: 'var(--primary)' },
  'Under Review': { bg: 'var(--warning-soft)', color: 'var(--warning)' },
  Shortlisted: { bg: 'color-mix(in srgb, #8b5cf6 14%, transparent)', color: '#7c3aed' },
  'Interview Scheduled': { bg: 'color-mix(in srgb, #f97316 14%, transparent)', color: '#ea580c' },
  Accepted: { bg: 'var(--success-soft)', color: 'var(--success)' },
  Rejected: { bg: 'var(--danger-soft)', color: 'var(--danger)' },
};

export const ApplicationTracker: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  // Load the student's submitted applications and nested internship details.
  const fetchApplications = async () => {
    setLoading(true);
    try { setApplications(await applicationService.getApplications()); }
    catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchApplications(); }, []);

  // After confirmation, delete on the server before removing the local row.
  const handleWithdraw = async (id: number) => {
    if (window.confirm('Withdraw this application? This cannot be undone.')) {
      try { await applicationService.withdrawApplication(id); setApplications((prev) => prev.filter((a) => a.id !== id)); }
      catch (err) { console.error(err); }
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      {/* Header */}
      <div className="card p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-rise">
        <div>
          <span className="eyebrow">Application tracker</span>
          <h1 className="mt-1 text-xl sm:text-2xl font-extrabold flex items-center gap-2"><Bookmark className="w-5 h-5" style={{ color: 'var(--primary)' }} /> Your pipeline</h1>
          <p className="text-xs mt-1" style={{ color: 'var(--muted)' }}>Track every application from submission to offer.</p>
        </div>
        <div className="px-4 py-2.5 rounded-xl text-xs font-bold self-start" style={{ background: 'var(--primary-soft)', color: 'var(--primary)' }}>
          {applications.length} total
        </div>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((n) => <div key={n} className="card p-6"><div className="h-20 skeleton" /></div>)}
        </div>
      ) : applications.length === 0 ? (
        <div className="card p-12 text-center space-y-3">
          <div className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto" style={{ background: 'var(--surface-2)' }}><Send className="w-7 h-7" style={{ color: 'var(--muted-2)' }} /></div>
          <h3 className="font-bold">No applications yet</h3>
          <p className="text-xs" style={{ color: 'var(--muted)' }}>Start applying to internships to track them here.</p>
        </div>
      ) : (
        <div className="space-y-3 stagger">
          {applications.map((app) => {
            const currentStep = STAGES.indexOf(app.status as typeof STAGES[number]) + 1;
            const badge = STATUS_BADGE[app.status] || STATUS_BADGE['Applied'];
            return (
              <div key={app.id} className="card p-5 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3" style={{ borderBottom: '1px solid var(--border)' }}>
                  <div className="flex items-center gap-3 min-w-0">
                    <img src={app.internship.company_logo || 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=120&q=80'} alt="" className="w-11 h-11 rounded-xl object-cover" style={{ border: '1px solid var(--border)' }} />
                    <div className="min-w-0">
                      <h3 className="font-bold text-sm truncate">{app.internship.title}</h3>
                      <div className="text-xs truncate" style={{ color: 'var(--muted)' }}>
                        {app.internship.company_name} · {app.internship.location} · {app.internship.stipend_currency}{app.internship.stipend_amount.toLocaleString()}/mo
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="badge px-3 py-1.5" style={{ background: badge.bg, color: badge.color }}>{app.status}</span>
                    <button onClick={() => handleWithdraw(app.id)} className="w-8 h-8 rounded-lg flex items-center justify-center transition" style={{ color: 'var(--muted-2)' }} onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--danger-soft)'; e.currentTarget.style.color = 'var(--danger)'; }} onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--muted-2)'; }} title="Withdraw">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Stepper */}
                <div className="grid grid-cols-5 gap-1.5">
                  {STAGE_LABELS.map((label, i) => {
                    const step = i + 1;
                    const done = step < currentStep;
                    const active = step === currentStep;
                    return (
                      <div key={label} className="text-center">
                        <div className="h-2 rounded-full transition-all" style={done || active ? { background: 'linear-gradient(90deg, var(--primary), var(--accent))' } : { background: 'var(--surface-3)' }} />
                        <span className="text-[10px] font-bold mt-1.5 block flex items-center justify-center gap-0.5" style={{ color: active ? 'var(--primary)' : done ? 'var(--text-soft)' : 'var(--muted-2)' }}>
                          {done && <CheckCircle2 className="w-3 h-3" style={{ color: 'var(--success)' }} />}{label}
                        </span>
                      </div>
                    );
                  })}
                </div>

                {app.cover_letter && (
                  <div className="text-xs italic p-3 rounded-xl" style={{ background: 'var(--surface-2)', color: 'var(--muted)', border: '1px solid var(--border)' }}>
                    "{app.cover_letter.slice(0, 160)}{app.cover_letter.length > 160 ? '…' : ''}"
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
