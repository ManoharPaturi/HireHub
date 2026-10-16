import React from 'react';
import { RecruiterProfile, RecruiterStats, Internship, RecruiterApplication } from '../../types';
import { TrendingUp, FileText, Star, CalendarCheck, ArrowRight, Plus } from 'lucide-react';

type RecruiterPage = 'dashboard' | 'post' | 'manage' | 'applicants' | 'interviews' | 'profile' | 'notifications' | 'settings';

interface Props {
  stats: RecruiterStats | null;
  internships: Internship[];
  applicants: RecruiterApplication[];
  profile: RecruiterProfile | null;
  onNavigate: (page: RecruiterPage) => void;
  onRefresh: () => void;
}

const STATUS_BADGE: Record<string, { bg: string; color: string }> = {
  Applied: { bg: 'var(--primary-soft)', color: 'var(--primary)' },
  'Under Review': { bg: 'var(--warning-soft)', color: 'var(--warning)' },
  Shortlisted: { bg: 'color-mix(in srgb, #8b5cf6 14%, transparent)', color: '#7c3aed' },
  'Interview Scheduled': { bg: 'color-mix(in srgb, #f97316 14%, transparent)', color: '#ea580c' },
  Accepted: { bg: 'var(--success-soft)', color: 'var(--success)' },
  Rejected: { bg: 'var(--danger-soft)', color: 'var(--danger)' },
};

