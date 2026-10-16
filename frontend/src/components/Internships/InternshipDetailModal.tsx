/*
 * Posting details and application dialog. Internal roles submit a cover
 * letter and optional resume through the parent callback. External roles open
 * a confirmation and then the company link without creating a local application.
 */

import React, { useState, useRef } from 'react';
import { Internship } from '../../types';
import {
  X, MapPin, Calendar, Wallet, ExternalLink, CheckCircle2, Send,
  Mail, Clock, ArrowRight, Building2, Upload, FileText,
} from 'lucide-react';

interface InternshipDetailModalProps {
  internship: Internship | null;
  onClose: () => void;
  onApplySubmit: (internshipId: number, coverLetter: string, resume?: File | null) => Promise<void>;
}

const FALLBACK_LOGO = 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=120&q=80';

export const InternshipDetailModal: React.FC<InternshipDetailModalProps> = ({
  internship,
  onClose,
  onApplySubmit,
}) => {
  const [showApplyForm, setShowApplyForm] = useState(false);
  const [showExternalRedirectModal, setShowExternalRedirectModal] = useState(false);

  const [coverLetter, setCoverLetter] = useState(
    "I'm excited to apply for this role. With my background in building real-world software and a strong eagerness to learn, I'm confident I can contribute meaningfully to your team."
  );
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  if (!internship) return null;

  const skillsList = internship.skills_required ? internship.skills_required.split(',').map((s) => s.trim()).filter(Boolean) : [];
  const deadline = internship.deadline ? new Date(internship.deadline) : null;
  const daysLeft = deadline ? Math.max(0, Math.ceil((deadline.getTime() - Date.now()) / 86400000)) : null;

  // External and internal applications follow different submission paths.
  const handleApplyClick = () => {
    if (internship.is_external) setShowExternalRedirectModal(true);
    else setShowApplyForm(true);
  };

  // Submit the selected posting, cover letter and optional file. Success
  // closes the dialog after a brief confirmation; the parent refreshes listings.
  const handleInternalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onApplySubmit(internship.id, coverLetter, resumeFile);
      setSuccessMsg('Application submitted successfully!');
      setTimeout(onClose, 1600);
    } catch (err) { console.error(err); }
    finally { setSubmitting(false); }
  };

  const fmtSize = (b: number) => (b < 1024 ? `${b} B` : b < 1024 * 1024 ? `${(b / 1024).toFixed(0)} KB` : `${(b / 1024 / 1024).toFixed(1)} MB`);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in"
      style={{ background: 'rgba(15,23,42,0.6)', backdropFilter: 'blur(6px)' }}
    >
      <div className="w-full max-w-3xl overflow-hidden rounded-3xl flex flex-col animate-scale-in" style={{ background: 'var(--surface)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-lg)', maxHeight: '92vh' }}>
        {/* Header */}
        <div className="p-6 relative" style={{ borderBottom: '1px solid var(--border)', background: 'var(--surface-2)' }}>
          <button onClick={onClose} className="absolute top-4 right-4 w-8 h-8 rounded-lg flex items-center justify-center transition" style={{ color: 'var(--muted)' }} onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-3)'; }} onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}>
            <X className="w-4 h-4" />
          </button>
          <div className="flex items-start gap-4 pr-8">
            <img src={internship.company_logo || FALLBACK_LOGO} alt={internship.company_name} className="w-16 h-16 rounded-2xl object-cover" style={{ border: '1px solid var(--border)' }} />
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-bold uppercase tracking-wide flex items-center gap-1" style={{ color: 'var(--primary)' }}><Building2 className="w-3.5 h-3.5" /> {internship.company_name}</span>
                {internship.is_external && <span className="badge" style={{ background: 'var(--warning-soft)', color: 'var(--warning)' }}>External</span>}
              </div>
              <h2 className="text-xl font-extrabold mt-0.5">{internship.title}</h2>
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs mt-2" style={{ color: 'var(--muted)' }}>
                <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {internship.location} · {internship.mode}</span>
                <span className="flex items-center gap-1 font-semibold" style={{ color: 'var(--success)' }}><Wallet className="w-3.5 h-3.5" /> {internship.stipend_currency}{internship.stipend_amount.toLocaleString()}/mo</span>
                <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5" /> {internship.duration}</span>
              </div>
            </div>
          </div>
        </div>

        {successMsg && (
          <div className="px-6 py-3 flex items-center justify-center gap-2 text-xs font-bold animate-fade-in" style={{ background: 'var(--success-soft)', color: 'var(--success)', borderBottom: '1px solid color-mix(in srgb, var(--success) 20%, transparent)' }}>
            <CheckCircle2 className="w-4 h-4" /> {successMsg}
          </div>
        )}

        {/* Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {showApplyForm ? (
            <form onSubmit={handleInternalSubmit} className="space-y-4">
              <div>
                <h3 className="font-bold text-sm flex items-center gap-2 mb-3" style={{ color: 'var(--primary)' }}>
                  <Send className="w-4 h-4" /> Apply to {internship.company_name}
                </h3>
                <div className="mb-3">
                  <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>Cover letter</label>
                  <textarea rows={4} required value={coverLetter} onChange={(e) => setCoverLetter(e.target.value)} className="textarea" />
                </div>
                <div>
                  <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>Resume / CV</label>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                    className="hidden"
                  />
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full px-4 py-3 rounded-xl flex items-center gap-3 text-left transition"
                    style={{ border: `1.5px dashed ${resumeFile ? 'var(--success)' : 'var(--border-strong)'}`, background: 'var(--surface-2)' }}
                  >
                    {resumeFile ? (
                      <>
                        <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: 'var(--success-soft)', color: 'var(--success)' }}><FileText className="w-4 h-4" /></div>
                        <div className="min-w-0 flex-1">
                          <p className="text-xs font-bold truncate">{resumeFile.name}</p>
                          <p className="text-[10px]" style={{ color: 'var(--muted)' }}>{fmtSize(resumeFile.size)} · click to replace</p>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: 'var(--primary-soft)', color: 'var(--primary)' }}><Upload className="w-4 h-4" /></div>
                        <div>
                          <p className="text-xs font-bold">Upload your resume</p>
                          <p className="text-[10px]" style={{ color: 'var(--muted)' }}>PDF or Word · max 8 MB</p>
                        </div>
                      </>
                    )}
                  </button>
                </div>
              </div>
              <div className="flex gap-2">
                <button type="button" onClick={() => setShowApplyForm(false)} className="btn btn-ghost flex-1">Cancel</button>
                <button type="submit" disabled={submitting} className="btn btn-primary flex-[2]">
                  {submitting ? 'Submitting…' : <>Submit application <Send className="w-3.5 h-3.5" /></>}
                </button>
              </div>
            </form>
          ) : (
            <>
              <Section title="Role overview">
                <p className="text-sm leading-relaxed whitespace-pre-line" style={{ color: 'var(--text-soft)' }}>{internship.description}</p>
              </Section>

              {skillsList.length > 0 && (
                <Section title="Skills required">
                  <div className="flex flex-wrap gap-1.5">
                    {skillsList.map((s, i) => <span key={i} className="chip" style={{ background: 'var(--primary-soft)', color: 'var(--primary)', borderColor: 'transparent' }}>{s}</span>)}
                  </div>
                </Section>
              )}

              {internship.responsibilities && (
                <Section title="Responsibilities">
                  <div className="text-sm leading-relaxed whitespace-pre-line p-4 rounded-xl" style={{ background: 'var(--surface-2)', color: 'var(--text-soft)' }}>{internship.responsibilities}</div>
                </Section>
              )}

              {internship.eligibility && (
                <Section title="Eligibility">
                  <div className="text-sm leading-relaxed p-4 rounded-xl" style={{ background: 'var(--primary-soft)', color: 'var(--text-soft)' }}>{internship.eligibility}</div>
                </Section>
              )}

              {internship.benefits && (
                <Section title="Perks & benefits">
                  <div className="text-sm leading-relaxed whitespace-pre-line p-4 rounded-xl" style={{ background: 'var(--success-soft)', color: 'var(--text-soft)' }}>{internship.benefits}</div>
                </Section>
              )}

              {internship.recruiter_name && (
                <div className="p-4 rounded-xl flex items-center justify-between" style={{ background: 'var(--surface-2)', border: '1px solid var(--border)' }}>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm" style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent))' }}>
                      {internship.recruiter_name.charAt(0)}
                    </div>
                    <div>
                      <div className="text-sm font-bold">{internship.recruiter_name}</div>
                      <div className="text-xs" style={{ color: 'var(--muted)' }}>{internship.recruiter_title || 'Recruiter'} · {internship.company_name}</div>
                    </div>
                  </div>
                  <a href={`mailto:${internship.recruiter_email}`} className="btn btn-ghost text-xs"><Mail className="w-3.5 h-3.5" /> Contact</a>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer CTA */}
        {!showApplyForm && !successMsg && (
          <div className="p-4 flex items-center justify-between gap-3" style={{ borderTop: '1px solid var(--border)', background: 'var(--surface-2)' }}>
            <div className="text-xs flex items-center gap-1.5" style={{ color: 'var(--muted)' }}>
              <Clock className="w-3.5 h-3.5" />
              {daysLeft !== null ? `${daysLeft} days left to apply` : 'Rolling applications'}
            </div>
            {internship.has_applied ? (
              <span className="badge px-4 py-2" style={{ background: 'var(--success-soft)', color: 'var(--success)' }}>✓ Application submitted</span>
            ) : (
              <button onClick={handleApplyClick} className="btn btn-primary">
                {internship.is_external ? <>Apply on company site <ExternalLink className="w-4 h-4" /></> : <>Apply now <ArrowRight className="w-4 h-4" /></>}
              </button>
            )}
          </div>
        )}
      </div>

      {/* External redirect confirmation */}
      {showExternalRedirectModal && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 animate-fade-in" style={{ background: 'rgba(15,23,42,0.75)' }} onClick={(e) => { if (e.target === e.currentTarget) setShowExternalRedirectModal(false); }}>
          <div className="w-full max-w-md rounded-3xl p-6 text-center space-y-4 animate-scale-in" style={{ background: 'var(--surface)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-lg)' }}>
            <div className="w-12 h-12 rounded-2xl flex items-center justify-center mx-auto" style={{ background: 'var(--warning-soft)', color: 'var(--warning)' }}>
              <ExternalLink className="w-6 h-6" />
            </div>
            <h3 className="font-extrabold text-base">External application</h3>
            <p className="text-xs leading-relaxed" style={{ color: 'var(--muted)' }}>
              This role is hosted by <strong style={{ color: 'var(--text)' }}>{internship.company_name}</strong>. You'll be redirected to their official careers site to complete your application.
            </p>
            <div className="flex gap-2 pt-1">
              <button onClick={() => setShowExternalRedirectModal(false)} className="btn btn-ghost flex-1">Back</button>
              <a href={internship.external_link || '#'} target="_blank" rel="noreferrer" onClick={() => setShowExternalRedirectModal(false)} className="btn btn-primary flex-1">
                Continue <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Reuse the same heading/body structure for each posting-detail section.
const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div>
    <h3 className="text-xs font-bold uppercase tracking-wider mb-2" style={{ color: 'var(--muted)' }}>{title}</h3>
    {children}
  </div>
);
