/*
 * Top-level routing and providers. Authentication supplies the account role;
 * the router chooses the student workspace, recruiter workspace or admin console.
 * The signed-out landing page opens the shared registration/login modal.
 */

import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { NotificationProvider } from './context/NotificationContext';
import { StudentApp } from './components/Student/StudentApp';
import { RecruiterApp } from './components/Recruiter/RecruiterApp';
import { AdminApp } from './components/Admin/AdminApp';
import { AdminLogin } from './components/Admin/AdminLogin';
import { AuthModal } from './components/Auth/AuthModal';
import {
  Briefcase, Sparkles, ArrowRight, ShieldCheck, Zap, Users, TrendingUp,
  Search, Bell, Bookmark, Building2, GraduationCap, CheckCircle2,
} from 'lucide-react';

// Wait for browser auth restoration, then choose the workspace from the
// account role. Backend dependencies remain responsible for API authorization.
const MainRouter: React.FC = () => {
  const { isAuthenticated, loading, user } = useAuth();
  const [authModal, setAuthModal] = useState<{ isOpen: boolean; tab: 'login' | 'register' }>({ isOpen: false, tab: 'login' });

  const open = (tab: 'login' | 'register') => setAuthModal({ isOpen: true, tab });
  const close = () => setAuthModal((m) => ({ ...m, isOpen: false }));

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center" style={{ background: 'var(--bg)' }}>
        <div className="relative">
          <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-white shadow-lg" style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent))' }}>
            <Briefcase className="w-7 h-7" />
          </div>
          <div className="absolute inset-0 rounded-2xl animate-ping" style={{ background: 'var(--primary)', opacity: 0.25 }} />
        </div>
        <p className="mt-5 text-sm font-semibold" style={{ color: 'var(--muted)' }}>Loading HireHub…</p>
      </div>
    );
  }

  if (isAuthenticated && user) {
    // Admins live only in the console — send them there.
    if (user.role === 'admin') {
      return (
        <Routes>
          <Route path="/admin" element={<AdminApp />} />
          <Route path="/*" element={<AdminApp />} />
        </Routes>
      );
    }
    return (
      <>
        <Routes>
          {/* Signed-in non-admins visiting /admin get the console sign-in */}
          <Route path="/admin" element={<AdminLogin />} />
          <Route path="/*" element={user.role === 'recruiter' ? <RecruiterApp /> : <StudentApp />} />
        </Routes>
        <AuthModal isOpen={authModal.isOpen} onClose={close} defaultTab={authModal.tab} />
      </>
    );
  }

  return (
    <>
      <Routes>
        {/* Separate admin entry point */}
        <Route path="/admin" element={<AdminLogin />} />
        <Route path="/*" element={<Landing onOpen={open} />} />
      </Routes>
      <AuthModal isOpen={authModal.isOpen} onClose={close} defaultTab={authModal.tab} />
    </>
  );
};

/* ---------------- Landing ---------------- */

