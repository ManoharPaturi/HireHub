/*
 * Student overview assembled from recommendations, applications and bookmarks.
 * The cards summarize those responses, while pipeline rows visualize each
 * application status. The displayed average stipend is for recommendations only.
 */

import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { internshipService, applicationService } from '../../services/api';
import { Internship, Application } from '../../types';
import { InternshipCard } from '../Internships/InternshipCard';
import {
  Send, Bookmark, Clock, Sparkles, TrendingUp, ArrowRight, Zap, Award,
} from 'lucide-react';

interface StudentDashboardProps {
  onNavigate: (tab: 'dashboard' | 'internships' | 'tracker' | 'saved' | 'messages' | 'profile') => void;
  onViewDetails: (internship: Internship) => void;
  onApply: (internship: Internship) => void;
}

export const StudentDashboard: React.FC<StudentDashboardProps> = ({ onNavigate, onViewDetails, onApply }) => {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState<Internship[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [savedCount, setSavedCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load independent dashboard datasets together; Promise.all waits until
    // all three API calls finish before updating the summary state.
    const load = async () => {
      setLoading(true);
      try {
        const [recs, apps, saved] = await Promise.all([
          internshipService.getRecommendations(),
          applicationService.getApplications(),
          internshipService.getSaved(),
        ]);
        setRecommendations(recs); setApplications(apps); setSavedCount(saved.length);
      } catch (err) { console.error(err); }
      finally { setLoading(false); }
    };
    load();
  }, []);

  // Use the server's saved result to update both the card flag and total.
  const handleToggleSave = async (id: number) => {
    try {
      const res = await internshipService.toggleSave(id);
      setRecommendations((prev) => prev.map((i) => (i.id === id ? { ...i, is_saved: res.saved } : i)));
      setSavedCount((c) => Math.max(0, c + (res.saved ? 1 : -1)));
    } catch (e) { console.error(e); }
  };

  const firstName = (user?.full_name || 'there').split(' ')[0];
  const shortlisted = applications.filter((a) => ['Shortlisted', 'Interview Scheduled', 'Accepted'].includes(a.status)).length;
  const avgStipend = recommendations.length
    ? Math.round(recommendations.reduce((s, r) => s + r.stipend_amount, 0) / recommendations.length)
    : 0;

  const stats = [
    { icon: Send, label: 'Applications', value: applications.length, color: 'var(--primary)', bg: 'var(--primary-soft)' },
    { icon: Bookmark, label: 'Saved', value: savedCount, color: 'var(--warning)', bg: 'var(--warning-soft)' },
    { icon: TrendingUp, label: 'Shortlisted', value: shortlisted, color: 'var(--success)', bg: 'var(--success-soft)' },
    { icon: Award, label: 'Avg stipend', value: avgStipend ? `${(avgStipend / 1000).toFixed(0)}k` : '—', color: 'var(--accent)', bg: 'color-mix(in srgb, var(--accent) 12%, transparent)' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      {/* Hero */}
      <div className="card p-6 sm:p-8 relative overflow-hidden animate-rise">
        <div className="absolute -right-16 -top-16 w-72 h-72 rounded-full blur-3xl animate-pulse-glow" style={{ background: 'var(--primary-soft)' }} />
        <div className="absolute inset-0 bg-grid opacity-40" style={{ maskImage: 'linear-gradient(to right, transparent, #000 30%, transparent 80%)', WebkitMaskImage: 'linear-gradient(to right, transparent, #000 30%, transparent 80%)' }} />
        <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-5">
          <div>
            <span className="badge mb-3" style={{ background: 'var(--primary-soft)', color: 'var(--primary)' }}>
              <Sparkles className="w-3 h-3" /> {recommendations.length > 0 ? `${recommendations.length} new matches` : 'Welcome'}
            </span>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">Welcome back, {firstName} 👋</h1>
            <p className="text-sm mt-2 max-w-xl" style={{ color: 'var(--muted)' }}>
              You have <strong style={{ color: 'var(--text)' }}>{applications.length} active application{applications.length !== 1 ? 's' : ''}</strong>. Keep the momentum going.
            </p>
          </div>
          <button onClick={() => onNavigate('internships')} className="btn btn-primary self-start md:self-auto">
            Browse internships <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 stagger">
        {stats.map((s) => (
          <div key={s.label} className="card p-5 flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0" style={{ background: s.bg, color: s.color }}>
              <s.icon className="w-5 h-5" />
            </div>
            <div className="min-w-0">
              <div className="text-2xl font-extrabold leading-none">{s.value}</div>
              <div className="text-xs font-medium mt-1" style={{ color: 'var(--muted)' }}>{s.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Pipeline preview */}
      <div className="card p-6 space-y-4">
        <div className="flex items-center justify-between pb-3" style={{ borderBottom: '1px solid var(--border)' }}>
          <h2 className="font-bold text-base flex items-center gap-2"><Clock className="w-4 h-4" style={{ color: 'var(--primary)' }} /> Active applications</h2>
          <button onClick={() => onNavigate('tracker')} className="text-xs font-semibold transition flex items-center gap-1" style={{ color: 'var(--primary)' }} onMouseEnter={(e) => { e.currentTarget.style.opacity = '0.7'; }} onMouseLeave={(e) => { e.currentTarget.style.opacity = '1'; }}>
            View all <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
        {applications.length === 0 ? (
          <div className="text-center py-10">
            <div className="w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-3" style={{ background: 'var(--surface-2)' }}><Send className="w-6 h-6" style={{ color: 'var(--muted-2)' }} /></div>
            <p className="text-sm font-semibold">No applications yet</p>
            <p className="text-xs mt-1" style={{ color: 'var(--muted)' }}>Browse listings and apply to get started.</p>
            <button onClick={() => onNavigate('internships')} className="btn btn-primary text-xs mt-4">Find internships</button>
          </div>
        ) : (
          <div className="space-y-3">
            {applications.slice(0, 2).map((app) => (
              <PipelineRow key={app.id} app={app} />
            ))}
          </div>
        )}
      </div>

      {/* Recommendations */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-extrabold text-lg flex items-center gap-2"><Zap className="w-5 h-5" style={{ color: 'var(--warning)' }} /> Recommended for you</h2>
            <p className="text-xs mt-0.5" style={{ color: 'var(--muted)' }}>Matched to your skills and preferences</p>
          </div>
          <button onClick={() => onNavigate('internships')} className="text-xs font-bold transition" style={{ color: 'var(--primary)' }}>See all</button>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((n) => (
              <div key={n} className="card p-5 space-y-4">
                <div className="flex items-center gap-3"><div className="w-11 h-11 rounded-xl skeleton" /><div className="flex-1 space-y-2"><div className="h-2.5 w-1/3 skeleton" /><div className="h-3.5 w-2/3 skeleton" /></div></div>
                <div className="h-12 skeleton" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 stagger">
            {recommendations.slice(0, 3).map((item) => (
              <InternshipCard key={item.id} internship={item} onViewDetails={onViewDetails} onToggleSave={handleToggleSave} onApply={onApply} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const STAGES = ['Applied', 'Under Review', 'Shortlisted', 'Interview Scheduled', 'Accepted'];
// Convert the stored status into a step index and highlight stages up to it.
const PipelineRow: React.FC<{ app: Application }> = ({ app }) => {
  const currentStep = STAGES.indexOf(app.status) + 1;
  return (
    <div className="p-4 rounded-xl" style={{ background: 'var(--surface-2)', border: '1px solid var(--border)' }}>
      <div className="flex items-center justify-between gap-3 mb-3">
        <div className="flex items-center gap-3 min-w-0">
          <img src={app.internship.company_logo || 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=120&q=80'} alt="" className="w-9 h-9 rounded-lg object-cover" />
          <div className="min-w-0">
            <div className="font-bold text-sm truncate">{app.internship.title}</div>
            <div className="text-xs truncate" style={{ color: 'var(--muted)' }}>{app.internship.company_name} · {app.internship.location}</div>
          </div>
        </div>
        <span className="badge flex-shrink-0" style={{ background: 'var(--primary-soft)', color: 'var(--primary)' }}>{app.status}</span>
      </div>
      <div className="grid grid-cols-5 gap-1.5">
        {STAGES.map((stage, i) => {
          const step = i + 1;
          const done = step < currentStep;
          const active = step === currentStep;
          return (
            <div key={stage} className="text-center">
              <div className="h-1.5 rounded-full transition-all" style={done || active ? { background: 'linear-gradient(90deg, var(--primary), var(--accent))' } : { background: 'var(--surface-3)' }} />
              <span className="text-[9px] font-bold mt-1 block" style={{ color: active ? 'var(--primary)' : 'var(--muted-2)' }}>{stage}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
