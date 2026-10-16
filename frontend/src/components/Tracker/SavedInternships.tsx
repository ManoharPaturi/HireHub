import React, { useEffect, useState } from 'react';
import { Internship } from '../../types';
import { internshipService } from '../../services/api';
import { InternshipCard } from '../Internships/InternshipCard';
import { Bookmark, ArrowRight, Search } from 'lucide-react';

interface SavedInternshipsProps {
  onViewDetails: (internship: Internship) => void;
  onApply: (internship: Internship) => void;
}

export const SavedInternships: React.FC<SavedInternshipsProps> = ({ onViewDetails, onApply }) => {
  const [saved, setSaved] = useState<Internship[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch = async () => {
    setLoading(true);
    try { setSaved(await internshipService.getSaved()); }
    catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetch(); }, []);

  const handleToggleSave = async (id: number) => {
    try {
      const res = await internshipService.toggleSave(id);
      if (!res.saved) {
        // Removing from saved → drop it from the list immediately.
        setSaved((prev) => prev.filter((i) => i.id !== id));
      } else {
        setSaved((prev) => prev.map((i) => (i.id === id ? { ...i, is_saved: true } : i)));
      }
    } catch (e) { console.error(e); }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <div className="card p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-rise">
        <div>
          <span className="eyebrow">Bookmarks</span>
          <h1 className="mt-1 text-xl sm:text-2xl font-extrabold flex items-center gap-2">
            <Bookmark className="w-5 h-5" style={{ color: 'var(--primary)' }} /> Saved internships
          </h1>
          <p className="text-xs mt-1" style={{ color: 'var(--muted)' }}>Roles you've bookmarked — saved to your account and available anywhere.</p>
        </div>
        <div className="px-4 py-2.5 rounded-xl text-xs font-bold self-start" style={{ background: 'var(--primary-soft)', color: 'var(--primary)' }}>
          {saved.length} saved
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((n) => (
            <div key={n} className="card p-5 space-y-4">
              <div className="flex items-center gap-3"><div className="w-11 h-11 rounded-xl skeleton" /><div className="flex-1 space-y-2"><div className="h-2.5 w-1/3 skeleton" /><div className="h-3.5 w-2/3 skeleton" /></div></div>
              <div className="h-12 skeleton" />
            </div>
          ))}
        </div>
      ) : saved.length === 0 ? (
        <div className="card p-12 text-center space-y-3">
          <div className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto" style={{ background: 'var(--surface-2)' }}>
            <Search className="w-7 h-7" style={{ color: 'var(--muted-2)' }} />
          </div>
          <h3 className="font-bold">No saved internships yet</h3>
          <p className="text-xs max-w-sm mx-auto" style={{ color: 'var(--muted)' }}>
            Tap the bookmark icon on any internship to save it here. Saved roles stay with your account across devices.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 stagger">
          {saved.map((item) => (
            <InternshipCard key={item.id} internship={item} onViewDetails={onViewDetails} onToggleSave={handleToggleSave} onApply={onApply} />
          ))}
        </div>
      )}
    </div>
  );
};
