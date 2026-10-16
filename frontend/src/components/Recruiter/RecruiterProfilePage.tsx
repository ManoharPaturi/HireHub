/*
 * Recruiter/company profile editor. State holds editable form values; a
 * successful update asks the parent workspace to reload the saved profile.
 */

import React, { useState } from 'react';
import { RecruiterProfile } from '../../types';
import { recruiterService } from '../../services/api';
import { CheckCircle2, Building2, User } from 'lucide-react';

interface Props {
  profile: RecruiterProfile | null;
  onRefresh: () => void;
}

export const RecruiterProfilePage: React.FC<Props> = ({ profile, onRefresh }) => {
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [form, setForm] = useState({
    full_name: profile?.full_name || '',
    designation: profile?.designation || '',
    company_name: profile?.company_name || '',
    industry: profile?.industry || '',
    company_size: profile?.company_size || '',
    company_website: profile?.company_website || '',
    location: profile?.location || '',
    phone: profile?.phone || '',
    linkedin_url: profile?.linkedin_url || '',
    bio: profile?.bio || '',
  });

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => setForm((f) => ({ ...f, [k]: e.target.value }));

  // Save company/contact fields and request a workspace reload on success.
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await recruiterService.updateProfile(form);
      setSaved(true);
      onRefresh();
      setTimeout(() => setSaved(false), 2500);
    } catch { alert('Failed to update profile.'); }
    finally { setLoading(false); }
  };

  if (!profile) return null;

  return (
    <div className="max-w-4xl space-y-6">
      {saved && (
        <div className="px-4 py-3 rounded-xl text-xs font-bold flex items-center gap-2 animate-fade-in" style={{ background: 'var(--success-soft)', color: 'var(--success)', border: '1px solid color-mix(in srgb, var(--success) 20%, transparent)' }}>
          <CheckCircle2 className="w-4 h-4" /> Profile updated successfully!
        </div>
      )}

      {/* Header */}
      <div className="card overflow-hidden animate-rise">
        <div className="h-24" style={{ background: 'linear-gradient(120deg, var(--primary), var(--accent))' }} />
        <div className="px-6 pb-6 flex flex-col sm:flex-row sm:items-end gap-4 -mt-12">
          <div className="w-24 h-24 rounded-3xl flex items-center justify-center text-white text-3xl font-bold shadow-lg flex-shrink-0" style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent))', border: '4px solid var(--surface)' }}>
            {profile.full_name[0]}
          </div>
          <div className="pb-1 flex-1">
            <h2 className="text-xl font-extrabold">{profile.full_name}</h2>
            <p className="text-sm" style={{ color: 'var(--muted)' }}>{profile.designation} at <span className="font-semibold" style={{ color: 'var(--primary)' }}>{profile.company_name}</span></p>
          </div>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="card p-6 sm:p-8 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h3 className="font-bold text-sm flex items-center gap-1.5 pb-2" style={{ borderBottom: '1px solid var(--border)' }}><User className="w-4 h-4" style={{ color: 'var(--primary)' }} /> Personal</h3>
            <Field label="Full name" value={form.full_name} onChange={set('full_name')} required />
            <Field label="Designation" value={form.designation} onChange={set('designation')} />
            <Field label="Phone" value={form.phone} onChange={set('phone')} />
            <Field label="LinkedIn URL" value={form.linkedin_url} onChange={set('linkedin_url')} />
          </div>
          <div className="space-y-4">
            <h3 className="font-bold text-sm flex items-center gap-1.5 pb-2" style={{ borderBottom: '1px solid var(--border)' }}><Building2 className="w-4 h-4" style={{ color: 'var(--primary)' }} /> Company</h3>
            <Field label="Company name" value={form.company_name} onChange={set('company_name')} required />
            <div className="grid grid-cols-2 gap-3">
              <Field label="Industry" value={form.industry} onChange={set('industry')} />
              <div>
                <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>Size</label>
                <select value={form.company_size} onChange={set('company_size')} className="select">
                  <option value="1-10">1–10</option><option value="11-50">11–50</option><option value="51-200">51–200</option>
                  <option value="201-1000">201–1,000</option><option value="1001-5000">1,001–5,000</option><option value="5000+">5,000+</option>
                </select>
              </div>
            </div>
            <Field label="Website" value={form.company_website} onChange={set('company_website')} />
            <Field label="HQ Location" value={form.location} onChange={set('location')} />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>About / bio</label>
          <textarea rows={4} value={form.bio} onChange={set('bio')} placeholder="Tell candidates what you look for…" className="textarea" />
        </div>

        <div className="flex justify-end pt-2" style={{ borderTop: '1px solid var(--border)' }}>
          <button type="submit" disabled={loading} className="btn btn-primary disabled:opacity-50">
            {loading ? 'Saving…' : 'Save changes'}
          </button>
        </div>
      </form>
    </div>
  );
};

// Shared controlled profile input with its label and editable value.
const Field: React.FC<{ label: string; value: string; onChange: any; required?: boolean }> = ({ label, value, onChange, required }) => (
  <div>
    <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>{label}{required && <span style={{ color: 'var(--danger)' }}> *</span>}</label>
    <input value={value} onChange={onChange} required={required} className="input" />
  </div>
);
