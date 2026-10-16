import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import { studentService } from '../../services/api';
import { StudentProfile, Document } from '../../types';
import {
  CheckCircle2, Save, MapPin, GraduationCap, Edit3, Globe, Award, User,
  Upload, FileText, Trash2,
} from 'lucide-react';

export const ProfileView: React.FC = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [editing, setEditing] = useState(false);

  const [fullName, setFullName] = useState(user?.full_name || '');
  const [phone, setPhone] = useState('');
  const [gender, setGender] = useState('');
  const [university, setUniversity] = useState('');
  const [degree, setDegree] = useState('');
  const [fieldOfStudy, setFieldOfStudy] = useState('');
  const [bio, setBio] = useState('');
  const [location, setLocation] = useState('');
  const [preferredMode, setPreferredMode] = useState('Remote');
  const [expectedStipend, setExpectedStipend] = useState('');
  const [portfolioUrl, setPortfolioUrl] = useState('');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const docInputRef = useRef<HTMLInputElement>(null);

  const [saving, setSaving] = useState(false);
  const [savedMsg, setSavedMsg] = useState('');
  const [loading, setLoading] = useState(true);

  const refreshProfile = async () => {
    try {
      const data = await studentService.getProfile();
      setProfile(data);
      if (data) {
        setFullName(data.full_name || ''); setPhone(data.phone || '');
        setGender(data.gender || '');
        setUniversity(data.university || ''); setDegree(data.degree || '');
        setFieldOfStudy(data.field_of_study || ''); setBio(data.bio || '');
        setLocation(data.location || ''); setPreferredMode(data.preferred_mode || 'Remote');
        setExpectedStipend(data.expected_stipend || ''); setPortfolioUrl(data.portfolio_url || '');
        setDocuments(data.documents || []);
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  useEffect(() => { refreshProfile(); }, []);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await studentService.updateProfile({
        full_name: fullName, phone, gender, university, degree, field_of_study: fieldOfStudy, bio,
        location, preferred_mode: preferredMode, expected_stipend: expectedStipend, portfolio_url: portfolioUrl,
      });
      await refreshProfile();
      setSavedMsg('Profile updated successfully!');
      setEditing(false);
      setTimeout(() => setSavedMsg(''), 2500);
    } catch (err) { console.error(err); }
    finally { setSaving(false); }
  };

  const handleUploadDoc = async (file: File) => {
    setUploading(true);
    try {
      await studentService.uploadDocument(file, 'resume');
      const docs = await studentService.getDocuments();
      setDocuments(docs);
    } catch (e) { console.error(e); alert('Upload failed. File may be too large (8 MB max).'); }
    finally { setUploading(false); }
  };

  const handleDeleteDoc = async (id: number) => {
    if (!window.confirm('Delete this document?')) return;
    try { await studentService.deleteDocument(id); setDocuments((prev) => prev.filter((d) => d.id !== id)); }
    catch (e) { console.error(e); }
  };

  const fmtSize = (b?: number) => !b ? '' : (b < 1024 ? `${b} B` : b < 1024 * 1024 ? `${(b / 1024).toFixed(0)} KB` : `${(b / 1024 / 1024).toFixed(1)} MB`);
  const GENDER_LABELS: Record<string, string> = { male: 'Male', female: 'Female', other: 'Other', prefer_not_to_say: 'Prefer not to say' };

  const avatar = profile?.avatar_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80';

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-4">
        <div className="card p-6 h-28 skeleton" />
        <div className="card p-6 h-96 skeleton" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      {savedMsg && (
        <div className="px-4 py-3 rounded-xl text-xs font-bold flex items-center gap-2 animate-fade-in" style={{ background: 'var(--success-soft)', color: 'var(--success)', border: '1px solid color-mix(in srgb, var(--success) 20%, transparent)' }}>
          <CheckCircle2 className="w-4 h-4" /> {savedMsg}
        </div>
      )}

      {/* Header card */}
      <div className="card overflow-hidden animate-rise">
        <div className="h-24" style={{ background: 'linear-gradient(120deg, var(--primary), var(--accent))' }} />
        <div className="px-6 pb-6 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div className="flex flex-col sm:flex-row sm:items-end gap-4 -mt-12">
            <img src={avatar} alt="Avatar" className="w-24 h-24 rounded-3xl object-cover" style={{ border: '4px solid var(--surface)', boxShadow: 'var(--shadow-md)' }} />
            <div className="pb-1">
              <h1 className="text-xl font-extrabold">{profile?.full_name || fullName}</h1>
              <p className="text-xs mt-0.5" style={{ color: 'var(--muted)' }}>{profile?.degree || degree} in {profile?.field_of_study || fieldOfStudy}</p>
              <div className="flex flex-wrap items-center gap-3 text-xs mt-2" style={{ color: 'var(--muted)' }}>
                <span className="flex items-center gap-1"><GraduationCap className="w-3.5 h-3.5" style={{ color: 'var(--primary)' }} /> {profile?.university || university || '—'}</span>
                <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" style={{ color: 'var(--danger)' }} /> {profile?.location || location || '—'}</span>
              </div>
            </div>
          </div>
          <button onClick={() => setEditing(!editing)} className="btn btn-ghost text-xs self-start sm:self-auto">
            <Edit3 className="w-3.5 h-3.5" /> {editing ? 'Cancel' : 'Edit profile'}
          </button>
        </div>
      </div>

      {/* Skills quick view */}
      {profile?.skills && profile.skills.length > 0 && (
        <div className="card p-6">
          <h3 className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--muted)' }}>Top skills</h3>
          <div className="flex flex-wrap gap-2">
            {profile.skills.map((sk) => (
              <span key={sk.id} className="chip" style={{ background: 'var(--primary-soft)', color: 'var(--primary)', borderColor: 'transparent' }}>
                {sk.skill_name} <span style={{ color: 'var(--muted)' }}>· {sk.proficiency_level}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Editable form */}
      <form onSubmit={handleSaveProfile} className="card p-6 space-y-6">
        <FormSection title="Personal information" icon={User}>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField label="Full name" value={fullName} onChange={setFullName} editing={editing} />
            <FormField label="Phone" value={phone} onChange={setPhone} editing={editing} />
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>Bio</label>
            <textarea rows={3} disabled={!editing} value={bio} onChange={(e) => setBio(e.target.value)} className="textarea disabled:opacity-60" placeholder="Tell recruiters about yourself…" />
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>Gender <span className="font-normal" style={{ color: 'var(--muted-2)' }}>(determines your avatar)</span></label>
            <select disabled={!editing} value={gender} onChange={(e) => setGender(e.target.value)} className="select disabled:opacity-60">
              <option value="">Prefer not to say</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
              <option value="prefer_not_to_say">Prefer not to say</option>
            </select>
          </div>
        </FormSection>

        <FormSection title="Academic background" icon={GraduationCap}>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <FormField label="University" value={university} onChange={setUniversity} editing={editing} />
            <FormField label="Degree" value={degree} onChange={setDegree} editing={editing} />
            <FormField label="Field of study" value={fieldOfStudy} onChange={setFieldOfStudy} editing={editing} />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>Preferred mode</label>
              <select disabled={!editing} value={preferredMode} onChange={(e) => setPreferredMode(e.target.value)} className="select disabled:opacity-60">
                <option>Remote</option><option>Hybrid</option><option>In-Office</option>
              </select>
            </div>
            <FormField label="Expected stipend" value={expectedStipend} onChange={setExpectedStipend} editing={editing} placeholder="₹35,000 / month" />
          </div>
        </FormSection>

        <FormSection title="Links & documents" icon={Globe}>
          <FormField label="Portfolio URL" value={portfolioUrl} onChange={setPortfolioUrl} editing={editing} placeholder="https://yourportfolio.dev" />
          <div>
            <p className="text-xs font-semibold mb-2" style={{ color: 'var(--text-soft)' }}>Uploaded documents (resume, cover letter, etc.)</p>
            <input
              ref={docInputRef}
              type="file"
              accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              className="hidden"
              onChange={(e) => { const f = e.target.files?.[0]; if (f) handleUploadDoc(f); e.target.value = ''; }}
            />
            <button
              type="button"
              onClick={() => docInputRef.current?.click()}
              disabled={uploading}
              className="w-full px-4 py-3 rounded-xl flex items-center gap-3 text-left transition disabled:opacity-50"
              style={{ border: '1.5px dashed var(--border-strong)', background: 'var(--surface-2)' }}
            >
              <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: 'var(--primary-soft)', color: 'var(--primary)' }}>
                <Upload className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-bold">{uploading ? 'Uploading…' : 'Upload a document'}</p>
                <p className="text-[10px]" style={{ color: 'var(--muted)' }}>PDF or Word · stored to your profile · max 8 MB</p>
              </div>
            </button>
            {documents.length > 0 && (
              <div className="space-y-2 mt-3">
                {documents.map((doc) => (
                  <div key={doc.id} className="p-3 rounded-xl flex items-center justify-between gap-3" style={{ background: 'var(--surface-2)', border: '1px solid var(--border)' }}>
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: 'var(--danger-soft)', color: 'var(--danger)' }}>
                        <FileText className="w-4 h-4" />
                      </div>
                      <div className="min-w-0">
                        <div className="text-xs font-bold truncate">{doc.file_name}</div>
                        <div className="text-[10px]" style={{ color: 'var(--muted)' }}>{doc.document_type}{doc.file_size ? ` · ${fmtSize(doc.file_size)}` : ''} · {new Date(doc.uploaded_at).toLocaleDateString()}</div>
                      </div>
                    </div>
                    <button type="button" onClick={() => handleDeleteDoc(doc.id)} className="w-7 h-7 rounded-lg flex items-center justify-center transition" style={{ color: 'var(--muted-2)' }}>
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </FormSection>

        {editing && (
          <div className="flex justify-end pt-2" style={{ borderTop: '1px solid var(--border)' }}>
            <button type="submit" disabled={saving} className="btn btn-primary">
              {saving ? 'Saving…' : <><Save className="w-4 h-4" /> Save changes</>}
            </button>
          </div>
        )}
      </form>
    </div>
  );
};

const FormSection: React.FC<{ title: string; icon: React.ElementType; children: React.ReactNode }> = ({ title, icon: Icon, children }) => (
  <div className="space-y-4">
    <h3 className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 pb-2" style={{ color: 'var(--muted)', borderBottom: '1px solid var(--border)' }}>
      <Icon className="w-3.5 h-3.5" /> {title}
    </h3>
    {children}
  </div>
);

const FormField: React.FC<{ label: string; value: string; onChange: any; editing: boolean; placeholder?: string }> = ({ label, value, onChange, editing, placeholder }) => (
  <div>
    <label className="block text-xs font-semibold mb-1.5" style={{ color: 'var(--text-soft)' }}>{label}</label>
    <input type="text" disabled={!editing} value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} className="input disabled:opacity-60" />
  </div>
);
