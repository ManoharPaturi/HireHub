import React, { useState } from 'react';
import { recruiterService } from '../../services/api';
import { Internship } from '../../types';
import { MapPin, Monitor, Clock, Wallet, FileText, Users, Trash2, Plus, ExternalLink } from 'lucide-react';

interface Props {
  internships: Internship[];
  onRefresh: () => void;
  onNavigate: (page: any) => void;
}

export const ManageInternships: React.FC<Props> = ({ internships, onRefresh, onNavigate }) => {
  const [filter, setFilter] = useState<'all' | 'active' | 'closed'>('all');
  const [deleting, setDeleting] = useState<number | null>(null);
  const [toggling, setToggling] = useState<number | null>(null);

  const filtered = internships.filter((i) => {
    if (filter === 'active') return i.is_active;
    if (filter === 'closed') return !i.is_active;
    return true;
  });

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this internship? All its applications will be removed.')) return;
    setDeleting(id);
    try { await recruiterService.deleteInternship(id); onRefresh(); }
    catch { alert('Failed to delete.'); }
    finally { setDeleting(null); }
  };

  const handleToggle = async (id: number) => {
    setToggling(id);
    try { await recruiterService.toggleInternship(id); onRefresh(); }
    catch { alert('Failed to update status.'); }
    finally { setToggling(null); }
  };

  const tabs = [
    { id: 'all' as const, label: 'All', count: internships.length },
    { id: 'active' as const, label: 'Active', count: internships.filter((i) => i.is_active).length },
    { id: 'closed' as const, label: 'Closed', count: internships.filter((i) => !i.is_active).length },
  ];

  return (
    <div className="max-w-5xl space-y-5">
      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex gap-1.5 p-1 rounded-xl" style={{ background: 'var(--surface-2)' }}>
          {tabs.map((t) => (
            <button key={t.id} onClick={() => setFilter(t.id)} className="px-4 py-1.5 rounded-lg text-sm font-semibold transition flex items-center gap-1.5"
              style={filter === t.id ? { background: 'var(--surface)', color: 'var(--primary)', boxShadow: 'var(--shadow-sm)' } : { color: 'var(--muted)' }}>
              {t.label} <span className="text-xs opacity-70">({t.count})</span>
            </button>
          ))}
        </div>
        <button onClick={() => onNavigate('post')} className="btn btn-primary text-xs self-start sm:self-auto">
          <Plus className="w-4 h-4" /> Post new
        </button>
      </div>

      {filtered.length === 0 ? (
        <div className="card p-16 text-center">
          <div className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-3" style={{ background: 'var(--surface-2)' }}><FileText className="w-7 h-7" style={{ color: 'var(--muted-2)' }} /></div>
          <p className="text-sm font-semibold">No internships here</p>
          <p className="text-xs mt-1" style={{ color: 'var(--muted)' }}>Post your first role to get started.</p>
          <button onClick={() => onNavigate('post')} className="btn btn-primary text-xs mt-4 mx-auto"><Plus className="w-4 h-4" /> Post internship</button>
        </div>
      ) : (
        <div className="space-y-3 stagger">
          {filtered.map((item) => (
            <div key={item.id} className="card p-5">
              <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <h4 className="font-bold text-base">{item.title}</h4>
                    <span className="badge" style={item.is_active ? { background: 'var(--success-soft)', color: 'var(--success)' } : { background: 'var(--surface-3)', color: 'var(--muted-2)' }}>
                      {item.is_active ? '● Active' : '○ Closed'}
                    </span>
                    {item.is_external && <span className="badge" style={{ background: 'var(--warning-soft)', color: 'var(--warning)' }}><ExternalLink className="w-3 h-3" /> External</span>}
                  </div>
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs" style={{ color: 'var(--muted)' }}>
                    <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {item.location}</span>
                    <span className="flex items-center gap-1"><Monitor className="w-3.5 h-3.5" /> {item.mode}</span>
                    <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {item.duration}</span>
                    <span className="flex items-center gap-1 font-semibold" style={{ color: 'var(--success)' }}><Wallet className="w-3.5 h-3.5" /> {item.stipend_currency}{item.stipend_amount.toLocaleString()}/mo</span>
                    <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5" /> {item.applications_count ?? 0} apps</span>
                    {item.deadline && <span className="flex items-center gap-1">⏰ {new Date(item.deadline).toLocaleDateString()}</span>}
                  </div>
                  {item.skills_required && (
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {item.skills_required.split(',').slice(0, 5).map((s, i) => <span key={i} className="chip">{s.trim()}</span>)}
                    </div>
                  )}
                </div>
                <div className="flex lg:flex-col gap-2 flex-shrink-0">
                  <button onClick={() => handleToggle(item.id)} disabled={toggling === item.id} className="btn btn-ghost text-xs flex-1 lg:flex-none">
                    {toggling === item.id ? '…' : item.is_active ? 'Close' : 'Reopen'}
                  </button>
                  <button onClick={() => onNavigate('applicants')} className="btn btn-soft text-xs flex-1 lg:flex-none">
                    Applicants
                  </button>
                  <button onClick={() => handleDelete(item.id)} disabled={deleting === item.id} className="btn btn-danger-soft text-xs flex-1 lg:flex-none">
                    <Trash2 className="w-3.5 h-3.5" /> {deleting === item.id ? '…' : 'Delete'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
