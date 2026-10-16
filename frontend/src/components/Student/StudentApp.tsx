/*
 * Student workspace shell. The selected tab chooses the dashboard, listings,
 * bookmarks, tracker, messages or profile. A shared detail modal submits
 * applications and triggers refetching of internship-related screens.
 */

import React, { useState } from 'react';
import { Navbar } from '../Layout/Navbar';
import { StudentDashboard } from '../Dashboard/StudentDashboard';
import { InternshipListings } from '../Internships/InternshipListings';
import { InternshipDetailModal } from '../Internships/InternshipDetailModal';
import { ApplicationTracker } from '../Tracker/ApplicationTracker';
import { SavedInternships } from '../Tracker/SavedInternships';
import { ProfileView } from '../Profile/ProfileView';
import { MessagesView } from '../Messages/MessagesView';
import { Internship } from '../../types';
import { applicationService } from '../../services/api';
import { Briefcase } from 'lucide-react';

export const StudentApp: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'internships' | 'tracker' | 'saved' | 'messages' | 'profile'>('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedInternship, setSelectedInternship] = useState<Internship | null>(null);
  // Bumped after a successful apply so list views refetch and show fresh applied/saved state.
  const [refreshKey, setRefreshKey] = useState(0);

  const handleViewDetails = (internship: Internship) => setSelectedInternship(internship);

  // Wait for the multipart submission to succeed before changing refreshKey.
  // A changed React key remounts listing/dashboard views and fetches fresh flags.
  const handleApplySubmit = async (internshipId: number, coverLetter: string, resume?: File | null) => {
    await applicationService.submitApplication(internshipId, coverLetter, resume ?? undefined);
    setRefreshKey((k) => k + 1);
  };

  // The student workspace is already authenticated, so this callback is a no-op.
  const handleOpenAuth = () => {};

  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'var(--bg)', color: 'var(--text)' }}>
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onOpenAuth={handleOpenAuth}
      />

      <main className="flex-1">
        {activeTab === 'dashboard' && (
          <StudentDashboard key={refreshKey} onNavigate={setActiveTab} onViewDetails={handleViewDetails} onApply={handleViewDetails} />
        )}
        {activeTab === 'internships' && (
          <InternshipListings key={refreshKey} searchQuery={searchQuery} setSearchQuery={setSearchQuery} onViewDetails={handleViewDetails} onApply={handleViewDetails} />
        )}
        {activeTab === 'saved' && <SavedInternships key={refreshKey} onViewDetails={handleViewDetails} onApply={handleViewDetails} />}
        {activeTab === 'tracker' && <ApplicationTracker />}
        {activeTab === 'messages' && <MessagesView />}
        {activeTab === 'profile' && <ProfileView />}
      </main>

      <footer style={{ borderTop: '1px solid var(--border)', background: 'var(--surface)' }}>
        <div className="max-w-7xl mx-auto px-4 py-6 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center text-white" style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent))' }}>
              <Briefcase className="w-3.5 h-3.5" />
            </div>
            <span className="text-xs font-semibold">HireHub</span>
            <span className="text-xs" style={{ color: 'var(--muted-2)' }}>· © 2026 · Where careers begin.</span>
          </div>
          <div className="flex items-center gap-4 text-xs" style={{ color: 'var(--muted)' }}>
            <span className="cursor-pointer transition hover:opacity-70">Privacy</span>
            <span className="cursor-pointer transition hover:opacity-70">Terms</span>
            <span className="cursor-pointer transition hover:opacity-70">Support</span>
          </div>
        </div>
      </footer>

      <InternshipDetailModal internship={selectedInternship} onClose={() => setSelectedInternship(null)} onApplySubmit={handleApplySubmit} />
    </div>
  );
};