// Marketing copy and statistics below are hard-coded display content,
// not measurements fetched from the database.
const Landing: React.FC<{ onOpen: (tab: 'login' | 'register') => void }> = ({ onOpen }) => {
  const features = [
    { icon: Search, title: 'Smart discovery', desc: 'AI-matched internships tuned to your skills, mode, and stipend goals.' },
    { icon: Zap, title: 'One-click apply', desc: 'Apply to roles in seconds with a reusable profile and resume link.' },
    { icon: Bookmark, title: 'Track everything', desc: 'A live pipeline from submitted → shortlisted → interview → offer.' },
    { icon: Bell, title: 'Real-time alerts', desc: 'Instant updates the moment a recruiter reviews your application.' },
    { icon: ShieldCheck, title: 'Verified employers', desc: 'Every listing is screened — no spam, no stale posts.' },
    { icon: TrendingUp, title: 'Career insights', desc: 'Stipend benchmarks and demand trends for every role.' },
  ];

  // These marketing figures are static sample copy, not database statistics
  // or an evaluated recommendation accuracy. Admin totals use API data instead.
  const stats = [
    { value: '12k+', label: 'Active internships' },
    { value: '850+', label: 'Hiring companies' },
    { value: '94%', label: 'Match accuracy' },
    { value: '48h', label: 'Avg. response' },
  ];

  const companies = ['Stripe', 'Notion', 'Figma', 'Spotify', 'Vercel', 'Linear'];

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg)' }}>
      {/* Nav */}
      <header className="sticky top-0 z-40 glass-nav">
        <div className="max-w-6xl mx-auto px-5 h-16 flex items-center justify-between">
          <Brand />
          <div className="flex items-center gap-2">
            <button onClick={() => onOpen('login')} className="btn btn-ghost hidden sm:inline-flex">Sign in</button>
            <button onClick={() => onOpen('register')} className="btn btn-primary">
              Get started <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-grid opacity-60" style={{ maskImage: 'radial-gradient(ellipse 80% 60% at 50% 0%, #000 40%, transparent 75%)', WebkitMaskImage: 'radial-gradient(ellipse 80% 60% at 50% 0%, #000 40%, transparent 75%)' }} />
        <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-[42rem] h-[42rem] rounded-full blur-3xl animate-blob" style={{ background: 'radial-gradient(circle, var(--primary-soft), transparent 60%)' }} />

        <div className="relative max-w-4xl mx-auto px-5 pt-20 pb-16 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold animate-rise" style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text-soft)', boxShadow: 'var(--shadow-sm)' }}>
            <Sparkles className="w-3.5 h-3.5" style={{ color: 'var(--primary)' }} />
            The modern way to land your next internship
          </div>

          <h1 className="mt-6 text-4xl sm:text-6xl font-extrabold tracking-tight animate-rise" style={{ animationDelay: '0.05s' }}>
            Where <span className="text-gradient">careers</span> begin.
          </h1>
          <p className="mt-5 text-base sm:text-lg max-w-2xl mx-auto animate-rise" style={{ color: 'var(--muted)', animationDelay: '0.1s' }}>
            Discover curated internships at the world's best companies, apply in one click, and track every step of your journey — all in one polished platform.
          </p>

          <div className="mt-9 flex flex-col sm:flex-row items-center justify-center gap-3 animate-rise" style={{ animationDelay: '0.15s' }}>
            <button onClick={() => onOpen('register')} className="btn btn-primary text-base px-6 py-3.5 w-full sm:w-auto">
              <GraduationCap className="w-5 h-5" /> Join as a student
            </button>
            <button onClick={() => onOpen('register')} className="btn btn-ghost text-base px-6 py-3.5 w-full sm:w-auto">
              <Building2 className="w-5 h-5" /> Hire talent
            </button>
          </div>

          {/* Trust row */}
          <div className="mt-14 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 opacity-70 animate-fade-in">
            {companies.map((c) => (
              <span key={c} className="text-sm font-bold tracking-tight" style={{ color: 'var(--muted)' }}>{c}</span>
            ))}
          </div>
        </div>

        {/* Stats strip */}
        <div className="relative max-w-4xl mx-auto px-5 pb-16">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {stats.map((s, i) => (
              <div key={s.label} className="card p-5 text-center animate-rise" style={{ animationDelay: `${0.2 + i * 0.05}s` }}>
                <div className="text-2xl sm:text-3xl font-extrabold" style={{ color: 'var(--primary)' }}>{s.value}</div>
                <div className="text-xs font-medium mt-1" style={{ color: 'var(--muted)' }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-5 py-16">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <span className="eyebrow">Everything you need</span>
          <h2 className="mt-2 text-3xl sm:text-4xl font-extrabold tracking-tight">Built for the whole journey</h2>
          <p className="mt-3 text-sm" style={{ color: 'var(--muted)' }}>
            From your first application to the final offer — HireHub keeps every step organized, fast, and transparent.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 stagger">
          {features.map((f) => (
            <div key={f.title} className="card card-hover p-6">
              <div className="w-11 h-11 rounded-xl flex items-center justify-center mb-4" style={{ background: 'var(--primary-soft)', color: 'var(--primary)' }}>
                <f.icon className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-base">{f.title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed" style={{ color: 'var(--muted)' }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Split CTA */}
      <section className="max-w-6xl mx-auto px-5 pb-20">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="card card-hover p-7 relative overflow-hidden">
            <div className="absolute -right-8 -top-8 w-40 h-40 rounded-full blur-2xl" style={{ background: 'var(--primary-soft)' }} />
            <div className="relative">
              <div className="w-11 h-11 rounded-xl flex items-center justify-center mb-4" style={{ background: 'var(--primary)', color: '#fff' }}>
                <GraduationCap className="w-5 h-5" />
              </div>
              <h3 className="text-xl font-extrabold">For students</h3>
              <ul className="mt-3 space-y-2 text-sm" style={{ color: 'var(--muted)' }}>
                {['Personalized recommendations', 'One-click applications', 'Live status pipeline'].map((t) => (
                  <li key={t} className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" style={{ color: 'var(--success)' }} /> {t}
                  </li>
                ))}
              </ul>
              <button onClick={() => onOpen('register')} className="btn btn-primary mt-6">
                Find your internship <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="card card-hover p-7 relative overflow-hidden">
            <div className="absolute -right-8 -top-8 w-40 h-40 rounded-full blur-2xl" style={{ background: 'color-mix(in srgb, var(--accent) 12%, transparent)' }} />
            <div className="relative">
              <div className="w-11 h-11 rounded-xl flex items-center justify-center mb-4" style={{ background: 'var(--text)', color: 'var(--surface)' }}>
                <Building2 className="w-5 h-5" />
              </div>
              <h3 className="text-xl font-extrabold">For recruiters</h3>
              <ul className="mt-3 space-y-2 text-sm" style={{ color: 'var(--muted)' }}>
                {['Post roles in minutes', 'Kanban applicant pipeline', 'Schedule interviews inline'].map((t) => (
                  <li key={t} className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" style={{ color: 'var(--success)' }} /> {t}
                  </li>
                ))}
              </ul>
              <button onClick={() => onOpen('register')} className="btn btn-ghost mt-6">
                Post a role <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t" style={{ borderColor: 'var(--border)', background: 'var(--surface)' }}>
        <div className="max-w-6xl mx-auto px-5 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Brand compact />
            <span className="text-xs" style={{ color: 'var(--muted-2)' }}>· © 2026 · Where careers begin.</span>
          </div>
          <div className="flex items-center gap-5 text-xs font-medium" style={{ color: 'var(--muted)' }}>
            <span className="hover:opacity-70 cursor-pointer transition">Privacy</span>
            <span className="hover:opacity-70 cursor-pointer transition">Terms</span>
            <span className="hover:opacity-70 cursor-pointer transition">Contact</span>
            <a href="/admin" className="hover:opacity-70 cursor-pointer transition flex items-center gap-1" style={{ color: 'var(--muted)' }}>
              <ShieldCheck className="w-3.5 h-3.5" /> Admin
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Shared visual wordmark; compact mode hides the text beside the icon.
const Brand: React.FC<{ compact?: boolean }> = ({ compact }) => (
  <div className="flex items-center gap-2.5 select-none">
    <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white shadow-sm" style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent))' }}>
      <Briefcase className="w-4.5 h-4.5" strokeWidth={2.5} />
    </div>
    {!compact && (
      <span className="text-lg font-extrabold tracking-tight" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
        Hire<span style={{ color: 'var(--primary)' }}>Hub</span>
      </span>
    )}
  </div>
);

// Provider nesting makes auth, theme and notifications available below
// the browser router.
const App: React.FC = () => (
  <Router>
    <AuthProvider>
      <ThemeProvider>
        <NotificationProvider>
          <MainRouter />
        </NotificationProvider>
      </ThemeProvider>
    </AuthProvider>
  </Router>
);

export default App;
