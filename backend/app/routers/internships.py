from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from app.db.database import get_db
from app.db.models import User, Student, Internship, SavedInternship, Application
from app.schemas.schemas import InternshipSchema
from app.routers.auth import get_current_user, oauth2_scheme_optional
from app.core.security import decode_access_token

router = APIRouter(prefix="/api/internships", tags=["Internships"])

def get_optional_user(token: Optional[str] = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)) -> Optional[User]:
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            user_id = int(payload["sub"])
            return db.query(User).filter(User.id == user_id).first()
    except Exception:
        pass
    return None

@router.get("", response_model=List[InternshipSchema])
def list_internships(
    search: Optional[str] = None,
    location: Optional[str] = None,
    mode: Optional[str] = None,
    min_stipend: Optional[int] = None,
    duration: Optional[str] = None,
    company: Optional[str] = None,
    skills: Optional[str] = None,  # comma-separated
    sort_by: Optional[str] = "newest",  # 'newest', 'stipend_desc', 'deadline_asc'
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    query = db.query(Internship)

    # Free text search across title, company, description, and skills
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Internship.title.ilike(search_pattern),
                Internship.company_name.ilike(search_pattern),
                Internship.description.ilike(search_pattern),
                Internship.skills_required.ilike(search_pattern)
            )
        )

    if location and location != "All":
        query = query.filter(Internship.location.ilike(f"%{location}%"))

    if mode and mode != "All":
        query = query.filter(Internship.mode == mode)

    if min_stipend:
        query = query.filter(Internship.stipend_amount >= min_stipend)

    if duration and duration != "All":
        query = query.filter(Internship.duration.ilike(f"%{duration}%"))

    if company:
        query = query.filter(Internship.company_name.ilike(f"%{company}%"))

    if skills:
        skill_list = [s.strip() for s in skills.split(",") if s.strip()]
        for sk in skill_list:
            query = query.filter(Internship.skills_required.ilike(f"%{sk}%"))

    # Sorting
    if sort_by == "stipend_desc":
        query = query.order_by(desc(Internship.stipend_amount))
    elif sort_by == "deadline_asc":
        query = query.order_by(asc(Internship.deadline))
    else:
        query = query.order_by(desc(Internship.created_at))

    # Pagination
    offset = (page - 1) * limit
    results = query.offset(offset).limit(limit).all()

    # Determine saved & applied flags if logged in
    saved_ids = set()
    applied_ids = set()
    if current_user:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if student:
            saved_records = db.query(SavedInternship.internship_id).filter(SavedInternship.student_id == student.id).all()
            saved_ids = {r[0] for r in saved_records}

            applied_records = db.query(Application.internship_id).filter(Application.student_id == student.id).all()
            applied_ids = {r[0] for r in applied_records}

    output = []
    for item in results:
        schema_obj = InternshipSchema.from_orm(item)
        schema_obj.is_saved = item.id in saved_ids
        schema_obj.has_applied = item.id in applied_ids
        output.append(schema_obj)

    return output


@router.get("/saved", response_model=List[InternshipSchema])
def list_saved_internships(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the internships the logged-in student has bookmarked."""
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        return []
    saved = db.query(SavedInternship).filter(SavedInternship.student_id == student.id).all()
    ids = [s.internship_id for s in saved]
    if not ids:
        return []
    items = db.query(Internship).filter(Internship.id.in_(ids)).order_by(desc(Internship.created_at)).all()

    applied_ids = {r[0] for r in db.query(Application.internship_id).filter(Application.student_id == student.id).all()}
    output = []
    for item in items:
        schema_obj = InternshipSchema.from_orm(item)
        schema_obj.is_saved = True
        schema_obj.has_applied = item.id in applied_ids
        output.append(schema_obj)
    return output


@router.get("/recommendations", response_model=List[InternshipSchema])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        return db.query(Internship).order_by(desc(Internship.created_at)).limit(5).all()

    student_skills = [ss.skill.name for ss in student.student_skills if ss.skill]
    
    query = db.query(Internship)
    if student_skills:
        # Match internships containing any of student's skills or preferred mode
        conditions = [Internship.skills_required.ilike(f"%{sk}%") for sk in student_skills]
        if student.preferred_mode:
            conditions.append(Internship.mode == student.preferred_mode)
        query = query.filter(or_(*conditions))

    results = query.order_by(desc(Internship.stipend_amount)).limit(6).all()
    if not results:
        results = db.query(Internship).order_by(desc(Internship.created_at)).limit(6).all()

    saved_ids = set()
    applied_ids = set()
    saved_records = db.query(SavedInternship.internship_id).filter(SavedInternship.student_id == student.id).all()
    saved_ids = {r[0] for r in saved_records}

    applied_records = db.query(Application.internship_id).filter(Application.student_id == student.id).all()
    applied_ids = {r[0] for r in applied_records}

    output = []
    for item in results:
        schema_obj = InternshipSchema.from_orm(item)
        schema_obj.is_saved = item.id in saved_ids
        schema_obj.has_applied = item.id in applied_ids
        output.append(schema_obj)

    return output


@router.get("/{internship_id}", response_model=InternshipSchema)
def get_internship_detail(
    internship_id: int,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    item = db.query(Internship).filter(Internship.id == internship_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Internship post not found")

    schema_obj = InternshipSchema.from_orm(item)
    if current_user:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if student:
            saved = db.query(SavedInternship).filter(
                SavedInternship.student_id == student.id,
                SavedInternship.internship_id == item.id
            ).first()
            schema_obj.is_saved = bool(saved)

            applied = db.query(Application).filter(
                Application.student_id == student.id,
                Application.internship_id == item.id
            ).first()
            schema_obj.has_applied = bool(applied)

    return schema_obj


@router.post("/{internship_id}/save")
def toggle_save_internship(
    internship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    saved_record = db.query(SavedInternship).filter(
        SavedInternship.student_id == student.id,
        SavedInternship.internship_id == internship_id
    ).first()

    if saved_record:
        db.delete(saved_record)
        db.commit()
        return {"saved": False, "message": "Internship removed from saved bookmarks."}
    else:
        new_save = SavedInternship(student_id=student.id, internship_id=internship_id)
        db.add(new_save)
        db.commit()
        return {"saved": True, "message": "Internship saved to your bookmarks."}
