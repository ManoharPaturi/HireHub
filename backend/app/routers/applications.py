import base64
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Student, Internship, Application, Notification, Document
from app.schemas.schemas import ApplicationResponseSchema
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/applications", tags=["Applications"])

MAX_FILE_BYTES = 8 * 1024 * 1024  # 8 MB


@router.post("", response_model=ApplicationResponseSchema)
async def submit_application(
    internship_id: int = Form(...),
    cover_letter: Optional[str] = Form(None),
    resume: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit an application. Resume is an optional file upload stored as a
    base64 data-URI in ``Application.resume_url`` (so the recruiter view and the
    existing schema keep working without a join). A copy is also saved as a
    ``Document`` row on the student profile."""
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship position not found")

    existing = db.query(Application).filter(
        Application.student_id == student.id,
        Application.internship_id == internship_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied for this internship position.")

    # Process optional resume file → base64 data URI.
    resume_data_uri: Optional[str] = None
    if resume is not None:
        raw = await resume.read()
        if len(raw) > MAX_FILE_BYTES:
            raise HTTPException(status_code=413, detail="Resume file too large (8 MB max).")
        if raw:
            ct = resume.content_type or "application/octet-stream"
            encoded = base64.b64encode(raw).decode("ascii")
            resume_data_uri = f"data:{ct};base64,{encoded}"
            # Persist a copy on the student profile too.
            db.add(Document(
                student_id=student.id, document_type="resume",
                file_name=resume.filename or "resume", file_url="",
                content_type=ct, file_size=len(raw), file_data=resume_data_uri,
            ))

    new_app = Application(
        student_id=student.id,
        internship_id=internship_id,
        status="Applied",
        cover_letter=cover_letter,
        resume_url=resume_data_uri or student.portfolio_url,
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    db.add(Notification(
        user_id=current_user.id, title="Application Submitted 🚀",
        message=f"Your application for '{internship.title}' at {internship.company_name} was successfully submitted.",
        type="application",
    ))

    # Notify the recruiter who owns this internship about the new applicant.
    if internship.recruiter_id and internship.recruiter and internship.recruiter.user_id:
        db.add(Notification(
            user_id=internship.recruiter.user_id, title="New Application 📢",
            message=f"{student.full_name} applied for '{internship.title}'.",
            type="application",
        ))
    db.commit()
    return new_app


@router.get("", response_model=List[ApplicationResponseSchema])
def list_student_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        return []
    return db.query(Application).filter(Application.student_id == student.id).order_by(Application.applied_at.desc()).all()


@router.delete("/{application_id}")
def withdraw_application(application_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    app = db.query(Application).filter(Application.id == application_id, Application.student_id == student.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application record not found")
    db.delete(app)
    db.commit()
    return {"message": "Application successfully withdrawn."}
