from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey
)
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="student")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    recruiter_profile = relationship("RecruiterProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")


class RecruiterProfile(Base):
    __tablename__ = "recruiter_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    full_name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    company_logo = Column(String(500), nullable=True)
    designation = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    company_website = Column(String(500), nullable=True)
    company_size = Column(String(100), nullable=True)
    industry = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    location = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="recruiter_profile")
    internships = relationship("Internship", back_populates="recruiter", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="recruiter", cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    gender = Column(String(20), nullable=True)  # male | female | other | prefer_not_to_say
    university = Column(String(255), nullable=True)
    degree = Column(String(255), nullable=True)
    field_of_study = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    cgpa = Column(Float, nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    preferred_mode = Column(String(50), default="Remote")
    expected_stipend = Column(String(100), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="student_profile")
    documents = relationship("Document", back_populates="student", cascade="all, delete-orphan")
    student_skills = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="student", cascade="all, delete-orphan")
    saved_internships = relationship("SavedInternship", back_populates="student", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type = Column(String(100), nullable=False)  # resume | cover_letter | transcript | other
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=True)  # legacy/optional external URL
    content_type = Column(String(100), nullable=True)  # e.g. application/pdf
    file_size = Column(Integer, nullable=True)  # bytes
    file_data = Column(MEDIUMTEXT, nullable=True)  # base64-encoded file payload (stored in DB)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    student = relationship("Student", back_populates="documents")


class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=True)
    student_skills = relationship("StudentSkill", back_populates="skill", cascade="all, delete-orphan")


class StudentSkill(Base):
    __tablename__ = "student_skills"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    proficiency_level = Column(String(50), default="Intermediate")
    student = relationship("Student", back_populates="student_skills")
    skill = relationship("Skill", back_populates="student_skills")


class Internship(Base):
    __tablename__ = "internships"
    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("recruiter_profiles.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(255), nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    company_logo = Column(String(500), nullable=True)
    location = Column(String(255), nullable=False, index=True)
    mode = Column(String(50), default="Remote")
    stipend_amount = Column(Integer, nullable=False, default=0)
    stipend_currency = Column(String(10), default="₹")
    duration = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    eligibility = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    recruiter_name = Column(String(255), nullable=True)
    recruiter_email = Column(String(255), nullable=True)
    recruiter_title = Column(String(255), nullable=True)
    skills_required = Column(String(500), nullable=True)
    is_external = Column(Boolean, default=False)
    external_link = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    recruiter = relationship("RecruiterProfile", back_populates="internships")
    applications = relationship("Application", back_populates="internship", cascade="all, delete-orphan")
    saved_by = relationship("SavedInternship", back_populates="internship", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="internship", cascade="all, delete-orphan")


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="Applied")
    cover_letter = Column(Text, nullable=True)
    # Holds either an external URL or the uploaded resume as a base64 data URI
    # (base64 of an 8 MB file is ~11 MB of text, so this must be MEDIUMTEXT —
    # a VARCHAR here makes every real-resume upload fail with "Data too long").
    resume_url = Column(MEDIUMTEXT, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)
    recruiter_notes = Column(Text, nullable=True)

    student = relationship("Student", back_populates="applications")
    internship = relationship("Internship", back_populates="applications")
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")


class Interview(Base):
    __tablename__ = "interviews"
    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("recruiter_profiles.id", ondelete="CASCADE"), nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="SET NULL"), nullable=True)
    scheduled_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    interview_type = Column(String(50), default="Video Call")
    meeting_link = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(50), default="Scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)

    recruiter = relationship("RecruiterProfile", back_populates="interviews")
    application = relationship("Application", back_populates="interviews")
    internship = relationship("Internship", back_populates="interviews")


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="notifications")


class SavedInternship(Base):
    __tablename__ = "saved_internships"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False, index=True)
    saved_at = Column(DateTime, default=datetime.utcnow)
    student = relationship("Student", back_populates="saved_internships")
    internship = relationship("Internship", back_populates="saved_by")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
