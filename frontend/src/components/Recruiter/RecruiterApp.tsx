import React, { useState, useEffect, useCallback } from 'react';
import { recruiterService, notificationService, messageService } from '../../services/api';
import { RecruiterProfile, RecruiterStats, Internship, RecruiterApplication, Interview, NotificationItem } from '../../types';
import { useAuth } from '../../context/AuthContext';
import { RecruiterDashboard } from './RecruiterDashboard';
import { PostInternship } from './PostInternship';
import { ManageInternships } from './ManageInternships';
import { ApplicantsView } from './ApplicantsView';
import { InterviewCalendar } from './InterviewCalendar';
import { RecruiterProfilePage } from './RecruiterProfilePage';
import { RecruiterSettings } from './RecruiterSettings';
import { MessagesView } from '../Messages/MessagesView';
import {
  Briefcase, LayoutDashboard, Plus, ListChecks, Users, Calendar,
  Bell, Building2, Settings, LogOut, ChevronLeft, Menu, MessageSquare,
} from 'lucide-react';

type RecruiterPage = 'dashboard' | 'post' | 'manage' | 'applicants' | 'interviews' | 'messages' | 'profile' | 'notifications' | 'settings';

const NAV: { id: RecruiterPage; label: string; icon: React.ElementType }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'post', label: 'Post Internship', icon: Plus },
  { id: 'manage', label: 'Manage', icon: ListChecks },
  { id: 'applicants', label: 'Applicants', icon: Users },
  { id: 'interviews', label: 'Interviews', icon: Calendar },
  { id: 'messages', label: 'Messages', icon: MessageSquare },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'profile', label: 'Profile', icon: Building2 },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export const RecruiterApp: React.FC = () => {
  const { user, logout } = useAuth();
  const [page, setPage] = useState<RecruiterPage>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileNav, setMobileNav] = useState(false);
  const [profile, setProfile] = useState<RecruiterProfile | null>(null);
  const [stats, setStats] = useState<RecruiterStats | null>(null);
  const [internships, setInternships] = useState<Internship[]>([]);
  const [applicants, setApplicants] = useState<RecruiterApplication[]>([]);
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadMessages, setUnreadMessages] = useState(0);
  const [messageWith, setMessageWith] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadAll(); }, []);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [p, s, ints, apps, ivs, notifs] = await Promise.all([
        recruiterService.getProfile(), recruiterService.getStats(), recruiterService.getMyInternships(),
        recruiterService.getApplicants(), recruiterService.getInterviews(), recruiterService.getNotifications(),
      ]);
      setProfile(p); setStats(s); setInternships(ints);
      setApplicants(apps); setInterviews(ivs); setNotifications(notifs);
    } catch { /* use defaults */ }
    finally { setLoading(false); }
    refreshLive();
  };

  // Light-weight poll so new applications / messages surface live (bell badge,
  // stats, applicants) without the recruiter reloading the page.
  const refreshLive = useCallback(async () => {
    try {
      const [notifs, s, apps, ivs, unread] = await Promise.all([
        recruiterService.getNotifications(), recruiterService.getStats(),
        recruiterService.getApplicants(), recruiterService.getInterviews(),
        messageService.getUnreadCount(),
      ]);
      setNotifications(notifs); setStats(s); setApplicants(apps);
      setInterviews(ivs); setUnreadMessages(unread.count);
    } catch { /* keep last known state */ }
  }, []);

  useEffect(() => {
    const t = setInterval(refreshLive, 15000);
    const onFocus = () => refreshLive();
    window.addEventListener('focus', onFocus);
    return () => { clearInterval(t); window.removeEventListener('focus', onFocus); };
  }, [refreshLive]);

  const markNotificationRead = async (id: number) => {
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    try { await notificationService.markRead(id); } catch { /* optimistic */ }
  };

  const markAllNotificationsRead = async () => {
    const unreadIds = notifications.filter((n) => !n.is_read).map((n) => n.id);
    if (unreadIds.length === 0) return;
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    try { await Promise.all(unreadIds.map((id) => notificationService.markRead(id))); }
    catch { refreshLive(); }
  };

  // Jump into the chat with a specific candidate (from the Applicants page).
  const openChatWith = (studentUserId: number) => {
    setMessageWith(studentUserId);
    setPage('messages');
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;
  const currentNav = NAV.find((n) => n.id === page);
  const navUnread = (id: RecruiterPage) =>
    id === 'notifications' ? unreadCount : id === 'messages' ? unreadMessages : 0;

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--bg)' }}>
      {/* Sidebar (desktop) */}
      <aside
        className={`hidden lg:flex flex-col flex-shrink-0 transition-all duration-300 ${sidebarOpen ? 'w-64' : 'w-[72px]'}`}
        style={{ background: 'var(--surface)', borderRight: '1px solid var(--border)' }}
      >
        <div className="h-16 flex items-center px-4" style={{ borderBottom: '1px solid var(--border)' }}>
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white shadow-sm flex-shrink-0" style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent))' }}>
              <Briefcase className="w-4.5 h-4.5" strokeWidth={2.5} />
            </div>
            {sidebarOpen && <span className="text-lg font-extrabold tracking-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>Hire<span style={{ color: 'var(--primary)' }}>Hub</span></span>}
          </div>
        </div>

        {sidebarOpen && profile && (
          <div className="px-4 py-4" style={{ borderBottom: '1px solid var(--border)' }}>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-sm flex-shrink-0" style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent))' }}>
                {profile.full_name?.[0] || 'R'}
              </div>
              <div className="min-w-0">
                <p className="text-sm font-bold truncate">{profile.full_name}</p>
                <p className="text-xs truncate" style={{ color: 'var(--muted)' }}>{profile.company_name}</p>
              </div>
            </div>
          </div>
        )}

        <nav className="flex-1 py-3 overflow-y-auto px-2 space-y-0.5">
          {NAV.map((item) => (
            <NavButton key={item.id} item={item} active={page === item.id} collapsed={!sidebarOpen} unread={navUnread(item.id)} onClick={() => setPage(item.id)} />
          ))}
        </nav>

        <div className="p-2 space-y-0.5" style={{ borderTop: '1px solid var(--border)' }}>
          <button onClick={logout} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition" style={{ color: 'var(--muted)' }} onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--danger-soft)'; e.currentTarget.style.color = 'var(--danger)'; }} onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--muted)'; }}>
            <LogOut className="w-4 h-4 flex-shrink-0" /> {sidebarOpen && 'Logout'}
          </button>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition" style={{ color: 'var(--muted)' }} onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-2)'; }} onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}>
            <ChevronLeft className={`w-4 h-4 flex-shrink-0 transition-transform ${sidebarOpen ? '' : 'rotate-180'}`} /> {sidebarOpen && 'Collapse'}
          </button>
        </div>
      </aside>

      {/* Mobile nav drawer */}
      {mobileNav && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="absolute inset-0 animate-fade-in" style={{ background: 'rgba(15,23,42,0.55)' }} onClick={() => setMobileNav(false)} />
          <aside className="relative w-72 flex flex-col animate-rise" style={{ background: 'var(--surface)' }}>
            <div className="h-16 flex items-center px-4" style={{ borderBottom: '1px solid var(--border)' }}>
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white" style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent))' }}><Briefcase className="w-4.5 h-4.5" /></div>
                <span className="text-lg font-extrabold">Hire<span style={{ color: 'var(--primary)' }}>Hub</span></span>
              </div>
            </div>
            <nav className="flex-1 py-3 px-2 space-y-0.5 overflow-y-auto">
              {NAV.map((item) => (
                <NavButton key={item.id} item={item} active={page === item.id} collapsed={false} unread={navUnread(item.id)} onClick={() => { setPage(item.id); setMobileNav(false); }} />
              ))}
            </nav>
            <div className="p-2" style={{ borderTop: '1px solid var(--border)' }}>
              <button onClick={logout} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition" style={{ color: 'var(--danger)' }} onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--danger-soft)'; }} onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}>
                <LogOut className="w-4 h-4" /> Logout
              </button>
            </div>
          </aside>
        </div>
      )}

      {/* Main */}
      <main className="flex-1 overflow-y-auto">
        {/* Topbar */}
        <header className="sticky top-0 z-30 glass-nav">
          <div className="px-4 sm:px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button onClick={() => setMobileNav(true)} className="lg:hidden w-9 h-9 rounded-xl flex items-center justify-center" style={{ color: 'var(--muted)' }}><Menu className="w-5 h-5" /></button>
              <div>
                <h1 className="font-extrabold text-base flex items-center gap-2">{currentNav && <currentNav.icon className="w-4 h-4" style={{ color: 'var(--primary)' }} />} {currentNav?.label}</h1>
                <p className="text-xs hidden sm:block" style={{ color: 'var(--muted)' }}>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={() => setPage('post')} className="btn btn-primary text-xs">
                <Plus className="w-4 h-4" /> <span className="hidden sm:inline">Post internship</span>
              </button>
              <button onClick={() => setPage('notifications')} className="relative w-9 h-9 rounded-xl flex items-center justify-center transition" style={{ color: 'var(--muted)', border: '1px solid var(--border)' }} onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-2)'; }} onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}>
                <Bell className="w-4 h-4" />
                {unreadCount > 0 && <span className="absolute top-1 right-1 w-2 h-2 rounded-full" style={{ background: 'var(--danger)' }} />}
              </button>
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="p-4 sm:p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="w-10 h-10 rounded-full border-2 animate-spin" style={{ borderColor: 'var(--primary)', borderTopColor: 'transparent' }} />
            </div>
          ) : (
            <>
              {page === 'dashboard' && <RecruiterDashboard stats={stats} internships={internships} applicants={applicants} profile={profile} onNavigate={setPage} onRefresh={loadAll} />}
              {page === 'post' && <PostInternship profile={profile} onSuccess={() => { setPage('manage'); loadAll(); }} />}
              {page === 'manage' && <ManageInternships internships={internships} onRefresh={loadAll} onNavigate={setPage} />}
              {page === 'applicants' && <ApplicantsView applicants={applicants} internships={internships} onRefresh={loadAll} interviews={interviews} onMessage={openChatWith} />}
              {page === 'interviews' && <InterviewCalendar interviews={interviews} applicants={applicants} onRefresh={loadAll} />}
              {page === 'messages' && <MessagesView initialUserId={messageWith} />}
              {page === 'profile' && <RecruiterProfilePage profile={profile} onRefresh={loadAll} />}
              {page === 'notifications' && <NotificationsPage notifications={notifications} onMarkRead={markNotificationRead} onMarkAllRead={markAllNotificationsRead} onRefresh={refreshLive} />}
              {page === 'settings' && <RecruiterSettings />}
            </>
          )}
        </div>
      </main>
    </div>
  );
};

