/*
 * Interview schedule display. Stored timestamps split interviews into upcoming
 * and past lists. Meeting links open externally; the calendar-grid alternative
 * is a placeholder rather than an implemented calendar.
 */

import React, { useState } from 'react';
import { Interview, RecruiterApplication } from '../../types';
import { Video, Clock, ExternalLink, Calendar, ListChecks } from 'lucide-react';

interface Props {
  interviews: Interview[];
  applicants: RecruiterApplication[];
  onRefresh: () => void;
}

export const InterviewCalendar: React.FC<Props> = ({ interviews }) => {
  const [view, setView] = useState<'list' | 'calendar'>('list');

  const now = Date.now();
  // Compare stored timestamps with the browser clock, then sort upcoming
  // interviews soonest first and past interviews most recent first.
  const upcoming = interviews.filter((i) => new Date(i.scheduled_at).getTime() > now).sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime());
  const past = interviews.filter((i) => new Date(i.scheduled_at).getTime() <= now).sort((a, b) => new Date(b.scheduled_at).getTime() - new Date(a.scheduled_at).getTime());

  // Format one interview's timestamp, duration, type and optional meeting link.
  const InterviewCard: React.FC<{ interview: Interview; dim?: boolean }> = ({ interview, dim }) => {
    const date = new Date(interview.scheduled_at);
    return (
      <div className="card p-4 flex items-center justify-between gap-4 transition" style={dim ? { opacity: 0.7 } : undefined} onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = 'var(--shadow-md)'; }} onMouseLeave={(e) => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = ''; }}>
        <div className="flex items-center gap-4 min-w-0">
          <div className="rounded-xl text-center flex-shrink-0 min-w-[68px] py-2 px-3" style={{ background: 'var(--primary-soft)', border: '1px solid var(--border)' }}>
            <p className="text-[10px] font-bold uppercase" style={{ color: 'var(--primary)' }}>{date.toLocaleString('default', { month: 'short' })}</p>
            <p className="text-xl font-extrabold leading-none my-0.5">{date.getDate()}</p>
            <p className="text-[10px]" style={{ color: 'var(--muted)' }}>{date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
          </div>
          <div className="min-w-0">
            <h4 className="font-bold text-sm truncate">{interview.candidate_name || 'Candidate'}</h4>
            <p className="text-xs truncate mb-1.5" style={{ color: 'var(--muted)' }}>{interview.internship_title}</p>
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="badge" style={{ background: 'var(--surface-2)', color: 'var(--text-soft)' }}><Video className="w-3 h-3" /> {interview.interview_type}</span>
              <span className="badge" style={{ background: 'var(--surface-2)', color: 'var(--text-soft)' }}><Clock className="w-3 h-3" /> {interview.duration_minutes}m</span>
              <span className="badge" style={interview.status === 'Completed' ? { background: 'var(--success-soft)', color: 'var(--success)' } : { background: 'var(--warning-soft)', color: 'var(--warning)' }}>{interview.status}</span>
            </div>
          </div>
        </div>
        <div className="flex flex-col gap-1.5 flex-shrink-0">
          {interview.meeting_link && (
            <a href={interview.meeting_link} target="_blank" rel="noreferrer" className="btn btn-primary text-xs">
              <ExternalLink className="w-3.5 h-3.5" /> Join
            </a>
          )}
          {interview.notes && (
            <button className="btn btn-ghost text-xs">Notes</button>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-4xl space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-extrabold">Interview schedule</h2>
          <p className="text-xs mt-0.5" style={{ color: 'var(--muted)' }}>{upcoming.length} upcoming · {past.length} past</p>
        </div>
        <div className="flex gap-1 p-1 rounded-xl" style={{ background: 'var(--surface-2)' }}>
          <button onClick={() => setView('list')} className="px-4 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5" style={view === 'list' ? { background: 'var(--surface)', color: 'var(--primary)', boxShadow: 'var(--shadow-sm)' } : { color: 'var(--muted)' }}><ListChecks className="w-3.5 h-3.5" /> List</button>
          <button onClick={() => setView('calendar')} className="px-4 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5" style={view === 'calendar' ? { background: 'var(--surface)', color: 'var(--primary)', boxShadow: 'var(--shadow-sm)' } : { color: 'var(--muted)' }}><Calendar className="w-3.5 h-3.5" /> Calendar</button>
        </div>
      </div>

      {view === 'list' ? (
        <div className="space-y-7">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--muted)' }}>Upcoming ({upcoming.length})</h3>
            {upcoming.length === 0 ? (
              <div className="card p-10 text-center">
                <div className="w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-3" style={{ background: 'var(--surface-2)' }}><Calendar className="w-6 h-6" style={{ color: 'var(--muted-2)' }} /></div>
                <p className="text-sm font-semibold">No upcoming interviews</p>
                <p className="text-xs mt-1" style={{ color: 'var(--muted)' }}>Schedule one from the Applicants tab.</p>
              </div>
            ) : (
              <div className="space-y-3 stagger">
                {upcoming.map((iv) => <InterviewCard key={iv.id} interview={iv} />)}
              </div>
            )}
          </div>
          {past.length > 0 && (
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--muted)' }}>Past ({past.length})</h3>
              <div className="space-y-3">
                {past.map((iv) => <InterviewCard key={iv.id} interview={iv} dim />)}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="card p-12 text-center">
          <div className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4" style={{ background: 'var(--surface-2)' }}><Calendar className="w-7 h-7" style={{ color: 'var(--muted-2)' }} /></div>
          <p className="text-sm font-semibold">Calendar grid coming soon</p>
          <p className="text-xs mt-1" style={{ color: 'var(--muted)' }}>Switch to list view to see all interviews.</p>
        </div>
      )}
    </div>
  );
};
