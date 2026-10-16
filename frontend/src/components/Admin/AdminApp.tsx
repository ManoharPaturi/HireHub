import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminService } from '../../services/api';
import { AdminStats, AdminChartData, AdminUser, AdminInternship, AdminApplication, AdminActivityItem } from '../../types';
import { useAuth } from '../../context/AuthContext';
import { DonutChart, BarList, DailyBars } from './charts';
import {
  LayoutDashboard, Users, Briefcase, FileText, LogOut, Search, ShieldCheck,
  GraduationCap, Building2, Send, Calendar, MessageSquare, TrendingUp,
  Power, Trash2, Activity, UserCheck, UserX, UserPlus,
} from 'lucide-react';

type AdminPage = 'overview' | 'users' | 'internships' | 'applications';

const NAV: { id: AdminPage; label: string; icon: React.ElementType }[] = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'users', label: 'Users', icon: Users },
  { id: 'internships', label: 'Internships', icon: Briefcase },
  { id: 'applications', label: 'Applications', icon: FileText },
];

// Console palette (self-contained — independent of the site theme tokens).
const C = {
  bg: '#141727', panel: '#1d2135', panel2: '#222642',
  border: 'rgba(255,255,255,0.07)', text: '#ffffff', soft: '#aab2cf',
  muted: '#8b93b0', faint: '#5a6284',
  blue: '#4f7cff', green: '#10b981', purple: '#8b5cf6',
  orange: '#f59e0b', pink: '#ec4899', cyan: '#06b6d4', red: '#ef4444',
};

