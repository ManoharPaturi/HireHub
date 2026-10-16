from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# ─────────────────────────────────────────────
# AUTH SCHEMAS
# ─────────────────────────────────────────────
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

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

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
class SkillSchema(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    class Config:
        from_attributes = True

class StudentSkillSchema(BaseModel):
    id: int
    skill_id: int
    skill_name: str
    proficiency_level: str

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

class RecruiterStatsSchema(BaseModel):
    active_posts: int
    total_applications: int
    shortlisted: int
    interviews_scheduled: int
    total_accepted: int


# ─────────────────────────────────────────────
# INTERNSHIP SCHEMAS
# ─────────────────────────────────────────────
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

class UpdateApplicationStatusRequest(BaseModel):
    status: str
    recruiter_notes: Optional[str] = None


# ─────────────────────────────────────────────
# APPLICATION SCHEMAS
# ─────────────────────────────────────────────
class ApplicationSubmitRequest(BaseModel):
    internship_id: int
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None

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
class ScheduleInterviewRequest(BaseModel):
    application_id: int
    internship_id: Optional[int] = None
    scheduled_at: datetime
    duration_minutes: Optional[int] = 30
    interview_type: Optional[str] = "Video Call"
    meeting_link: Optional[str] = None
    notes: Optional[str] = None

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
class MessageCreateRequest(BaseModel):
    receiver_id: int
    content: str

class MessageSchema(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    sent_at: datetime
    class Config:
        from_attributes = True

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
