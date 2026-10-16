/*
 * Student navigation, search, account menu and unread badges. Authentication,
 * theme and notifications come from their shared contexts; the selected tab
 * and search text are controlled by the parent StudentApp.
 */

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { useNotifications } from '../../context/NotificationContext';
import { messageService } from '../../services/api';
import {
  Briefcase, Search, Bell, Moon, Sun, User as UserIcon, LogOut,
  Bookmark, LayoutDashboard, ChevronDown, Check, MessageSquare,
} from 'lucide-react';

interface NavbarProps {
  activeTab: 'dashboard' | 'internships' | 'tracker' | 'saved' | 'messages' | 'profile';
  setActiveTab: (tab: 'dashboard' | 'internships' | 'tracker' | 'saved' | 'messages' | 'profile') => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  onOpenAuth: (mode: 'signin' | 'signup') => void;
}

const TABS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'internships', label: 'Internships', icon: Briefcase },
  { id: 'saved', label: 'Saved', icon: Bookmark },
  { id: 'tracker', label: 'Tracker', icon: Check },
  { id: 'messages', label: 'Messages', icon: MessageSquare },
] as const;

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  searchQuery,
  setSearchQuery,
  onOpenAuth,
}) => {
  const { user, isAuthenticated, logout } = useAuth();
  const { darkMode, toggleDarkMode } = useTheme();
  const { notifications, unreadCount, markAsRead } = useNotifications();

  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [unreadMessages, setUnreadMessages] = useState(0);
  const notifRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);

  // Unread message badge for the Messages tab (light poll).
  useEffect(() => {
    if (!isAuthenticated) { setUnreadMessages(0); return; }
    let alive = true;
    // Refresh the unread incoming-message count for the navigation badge.
    const load = async () => {
      try { const { count } = await messageService.getUnreadCount(); if (alive) setUnreadMessages(count); }
      catch { /* ignore */ }
    };
    load();
    const t = setInterval(load, 15000);
    return () => { alive = false; clearInterval(t); };
  }, [isAuthenticated]);

  // Close popovers on outside click
  useEffect(() => {
    // Close dropdowns when a click occurs outside their respective containers.
    const handler = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) setShowNotifications(false);
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) setShowProfileMenu(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const avatar = user?.avatar_url || (
    user?.role === 'recruiter'
      ? 'https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?auto=format&fit=crop&w=120&q=80'
      : 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80'
  );

  return (
    <header className="sticky top-0 z-40 glass-nav">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        {/* Brand + nav */}
        <div className="flex items-center gap-6">
          <button onClick={() => setActiveTab('dashboard')} className="flex items-center gap-2.5 select-none group">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white shadow-sm transition-transform group-hover:scale-105" style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent))' }}>
              <Briefcase className="w-4.5 h-4.5" strokeWidth={2.5} />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-extrabold tracking-tight hidden sm:block" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                Hire<span style={{ color: 'var(--primary)' }}>Hub</span>
              </span>
              <span className="badge hidden lg:inline-flex" style={{ background: 'var(--primary-soft)', color: 'var(--primary)' }}>STUDENT</span>
            </div>
          </button>

          <nav className="hidden md:flex items-center gap-1">
            {TABS.map((t) => {
              const active = activeTab === t.id;
              return (
                <button
                  key={t.id}
                  onClick={() => setActiveTab(t.id)}
                  className="px-3 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all"
                  style={
                    active
                      ? { background: 'var(--primary-soft)', color: 'var(--primary)' }
                      : { color: 'var(--muted)' }
                  }
                  onMouseEnter={(e) => { if (!active) e.currentTarget.style.color = 'var(--text)'; }}
                  onMouseLeave={(e) => { if (!active) e.currentTarget.style.color = 'var(--muted)'; }}
                >
                  <t.icon className="w-4 h-4" /> {t.label}
                  {t.id === 'messages' && unreadMessages > 0 && (
                    <span className="ml-0.5 min-w-[16px] h-4 px-1 rounded-full text-[9px] font-bold flex items-center justify-center text-white" style={{ background: 'var(--danger)' }}>
                      {unreadMessages > 9 ? '9+' : unreadMessages}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Search */}
        <div className="flex-1 max-w-md hidden sm:block">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--muted-2)' }} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => setActiveTab('internships')}
              placeholder="Search roles, companies, skills…"
              className="input pl-9"
              style={{ borderRadius: 12 }}
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={toggleDarkMode}
            className="w-9 h-9 rounded-xl flex items-center justify-center transition"
            style={{ color: 'var(--muted)' }}
            onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-3)'; e.currentTarget.style.color = 'var(--text)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--muted)'; }}
            title="Toggle theme"
            aria-label="Toggle theme"
          >
            {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>

          {/* Notifications */}
          <div className="relative" ref={notifRef}>
            <button
              onClick={() => { setShowNotifications((v) => !v); setShowProfileMenu(false); }}
              className="relative w-9 h-9 rounded-xl flex items-center justify-center transition"
              style={{ color: 'var(--muted)' }}
              onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-3)'; e.currentTarget.style.color = 'var(--text)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--muted)'; }}
              aria-label="Notifications"
            >
              <Bell className="w-4 h-4" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 min-w-[16px] h-4 px-1 rounded-full text-[9px] font-bold flex items-center justify-center text-white animate-pulse" style={{ background: 'var(--danger)' }}>
                  {unreadCount}
                </span>
              )}
            </button>

            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 sm:w-96 card overflow-hidden animate-scale-in" style={{ borderRadius: 16 }}>
                <div className="px-4 py-3 flex items-center justify-between" style={{ borderBottom: '1px solid var(--border)' }}>
                  <h3 className="font-bold text-sm">Notifications</h3>
                  {unreadCount > 0 && <span className="badge" style={{ background: 'var(--primary-soft)', color: 'var(--primary)' }}>{unreadCount} new</span>}
                </div>
                <div className="max-h-80 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="p-8 text-center text-xs" style={{ color: 'var(--muted)' }}>You're all caught up 🎉</div>
                  ) : (
                    notifications.slice(0, 12).map((n) => (
                      <button
                        key={n.id}
                        onClick={() => markAsRead(n.id)}
                        className="w-full text-left px-4 py-3 flex items-start gap-3 transition"
                        style={{ borderBottom: '1px solid var(--border)', background: !n.is_read ? 'var(--primary-soft)' : 'transparent' }}
                        onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-2)'; }}
                        onMouseLeave={(e) => { e.currentTarget.style.background = !n.is_read ? 'var(--primary-soft)' : 'transparent'; }}
                      >
                        <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 text-sm" style={{ background: n.type === 'application' ? 'var(--success-soft)' : n.type === 'message' ? 'var(--primary-soft)' : 'var(--surface-3)' }}>
                          {n.type === 'application' ? '📄' : n.type === 'message' ? '💬' : n.type === 'alert' ? '🚨' : '🔔'}
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-xs font-semibold leading-snug">{n.title}</p>
                          <p className="text-[11px] mt-0.5 leading-snug" style={{ color: 'var(--muted)' }}>{n.message}</p>
                        </div>
                        {!n.is_read && <span className="w-2 h-2 rounded-full flex-shrink-0 mt-1.5" style={{ background: 'var(--primary)' }} />}
                      </button>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Profile / Auth */}
          {isAuthenticated ? (
            <div className="relative" ref={profileRef}>
              <button
                onClick={() => { setShowProfileMenu((v) => !v); setShowNotifications(false); }}
                className="flex items-center gap-2 pl-1 pr-2 py-1 rounded-xl transition"
                style={{ border: '1px solid var(--border)' }}
                onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-2)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
              >
                <img src={avatar} alt="Avatar" className="w-7 h-7 rounded-lg object-cover" />
                <span className="text-xs font-semibold hidden lg:inline max-w-[90px] truncate">{user?.full_name}</span>
                <ChevronDown className="w-3.5 h-3.5" style={{ color: 'var(--muted-2)' }} />
              </button>

              {showProfileMenu && (
                <div className="absolute right-0 mt-2 w-60 card py-2 animate-scale-in overflow-hidden" style={{ borderRadius: 16 }}>
                  <div className="px-4 py-2.5" style={{ borderBottom: '1px solid var(--border)' }}>
                    <div className="text-sm font-bold truncate">{user?.full_name}</div>
                    <div className="text-[11px] truncate" style={{ color: 'var(--muted)' }}>{user?.email}</div>
                  </div>
                  <MenuItem icon={UserIcon} label="View & edit profile" onClick={() => { setActiveTab('profile'); setShowProfileMenu(false); }} />
                  <MenuItem icon={Bookmark} label="Saved internships" onClick={() => { setActiveTab('saved'); setShowProfileMenu(false); }} />
                  <MenuItem icon={Check} label="Application tracker" onClick={() => { setActiveTab('tracker'); setShowProfileMenu(false); }} />
                  <div style={{ borderTop: '1px solid var(--border)', marginTop: 4 }}>
                    <MenuItem icon={LogOut} label="Sign out" danger onClick={() => { logout(); setShowProfileMenu(false); }} />
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <button onClick={() => onOpenAuth('signin')} className="btn btn-ghost text-xs">Sign in</button>
              <button onClick={() => onOpenAuth('signup')} className="btn btn-primary text-xs">Get started</button>
            </div>
          )}
        </div>
      </div>

      {/* Mobile nav */}
      <nav className="md:hidden flex items-center gap-1 px-4 pb-2 overflow-x-auto">
        {TABS.map((t) => {
          const active = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition flex-shrink-0"
              style={active ? { background: 'var(--primary-soft)', color: 'var(--primary)' } : { color: 'var(--muted)' }}
            >
              <t.icon className="w-3.5 h-3.5" /> {t.label}
            </button>
          );
        })}
      </nav>
    </header>
  );
};

// Reuse icon, label and callback rendering inside the account menu.
const MenuItem: React.FC<{ icon: React.ElementType; label: string; onClick: () => void; danger?: boolean }> = ({ icon: Icon, label, onClick, danger }) => (
  <button
    onClick={onClick}
    className="w-full text-left px-4 py-2.5 text-xs font-medium flex items-center gap-2.5 transition"
    style={{ color: danger ? 'var(--danger)' : 'var(--text-soft)' }}
    onMouseEnter={(e) => { e.currentTarget.style.background = danger ? 'var(--danger-soft)' : 'var(--surface-2)'; }}
    onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
  >
    <Icon className="w-4 h-4" /> {label}
  </button>
);