const NavButton: React.FC<{ item: { id: string; label: string; icon: React.ElementType }; active: boolean; collapsed: boolean; unread: number; onClick: () => void }> = ({ item, active, collapsed, unread, onClick }) => (
  <button onClick={onClick} title={collapsed ? item.label : undefined} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition relative"
    style={active ? { background: 'var(--primary-soft)', color: 'var(--primary)' } : { color: 'var(--muted)' }}
    onMouseEnter={(e) => { if (!active) { e.currentTarget.style.background = 'var(--surface-2)'; e.currentTarget.style.color = 'var(--text)'; } }}
    onMouseLeave={(e) => { if (!active) { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--muted)'; } }}
  >
    {active && <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 rounded-r-full" style={{ background: 'var(--primary)' }} />}
    <item.icon className="w-4 h-4 flex-shrink-0" />
    {!collapsed && <span className="flex-1 text-left">{item.label}</span>}
    {!collapsed && unread > 0 && <span className="text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center text-white" style={{ background: 'var(--danger)' }}>{unread > 9 ? '9+' : unread}</span>}
  </button>
);

// Inline notifications page
const NotificationsPage: React.FC<{
  notifications: NotificationItem[];
  onMarkRead: (id: number) => void;
  onMarkAllRead: () => void;
  onRefresh: () => void;
}> = ({ notifications, onMarkRead, onMarkAllRead, onRefresh }) => {
  const unread = notifications.filter((n) => !n.is_read).length;
  return (
    <div className="max-w-2xl space-y-3">
      <div className="flex items-center justify-between gap-3 mb-2">
        <h2 className="font-extrabold text-lg">Notifications</h2>
        <div className="flex items-center gap-2">
          <button onClick={onRefresh} className="btn btn-ghost text-xs">Refresh</button>
          {unread > 0 && <button onClick={onMarkAllRead} className="btn btn-soft text-xs">Mark all read ({unread})</button>}
        </div>
      </div>
      {notifications.length === 0 ? (
        <div className="card p-12 text-center">
          <div className="w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-3" style={{ background: 'var(--surface-2)' }}><Bell className="w-6 h-6" style={{ color: 'var(--muted-2)' }} /></div>
          <p className="text-sm font-semibold">No notifications</p>
          <p className="text-xs" style={{ color: 'var(--muted)' }}>You're all caught up.</p>
        </div>
      ) : (
        notifications.map((n) => (
          <button
            key={n.id}
            onClick={() => !n.is_read && onMarkRead(n.id)}
            className="card p-4 flex items-start gap-3 w-full text-left transition"
            style={ !n.is_read ? { borderColor: 'var(--primary)', background: 'var(--primary-soft)' } : undefined }
            title={n.is_read ? undefined : 'Mark as read'}
          >
            <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 text-base" style={{ background: n.type === 'application' ? 'var(--success-soft)' : n.type === 'message' ? 'var(--primary-soft)' : 'var(--surface-2)' }}>
              {n.type === 'application' ? '📄' : n.type === 'message' ? '💬' : n.type === 'alert' ? '🚨' : '🔔'}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-bold">{n.title}</p>
              <p className="text-xs mt-0.5" style={{ color: 'var(--muted)' }}>{n.message}</p>
              <p className="text-[10px] mt-1" style={{ color: 'var(--muted-2)' }}>{new Date(n.created_at).toLocaleString()}</p>
            </div>
            {!n.is_read && <span className="w-2 h-2 rounded-full flex-shrink-0 mt-1.5" style={{ background: 'var(--primary)' }} />}
          </button>
        ))
      )}
    </div>
  );
};