export const RecruiterDashboard: React.FC<Props> = ({ stats, internships, applicants, profile, onNavigate }) => {
  const s = stats || { active_posts: 0, total_applications: 0, shortlisted: 0, interviews_scheduled: 0, total_accepted: 0 };
  const recentApplicants = applicants.slice(0, 5);
  const recentInternships = internships.slice(0, 4);
  const firstName = (profile?.full_name || 'Recruiter').split(' ')[0];

  const kpis = [
    { icon: Plus, label: 'Active postings', value: s.active_posts, color: 'var(--primary)', bg: 'var(--primary-soft)' },
    { icon: FileText, label: 'Total applications', value: s.total_applications, color: 'var(--accent)', bg: 'color-mix(in srgb, var(--accent) 12%, transparent)' },
    { icon: Star, label: 'Shortlisted', value: s.shortlisted, color: 'var(--warning)', bg: 'var(--warning-soft)' },
    { icon: CalendarCheck, label: 'Interviews', value: s.interviews_scheduled, color: 'var(--success)', bg: 'var(--success-soft)' },
  ];

  const pipelineGroups = [
    { status: 'Applied', label: 'Applied', color: 'var(--primary)' },
    { status: 'Shortlisted', label: 'Shortlisted', color: '#7c3aed' },
    { status: 'Interview Scheduled', label: 'Interview', color: '#ea580c' },
    { status: 'Accepted', label: 'Accepted', color: 'var(--success)' },
  ];

  return (
    <div className="space-y-6 max-w-7xl">
      {/* Welcome banner */}
      <div className="card p-6 relative overflow-hidden animate-rise">
        <div className="absolute -right-12 -top-12 w-56 h-56 rounded-full blur-3xl animate-pulse-glow" style={{ background: 'var(--primary-soft)' }} />
        <div className="relative flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="eyebrow">Recruiter dashboard</span>
            <h2 className="mt-1 text-2xl font-extrabold">Welcome back, {firstName} 👋</h2>
            <p className="text-sm mt-1" style={{ color: 'var(--muted)' }}>{profile?.company_name} · {profile?.designation || 'Recruiter'}</p>
          </div>
          <button onClick={() => onNavigate('post')} className="btn btn-primary self-start sm:self-auto">
            <Plus className="w-4 h-4" /> Post new role
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 stagger">
        {kpis.map((k) => (
          <div key={k.label} className="card p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: k.bg, color: k.color }}>
                <k.icon className="w-5 h-5" />
              </div>
              <span className="text-3xl font-extrabold">{k.value}</span>
            </div>
            <p className="text-xs font-medium" style={{ color: 'var(--muted)' }}>{k.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Postings */}
        <div className="xl:col-span-2 card p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-sm">My internship postings</h3>
            <button onClick={() => onNavigate('manage')} className="text-xs font-semibold flex items-center gap-1 transition" style={{ color: 'var(--primary)' }} onMouseEnter={(e) => { e.currentTarget.style.opacity = '0.7'; }} onMouseLeave={(e) => { e.currentTarget.style.opacity = '1'; }}>
              View all <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
          {recentInternships.length === 0 ? (
            <div className="text-center py-10">
              <div className="w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-3" style={{ background: 'var(--surface-2)' }}><Plus className="w-6 h-6" style={{ color: 'var(--muted-2)' }} /></div>
              <p className="text-sm font-semibold">No postings yet</p>
              <button onClick={() => onNavigate('post')} className="btn btn-soft text-xs mt-3">Post your first role</button>
            </div>
          ) : (
            <div className="space-y-2">
              {recentInternships.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-3 rounded-xl transition" style={{ background: 'var(--surface-2)' }} onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-3)'; }} onMouseLeave={(e) => { e.currentTarget.style.background = 'var(--surface-2)'; }}>
                  <div className="min-w-0">
                    <p className="text-sm font-bold truncate">{item.title}</p>
                    <p className="text-xs mt-0.5" style={{ color: 'var(--muted)' }}>{item.mode} · {item.duration} · {item.stipend_currency}{item.stipend_amount.toLocaleString()}/mo</p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                    <span className="badge" style={{ background: 'var(--surface-3)', color: 'var(--muted)' }}>{item.applications_count || 0} apps</span>
                    <span className="badge" style={item.is_active ? { background: 'var(--success-soft)', color: 'var(--success)' } : { background: 'var(--surface-3)', color: 'var(--muted-2)' }}>
                      {item.is_active ? 'Active' : 'Closed'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Pipeline summary */}
        <div className="card p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-sm">Pipeline summary</h3>
            <button onClick={() => onNavigate('applicants')} className="text-xs font-semibold flex items-center gap-1 transition" style={{ color: 'var(--primary)' }} onMouseEnter={(e) => { e.currentTarget.style.opacity = '0.7'; }} onMouseLeave={(e) => { e.currentTarget.style.opacity = '1'; }}>
              View <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="space-y-3">
            {pipelineGroups.map((g) => {
              const count = applicants.filter((a) => a.status === g.status).length;
              const pct = s.total_applications > 0 ? Math.round((count / s.total_applications) * 100) : 0;
              return (
                <div key={g.status}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold" style={{ color: 'var(--text-soft)' }}>{g.label}</span>
                    <span className="text-sm font-extrabold">{count}</span>
                  </div>
                  <div className="w-full rounded-full h-1.5" style={{ background: 'var(--surface-3)' }}>
                    <div className="h-1.5 rounded-full transition-all" style={{ width: `${pct}%`, background: g.color }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Recent applicants */}
      <div className="card p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold text-sm">Recent applicants</h3>
          <button onClick={() => onNavigate('applicants')} className="text-xs font-semibold flex items-center gap-1 transition" style={{ color: 'var(--primary)' }} onMouseEnter={(e) => { e.currentTarget.style.opacity = '0.7'; }} onMouseLeave={(e) => { e.currentTarget.style.opacity = '1'; }}>
            View all <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
        {recentApplicants.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-sm" style={{ color: 'var(--muted)' }}>No applicants yet. Post roles to start receiving applications.</p>
          </div>
        ) : (
          <div className="overflow-x-auto -mx-2">
            <table className="w-full text-sm">
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  {['Candidate', 'Position', 'University', 'CGPA', 'Status', 'Applied'].map((h) => (
                    <th key={h} className="text-left text-xs font-bold px-2 py-2" style={{ color: 'var(--muted)' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {recentApplicants.map((app) => (
                  <tr key={app.id} className="transition" style={{ borderBottom: '1px solid var(--border)' }} onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-2)'; }} onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}>
                    <td className="px-2 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-lg flex items-center justify-center text-white text-xs font-bold flex-shrink-0" style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent))' }}>{app.student_name[0]}</div>
                        <div className="min-w-0">
                          <p className="font-bold text-xs truncate">{app.student_name}</p>
                          <p className="text-[10px] truncate" style={{ color: 'var(--muted)' }}>{app.student_email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-2 py-3 text-xs truncate max-w-[160px]" style={{ color: 'var(--text-soft)' }}>{app.internship_title}</td>
                    <td className="px-2 py-3 text-xs" style={{ color: 'var(--muted)' }}>{app.student_university || '—'}</td>
                    <td className="px-2 py-3 text-xs font-semibold">{app.student_cgpa ?? '—'}</td>
                    <td className="px-2 py-3"><span className="badge" style={STATUS_BADGE[app.status] || STATUS_BADGE['Applied']}>{app.status}</span></td>
                    <td className="px-2 py-3 text-xs" style={{ color: 'var(--muted)' }}>{new Date(app.applied_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