export const AdminApp: React.FC = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [page, setPage] = useState<AdminPage>('overview');
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [charts, setCharts] = useState<AdminChartData | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [internships, setInternships] = useState<AdminInternship[]>([]);
  const [applications, setApplications] = useState<AdminApplication[]>([]);
  const [activity, setActivity] = useState<AdminActivityItem[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const [s, c, act] = await Promise.all([
        adminService.getStats(), adminService.getCharts(), adminService.getActivity(8),
      ]);
      setStats(s); setCharts(c); setActivity(act);
      if (page === 'users') setUsers(await adminService.getUsers());
      if (page === 'internships') setInternships(await adminService.getInternships());
      if (page === 'applications') setApplications(await adminService.getApplications());
    } catch (e: any) {
      if (e?.response?.status === 403) { navigate('/admin'); }
    } finally { setLoading(false); }
  }, [page, navigate]);

  useEffect(() => { load(); }, [load]);

  const currentNav = NAV.find((n) => n.id === page);
  const today = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });

  const logoutAdmin = () => {
    // Clears token + context state, then leaves the console.
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen flex" style={{ background: C.bg }}>
      {/* ── Sidebar ── */}
      <aside className="hidden lg:flex flex-col w-60 flex-shrink-0" style={{ background: '#171a2e', borderRight: `1px solid ${C.border}` }}>
        <div className="h-16 flex items-center gap-2.5 px-5" style={{ borderBottom: `1px solid ${C.border}` }}>
          <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'linear-gradient(135deg, #4f7cff, #8b5cf6)' }}>
            <ShieldCheck className="w-4.5 h-4.5 text-white" strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-sm font-extrabold text-white leading-tight">HireHub</p>
            <p className="text-[10px] font-semibold" style={{ color: C.faint }}>ADMIN CONSOLE</p>
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV.map((item) => {
            const active = page === item.id;
            return (
              <button
                key={item.id} onClick={() => setPage(item.id)}
                className="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition relative"
                style={active ? { background: 'rgba(79,124,255,0.14)', color: C.blue } : { color: C.muted }}
                onMouseEnter={(e) => { if (!active) { e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; e.currentTarget.style.color = C.soft; } }}
                onMouseLeave={(e) => { if (!active) { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = C.muted; } }}
              >
                {active && <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 rounded-r-full" style={{ background: C.blue }} />}
                <item.icon className="w-4 h-4 flex-shrink-0" /> {item.label}
              </button>
            );
          })}
        </nav>

        {/* user card */}
        <div className="p-3" style={{ borderTop: `1px solid ${C.border}` }}>
          <div className="flex items-center gap-3 p-2.5 rounded-xl" style={{ background: C.panel }}>
            <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'linear-gradient(135deg, #4f7cff, #8b5cf6)' }}>
              <ShieldCheck className="w-4 h-4 text-white" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-bold text-white truncate">Platform Admin</p>
              <p className="text-[10px] truncate" style={{ color: C.faint }}>admin@hirehub.com</p>
            </div>
            <button onClick={logoutAdmin} title="Sign out" className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 transition" style={{ color: C.muted }} onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(239,68,68,0.14)'; e.currentTarget.style.color = C.red; }} onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = C.muted; }}>
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="flex-1 min-w-0">
        {/* header */}
        <header className="sticky top-0 z-20 px-4 sm:px-7 h-16 flex items-center justify-between" style={{ background: 'rgba(20,23,39,0.85)', backdropFilter: 'blur(10px)', borderBottom: `1px solid ${C.border}` }}>
          <div>
            <h1 className="text-base font-extrabold text-white flex items-center gap-2">
              {currentNav && <currentNav.icon className="w-4 h-4" style={{ color: C.blue }} />} {currentNav?.label}
            </h1>
            <p className="text-[11px] hidden sm:block" style={{ color: C.faint }}>{today}</p>
          </div>
          {/* mobile nav */}
          <div className="lg:hidden flex items-center gap-1.5">
            {NAV.map((n) => (
              <button key={n.id} onClick={() => setPage(n.id)} className="w-9 h-9 rounded-xl flex items-center justify-center transition"
                style={page === n.id ? { background: 'rgba(79,124,255,0.14)', color: C.blue } : { color: C.muted, border: `1px solid ${C.border}` }}>
                <n.icon className="w-4 h-4" />
              </button>
            ))}
            <button onClick={logoutAdmin} className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ color: C.muted, border: `1px solid ${C.border}` }}>
              <LogOut className="w-4 h-4" />
            </button>
          </div>
          <div className="hidden lg:flex items-center gap-3">
            <span className="badge px-2.5 py-1 text-[10px] font-bold rounded-full" style={{ background: 'rgba(16,185,129,0.12)', color: C.green }}>● LIVE</span>
            <button onClick={load} className="w-9 h-9 rounded-xl flex items-center justify-center transition" style={{ color: C.muted, border: `1px solid ${C.border}` }} title="Refresh data" onMouseEnter={(e) => { e.currentTarget.style.background = C.panel; }} onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}>
              <Activity className="w-4 h-4" />
            </button>
          </div>
        </header>

        <div className="p-4 sm:p-7">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="w-10 h-10 rounded-full border-2 animate-spin" style={{ borderColor: C.blue, borderTopColor: 'transparent' }} />
            </div>
          ) : (
            <>
              {page === 'overview' && <Overview stats={stats} charts={charts} activity={activity} onGo={setPage} />}
              {page === 'users' && <UsersPage users={users} onRefresh={load} setUsers={setUsers} />}
              {page === 'internships' && <InternshipsPage internships={internships} onRefresh={load} />}
              {page === 'applications' && <ApplicationsPage applications={applications} />}
            </>
          )}
        </div>
      </main>
    </div>
  );
};

/* ── shared bits ── */
const Panel: React.FC<{ title?: string; sub?: string; children: React.ReactNode; className?: string }> = ({ title, sub, children, className = '' }) => (
  <div className={`rounded-2xl p-5 ${className}`} style={{ background: C.panel, border: `1px solid ${C.border}` }}>
    {title && (
      <div className="mb-4">
        <h3 className="text-sm font-bold text-white">{title}</h3>
        {sub && <p className="text-[11px] mt-0.5" style={{ color: C.faint }}>{sub}</p>}
      </div>
    )}
    {children}
  </div>
);

const STATUS_COLORS: Record<string, string> = {
  'Applied': C.blue, 'Under Review': C.orange, 'Shortlisted': C.purple,
  'Interview Scheduled': C.cyan, 'Accepted': C.green, 'Rejected': C.red,
};
const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const col = STATUS_COLORS[status] || C.muted;
  return (
    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold whitespace-nowrap" style={{ background: `${col}1f`, color: col }}>{status}</span>
  );
};

