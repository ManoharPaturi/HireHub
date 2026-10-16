import axios from 'axios';
import {
  Internship, StudentProfile, RecruiterProfile, Application,
  RecruiterApplication, RecruiterStats, Interview, NotificationItem,
  Document, ChatMessage, MessageContact,
  AdminStats, AdminChartData, AdminUser, AdminInternship, AdminApplication, AdminActivityItem,
} from '../types';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

// NOTE: no instance-level Content-Type default. axios already sets
// application/json for plain-object bodies, and leaving FormData requests
// header-free lets the browser attach multipart/form-data; boundary=... —
// a pinned 'application/json' default here breaks every file upload (HTTP 422).
export const api = axios.create({ baseURL: API_BASE_URL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt_token');
  if (token && config.headers) config.headers.Authorization = `Bearer ${token}`;
  return config;
}, (error) => Promise.reject(error));

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authService = {
  login: async (email: string, password: string, remember_me = false) => {
    const res = await api.post('/auth/login', { email, password, remember_me });
    if (res.data.access_token) {
      localStorage.setItem('jwt_token', res.data.access_token);
      localStorage.setItem('user_info', JSON.stringify(res.data));
    }
    return res.data;
  },
  register: async (payload: any) => {
    const res = await api.post('/auth/register', payload);
    if (res.data.access_token) {
      localStorage.setItem('jwt_token', res.data.access_token);
      localStorage.setItem('user_info', JSON.stringify(res.data));
    }
    return res.data;
  },
  forgotPassword: async (email: string) => (await api.post('/auth/forgot-password', { email })).data,
  logout: () => { localStorage.removeItem('jwt_token'); localStorage.removeItem('user_info'); },
  getMe: async () => (await api.get('/auth/me')).data,
};

// ── Student ───────────────────────────────────────────────────────────────────
export const studentService = {
  getProfile: async (): Promise<StudentProfile> => (await api.get('/students/profile')).data,
  updateProfile: async (data: any): Promise<StudentProfile> => (await api.put('/students/profile', data)).data,
  // Documents (#2)
  getDocuments: async (): Promise<Document[]> => (await api.get('/students/documents')).data,
  uploadDocument: async (file: File, document_type = 'resume'): Promise<Document> => {
    const form = new FormData();
    form.append('file', file);
    form.append('document_type', document_type);
    // The axios instance sets a default Content-Type: application/json (see
    // axios.create above). For FormData we must clear it so axios attaches the
    // correct multipart/form-data; boundary=... header automatically —
    // otherwise the server cannot parse the body (HTTP 422).
    const res = await api.post('/students/documents', form, { headers: { 'Content-Type': undefined } });
    return res.data;
  },
  getDocumentFile: async (id: number) =>
    (await api.get(`/students/documents/${id}`, { responseType: 'blob' })).data,
  deleteDocument: async (id: number) => (await api.delete(`/students/documents/${id}`)).data,
};

// ── Internships ───────────────────────────────────────────────────────────────
export const internshipService = {
  getInternships: async (params?: any): Promise<Internship[]> => (await api.get('/internships', { params })).data,
  getRecommendations: async (): Promise<Internship[]> => (await api.get('/internships/recommendations')).data,
  getSaved: async (): Promise<Internship[]> => (await api.get('/internships/saved')).data, // #3
  getInternshipDetail: async (id: number): Promise<Internship> => (await api.get(`/internships/${id}`)).data,
  toggleSave: async (id: number) => (await api.post(`/internships/${id}/save`)).data,
};

// ── Applications ──────────────────────────────────────────────────────────────
export const applicationService = {
  // #2: multipart submit with optional resume file
  submitApplication: async (internship_id: number, cover_letter: string, resume?: File | null): Promise<Application> => {
    const form = new FormData();
    form.append('internship_id', String(internship_id));
    if (cover_letter) form.append('cover_letter', cover_letter);
    if (resume) form.append('resume', resume);
    // Clear the instance default Content-Type so axios sets the correct
    // multipart/form-data; boundary=... header for the FormData body.
    const res = await api.post('/applications', form, { headers: { 'Content-Type': undefined } });
    return res.data;
  },
  getApplications: async (): Promise<Application[]> => (await api.get('/applications')).data,
  withdrawApplication: async (id: number) => (await api.delete(`/applications/${id}`)).data,
};

