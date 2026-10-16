/*
 * Dedicated admin sign-in page. It calls the admin authentication endpoint;
 * normal student/recruiter credentials are rejected there. Successful context
 * updates make the top-level router render the admin console.
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { ShieldCheck, Lock, Mail, ArrowLeft, AlertCircle } from 'lucide-react';

export const AdminLogin: React.FC = () => {
  const { loginAdmin } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Call the dedicated admin login, display a backend error when rejected,
  // and let the auth context/router handle a successful workspace change.
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      // On success the auth context updates and the app routes to the console.
      await loginAdmin(email.trim(), password);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Sign in failed. Please try again.');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden" style={{ background: '#141727' }}>
      {/* ambient glows */}
      <div className="absolute -top-32 -left-32 w-96 h-96 rounded-full" style={{ background: 'radial-gradient(circle, rgba(79,124,255,0.18), transparent 70%)' }} />
      <div className="absolute -bottom-32 -right-32 w-96 h-96 rounded-full" style={{ background: 'radial-gradient(circle, rgba(139,92,246,0.15), transparent 70%)' }} />

      <div className="w-full max-w-md relative">
        <Link to="/" className="inline-flex items-center gap-1.5 text-xs font-medium mb-6 transition hover:opacity-80" style={{ color: '#8b93b0' }}>
          <ArrowLeft className="w-3.5 h-3.5" /> Back to HireHub
        </Link>

        <div className="rounded-3xl p-8" style={{ background: '#1d2135', border: '1px solid rgba(255,255,255,0.07)', boxShadow: '0 24px 60px rgba(0,0,0,0.4)' }}>
          <div className="flex flex-col items-center text-center mb-7">
            <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-4" style={{ background: 'linear-gradient(135deg, #4f7cff, #8b5cf6)', boxShadow: '0 8px 24px rgba(79,124,255,0.35)' }}>
              <ShieldCheck className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-xl font-extrabold text-white tracking-tight">Admin Console</h1>
            <p className="text-xs mt-1.5" style={{ color: '#8b93b0' }}>
              Restricted area — platform operators only
            </p>
          </div>

          {error && (
            <div className="mb-4 px-3.5 py-2.5 rounded-xl text-xs font-semibold flex items-center gap-2" style={{ background: 'rgba(239,68,68,0.12)', color: '#f87171', border: '1px solid rgba(239,68,68,0.25)' }}>
              <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[11px] font-semibold mb-1.5 uppercase tracking-wider" style={{ color: '#8b93b0' }}>Email</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: '#5a6284' }} />
                <input
                  type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@hirehub.com"
                  className="w-full pl-10 pr-4 py-3 rounded-xl text-sm text-white outline-none transition focus:ring-2"
                  style={{ background: '#141727', border: '1px solid rgba(255,255,255,0.08)' }}
                />
              </div>
            </div>
            <div>
              <label className="block text-[11px] font-semibold mb-1.5 uppercase tracking-wider" style={{ color: '#8b93b0' }}>Password</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: '#5a6284' }} />
                <input
                  type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-3 rounded-xl text-sm text-white outline-none transition focus:ring-2"
                  style={{ background: '#141727', border: '1px solid rgba(255,255,255,0.08)' }}
                />
              </div>
            </div>
            <button
              type="submit" disabled={loading}
              className="w-full py-3 rounded-xl text-sm font-bold text-white transition disabled:opacity-60"
              style={{ background: 'linear-gradient(135deg, #4f7cff, #8b5cf6)', boxShadow: '0 8px 24px rgba(79,124,255,0.35)' }}
            >
              {loading ? 'Signing in…' : 'Sign in to console'}
            </button>
          </form>

          <div className="mt-6 pt-5 text-center" style={{ borderTop: '1px solid rgba(255,255,255,0.07)' }}>
            <p className="text-[11px]" style={{ color: '#5a6284' }}>
              Demo credentials — <span style={{ color: '#8b93b0' }}>admin@hirehub.com · admin123</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