/* ── Overview ── */
const Overview: React.FC<{
  stats: AdminStats | null; charts: AdminChartData | null;
  activity: AdminActivityItem[]; onGo: (p: AdminPage) => void;
}> = ({ stats, charts, activity, onGo }) => {
  if (!stats || !charts) return null;
  const kpis = [
    { label: 'Total Students', value: stats.total_students.toLocaleString(), icon: GraduationCap, color: C.blue, bg: 'rgba(79,124,255,0.14)', trend: `+${stats.new_users_week} this week` },
    { label: 'Total Recruiters', value: stats.total_recruiters.toLocaleString(), icon: Building2, color: C.purple, bg: 'rgba(139,92,246,0.14)', trend: `${stats.active_internships} active posts` },
    { label: 'Total Internships', value: stats.total_internships.toLocaleString(), icon: Briefcase, color: C.orange, bg: 'rgba(245,158,11,0.14)', trend: `avg ₹${stats.avg_stipend.toLocaleString()}/mo` },
    { label: 'Total Applications', value: stats.total_applications.toLocaleString(), icon: Send, color: C.green, bg: 'rgba(16,185,129,0.14)', trend: `+${stats.new_apps_week} this week` },
    { label: 'Interviews', value: stats.total_interviews.toLocaleString(), icon: Calendar, color: C.cyan, bg: 'rgba(6,182,212,0.14)', trend: 'scheduled' },
    { label: 'Messages', value: stats.total_messages.toLocaleString(), icon: MessageSquare, color: C.pink, bg: 'rgba(236,72,153,0.14)', trend: 'exchanged' },
  ];

  return (
    <div className="space-y-5">
      {/* KPI row */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        {kpis.map((k) => (
          <div key={k.label} className="rounded-2xl p-4" style={{ background: C.panel, border: `1px solid ${C.border}` }}>
            <div className="w-9 h-9 rounded-xl flex items-center justify-center mb-3" style={{ background: k.bg }}>
              <k.icon className="w-4.5 h-4.5" style={{ color: k.color }} />
            </div>
            <p className="text-xl font-extrabold text-white leading-none">{k.value}</p>
            <p className="text-[11px] mt-1.5 font-medium" style={{ color: C.soft }}>{k.label}</p>
            <p className="text-[10px] mt-0.5 flex items-center gap-1" style={{ color: k.color }}>
              <TrendingUp className="w-3 h-3" /> {k.trend}
            </p>
          </div>
        ))}
      </div>

      {/* charts row */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <Panel title="Applications" sub="Last 14 days" className="xl:col-span-2">
          <DailyBars data={charts.applications_timeline} />
        </Panel>
        <Panel title="Pipeline" sub="Applications by status">
          <DonutChart data={charts.by_status} centerLabel="total" />
        </Panel>
      </div>

      {/* breakdowns row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Panel title="Work mode" sub="Applications by internship mode">
          <BarList data={charts.by_mode} />
        </Panel>
        <Panel title="Top universities" sub="Students by university">
          <BarList data={charts.top_universities} />
        </Panel>
        <Panel title="Top fields" sub="Students by field of study">
          <BarList data={charts.top_fields} />
        </Panel>
      </div>

      {/* top companies + quick actions */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <Panel title="Top companies" sub="By applications received" className="xl:col-span-2">
          <BarList data={charts.top_companies} />
        </Panel>
        <Panel title="Quick actions">
          <div className="space-y-2.5">
            {([
              { label: 'Manage users', icon: Users, page: 'users' as AdminPage, color: C.blue },
              { label: 'Review internships', icon: Briefcase, page: 'internships' as AdminPage, color: C.orange },
              { label: 'Applications feed', icon: FileText, page: 'applications' as AdminPage, color: C.green },
            ]).map((a) => (
              <button key={a.label} onClick={() => onGo(a.page)}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold text-white transition"
                style={{ background: C.panel2, border: `1px solid ${C.border}` }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = a.color; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = C.border; }}>
                <a.icon className="w-4 h-4" style={{ color: a.color }} /> {a.label}
              </button>
            ))}
          </div>
        </Panel>
      </div>

      {/* activity log */}
      <ActivityLog activity={activity} />
    </div>
  );
};

const relTime = (iso: string) => {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
};

const ActivityLog: React.FC<{ activity: AdminActivityItem[] }> = ({ activity }) => {
  const META: Record<string, { icon: React.ElementType; color: string; bg: string }> = {
    application: { icon: Send, color: C.blue, bg: 'rgba(79,124,255,0.13)' },
    internship: { icon: Briefcase, color: C.orange, bg: 'rgba(245,158,11,0.13)' },
    user: { icon: UserPlus, color: C.green, bg: 'rgba(16,185,129,0.13)' },
    interview: { icon: Calendar, color: C.cyan, bg: 'rgba(6,182,212,0.13)' },
  };
  return (
    <Panel title="Activity log" sub="Latest events across the platform">
      {activity.length === 0 ? (
        <p className="text-xs py-4 text-center" style={{ color: C.faint }}>No recent activity.</p>
      ) : (
        <div className="divide-y" style={{ borderColor: C.border }}>
          {activity.map((e, i) => {
            const m = META[e.type] || META.user;
            return (
              <div key={i} className="flex items-center gap-3 py-2.5 first:pt-0 last:pb-0">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: m.bg }}>
                  <m.icon className="w-3.5 h-3.5" style={{ color: m.color }} />
                </div>
                <p className="text-xs flex-1 min-w-0 truncate" style={{ color: C.soft }}>
                  <strong className="text-white">{e.actor}</strong> {e.detail}
                </p>
                <span className="text-[10px] flex-shrink-0 font-medium" style={{ color: C.faint }}>{relTime(e.at)}</span>
              </div>
            );
          })}
        </div>
      )}
    </Panel>
  );
};

