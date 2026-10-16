# Student profiles, skills and documents. Profile queries start from the
# authenticated account ID. Document metadata is returned in lists, while a
# separate endpoint returns the full Base64 file payload when requested.

import base64
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Student, Skill, StudentSkill, Document
from app.schemas.schemas import (
    StudentProfileSchema, StudentProfileUpdateRequest, StudentSkillSchema,
    DocumentSchema,
)
from app.routers.auth import get_current_user
from app.core.avatars import pick_avatar

router = APIRouter(prefix="/api/students", tags=["Students"])


# Assemble a single response from the student row, login email, linked
# skills and document metadata. File contents are excluded from this view.
@router.get("/profile", response_model=StudentProfileSchema)
def get_student_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    skills_data = [
        StudentSkillSchema(
            id=ss.id, skill_id=ss.skill_id,
            skill_name=ss.skill.name if ss.skill else "Skill",
            proficiency_level=ss.proficiency_level,
        )
        for ss in student.student_skills
    ]

    docs_data = [
        DocumentSchema(
            id=d.id, document_type=d.document_type, file_name=d.file_name,
            file_url=d.file_url or "", content_type=d.content_type,
            file_size=d.file_size, uploaded_at=d.uploaded_at,
            has_file=bool(d.file_data),
        )
        for d in student.documents
    ]

    return StudentProfileSchema(
        id=student.id, user_id=student.user_id, email=current_user.email,
        full_name=student.full_name, phone=student.phone,
        avatar_url=student.avatar_url or pick_avatar(student.gender, student.id),
        gender=student.gender,
        university=student.university, degree=student.degree,
        field_of_study=student.field_of_study, graduation_year=student.graduation_year,
        cgpa=student.cgpa, bio=student.bio, location=student.location,
        preferred_mode=student.preferred_mode, expected_stipend=student.expected_stipend,
        portfolio_url=student.portfolio_url, github_url=student.github_url,
        linkedin_url=student.linkedin_url, skills=skills_data, documents=docs_data,
    )


# Apply profile fields and, if skills were supplied, replace the student's
# skill links using existing or newly inserted global Skill records.
@router.put("/profile", response_model=StudentProfileSchema)
def update_student_profile(
    payload: StudentProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    # Track if gender changed so we can refresh the avatar.
    new_gender = payload.gender if payload.gender is not None else student.gender

    for key, val in payload.dict(exclude_unset=True).items():
        if key == "skills":
            continue
        if val is not None:
            setattr(student, key, val)

    # Refresh avatar to match the (possibly new) gender.
    if payload.gender is not None and payload.gender != student.gender:
        student.avatar_url = pick_avatar(payload.gender, student.id)
    student.gender = new_gender

    # An omitted skills field leaves the existing links intact. An empty list
    # explicitly requests removal of all this student's skill links.
    if payload.skills is not None:
        db.query(StudentSkill).filter(StudentSkill.student_id == student.id).delete()
        db.commit()
        for skill_name in payload.skills:
            skill = db.query(Skill).filter(Skill.name == skill_name).first()
            if not skill:
                skill = Skill(name=skill_name, category="General")
                db.add(skill)
                db.commit()
                db.refresh(skill)
            db.add(StudentSkill(student_id=student.id, skill_id=skill.id, proficiency_level="Intermediate"))

    db.commit()
    db.refresh(student)
    return get_student_profile(current_user=current_user, db=db)


# ── Document upload (#2): base64 stored in DB ────────────────────────────
MAX_FILE_BYTES = 8 * 1024 * 1024  # 8 MB cap


# Read the uploaded bytes, enforce the size cap, encode a data URI and
# store it with filename/type/size metadata under the student profile.
@router.post("/documents", response_model=DocumentSchema)
async def upload_document(
    document_type: str = Form("resume"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    raw = await file.read()
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="File too large (8 MB max).")

    encoded = base64.b64encode(raw).decode("ascii")
    data_uri = f"data:{file.content_type or 'application/octet-stream'};base64,{encoded}"

    doc = Document(
        student_id=student.id,
        document_type=document_type,
        file_name=file.filename or "document",
        file_url="",  # legacy field; payload lives in file_data
        content_type=file.content_type,
        file_size=len(raw),
        file_data=data_uri,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return DocumentSchema(
        id=doc.id, document_type=doc.document_type, file_name=doc.file_name,
        file_url="", content_type=doc.content_type, file_size=doc.file_size,
        uploaded_at=doc.uploaded_at, has_file=True,
    )


# Return document metadata without transferring every stored file payload.
@router.get("/documents", response_model=list[DocumentSchema])
def list_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        return []
    return [
        DocumentSchema(
            id=d.id, document_type=d.document_type, file_name=d.file_name,
            file_url=d.file_url or "", content_type=d.content_type,
            file_size=d.file_size, uploaded_at=d.uploaded_at,
            has_file=bool(d.file_data),
        )
        for d in student.documents
    ]


# Check document ownership and return the stored data URI separately
# from the metadata list for viewing or downloading.
@router.get("/documents/{document_id}")
def get_document_file(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return the full data-URI payload so the client can view/download the file."""
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    doc = db.query(Document).filter(Document.id == document_id, Document.student_id == student.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.file_data:
        raise HTTPException(status_code=404, detail="No file payload stored.")
    return {"file_name": doc.file_name, "content_type": doc.content_type, "data": doc.file_data}


# Delete only a document associated with the current student profile.
@router.delete("/documents/{document_id}")
def delete_document(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    doc = db.query(Document).filter(Document.id == document_id, Document.student_id == student.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted."}
