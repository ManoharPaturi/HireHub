import React, { useEffect, useState } from 'react';
import { Internship } from '../../types';
import { internshipService } from '../../services/api';
import { InternshipCard } from './InternshipCard';
import {
  SlidersHorizontal, LayoutGrid, List, RotateCcw, MapPin, Briefcase,
  ArrowUpDown, ChevronLeft, ChevronRight, Search,
} from 'lucide-react';

interface InternshipListingsProps {
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  onViewDetails: (internship: Internship) => void;
  onApply: (internship: Internship) => void;
}

const FILTER_SKILLS = ['React.js', 'TypeScript', 'Python', 'FastAPI', 'Figma', 'Data Analysis'];
const LOCATIONS = ['All', 'San Francisco, CA', 'New York, NY', 'Remote', 'Boston, MA'];
const MODES = ['All', 'Remote', 'In-Office', 'Hybrid'];

export const InternshipListings: React.FC<InternshipListingsProps> = ({
  searchQuery,
  setSearchQuery,
  onViewDetails,
  onApply,
}) => {
  const [internships, setInternships] = useState<Internship[]>([]);
  const [loading, setLoading] = useState(true);

  const [selectedLocation, setSelectedLocation] = useState('All');
  const [selectedMode, setSelectedMode] = useState('All');
  const [minStipend, setMinStipend] = useState<number>(0);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState('newest');

  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [page, setPage] = useState(1);

  const fetchInternships = async () => {
    setLoading(true);
    try {
      const data = await internshipService.getInternships({
        search: searchQuery || undefined,
        location: selectedLocation !== 'All' ? selectedLocation : undefined,
        mode: selectedMode !== 'All' ? selectedMode : undefined,
        min_stipend: minStipend > 0 ? minStipend : undefined,
        skills: selectedSkills.length > 0 ? selectedSkills.join(',') : undefined,
        sort_by: sortBy,
        page,
        limit: 12,
      });
      setInternships(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInternships();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchQuery, selectedLocation, selectedMode, minStipend, selectedSkills, sortBy, page]);

  const toggleSkillFilter = (skill: string) =>
    setSelectedSkills((prev) => (prev.includes(skill) ? prev.filter((s) => s !== skill) : [...prev, skill]));

  const handleToggleSave = async (id: number) => {
    try {
      const res = await internshipService.toggleSave(id);
      setInternships((prev) => prev.map((item) => (item.id === id ? { ...item, is_saved: res.saved } : item)));
    } catch (e) { console.error(e); }
  };

  const resetFilters = () => {
    setSelectedLocation('All'); setSelectedMode('All'); setMinStipend(0);
    setSelectedSkills([]); setSearchQuery(''); setSortBy('newest'); setPage(1);
  };

  const activeFilterCount =
    (selectedLocation !== 'All' ? 1 : 0) + (selectedMode !== 'All' ? 1 : 0) +
    (minStipend > 0 ? 1 : 0) + selectedSkills.length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      {/* Header banner */}
      <div className="card p-6 sm:p-7 relative overflow-hidden animate-rise">
        <div className="absolute -right-10 -top-10 w-48 h-48 rounded-full blur-3xl" style={{ background: 'var(--primary-soft)' }} />
        <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <span className="eyebrow">Verified opportunities</span>
            <h1 className="mt-1 text-2xl sm:text-3xl font-extrabold tracking-tight">Explore internships</h1>
            <p className="text-sm mt-1.5" style={{ color: 'var(--muted)' }}>
              Filter by tech stack, stipend, and work mode to find your ideal role.
            </p>
          </div>
          <div className="flex items-center gap-1 p-1 rounded-xl self-start md:self-auto" style={{ background: 'var(--surface-2)' }}>
            <button onClick={() => setViewMode('grid')} className="px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition" style={viewMode === 'grid' ? { background: 'var(--surface)', color: 'var(--primary)', boxShadow: 'var(--shadow-sm)' } : { color: 'var(--muted)' }}>
              <LayoutGrid className="w-4 h-4" /> Grid
            </button>
            <button onClick={() => setViewMode('list')} className="px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition" style={viewMode === 'list' ? { background: 'var(--surface)', color: 'var(--primary)', boxShadow: 'var(--shadow-sm)' } : { color: 'var(--muted)' }}>
              <List className="w-4 h-4" /> List
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filters sidebar */}
        <aside className="lg:col-span-1 space-y-5">
          <div className="card p-5 lg:sticky lg:top-20">
            <div className="flex items-center justify-between pb-3" style={{ borderBottom: '1px solid var(--border)' }}>
              <h3 className="font-bold text-sm flex items-center gap-2"><SlidersHorizontal className="w-4 h-4" style={{ color: 'var(--primary)' }} /> Filters {activeFilterCount > 0 && <span className="badge ml-1" style={{ background: 'var(--primary-soft)', color: 'var(--primary)' }}>{activeFilterCount}</span>}</h3>
              {activeFilterCount > 0 && (
                <button onClick={resetFilters} className="text-xs font-semibold flex items-center gap-1 transition" style={{ color: 'var(--primary)' }} onMouseEnter={(e) => { e.currentTarget.style.opacity = '0.7'; }} onMouseLeave={(e) => { e.currentTarget.style.opacity = '1'; }}>
                  <RotateCcw className="w-3 h-3" /> Reset
                </button>
              )}
            </div>

            {/* Sort */}
            <div className="mt-4">
              <label className="text-xs font-bold uppercase block mb-2 flex items-center gap-1" style={{ color: 'var(--muted)' }}>
                <ArrowUpDown className="w-3.5 h-3.5" /> Sort by
              </label>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="select">
                <option value="newest">Newest first</option>
                <option value="stipend_desc">Stipend: high to low</option>
                <option value="deadline_asc">Earliest deadline</option>
              </select>
            </div>

            {/* Mode */}
            <div className="mt-5">
              <label className="text-xs font-bold uppercase block mb-2" style={{ color: 'var(--muted)' }}>Work mode</label>
              <div className="grid grid-cols-2 gap-1.5">
                {MODES.map((m) => (
                  <button key={m} onClick={() => setSelectedMode(m)} className="py-1.5 px-2 rounded-lg text-xs font-medium transition"
                    style={selectedMode === m ? { background: 'var(--primary)', color: '#fff' } : { background: 'var(--surface-2)', color: 'var(--text-soft)', border: '1px solid var(--border)' }}>
                    {m}
                  </button>
                ))}
              </div>
            </div>

            {/* Stipend */}
            <div className="mt-5">
              <div className="flex items-center justify-between text-xs font-bold mb-2">
                <span className="uppercase" style={{ color: 'var(--muted)' }}>Min stipend</span>
                <span style={{ color: 'var(--primary)' }}>{internships[0]?.stipend_currency || '₹'}{minStipend.toLocaleString()}+</span>
              </div>
              <input type="range" min="0" max="60000" step="5000" value={minStipend} onChange={(e) => setMinStipend(Number(e.target.value))} className="w-full cursor-pointer" style={{ accentColor: 'var(--primary)' }} />
            </div>

            {/* Skills */}
            <div className="mt-5">
              <label className="text-xs font-bold uppercase block mb-2" style={{ color: 'var(--muted)' }}>Skills</label>
              <div className="flex flex-wrap gap-1.5">
                {FILTER_SKILLS.map((sk) => {
                  const sel = selectedSkills.includes(sk);
                  return (
                    <button key={sk} onClick={() => toggleSkillFilter(sk)} className="px-2.5 py-1 rounded-lg text-xs font-medium transition"
                      style={sel ? { background: 'var(--primary)', color: '#fff' } : { background: 'var(--surface-2)', color: 'var(--text-soft)', border: '1px solid var(--border)' }}>
                      {sk}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Location */}
            <div className="mt-5">
              <label className="text-xs font-bold uppercase block mb-2 flex items-center gap-1" style={{ color: 'var(--muted)' }}>
                <MapPin className="w-3.5 h-3.5" /> Location
              </label>
              <select value={selectedLocation} onChange={(e) => setSelectedLocation(e.target.value)} className="select">
                {LOCATIONS.map((loc) => <option key={loc} value={loc}>{loc}</option>)}
              </select>
            </div>
          </div>
        </aside>

        {/* Results */}
        <div className="lg:col-span-3 space-y-4">
          <div className="flex items-center justify-between text-xs px-1" style={{ color: 'var(--muted)' }}>
            <span>
              {loading ? 'Searching…' : <>Showing <strong style={{ color: 'var(--text)' }}>{internships.length}</strong> position{internships.length !== 1 ? 's' : ''}</>}
            </span>
            <span className="hidden sm:flex items-center gap-1.5"><Briefcase className="w-3.5 h-3.5" /> Page {page}</span>
          </div>

          {loading ? (
            <div className={`grid gap-4 ${viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-1'}`}>
              {[1, 2, 3, 4].map((n) => (
                <div key={n} className="card p-5 space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="w-11 h-11 rounded-xl skeleton" />
                    <div className="space-y-2 flex-1">
                      <div className="h-2.5 w-1/3 skeleton" />
                      <div className="h-3.5 w-2/3 skeleton" />
                    </div>
                  </div>
                  <div className="h-12 skeleton" />
                  <div className="h-8 skeleton" />
                </div>
              ))}
            </div>
          ) : internships.length === 0 ? (
            <div className="card p-12 text-center space-y-3">
              <div className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto" style={{ background: 'var(--surface-2)' }}>
                <Search className="w-7 h-7" style={{ color: 'var(--muted-2)' }} />
              </div>
              <h3 className="font-bold">No matching internships</h3>
              <p className="text-xs max-w-sm mx-auto" style={{ color: 'var(--muted)' }}>Try adjusting your search criteria or resetting filters to see more results.</p>
              <button onClick={resetFilters} className="btn btn-primary text-xs mx-auto">Reset filters</button>
            </div>
          ) : (
            <div className={`grid gap-4 ${viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-1'} stagger`}>
              {internships.map((item) => (
                <InternshipCard key={item.id} internship={item} onViewDetails={onViewDetails} onToggleSave={handleToggleSave} onApply={onApply} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {!loading && internships.length > 0 && (
            <div className="flex items-center justify-center gap-2 pt-4">
              <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)} className="btn btn-ghost text-xs disabled:opacity-40">
                <ChevronLeft className="w-4 h-4" /> Prev
              </button>
              <span className="px-3 py-1.5 rounded-lg text-xs font-bold" style={{ background: 'var(--primary-soft)', color: 'var(--primary)' }}>Page {page}</span>
              <button disabled={internships.length < 12} onClick={() => setPage((p) => p + 1)} className="btn btn-ghost text-xs disabled:opacity-40">
                Next <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
