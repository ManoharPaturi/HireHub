# Recruiter workspace API. The role dependency loads the recruiter profile,
# while posting/applicant queries normally filter by that profile ID. Related
# student and internship records supply the candidate details shown in the UI.

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.database import get_db
from app.db.models import (
    User, RecruiterProfile, Internship, Application, Interview, Student, Notification
)
from app.schemas.schemas import (
    RecruiterProfileSchema, RecruiterProfileUpdateRequest, RecruiterStatsSchema,
    InternshipSchema, PostInternshipRequest, RecruiterApplicationSchema,
    UpdateApplicationStatusRequest, InterviewSchema, ScheduleInterviewRequest, NotificationSchema
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/recruiter", tags=["Recruiter"])


# Reject non-recruiter roles and resolve the account's recruiter profile.
# Profile IDs, rather than user IDs, own internship and interview records.
def get_recruiter(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> RecruiterProfile:
    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiter access only.")
    profile = db.query(RecruiterProfile).filter(RecruiterProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Recruiter profile not found.")
    return profile


# ── Profile ───────────────────────────────────────────────────────────────────
# Build the recruiter response from profile fields plus the login email.
@router.get("/profile", response_model=RecruiterProfileSchema)
def get_profile(recruiter: RecruiterProfile = Depends(get_recruiter),
                current_user: User = Depends(get_current_user)):
    return RecruiterProfileSchema(
        id=recruiter.id, user_id=recruiter.user_id, email=current_user.email,
        full_name=recruiter.full_name, company_name=recruiter.company_name,
        company_logo=recruiter.company_logo, designation=recruiter.designation,
        phone=recruiter.phone, company_website=recruiter.company_website,
        company_size=recruiter.company_size, industry=recruiter.industry,
        bio=recruiter.bio, linkedin_url=recruiter.linkedin_url, location=recruiter.location
    )


# Apply supplied non-null profile fields, commit, and return the saved view.
@router.put("/profile", response_model=RecruiterProfileSchema)
def update_profile(payload: RecruiterProfileUpdateRequest,
                   recruiter: RecruiterProfile = Depends(get_recruiter),
                   current_user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    for key, val in payload.dict(exclude_unset=True).items():
        if val is not None:
            setattr(recruiter, key, val)
    db.commit()
    db.refresh(recruiter)
    return get_profile(recruiter=recruiter, current_user=current_user)


# ── Stats KPI ─────────────────────────────────────────────────────────────────
# Collect this recruiter's internship IDs, then count related applications
# and interviews. The shortlisted total also includes interview/accepted stages.
@router.get("/stats", response_model=RecruiterStatsSchema)
def get_stats(recruiter: RecruiterProfile = Depends(get_recruiter), db: Session = Depends(get_db)):
    internship_ids = [i.id for i in db.query(Internship.id).filter(Internship.recruiter_id == recruiter.id).all()]
    active_posts = db.query(Internship).filter(
        Internship.recruiter_id == recruiter.id, Internship.is_active == True).count()
    total_apps = db.query(Application).filter(Application.internship_id.in_(internship_ids)).count()
    shortlisted = db.query(Application).filter(
        Application.internship_id.in_(internship_ids),
        Application.status.in_(["Shortlisted", "Interview Scheduled", "Accepted"])).count()
    interviews = db.query(Interview).filter(Interview.recruiter_id == recruiter.id).count()
    accepted = db.query(Application).filter(
        Application.internship_id.in_(internship_ids), Application.status == "Accepted").count()
    return RecruiterStatsSchema(
        active_posts=active_posts, total_applications=total_apps,
        shortlisted=shortlisted, interviews_scheduled=interviews, total_accepted=accepted
    )


# ── Internships ───────────────────────────────────────────────────────────────
# Create a posting owned by the current recruiter. Company and contact
# fields are copied onto the posting for its public listing response.
@router.post("/internships", response_model=InternshipSchema)
def post_internship(payload: PostInternshipRequest,
                    recruiter: RecruiterProfile = Depends(get_recruiter),
                    db: Session = Depends(get_db)):
    new_int = Internship(
        recruiter_id=recruiter.id, title=payload.title,
        company_name=payload.company_name or recruiter.company_name,
        company_logo=payload.company_logo or recruiter.company_logo,
        location=payload.location, mode=payload.mode,
        stipend_amount=payload.stipend_amount, stipend_currency=payload.stipend_currency,
        duration=payload.duration, description=payload.description,
        eligibility=payload.eligibility, responsibilities=payload.responsibilities,
        benefits=payload.benefits, skills_required=payload.skills_required,
        recruiter_name=recruiter.full_name, recruiter_email=recruiter.user.email,
        recruiter_title=recruiter.designation,
        is_external=payload.is_external, external_link=payload.external_link,
        deadline=payload.deadline, is_active=True
    )
    db.add(new_int)
    db.commit()
    db.refresh(new_int)
    schema = InternshipSchema.from_orm(new_int)
    schema.applications_count = 0
    return schema


# Load only this recruiter's postings and calculate an application count
# for each card in the Manage view.
@router.get("/internships", response_model=List[InternshipSchema])
def list_my_internships(recruiter: RecruiterProfile = Depends(get_recruiter), db: Session = Depends(get_db)):
    items = db.query(Internship).filter(Internship.recruiter_id == recruiter.id).order_by(desc(Internship.created_at)).all()
    result = []
    for item in items:
        s = InternshipSchema.from_orm(item)
        s.applications_count = len(item.applications)
        result.append(s)
    return result


# Find a posting by both its ID and owner before applying supplied fields.
@router.put("/internships/{internship_id}", response_model=InternshipSchema)
def update_internship(internship_id: int, payload: PostInternshipRequest,
                      recruiter: RecruiterProfile = Depends(get_recruiter),
                      db: Session = Depends(get_db)):
    item = db.query(Internship).filter(
        Internship.id == internship_id, Internship.recruiter_id == recruiter.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Internship not found")
    for key, val in payload.dict(exclude_unset=True).items():
        if val is not None:
            setattr(item, key, val)
    db.commit()
    db.refresh(item)
    s = InternshipSchema.from_orm(item)
    s.applications_count = len(item.applications)
    return s


# Delete an owned posting. Related records may also be deleted through
# the SQLAlchemy relationships and database foreign-key rules.
@router.delete("/internships/{internship_id}")
def delete_internship(internship_id: int,
                      recruiter: RecruiterProfile = Depends(get_recruiter),
                      db: Session = Depends(get_db)):
    item = db.query(Internship).filter(
        Internship.id == internship_id, Internship.recruiter_id == recruiter.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Internship not found")
    db.delete(item)
    db.commit()
    return {"message": "Internship deleted successfully."}


# Flip the stored active flag without deleting the posting or applications.
@router.put("/internships/{internship_id}/toggle")
def toggle_internship_status(internship_id: int,
                              recruiter: RecruiterProfile = Depends(get_recruiter),
                              db: Session = Depends(get_db)):
    item = db.query(Internship).filter(
        Internship.id == internship_id, Internship.recruiter_id == recruiter.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Internship not found")
    item.is_active = not item.is_active
    db.commit()
    return {"is_active": item.is_active}


# ── Applicants ────────────────────────────────────────────────────────────────
# Load applications for owned internships and combine each with student
# profile/skill details. Large uploaded resumes are omitted from list responses;
# a separate endpoint supplies the file when the recruiter requests it.
@router.get("/applicants", response_model=List[RecruiterApplicationSchema])
def list_applicants(internship_id: Optional[int] = None,
                    recruiter: RecruiterProfile = Depends(get_recruiter),
                    db: Session = Depends(get_db)):
    my_ids = [i.id for i in db.query(Internship.id).filter(Internship.recruiter_id == recruiter.id).all()]
    query = db.query(Application).filter(Application.internship_id.in_(my_ids))
    if internship_id:
        query = query.filter(Application.internship_id == internship_id)
    apps = query.order_by(desc(Application.applied_at)).all()

    result = []
    for app in apps:
        student = app.student
        skills = ", ".join([ss.skill.name for ss in (student.student_skills if student else []) if ss.skill]) or None
        # A recruiter should not receive the raw data-URI payload in the list
        # (it can be large); surface a flag + original filename instead.
        raw_resume = app.resume_url or ""
        has_resume = bool(raw_resume) and raw_resume.startswith("data:")
        resume_filename = None
        if has_resume:
            ct = raw_resume.split(";")[0].replace("data:", "") if ";" in raw_resume else "file"
            ext = "pdf" if "pdf" in ct else ("docx" if "word" in ct else "doc")
            resume_filename = f"resume_{(student.full_name if student else 'candidate').split()[0].lower()}.{ext}"
        result.append(RecruiterApplicationSchema(
            id=app.id, student_id=app.student_id,
            student_user_id=student.user_id if student else None,
            internship_id=app.internship_id,
            status=app.status, cover_letter=app.cover_letter,
            resume_url=raw_resume if (not has_resume) else None,
            resume_filename=resume_filename, has_resume=has_resume,
            applied_at=app.applied_at, recruiter_notes=app.recruiter_notes,
            student_name=student.full_name if student else "Unknown",
            student_email=student.user.email if student and student.user else "",
            student_phone=student.phone if student else None,
            student_avatar=student.avatar_url if student else None,
            student_bio=student.bio if student else None,
            student_university=student.university if student else None,
            student_degree=student.degree if student else None,
            student_field_of_study=student.field_of_study if student else None,
            student_cgpa=student.cgpa if student else None,
            student_location=student.location if student else None,
            student_portfolio=student.portfolio_url if student else None,
            student_linkedin=student.linkedin_url if student else None,
            student_skills=skills,
            internship_title=app.internship.title if app.internship else "",
        ))
    return result


# Update an owned application and queue a student notification in the same
# commit. The supplied status string is stored directly, not enforced as a
# strict sequence of transitions by this function.
@router.put("/applications/{app_id}/status")
def update_app_status(app_id: int, payload: UpdateApplicationStatusRequest,
                      recruiter: RecruiterProfile = Depends(get_recruiter),
                      db: Session = Depends(get_db)):
    my_ids = [i.id for i in db.query(Internship.id).filter(Internship.recruiter_id == recruiter.id).all()]
    app = db.query(Application).filter(Application.id == app_id,
                                       Application.internship_id.in_(my_ids)).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.status = payload.status
    if payload.recruiter_notes:
        app.recruiter_notes = payload.recruiter_notes

    # Notify the student
    if app.student and app.student.user_id:
        notif = Notification(
            user_id=app.student.user_id,
            title=f"Application Status Updated: {payload.status}",
            message=f"Your application for '{app.internship.title}' has been updated to '{payload.status}'.",
            type="application"
        )
        db.add(notif)
    db.commit()
    return {"message": "Status updated.", "status": payload.status}


# Verify the application belongs to an owned internship before returning
# the file data, or preserve an external URL for older application records.
@router.get("/applications/{app_id}/resume")
def get_applicant_resume(app_id: int,
                         recruiter: RecruiterProfile = Depends(get_recruiter),
                         db: Session = Depends(get_db)):
    """Securely return the resume payload for an application the recruiter owns.
    The data-URI is returned so the client can open/download it in-browser."""
    my_ids = [i.id for i in db.query(Internship.id).filter(Internship.recruiter_id == recruiter.id).all()]
    app = db.query(Application).filter(Application.id == app_id, Application.internship_id.in_(my_ids)).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    raw = app.resume_url or ""
    if not raw.startswith("data:"):
        # Legacy URL resume — return as-is (external link).
        return {"file_name": "resume", "content_type": "url", "data": raw, "url": raw}
    ct = raw.split(";")[0].replace("data:", "") if ";" in raw else "application/octet-stream"
    return {"file_name": f"resume_{(app.student.full_name if app.student else 'candidate').split()[0].lower()}.{('pdf' if 'pdf' in ct else 'docx')}", "content_type": ct, "data": raw}


# ── Interviews ────────────────────────────────────────────────────────────────
# Insert the supplied interview details, then update the referenced
# application to Interview Scheduled and notify its student. These steps
# currently use separate commits, so they are not one atomic transaction.
@router.post("/interviews", response_model=InterviewSchema)
def schedule_interview(payload: ScheduleInterviewRequest,
                       recruiter: RecruiterProfile = Depends(get_recruiter),
                       db: Session = Depends(get_db)):
    interview = Interview(
        recruiter_id=recruiter.id, application_id=payload.application_id,
        internship_id=payload.internship_id, scheduled_at=payload.scheduled_at,
        duration_minutes=payload.duration_minutes or 30,
        interview_type=payload.interview_type or "Video Call",
        meeting_link=payload.meeting_link, notes=payload.notes, status="Scheduled"
    )
    # The application_id comes from the submitted request. This function does
    # not separately verify that the referenced application belongs to the current
    # recruiter before insertion; the foreign key only checks record existence.
    db.add(interview)
    db.commit()
    db.refresh(interview)

    app = db.query(Application).filter(Application.id == payload.application_id).first()
    if app:
        app.status = "Interview Scheduled"
        if app.student and app.student.user_id:
            notif = Notification(
                user_id=app.student.user_id,
                title="Interview Scheduled 📅",
                message=f"Your interview for '{app.internship.title}' is scheduled for {payload.scheduled_at.strftime('%b %d, %Y at %I:%M %p')}.",
                type="info"
            )
            db.add(notif)
        db.commit()

    s = InterviewSchema.from_orm(interview)
    if app and app.student:
        s.candidate_name = app.student.full_name
    if app and app.internship:
        s.internship_title = app.internship.title
    return s


# Return this recruiter's interviews in date order and add candidate/job
# names from the related application and internship for display.
@router.get("/interviews", response_model=List[InterviewSchema])
def list_interviews(recruiter: RecruiterProfile = Depends(get_recruiter), db: Session = Depends(get_db)):
    interviews = db.query(Interview).filter(
        Interview.recruiter_id == recruiter.id).order_by(Interview.scheduled_at).all()
    result = []
    for iv in interviews:
        s = InterviewSchema.from_orm(iv)
        if iv.application and iv.application.student:
            s.candidate_name = iv.application.student.full_name
        if iv.internship:
            s.internship_title = iv.internship.title
        result.append(s)
    return result


# ── Notifications ─────────────────────────────────────────────────────────────
# Return alerts addressed to the authenticated user, newest first.
@router.get("/notifications", response_model=List[NotificationSchema])
def recruiter_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.user_id == current_user.id).order_by(
        desc(Notification.created_at)).all()
