/*
 * TypeScript response shapes used by screens and API services. These types
 * help the compiler check object fields; they do not create database tables
 * or validate HTTP data at runtime. Names correspond to backend response schemas.
 */

// A catalog skill, independent of any individual student.
export interface Skill { id: number; name: string; category?: string; }
// A student/skill link with the display name and proficiency level.
export interface StudentSkill { id: number; skill_id: number; skill_name: string; proficiency_level: string; }
// Upload metadata only; file contents are fetched separately.
export interface Document {
  id: number; document_type: string; file_name: string; file_url?: string;
  content_type?: string; file_size?: number; uploaded_at: string; has_file?: boolean;
}

export type Gender = 'male' | 'female' | 'other' | 'prefer_not_to_say';

// Saved academic/contact details plus nested skills and document metadata.
export interface StudentProfile {
  id: number; user_id: number; email: string; full_name: string; phone?: string;
  avatar_url?: string; gender?: string;
  university?: string; degree?: string; field_of_study?: string;
  graduation_year?: number; cgpa?: number; bio?: string; location?: string;
  preferred_mode?: string; expected_stipend?: string; portfolio_url?: string;
  github_url?: string; linkedin_url?: string; skills: StudentSkill[]; documents: Document[];
}

// Company/contact details owned by a recruiter account.
export interface RecruiterProfile {
  id: number; user_id: number; email: string; full_name: string; company_name: string;
  company_logo?: string; designation?: string; phone?: string; company_website?: string;
  company_size?: string; industry?: string; bio?: string; linkedin_url?: string; location?: string;
}

// Recruiter dashboard totals returned by the API.
export interface RecruiterStats {
  active_posts: number; total_applications: number; shortlisted: number;
  interviews_scheduled: number; total_accepted: number;
}

// Posting data plus optional account-specific bookmark/application flags.
export interface Internship {
  id: number; title: string; company_name: string; company_logo?: string;
  location: string; mode: string; stipend_amount: number; stipend_currency: string;
  duration: string; description: string; eligibility?: string; responsibilities?: string;
  benefits?: string; recruiter_name?: string; recruiter_email?: string; recruiter_title?: string;
  skills_required?: string; is_external: boolean; external_link?: string;
  is_active?: boolean; deadline?: string; created_at: string;
  is_saved?: boolean; has_applied?: boolean; applications_count?: number;
}

// Student tracker record with the associated internship nested inside it.
export interface Application {
  id: number; student_id: number; internship_id: number;
  status: 'Applied' | 'Under Review' | 'Shortlisted' | 'Interview Scheduled' | 'Accepted' | 'Rejected';
  cover_letter?: string; resume_url?: string; applied_at: string;
  recruiter_notes?: string; internship: Internship;
}

// Expanded candidate information prepared for recruiter review.
export interface RecruiterApplication {
  id: number; student_id: number; student_user_id?: number; internship_id: number; status: string;
  cover_letter?: string; resume_url?: string; resume_filename?: string; has_resume?: boolean;
  applied_at: string; recruiter_notes?: string;
  student_name: string; student_email: string;
  student_phone?: string; student_avatar?: string; student_bio?: string;
  student_university?: string; student_degree?: string; student_field_of_study?: string;
  student_cgpa?: number; student_location?: string; student_portfolio?: string;
  student_linkedin?: string; student_skills?: string;
  internship_title: string;
}

// Meeting details with optional candidate/posting display names.
export interface Interview {
  id: number; recruiter_id: number; application_id: number; internship_id?: number;
  scheduled_at: string; duration_minutes: number; interview_type: string;
  meeting_link?: string; notes?: string; status: string; created_at: string;
  candidate_name?: string; internship_title?: string;
}

// An account-owned alert; is_read controls unread badges.
export interface NotificationItem {
  id: number; title: string; message: string;
  type: 'info' | 'application' | 'recommendation' | 'alert' | 'message';
  is_read: boolean; created_at: string;
}

// A directed message; IDs refer to accounts in the users table.
export interface ChatMessage {
  id: number; sender_id: number; receiver_id: number;
  content: string; is_read: boolean; sent_at: string;
}

// One permitted conversation partner, with preview and unread count.
export interface MessageContact {
  user_id: number;
  full_name: string;
  avatar_url?: string;
  subtitle?: string;
  internship_id?: number;
  internship_title?: string;
  last_message?: string;
  last_at?: string;
  unread?: number;
}

export type UserRole = 'student' | 'recruiter' | 'admin';

// ── Admin ─────────────────────────────────────────────────────────────────────
// Platform-wide counts and stipend summary for the administrator.
export interface AdminStats {
  total_students: number; total_recruiters: number;
  total_internships: number; active_internships: number;
  total_applications: number; total_interviews: number; total_messages: number;
  avg_stipend: number; new_users_week: number; new_apps_week: number;
}

// Grouped labels and values, already aggregated by backend queries.
export interface AdminChartData {
  applications_timeline: { date: string; count: number }[];
  by_status: { label: string; value: number; color: string }[];
  by_mode: { label: string; value: number; color: string }[];
  top_universities: { label: string; value: number }[];
  top_fields: { label: string; value: number }[];
  top_companies: { label: string; value: number }[];
}

// Management-list identity with role-specific optional profile details.
export interface AdminUser {
  id: number; email: string; role: 'student' | 'recruiter'; is_active: boolean; created_at: string;
  full_name?: string; avatar_url?: string;
  university?: string; field?: string; applications?: number;
  company?: string; designation?: string; internships?: number;
}

// Posting summary enriched with an application count for admin review.
export interface AdminInternship {
  id: number; title: string; company_name: string; location: string; mode: string;
  stipend_amount: number; stipend_currency: string; duration: string;
  is_active: boolean; is_external: boolean; deadline?: string; created_at: string;
  recruiter_name?: string; applications: number;
}

// Read-only recent application summary with candidate and posting labels.
export interface AdminApplication {
  id: number; student_name: string; student_email?: string;
  internship_title: string; company_name: string;
  status: string; applied_at: string; has_resume: boolean;
}

// A display event assembled from existing records, not a durable audit log.
export interface AdminActivityItem {
  type: 'application' | 'internship' | 'user' | 'interview';
  actor: string;
  detail: string;
  at: string;
}