/* ── Users ── */
const UsersPage: React.FC<{ users: AdminUser[]; onRefresh: () => void; setUsers: (u: AdminUser[]) => void }> = ({ users, onRefresh, setUsers }) => {
  const [filter, setFilter] = useState<'all' | 'student' | 'recruiter'>('all');
  const [search, setSearch] = useState('');
  const [busy, setBusy] = useState<number | null>(null);

  useEffect(() => {
    const t = setTimeout(async () => {
      setUsers(await adminService.getUsers({ role: filter !== 'all' ? filter : undefined, search: search || undefined }));
    }, 250);
    return () => clearTimeout(t);
  }, [filter, search, setUsers]);

  const toggle = async (u: AdminUser) => {
    setBusy(u.id);
    try {
      await adminService.toggleUser(u.id);
      setUsers(users.map((x) => (x.id === u.id ? { ...x, is_active: !x.is_active } : x)));
    } catch { onRefresh(); }
    finally { setBusy(null); }
  };

  const remove = async (u: AdminUser) => {
    if (!window.confirm(`Remove ${u.email}? This deletes their profile and applications.`)) return;
    setBusy(u.id);
    try { await adminService.deleteUser(u.id); setUsers(users.filter((x) => x.id !== u.id)); }
    catch { onRefresh(); }
    finally { setBusy(null); }
  };

  const filtered = users;

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 justify-between">
        <div className="flex items-center gap-1.5">
          {(['all', 'student', 'recruiter'] as const).map((f) => (
            <button key={f} onClick={() => setFilter(f)} className="px-3.5 py-2 rounded-xl text-xs font-bold capitalize transition"
              style={filter === f ? { background: 'rgba(79,124,255,0.14)', color: C.blue } : { color: C.muted, background: C.panel, border: `1px solid ${C.border}` }}>
              {f} {f !== 'all' && `(${users.filter((u) => u.role === f).length})`}
            </button>
          ))}
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5" style={{ color: C.faint }} />
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search name, email, company…"
            className="pl-9 pr-4 py-2.5 rounded-xl text-xs text-white outline-none w-full sm:w-64"
            style={{ background: C.panel, border: `1px solid ${C.border}` }} />
        </div>
      </div>

      <div className="rounded-2xl overflow-hidden" style={{ background: C.panel, border: `1px solid ${C.border}` }}>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr style={{ borderBottom: `1px solid ${C.border}` }}>
                {['User', 'Role', 'Detail', 'Joined', 'Status', ''].map((h) => (
                  <th key={h} className="px-4 py-3 text-[10px] font-bold uppercase tracking-wider whitespace-nowrap" style={{ color: C.faint }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 && (
                <tr><td colSpan={6} className="px-4 py-10 text-center text-xs" style={{ color: C.faint }}>No users match.</td></tr>
              )}
              {filtered.map((u) => (
                <tr key={u.id} style={{ borderBottom: `1px solid ${C.border}` }}>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2.5">
                      {u.avatar_url ? (
                        <img src={u.avatar_url} alt="" className="w-8 h-8 rounded-lg object-cover flex-shrink-0" />
                      ) : (
                        <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 text-[11px] font-bold text-white"
                          style={{ background: u.role === 'student' ? 'rgba(79,124,255,0.25)' : 'rgba(139,92,246,0.25)' }}>
                          {(u.full_name || u.email)[0].toUpperCase()}
                        </div>
                      )}
                      <div className="min-w-0">
                        <p className="text-xs font-bold text-white truncate">{u.full_name || u.email.split('@')[0]}</p>
                        <p className="text-[10px] truncate" style={{ color: C.faint }}>{u.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold capitalize" style={{ background: u.role === 'student' ? 'rgba(79,124,255,0.14)' : 'rgba(139,92,246,0.14)', color: u.role === 'student' ? C.blue : C.purple }}>
                      {u.role}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs whitespace-nowrap" style={{ color: C.soft }}>
                    {u.role === 'student'
                      ? `${u.university || '—'}${u.applications !== undefined ? ` · ${u.applications} apps` : ''}`
                      : `${u.company || '—'}${u.internships !== undefined ? ` · ${u.internships} posts` : ''}`}
                  </td>
                  <td className="px-4 py-3 text-xs whitespace-nowrap" style={{ color: C.muted }}>{new Date(u.created_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3">
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-bold inline-flex items-center gap-1 whitespace-nowrap"
                      style={u.is_active ? { background: 'rgba(16,185,129,0.12)', color: C.green } : { background: 'rgba(239,68,68,0.12)', color: C.red }}>
                      {u.is_active ? <UserCheck className="w-3 h-3" /> : <UserX className="w-3 h-3" />} {u.is_active ? 'Active' : 'Disabled'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1.5 justify-end">
                      <button onClick={() => toggle(u)} disabled={busy === u.id} title={u.is_active ? 'Disable user' : 'Enable user'}
                        className="w-7 h-7 rounded-lg flex items-center justify-center transition disabled:opacity-40"
                        style={{ color: u.is_active ? C.orange : C.green, background: C.panel2 }} onMouseEnter={(e) => { e.currentTarget.style.borderColor = C.border; }}>
                        <Power className="w-3.5 h-3.5" />
                      </button>
                      <button onClick={() => remove(u)} disabled={busy === u.id} title="Delete user"
                        className="w-7 h-7 rounded-lg flex items-center justify-center transition disabled:opacity-40"
                        style={{ color: C.red, background: C.panel2 }}>
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

/* ── Internships ── */
const InternshipsPage: React.FC<{ internships: AdminInternship[]; onRefresh: () => void }> = ({ internships, onRefresh }) => {
  const [busy, setBusy] = useState<number | null>(null);

  const toggle = async (i: AdminInternship) => {
    setBusy(i.id);
    try { await adminService.toggleInternship(i.id); onRefresh(); }
    finally { setBusy(null); }
  };
  const remove = async (i: AdminInternship) => {
    if (!window.confirm(`Delete "${i.title}" at ${i.company_name}?`)) return;
    setBusy(i.id);
    try { await adminService.deleteInternship(i.id); onRefresh(); }
    finally { setBusy(null); }
  };

  return (
    <div className="rounded-2xl overflow-hidden" style={{ background: C.panel, border: `1px solid ${C.border}` }}>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr style={{ borderBottom: `1px solid ${C.border}` }}>
              {['Internship', 'Company', 'Mode', 'Stipend', 'Apps', 'Posted', 'Status', ''].map((h) => (
                <th key={h} className="px-4 py-3 text-[10px] font-bold uppercase tracking-wider whitespace-nowrap" style={{ color: C.faint }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {internships.map((i) => (
              <tr key={i.id} style={{ borderBottom: `1px solid ${C.border}` }}>
                <td className="px-4 py-3">
                  <p className="text-xs font-bold text-white">{i.title}</p>
                  <p className="text-[10px]" style={{ color: C.faint }}>{i.location} · {i.duration}</p>
                </td>
                <td className="px-4 py-3 text-xs" style={{ color: C.soft }}>{i.company_name}{i.is_external && <span className="ml-1.5 px-1.5 py-0.5 rounded text-[9px] font-bold" style={{ background: 'rgba(245,158,11,0.14)', color: C.orange }}>EXT</span>}</td>
                <td className="px-4 py-3 text-xs" style={{ color: C.muted }}>{i.mode}</td>
                <td className="px-4 py-3 text-xs whitespace-nowrap" style={{ color: C.soft }}>{i.stipend_currency}{i.stipend_amount.toLocaleString()}<span style={{ color: C.faint }}>/mo</span></td>
                <td className="px-4 py-3"><span className="px-2 py-0.5 rounded-lg text-[10px] font-bold" style={{ background: 'rgba(79,124,255,0.12)', color: C.blue }}>{i.applications}</span></td>
                <td className="px-4 py-3 text-xs whitespace-nowrap" style={{ color: C.muted }}>{new Date(i.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-3">
                  <span className="px-2.5 py-1 rounded-full text-[10px] font-bold whitespace-nowrap"
                    style={i.is_active ? { background: 'rgba(16,185,129,0.12)', color: C.green } : { background: 'rgba(239,68,68,0.12)', color: C.red }}>
                    {i.is_active ? 'Active' : 'Closed'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5 justify-end">
                    <button onClick={() => toggle(i)} disabled={busy === i.id} title={i.is_active ? 'Close posting' : 'Reopen posting'}
                      className="w-7 h-7 rounded-lg flex items-center justify-center transition disabled:opacity-40"
                      style={{ color: i.is_active ? C.orange : C.green, background: C.panel2 }}>
                      <Power className="w-3.5 h-3.5" />
                    </button>
                    <button onClick={() => remove(i)} disabled={busy === i.id} title="Delete posting"
                      className="w-7 h-7 rounded-lg flex items-center justify-center transition disabled:opacity-40"
                      style={{ color: C.red, background: C.panel2 }}>
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

/* ── Applications ── */
const ApplicationsPage: React.FC<{ applications: AdminApplication[] }> = ({ applications }) => (
  <div className="rounded-2xl overflow-hidden" style={{ background: C.panel, border: `1px solid ${C.border}` }}>
    <div className="overflow-x-auto">
      <table className="w-full text-left">
        <thead>
          <tr style={{ borderBottom: `1px solid ${C.border}` }}>
            {['Candidate', 'Internship', 'Status', 'Resume', 'Applied'].map((h) => (
              <th key={h} className="px-4 py-3 text-[10px] font-bold uppercase tracking-wider whitespace-nowrap" style={{ color: C.faint }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {applications.map((a) => (
            <tr key={a.id} style={{ borderBottom: `1px solid ${C.border}` }}>
              <td className="px-4 py-3">
                <p className="text-xs font-bold text-white">{a.student_name}</p>
                <p className="text-[10px]" style={{ color: C.faint }}>{a.student_email}</p>
              </td>
              <td className="px-4 py-3">
                <p className="text-xs" style={{ color: C.soft }}>{a.internship_title}</p>
                <p className="text-[10px]" style={{ color: C.faint }}>{a.company_name}</p>
              </td>
              <td className="px-4 py-3"><StatusBadge status={a.status} /></td>
              <td className="px-4 py-3 text-xs" style={{ color: a.has_resume ? C.green : C.faint }}>{a.has_resume ? 'Attached' : '—'}</td>
              <td className="px-4 py-3 text-xs whitespace-nowrap" style={{ color: C.muted }}>{new Date(a.applied_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);
