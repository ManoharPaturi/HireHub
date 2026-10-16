# API data contracts. Pydantic models describe incoming request fields and
# outgoing response fields; they are separate from the SQLAlchemy table models.
# Optional fields may be omitted. from_attributes allows responses to be built
# from ORM objects, including the related records requested by a response model.

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# ─────────────────────────────────────────────
# AUTH SCHEMAS
# ─────────────────────────────────────────────
# Registration fields shared across roles, with optional student/company details.
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Optional[str] = "student"
    # Student fields
    university: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None
    phone: Optional[str] = None
    preferred_mode: Optional[str] = "Remote"
    expected_stipend: Optional[str] = None
    gender: Optional[str] = None
    skills: Optional[List[str]] = []
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    # Recruiter fields
    company_name: Optional[str] = None
    designation: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    company_website: Optional[str] = None

# Login request fields; remember_me is accepted but does not change token duration.
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False

# Email-only request shape for the current reset placeholder endpoint.
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

# Login response: bearer token plus the identity needed by the frontend.
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: str
    role: str
    avatar_url: Optional[str] = None
    gender: Optional[str] = None


# ─────────────────────────────────────────────
# STUDENT SCHEMAS
# ─────────────────────────────────────────────
# Shared catalog entry returned without student-specific proficiency.
class SkillSchema(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    class Config:
        from_attributes = True

# Student-skill link enriched with a display name and proficiency.
class StudentSkillSchema(BaseModel):
    id: int
    skill_id: int
    skill_name: str
    proficiency_level: str

# File metadata response. has_file signals stored bytes without exposing them.
class DocumentSchema(BaseModel):
    id: int
    document_type: str
    file_name: str
    file_url: Optional[str] = None
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_at: datetime
    has_file: Optional[bool] = False
    class Config:
        from_attributes = True

# Combined profile response with nested skill links and document metadata.
class StudentProfileSchema(BaseModel):
    id: int
    user_id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: Optional[str] = None
    university: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    preferred_mode: Optional[str] = None
    expected_stipend: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    skills: List[StudentSkillSchema] = []
    documents: List[DocumentSchema] = []

# Optional update fields; routes use exclude_unset to distinguish omissions.
class StudentProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    university: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    preferred_mode: Optional[str] = None
    expected_stipend: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    skills: Optional[List[str]] = None


# ─────────────────────────────────────────────
# RECRUITER SCHEMAS
# ─────────────────────────────────────────────
# Company/contact profile returned together with its account email.
class RecruiterProfileSchema(BaseModel):
    id: int
    user_id: int
    email: str
    full_name: str
    company_name: str
    company_logo: Optional[str] = None
    designation: Optional[str] = None
    phone: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    location: Optional[str] = None

# Editable recruiter fields, separate from login credentials.
class RecruiterProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    company_logo: Optional[str] = None
    designation: Optional[str] = None
    phone: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    location: Optional[str] = None

# Counts displayed on the recruiter dashboard.
class RecruiterStatsSchema(BaseModel):
    active_posts: int
    total_applications: int
    shortlisted: int
    interviews_scheduled: int
    total_accepted: int


# ─────────────────────────────────────────────
# INTERNSHIP SCHEMAS
# ─────────────────────────────────────────────
# Public posting fields plus per-student saved/applied flags and applicant count.
class InternshipSchema(BaseModel):
    id: int
    title: str
    company_name: str
    company_logo: Optional[str] = None
    location: str
    mode: str
    stipend_amount: int
    stipend_currency: str
    duration: str
    description: str
    eligibility: Optional[str] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    recruiter_title: Optional[str] = None
    skills_required: Optional[str] = None
    is_external: bool
    external_link: Optional[str] = None
    is_active: bool = True
    deadline: Optional[datetime] = None
    created_at: datetime
    is_saved: Optional[bool] = False
    has_applied: Optional[bool] = False
    applications_count: Optional[int] = 0
    class Config:
        from_attributes = True

# Posting data submitted by the recruiter create/update endpoints.
class PostInternshipRequest(BaseModel):
    title: str
    company_name: str
    company_logo: Optional[str] = None
    location: str
    mode: str = "Remote"
    stipend_amount: int = 0
    stipend_currency: str = "₹"
    duration: str
    description: str
    eligibility: Optional[str] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
    skills_required: Optional[str] = None
    is_external: bool = False
    external_link: Optional[str] = None
    deadline: Optional[datetime] = None

# Status and optional notes; status is a string rather than an enum constraint.
class UpdateApplicationStatusRequest(BaseModel):
    status: str
    recruiter_notes: Optional[str] = None


# ─────────────────────────────────────────────
# APPLICATION SCHEMAS
# ─────────────────────────────────────────────
# Legacy JSON application shape; the current submission route uses Form/File.
class ApplicationSubmitRequest(BaseModel):
    internship_id: int
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None

# Student tracker response, including the related internship as a nested object.
class ApplicationResponseSchema(BaseModel):
    id: int
    student_id: int
    internship_id: int
    status: str
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    applied_at: datetime
    recruiter_notes: Optional[str] = None
    internship: InternshipSchema
    class Config:
        from_attributes = True

# Candidate details assembled for recruiter review; resume content loads separately.
class RecruiterApplicationSchema(BaseModel):
    id: int
    student_id: int
    student_user_id: Optional[int] = None
    internship_id: int
    status: str
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    resume_filename: Optional[str] = None
    applied_at: datetime
    recruiter_notes: Optional[str] = None
    student_name: str
    student_email: str
    student_phone: Optional[str] = None
    student_avatar: Optional[str] = None
    student_bio: Optional[str] = None
    student_university: Optional[str] = None
    student_degree: Optional[str] = None
    student_field_of_study: Optional[str] = None
    student_cgpa: Optional[float] = None
    student_location: Optional[str] = None
    student_portfolio: Optional[str] = None
    student_linkedin: Optional[str] = None
    student_skills: Optional[str] = None
    has_resume: Optional[bool] = False
    internship_title: str


# ─────────────────────────────────────────────
# INTERVIEW SCHEMAS
# ─────────────────────────────────────────────
# Interview inputs, including the application ID and meeting details.
class ScheduleInterviewRequest(BaseModel):
    application_id: int
    internship_id: Optional[int] = None
    scheduled_at: datetime
    duration_minutes: Optional[int] = 30
    interview_type: Optional[str] = "Video Call"
    meeting_link: Optional[str] = None
    notes: Optional[str] = None

# Saved interview response enriched with candidate and internship display names.
class InterviewSchema(BaseModel):
    id: int
    recruiter_id: int
    application_id: int
    internship_id: Optional[int] = None
    scheduled_at: datetime
    duration_minutes: int
    interview_type: str
    meeting_link: Optional[str] = None
    notes: Optional[str] = None
    status: str
    created_at: datetime
    candidate_name: Optional[str] = None
    internship_title: Optional[str] = None
    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# NOTIFICATION / MESSAGE SCHEMAS
# ─────────────────────────────────────────────
# Stored alert returned to the notification bell/list.
class NotificationSchema(BaseModel):
    id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime
    class Config:
        from_attributes = True

# ─────────────────────────────────────────────
# New message input: recipient account ID and message text.
class MessageCreateRequest(BaseModel):
    receiver_id: int
    content: str

# Stored message output with participant IDs, read flag and timestamp.
class MessageSchema(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    sent_at: datetime
    class Config:
        from_attributes = True

# Conversation-list entry with partner details, latest preview and unread count.
class MessageContactSchema(BaseModel):
    """The other party in a conversation. Works for both roles:
    student → recruiter of an applied-to internship; recruiter → student applicant."""
    user_id: int
    full_name: str
    avatar_url: Optional[str] = None
    subtitle: Optional[str] = None          # company (recruiter) or university (student)
    internship_id: Optional[int] = None
    internship_title: Optional[str] = None
    last_message: Optional[str] = None
    last_at: Optional[datetime] = None
    unread: Optional[int] = 0
