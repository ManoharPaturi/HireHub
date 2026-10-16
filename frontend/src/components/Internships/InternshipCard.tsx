import React from 'react';
import { Internship } from '../../types';
import { MapPin, Calendar, Wallet, Bookmark, ExternalLink, ArrowUpRight, Clock } from 'lucide-react';

interface InternshipCardProps {
  internship: Internship;
  onViewDetails: (internship: Internship) => void;
  onToggleSave: (id: number) => void;
  onApply: (internship: Internship) => void;
}

const FALLBACK_LOGO = 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=120&q=80';

export const InternshipCard: React.FC<InternshipCardProps> = ({
  internship,
  onViewDetails,
  onToggleSave,
  onApply,
}) => {
  const skillsList = internship.skills_required ? internship.skills_required.split(',').map((s) => s.trim()).filter(Boolean) : [];

  const modeStyle: Record<string, React.CSSProperties> = {
    Remote: { background: 'var(--success-soft)', color: 'var(--success)' },
    Hybrid: { background: 'var(--warning-soft)', color: 'var(--warning)' },
    'In-Office': { background: 'var(--primary-soft)', color: 'var(--primary)' },
  };

  const deadline = internship.deadline ? new Date(internship.deadline) : null;
  const daysLeft = deadline ? Math.max(0, Math.ceil((deadline.getTime() - Date.now()) / 86400000)) : null;

  return (
    <div className="card card-hover p-5 flex flex-col h-full group">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-3 min-w-0">
          <img
            src={internship.company_logo || FALLBACK_LOGO}
            alt={internship.company_name}
            className="w-11 h-11 rounded-xl object-cover flex-shrink-0"
            style={{ border: '1px solid var(--border)' }}
          />
          <div className="min-w-0">
            <div className="text-xs font-bold uppercase tracking-wide" style={{ color: 'var(--muted)' }}>{internship.company_name}</div>
            <h3
              onClick={() => onViewDetails(internship)}
              className="font-bold text-[15px] leading-snug cursor-pointer line-clamp-1 transition-colors"
              style={{ color: 'var(--text)' }}
              onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--primary)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text)'; }}
            >
              {internship.title}
            </h3>
          </div>
        </div>
        <button
          onClick={() => onToggleSave(internship.id)}
          className="w-9 h-9 rounded-xl flex items-center justify-center transition flex-shrink-0"
          style={internship.is_saved ? { background: 'var(--warning-soft)', color: 'var(--warning)' } : { background: 'var(--surface-2)', color: 'var(--muted-2)', border: '1px solid var(--border)' }}
          aria-label={internship.is_saved ? 'Remove bookmark' : 'Save internship'}
          title={internship.is_saved ? 'Saved' : 'Save'}
        >
          <Bookmark className={`w-4 h-4 ${internship.is_saved ? 'fill-current' : ''}`} />
        </button>
      </div>

      {/* Meta badges */}
      <div className="flex flex-wrap items-center gap-1.5 mb-3">
        <span className="badge" style={modeStyle[internship.mode] || modeStyle['In-Office']}>{internship.mode}</span>
        {daysLeft !== null && (
          <span className="badge" style={{ background: 'var(--surface-2)', color: 'var(--muted)' }}>
            <Clock className="w-3 h-3" /> {daysLeft}d left
          </span>
        )}
        {internship.is_external && (
          <span className="badge" style={{ background: 'var(--warning-soft)', color: 'var(--warning)' }}>
            <ExternalLink className="w-3 h-3" /> External
          </span>
        )}
      </div>

      {/* Meta row */}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs mb-3" style={{ color: 'var(--muted)' }}>
        <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" style={{ color: 'var(--muted-2)' }} /> {internship.location}</span>
        <span className="flex items-center gap-1 font-semibold" style={{ color: 'var(--success)' }}>
          <Wallet className="w-3.5 h-3.5" /> {internship.stipend_currency}{internship.stipend_amount.toLocaleString()}/mo
        </span>
        <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5" style={{ color: 'var(--muted-2)' }} /> {internship.duration}</span>
      </div>

      {/* Description */}
      <p className="text-xs leading-relaxed mb-4 line-clamp-2 flex-1" style={{ color: 'var(--text-soft)' }}>
        {internship.description}
      </p>

      {/* Skills */}
      {skillsList.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-4">
          {skillsList.slice(0, 4).map((sk, idx) => (
            <span key={idx} className="chip">{sk}</span>
          ))}
          {skillsList.length > 4 && <span className="chip" style={{ color: 'var(--primary)' }}>+{skillsList.length - 4}</span>}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between gap-2 pt-3" style={{ borderTop: '1px solid var(--border)' }}>
        <button onClick={() => onViewDetails(internship)} className="btn btn-ghost text-xs">
          Details
        </button>
        {internship.has_applied ? (
          <span className="badge px-3 py-2" style={{ background: 'var(--success-soft)', color: 'var(--success)' }}>✓ Applied</span>
        ) : (
          <button onClick={() => onApply(internship)} className="btn btn-primary text-xs">
            {internship.is_external ? <>Apply <ExternalLink className="w-3.5 h-3.5" /></> : <>Apply now <ArrowUpRight className="w-3.5 h-3.5" /></>}
          </button>
        )}
      </div>
    </div>
  );
};
