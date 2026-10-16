import React, { useState } from 'react';
import { recruiterService } from '../../services/api';
import { RecruiterProfile } from '../../types';
import { Check, ChevronLeft, ChevronRight, Sparkles } from 'lucide-react';

interface Props { profile: RecruiterProfile | null; onSuccess: () => void; }

const SKILLS = ['React.js', 'TypeScript', 'Python', 'Node.js', 'FastAPI', 'SQL & MySQL',
  'Figma', 'UI/UX Design', 'Machine Learning', 'Data Analysis', 'Next.js', 'Docker',
  'GraphQL', 'Digital Marketing', 'Product Management', 'Go', 'Rust', 'Java'];

export const PostInternship: React.FC<Props> = ({ profile, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [step, setStep] = useState<1 | 2>(1);
  const [form, setForm] = useState({
    title: '', company_name: profile?.company_name || '', location: '',
    mode: 'Remote', stipend_amount: '0', stipend_currency: '₹',
    duration: '3 Months', description: '', eligibility: '',
    responsibilities: '', benefits: '', is_external: 'false',
    external_link: '', deadline: '',
  });

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const toggleSkill = (s: string) =>
    setSelectedSkills((prev) => (prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      await recruiterService.postInternship({
        ...form,
        stipend_amount: parseInt(form.stipend_amount) || 0,
        is_external: form.is_external === 'true',
        deadline: form.deadline || null,
        skills_required: selectedSkills.join(', '),
        company_name: form.company_name || profile?.company_name || 'My Company',
        company_logo: profile?.company_logo,
      });
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to post internship. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const canProceedStep1 = form.title && form.location;
  const canSubmit = canProceedStep1 && form.description;

  return (
    <div className="max-w-3xl">
      {/* Progress */}
      <div className="flex items-center gap-3 mb-8">
        {[
          { n: 1, l: 'Basic details' },
          { n: 2, l: 'Description & skills' },
        ].map(({ n, l }, i) => (
          <React.Fragment key={n}>
            <button onClick={() => setStep(n as 1 | 2)} className="flex items-center gap-2 text-sm font-medium transition" style={{ color: step === n ? 'var(--primary)' : step > n ? 'var(--success)' : 'var(--muted)' }}>
              <span className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold"
                style={step === n ? { background: 'var(--primary)', color: '#fff' } : step > n ? { background: 'var(--success-soft)', color: 'var(--success)' } : { background: 'var(--surface-2)', color: 'var(--muted)', border: '1px solid var(--border)' }}>
                {step > n ? <Check className="w-3.5 h-3.5" /> : n}
              </span>
              {l}
            </button>
            {i === 0 && <div className="flex-1 h-px" style={{ background: 'var(--border)' }} />}
          </React.Fragment>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        {error && (
          <div className="mb-4 rounded-xl px-3 py-2.5 text-xs font-medium animate-fade-in" style={{ background: 'var(--danger-soft)', color: 'var(--danger)', border: '1px solid color-mix(in srgb, var(--danger) 25%, transparent)' }}>
            {error}
          </div>
        )}

        {/* Step 1 */}
        {step === 1 && (
          <div className="card p-6 space-y-5 animate-rise">
            <div>
              <h3 className="font-bold text-base">Basic details</h3>
              <p className="text-xs mt-0.5" style={{ color: 'var(--muted)' }}>Tell candidates what the role is.</p>
            </div>
            <FormRow label="Internship title" required>
              <input value={form.title} onChange={set('title')} placeholder="e.g. Frontend Engineering Intern" className="input" required />
            </FormRow>
            <div className="grid grid-cols-2 gap-4">
              <FormRow label="Company" required>
                <input value={form.company_name} onChange={set('company_name')} placeholder="Your company" className="input" required />
              </FormRow>
              <FormRow label="Location" required>
                <input value={form.location} onChange={set('location')} placeholder="e.g. San Francisco, CA" className="input" required />
              </FormRow>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <FormRow label="Work mode">
                <select value={form.mode} onChange={set('mode')} className="select"><option>Remote</option><option>Hybrid</option><option>In-Office</option></select>
              </FormRow>
              <FormRow label="Duration">
                <select value={form.duration} onChange={set('duration')} className="select"><option>1 Month</option><option>2 Months</option><option>3 Months</option><option>4 Months</option><option>6 Months</option><option>12 Months</option></select>
              </FormRow>
              <FormRow label="Stipend" required>
                <div className="flex gap-2">
                  <select value={form.stipend_currency} onChange={set('stipend_currency')} className="select" style={{ width: 'auto' }}><option>₹</option><option>$</option><option>€</option></select>
                  <input type="number" value={form.stipend_amount} onChange={set('stipend_amount')} min="0" placeholder="30000" className="input" />
                </div>
              </FormRow>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <FormRow label="Posting type">
                <select value={form.is_external} onChange={set('is_external')} className="select">
                  <option value="false">Internal (apply on portal)</option>
                  <option value="true">External (link to your site)</option>
                </select>
              </FormRow>
              <FormRow label="Deadline">
                <input type="date" value={form.deadline} onChange={set('deadline')} className="input" />
              </FormRow>
            </div>
            {form.is_external === 'true' && (
              <FormRow label="External application URL">
                <input value={form.external_link} onChange={set('external_link')} placeholder="https://company.com/careers/intern" className="input" />
              </FormRow>
            )}
            <div className="flex justify-end">
              <button type="button" onClick={() => setStep(2)} disabled={!canProceedStep1} className="btn btn-primary disabled:opacity-50">
                Next <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Step 2 */}
        {step === 2 && (
          <div className="card p-6 space-y-5 animate-rise">
            <div>
              <h3 className="font-bold text-base">Description & skills</h3>
              <p className="text-xs mt-0.5" style={{ color: 'var(--muted)' }}>Paint a clear picture of the role.</p>
            </div>
            <FormRow label="Description" required>
              <textarea rows={4} value={form.description} onChange={set('description')} placeholder="Describe what the intern will work on and the impact of this role…" className="textarea" required />
            </FormRow>
            <FormRow label="Eligibility">
              <textarea rows={2} value={form.eligibility} onChange={set('eligibility')} placeholder="e.g. Currently enrolled in CS or related field" className="textarea" />
            </FormRow>
            <FormRow label="Responsibilities">
              <textarea rows={3} value={form.responsibilities} onChange={set('responsibilities')} placeholder={"• Build new features\n• Write tests\n• Participate in code reviews"} className="textarea" />
            </FormRow>
            <FormRow label="Benefits & perks">
              <textarea rows={2} value={form.benefits} onChange={set('benefits')} placeholder={"• Competitive stipend\n• Mentorship\n• Equipment allowance"} className="textarea" />
            </FormRow>
            <div>
              <label className="block text-xs font-semibold mb-2" style={{ color: 'var(--text-soft)' }}>Required skills</label>
              <div className="flex flex-wrap gap-1.5">
                {SKILLS.map((s) => {
                  const sel = selectedSkills.includes(s);
                  return (
                    <button type="button" key={s} onClick={() => toggleSkill(s)} className="px-3 py-1 rounded-lg text-xs font-medium transition"
                      style={sel ? { background: 'var(--primary-soft)', color: 'var(--primary)', border: '1px solid color-mix(in srgb, var(--primary) 30%, transparent)' } : { background: 'var(--surface-2)', color: 'var(--muted)', border: '1px solid var(--border)' }}>
                      {s}
                    </button>
                  );
                })}
              </div>
            </div>
            <div className="flex justify-between pt-2" style={{ borderTop: '1px solid var(--border)' }}>
              <button type="button" onClick={() => setStep(1)} className="btn btn-ghost">
                <ChevronLeft className="w-4 h-4" /> Back
              </button>
              <button type="submit" disabled={loading || !canSubmit} className="btn btn-primary disabled:opacity-50">
                {loading ? (
                  <span className="flex items-center gap-2"><span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" /> Publishing…</span>
                ) : <><Sparkles className="w-4 h-4" /> Publish internship</>}
              </button>
            </div>
          </div>
        )}
      </form>
    </div>
  );
};

const FormRow: React.FC<{ label: string; children: React.ReactNode; required?: boolean }> = ({ label, children, required }) => (
  <div>
    <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>{label}{required && <span style={{ color: 'var(--danger)' }}> *</span>}</label>
    {children}
  </div>
);