// ── Notifications ─────────────────────────────────────────────────────────────
export const notificationService = {
  getNotifications: async (): Promise<NotificationItem[]> => (await api.get('/notifications')).data,
  markRead: async (id: number) => (await api.put(`/notifications/${id}/read`)).data,
};

// ── Messages (student ↔ recruiter conversations) ──────────────────────────────
export const messageService = {
  // Role-aware: students get their recruiters, recruiters get their applicants.
  getContacts: async (): Promise<MessageContact[]> => (await api.get('/messages/contacts')).data,
  getMessages: async (other_user_id: number): Promise<ChatMessage[]> =>
    (await api.get('/messages', { params: { other_user_id } })).data,
  sendMessage: async (receiver_id: number, content: string): Promise<ChatMessage> =>
    (await api.post('/messages', { receiver_id, content })).data,
  getUnreadCount: async (): Promise<{ count: number }> => (await api.get('/messages/unread')).data,
};

// ── Recruiter ─────────────────────────────────────────────────────────────────
export const recruiterService = {
  getProfile: async (): Promise<RecruiterProfile> => (await api.get('/recruiter/profile')).data,
  updateProfile: async (data: any): Promise<RecruiterProfile> => (await api.put('/recruiter/profile', data)).data,
  getStats: async (): Promise<RecruiterStats> => (await api.get('/recruiter/stats')).data,
  // Internships
  postInternship: async (payload: any): Promise<Internship> => (await api.post('/recruiter/internships', payload)).data,
  getMyInternships: async (): Promise<Internship[]> => (await api.get('/recruiter/internships')).data,
  updateInternship: async (id: number, payload: any): Promise<Internship> =>
    (await api.put(`/recruiter/internships/${id}`, payload)).data,
  deleteInternship: async (id: number) => (await api.delete(`/recruiter/internships/${id}`)).data,
  toggleInternship: async (id: number) => (await api.put(`/recruiter/internships/${id}/toggle`)).data,
  // Applicants
  getApplicants: async (internship_id?: number): Promise<RecruiterApplication[]> =>
    (await api.get('/recruiter/applicants', { params: internship_id ? { internship_id } : {} })).data,
  updateApplicationStatus: async (id: number, status: string, notes?: string) =>
    (await api.put(`/recruiter/applications/${id}/status`, { status, recruiter_notes: notes })).data,
  // #7: secure resume access
  getResume: async (appId: number) => (await api.get(`/recruiter/applications/${appId}/resume`)).data,
  // Interviews
  scheduleInterview: async (payload: any): Promise<Interview> =>
    (await api.post('/recruiter/interviews', payload)).data,
  getInterviews: async (): Promise<Interview[]> => (await api.get('/recruiter/interviews')).data,
  // Notifications
  getNotifications: async (): Promise<NotificationItem[]> => (await api.get('/recruiter/notifications')).data,
};

// ── Admin (platform dashboard) ────────────────────────────────────────────────
export const adminService = {
  login: async (email: string, password: string) => {
    const res = await api.post('/admin/login', { email, password });
    if (res.data.access_token) {
      localStorage.setItem('jwt_token', res.data.access_token);
      localStorage.setItem('user_info', JSON.stringify(res.data));
    }
    return res.data;
  },
  getStats: async (): Promise<AdminStats> => (await api.get('/admin/stats')).data,
  getCharts: async (): Promise<AdminChartData> => (await api.get('/admin/charts')).data,
  // Users
  getUsers: async (params?: { role?: string; search?: string }): Promise<AdminUser[]> =>
    (await api.get('/admin/users', { params })).data,
  toggleUser: async (id: number) => (await api.put(`/admin/users/${id}/toggle-active`)).data,
  deleteUser: async (id: number) => (await api.delete(`/admin/users/${id}`)).data,
  // Internships
  getInternships: async (): Promise<AdminInternship[]> => (await api.get('/admin/internships')).data,
  toggleInternship: async (id: number) => (await api.put(`/admin/internships/${id}/toggle`)).data,
  deleteInternship: async (id: number) => (await api.delete(`/admin/internships/${id}`)).data,
  // Applications
  getApplications: async (limit = 100): Promise<AdminApplication[]> =>
    (await api.get('/admin/applications', { params: { limit } })).data,
  // Activity feed
  getActivity: async (limit = 40): Promise<AdminActivityItem[]> =>
    (await api.get('/admin/activity', { params: { limit } })).data,
};
