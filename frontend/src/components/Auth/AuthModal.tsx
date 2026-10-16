/*
 * Shared sign-in and student/recruiter registration dialog. Role-specific
 * form fields are collected locally and converted into the backend request
 * shape. Authentication context stores the returned token and account identity.
 */

import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Briefcase, Eye, EyeOff, X, Check, Sparkles, GraduationCap, Building2 } from 'lucide-react';

interface AuthModalProps { isOpen: boolean; onClose: () => void; defaultTab?: 'login' | 'register'; }

const SKILLS_LIST = ['React.js', 'TypeScript', 'Python', 'Node.js', 'Figma', 'SQL & MySQL',
  'FastAPI', 'Machine Learning', 'UI/UX Design', 'Data Analysis', 'Next.js', 'Docker'];

type AuthMode = 'login' | 'register-student' | 'register-recruiter';

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, defaultTab = 'login' }) => {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<AuthMode>(defaultTab === 'register' ? 'register-student' : 'login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPwd, setShowPwd] = useState(false);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [form, setForm] = useState({
    email: '', password: '', full_name: '', phone: '', university: '', degree: '',
    field_of_study: '', graduation_year: '', cgpa: '', bio: '', location: '',
    preferred_mode: 'Remote', expected_stipend: '', portfolio_url: '', github_url: '', linkedin_url: '',
    company_name: '', designation: '', company_size: '', industry: '', company_website: '',
    gender: '',
  });

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const toggleSkill = (s: string) =>
    setSelectedSkills((prev) => (prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]));

  // Switch form mode and discard the previous mode's error message.
  const switchMode = (m: AuthMode) => { setMode(m); setError(''); };

  // Use login for existing accounts; otherwise build a student or recruiter
  // registration payload. Convert graduation year from form text to a number.
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      if (mode === 'login') {
        await login(form.email, form.password);
        onClose();
      } else {
        const role = mode === 'register-recruiter' ? 'recruiter' : 'student';
        const payload: any = { email: form.email, password: form.password, full_name: form.full_name, role };
        if (role === 'student') {
          Object.assign(payload, {
            phone: form.phone, university: form.university, degree: form.degree,
            field_of_study: form.field_of_study, graduation_year: form.graduation_year ? parseInt(form.graduation_year) : undefined,
            bio: form.bio, location: form.location, preferred_mode: form.preferred_mode,
            expected_stipend: form.expected_stipend, portfolio_url: form.portfolio_url,
            github_url: form.github_url, linkedin_url: form.linkedin_url,
            gender: form.gender || undefined, skills: selectedSkills,
          });
        } else {
          Object.assign(payload, {
            company_name: form.company_name, designation: form.designation, company_size: form.company_size,
            industry: form.industry, company_website: form.company_website, phone: form.phone, location: form.location,
          });
        }
        await register(payload);
        onClose();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const isLogin = mode === 'login';
  const isRecruiter = mode === 'register-recruiter';

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in"
      style={{ background: 'rgba(15,23,42,0.55)', backdropFilter: 'blur(6px)' }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="w-full max-w-4xl overflow-hidden rounded-3xl flex flex-col sm:flex-row animate-scale-in" style={{ background: 'var(--surface)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-lg)', maxHeight: '92vh' }}>
        {/* Marketing sidebar */}
        <div className="hidden sm:flex flex-col justify-between w-2/5 p-8 relative overflow-hidden text-white" style={{ background: 'linear-gradient(150deg, var(--primary), #4338ca 60%, var(--accent))' }}>
          <div className="absolute -top-16 -right-16 w-56 h-56 rounded-full blur-3xl animate-pulse-glow" style={{ background: 'rgba(255,255,255,0.18)' }} />
          <div className="relative">
            <div className="flex items-center gap-2 mb-10">
              <div className="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center"><Briefcase className="w-5 h-5" /></div>
              <span className="text-lg font-extrabold" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>HireHub</span>
            </div>
            <h3 className="text-2xl font-extrabold leading-tight">
              {isLogin ? 'Welcome back.' : isRecruiter ? 'Hire smarter.' : 'Land your dream role.'}
            </h3>
            <p className="text-sm text-white/80 mt-2 leading-relaxed">
              {isLogin
                ? 'Sign in to pick up where you left off — your applications and matches await.'
                : isRecruiter
                ? 'Reach thousands of qualified students and manage your hiring pipeline in one place.'
                : 'Join thousands of students discovering curated internships every day.'}
            </p>
          </div>
          <ul className="relative space-y-2.5 mt-8">
            {(isRecruiter
              ? ['Post unlimited roles', 'Kanban applicant pipeline', 'Inline interview scheduling']
              : ['Personalized matches', 'One-click applications', 'Real-time status updates']
            ).map((t) => (
              <li key={t} className="flex items-center gap-2 text-sm text-white/90">
                <span className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center"><Check className="w-3 h-3" /></span> {t}
              </li>
            ))}
          </ul>
        </div>

        {/* Form panel */}
        <div className="flex-1 p-6 sm:p-8 overflow-y-auto">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2 sm:hidden">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center text-white" style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent))' }}>
                <Briefcase className="w-4 h-4" />
              </div>
              <span className="font-extrabold">Hire<span style={{ color: 'var(--primary)' }}>Hub</span></span>
            </div>
            <div className="hidden sm:block" />
            <button onClick={onClose} className="w-8 h-8 rounded-lg flex items-center justify-center transition" style={{ color: 'var(--muted)' }} onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-3)'; }} onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}>
              <X className="w-4 h-4" />
            </button>
          </div>

          <h2 className="text-xl font-extrabold mb-1">
            {isLogin ? 'Sign in to your account' : isRecruiter ? 'Create a recruiter account' : 'Create your student account'}
          </h2>
          <p className="text-xs mb-5" style={{ color: 'var(--muted)' }}>
            {isLogin ? 'Enter your credentials to continue.' : 'Takes less than a minute. No credit card required.'}
          </p>

          {/* Tabs */}
          <div className="grid grid-cols-3 gap-1 p-1 rounded-xl mb-5" style={{ background: 'var(--surface-2)' }}>
            {[
              { key: 'login' as const, label: 'Sign in', icon: null },
              { key: 'register-student' as const, label: 'Student', icon: GraduationCap },
              { key: 'register-recruiter' as const, label: 'Recruiter', icon: Building2 },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => switchMode(tab.key)}
                className="py-2 text-xs font-semibold rounded-lg transition flex items-center justify-center gap-1.5"
                style={mode === tab.key ? { background: 'var(--surface)', color: 'var(--primary)', boxShadow: 'var(--shadow-sm)' } : { color: 'var(--muted)' }}
              >
                {tab.icon && <tab.icon className="w-3.5 h-3.5" />} {tab.label}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-3.5">
            {error && (
              <div className="rounded-xl px-3 py-2.5 text-xs font-medium animate-fade-in" style={{ background: 'var(--danger-soft)', color: 'var(--danger)', border: '1px solid color-mix(in srgb, var(--danger) 25%, transparent)' }}>
                {error}
              </div>
            )}

            {isLogin && (
              <>
                <Field label="Email" type="email" value={form.email} onChange={set('email')} placeholder="you@example.com" required />
                <PasswordWithToggle label="Password" value={form.password} onChange={set('password')} show={showPwd} setShow={setShowPwd} placeholder="••••••••" required />
                <div className="flex items-center justify-between text-xs">
                  <span className="cursor-pointer font-medium hover:underline" style={{ color: 'var(--primary)' }}>Forgot password?</span>
                </div>
                <div className="rounded-xl p-3 text-[11px] animate-fade-in" style={{ background: 'var(--surface-2)', border: '1px dashed var(--border)' }}>
                  <p style={{ color: 'var(--muted)' }} className="mb-1.5 font-semibold flex items-center gap-1"><Sparkles className="w-3.5 h-3.5" style={{ color: 'var(--primary)' }} /> Try a demo account</p>
                  <div className="grid grid-cols-1 gap-1 font-mono">
                    <span>👨‍🎓 student@demo.com · password123</span>
                    <span>💼 recruiter@stripe.com · recruiter123</span>
                    <span style={{ color: 'var(--muted-2)' }}>also: recruiter@{`{notion,figma,spotify,vercel,linear}`}.com</span>
                  </div>
                </div>
              </>
            )}

            {mode === 'register-student' && (
              <>
                <div className="grid grid-cols-2 gap-3">
                  <Field label="Full name" value={form.full_name} onChange={set('full_name')} placeholder="Alex Morgan" required />
                  <Field label="Phone" value={form.phone} onChange={set('phone')} placeholder="+1 555 0100" />
                </div>
                <Field label="Email" type="email" value={form.email} onChange={set('email')} placeholder="alex@university.edu" required />
                <PasswordWithToggle label="Password" value={form.password} onChange={set('password')} show={showPwd} setShow={setShowPwd} placeholder="Create a password" required />
                <div className="grid grid-cols-2 gap-3">
                  <Field label="University" value={form.university} onChange={set('university')} placeholder="Stanford University" />
                  <Field label="Field of study" value={form.field_of_study} onChange={set('field_of_study')} placeholder="Computer Science" />
                </div>
                <SelectField label="Gender" value={form.gender} onChange={set('gender')} options={['male', 'female', 'other', 'prefer_not_to_say']} placeholder="Select gender (for your avatar)" />
                <div>
                  <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>Skills</label>
                  <div className="flex flex-wrap gap-1.5">
                    {SKILLS_LIST.map((s) => {
                      const sel = selectedSkills.includes(s);
                      return (
                        <button type="button" key={s} onClick={() => toggleSkill(s)}
                          className="px-2.5 py-1 rounded-lg text-xs font-medium transition"
                          style={sel ? { background: 'var(--primary-soft)', color: 'var(--primary)', border: '1px solid color-mix(in srgb, var(--primary) 30%, transparent)' } : { background: 'var(--surface-2)', color: 'var(--muted)', border: '1px solid var(--border)' }}
                        >{s}</button>
                      );
                    })}
                  </div>
                </div>
              </>
            )}

            {isRecruiter && (
              <>
                <div className="grid grid-cols-2 gap-3">
                  <Field label="Full name" value={form.full_name} onChange={set('full_name')} placeholder="Sarah Jenkins" required />
                  <Field label="Phone" value={form.phone} onChange={set('phone')} placeholder="+1 415 555 0100" />
                </div>
                <Field label="Work email" type="email" value={form.email} onChange={set('email')} placeholder="sarah@company.com" required />
                <PasswordWithToggle label="Password" value={form.password} onChange={set('password')} show={showPwd} setShow={setShowPwd} placeholder="Create a password" required />
                <Field label="Company name" value={form.company_name} onChange={set('company_name')} placeholder="Stripe" required />
                <div className="grid grid-cols-2 gap-3">
                  <Field label="Designation" value={form.designation} onChange={set('designation')} placeholder="Technical Recruiter" />
                  <SelectField label="Company size" value={form.company_size} onChange={set('company_size')} options={['1-10', '11-50', '51-200', '201-1000', '1001-5000', '5000+']} />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <Field label="Industry" value={form.industry} onChange={set('industry')} placeholder="FinTech" />
                  <Field label="Website" value={form.company_website} onChange={set('company_website')} placeholder="https://company.com" />
                </div>
              </>
            )}

            <button type="submit" disabled={loading} className="btn btn-primary w-full py-3 text-sm mt-2">
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  {isLogin ? 'Signing in…' : 'Creating account…'}
                </span>
              ) : (
                <>{isLogin ? 'Sign in' : 'Create account'} →</>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Shared labeled input used by registration fields.
const Field: React.FC<{ label: string; type?: string; value: string; onChange: any; placeholder?: string; required?: boolean }> = ({ label, type = 'text', value, onChange, placeholder, required }) => (
  <div>
    <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>{label}{required && <span style={{ color: 'var(--danger)' }}>*</span>}</label>
    <input type={type} value={value} onChange={onChange} placeholder={placeholder} required={required} className="input" />
  </div>
);

// Shared labeled dropdown for predefined registration choices.
const SelectField: React.FC<{ label: string; value: string; onChange: any; options: string[]; placeholder?: string }> = ({ label, value, onChange, options, placeholder }) => {
  const LABELS: Record<string, string> = { male: 'Male', female: 'Female', other: 'Other', prefer_not_to_say: 'Prefer not to say' };
  return (
    <div>
      <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>{label}</label>
      <select value={value} onChange={onChange} className="select">
        <option value="">{placeholder || 'Select…'}</option>
        {options.map((o) => <option key={o} value={o}>{LABELS[o] || o}</option>)}
      </select>
    </div>
  );
};

// Switch password visibility locally without changing the submitted value.
const PasswordWithToggle: React.FC<{ label: string; value: string; onChange: any; show: boolean; setShow: (v: boolean) => void; placeholder?: string; required?: boolean }> = ({ label, value, onChange, show, setShow, placeholder, required }) => (
  <div>
    <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>{label}{required && <span style={{ color: 'var(--danger)' }}>*</span>}</label>
    <div className="relative">
      <input type={show ? 'text' : 'password'} value={value} onChange={onChange} placeholder={placeholder} required={required} className="input pr-10" />
      <button type="button" onClick={() => setShow(!show)} className="absolute right-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--muted-2)' }}>
        {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
      </button>
    </div>
  </div>
);
