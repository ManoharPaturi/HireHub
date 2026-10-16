# Administrative API with a separate login and an admin-role dependency.
# Counts and grouped queries build dashboard summaries; management routes change
# accounts and postings. Activity is assembled from current database records.

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from app.db.database import get_db
from app.db.models import (
    User, Student, RecruiterProfile, Internship, Application,
    Interview, Message, Notification,
)
from app.schemas.schemas import TokenResponse
from app.core.security import create_access_token, get_password_hash, verify_password
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ── Auth ─────────────────────────────────────────────────────────────────────

# Use the dedicated entry point to authenticate active admin accounts only.
@router.post("/login", response_model=TokenResponse)
def admin_login(payload: dict, db: Session = Depends(get_db)):
    """Dedicated admin login. Only role='admin' accounts may enter here —
    the regular /api/auth/login rejects admin accounts to keep the flows separate."""
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid admin credentials.")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="This account is not an administrator.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This admin account is disabled.")
    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    return TokenResponse(
        access_token=token, token_type="bearer", role="admin",
        user_id=user.id, email=user.email,
        full_name="Platform Admin", avatar_url=None, gender=None,
    )


# Reuse token validation and then require the admin role for management APIs.
def get_current_admin(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required.")
    return current_user


# ── Overview / KPIs ──────────────────────────────────────────────────────────

# COUNT measures record totals; AVG computes the active-post stipend mean.
# Date filters separately count recent signups and applications.
@router.get("/stats")
def platform_stats(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    total_students = db.query(Student).count()
    total_recruiters = db.query(RecruiterProfile).count()
    total_internships = db.query(Internship).count()
    active_internships = db.query(Internship).filter(Internship.is_active == True).count()  # noqa: E712
    total_applications = db.query(Application).count()
    total_interviews = db.query(Interview).count()
    total_messages = db.query(Message).count()
    avg_stipend = db.query(func.avg(Internship.stipend_amount)).filter(
        Internship.is_active == True  # noqa: E712
    ).scalar()

    # New users in the last 7 days for the KPI trend chips.
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_week = db.query(User).filter(
        User.role != "admin", User.created_at >= week_ago).count()
    new_apps_week = db.query(Application).filter(Application.applied_at >= week_ago).count()

    return {
        "total_students": total_students,
        "total_recruiters": total_recruiters,
        "total_internships": total_internships,
        "active_internships": active_internships,
        "total_applications": total_applications,
        "total_interviews": total_interviews,
        "total_messages": total_messages,
        "avg_stipend": round(float(avg_stipend)) if avg_stipend else 0,
        "new_users_week": new_users_week,
        "new_apps_week": new_apps_week,
    }


# Build chart-ready labels and values from database queries: daily counts,
# status/mode distributions, and top universities, fields and companies.
@router.get("/charts")
def chart_data(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Aggregates for the overview charts, in the spirit of a traffic panel:
    applications-over-time, by-status donut, by-mode bars, and top lists."""
    # Applications per day, last 14 days.
    days: List[dict] = []
    today = datetime.utcnow().date()
    for i in range(13, -1, -1):
        day = today - timedelta(days=i)
        count = db.query(Application).filter(
            func.date(Application.applied_at) == day).count()
        days.append({"date": day.isoformat(), "count": count})

    # By status.
    status_rows = db.query(Application.status, func.count(Application.id)).group_by(Application.status).all()
    status_colors = {
        "Applied": "#4f7cff", "Under Review": "#f59e0b", "Shortlisted": "#8b5cf6",
        "Interview Scheduled": "#06b6d4", "Accepted": "#10b981", "Rejected": "#ef4444",
    }
    by_status = [{"label": s or "Applied", "value": c, "color": status_colors.get(s, "#64748b")}
                 for s, c in status_rows]

    # By work mode (of applied-to internships).
    # A JOIN connects applications to their posting before grouping by mode.
    # Counting application IDs measures applications per mode, not posting totals.
    mode_rows = (
        db.query(Internship.mode, func.count(Application.id))
        .join(Application, Application.internship_id == Internship.id)
        .group_by(Internship.mode).all()
    )
    mode_colors = {"Remote": "#4f7cff", "Hybrid": "#8b5cf6", "In-Office": "#f59e0b"}
    by_mode = [{"label": m or "—", "value": c, "color": mode_colors.get(m, "#64748b")}
               for m, c in mode_rows]

    # Top universities by student count.
    uni_rows = (
        db.query(Student.university, func.count(Student.id))
        .filter(Student.university.isnot(None), Student.university != "")
        .group_by(Student.university).order_by(func.count(Student.id).desc()).limit(5).all()
    )
    top_universities = [{"label": u, "value": c} for u, c in uni_rows]

    # Top fields of study.
    field_rows = (
        db.query(Student.field_of_study, func.count(Student.id))
        .filter(Student.field_of_study.isnot(None), Student.field_of_study != "")
        .group_by(Student.field_of_study).order_by(func.count(Student.id).desc()).limit(5).all()
    )
    top_fields = [{"label": f, "value": c} for f, c in field_rows]

    # Top companies by applications received.
    comp_rows = (
        db.query(Internship.company_name, func.count(Application.id))
        .join(Application, Application.internship_id == Internship.id)
        .group_by(Internship.company_name).order_by(func.count(Application.id).desc()).limit(5).all()
    )
    top_companies = [{"label": c_, "value": n} for c_, n in comp_rows]

    return {
        "applications_timeline": days,
        "by_status": by_status,
        "by_mode": by_mode,
        "top_universities": top_universities,
        "top_fields": top_fields,
        "top_companies": top_companies,
    }


# ── Users management ─────────────────────────────────────────────────────────

# Load up to 200 non-admin accounts, enrich them from their profiles, and
# apply name/email/company search in Python after the limited database query.
@router.get("/users")
def list_users(
    role: Optional[str] = None,
    search: Optional[str] = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    q = db.query(User).filter(User.role != "admin")
    if role in ("student", "recruiter"):
        q = q.filter(User.role == role)

    users = q.order_by(User.created_at.desc()).limit(200).all()
    # Search across email, profile name and company (Python-side: small dataset,
    # and profile fields live in separate tables).
    if search:
        needle = search.strip().lower()

        # Compare the search text against this account's combined identity fields.
        def matches(u: User, name: Optional[str], company: Optional[str]) -> bool:
            hay = " ".join(filter(None, [u.email, name, company])).lower()
            return needle in hay
    else:
        # Compare the search text against this account's combined identity fields.
        def matches(u: User, name: Optional[str], company: Optional[str]) -> bool:
            return True

    out = []
    for u in users:
        detail = {}
        full_name = u.email.split("@")[0].title()
        avatar_url = None
        if u.role == "student":
            s = u.student_profile
            if s:
                full_name = s.full_name
                avatar_url = s.avatar_url
                detail = {"university": s.university, "field": s.field_of_study,
                          "applications": db.query(Application).filter(Application.student_id == s.id).count()}
        elif u.role == "recruiter":
            r = u.recruiter_profile
            if r:
                full_name = r.full_name
                avatar_url = r.company_logo
                detail = {"company": r.company_name, "designation": r.designation,
                          "internships": db.query(Internship).filter(Internship.recruiter_id == r.id).count()}
        if not matches(u, full_name, detail.get("company")):
            continue
        out.append({
            "id": u.id, "email": u.email, "role": u.role, "is_active": u.is_active,
            "created_at": u.created_at, "full_name": full_name, "avatar_url": avatar_url,
            **detail,
        })
    return out


# Enable or disable a non-admin account. Protected requests check is_active
# again, so an existing token does not bypass account deactivation.
@router.put("/users/{user_id}/toggle-active")
def toggle_user(user_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.role != "admin").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_active = not user.is_active
    db.commit()
    return {"id": user.id, "is_active": user.is_active}


# Delete the selected non-admin ORM object; related deletions follow
# the model relationships and foreign-key constraints.
@router.delete("/users/{user_id}")
def delete_user(user_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.role != "admin").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    db.delete(user)  # cascades to profiles/applications/etc.
    db.commit()
    return {"message": f"User {user.email} removed."}


# ── Internships management ───────────────────────────────────────────────────

# Expose posting metadata and per-post application totals for admin review.
@router.get("/internships")
def list_all_internships(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    internships = db.query(Internship).order_by(Internship.created_at.desc()).all()
    out = []
    for i in internships:
        out.append({
            "id": i.id, "title": i.title, "company_name": i.company_name,
            "location": i.location, "mode": i.mode, "stipend_amount": i.stipend_amount,
            "stipend_currency": i.stipend_currency, "duration": i.duration,
            "is_active": i.is_active, "is_external": bool(i.is_external),
            "deadline": i.deadline, "created_at": i.created_at,
            "recruiter_name": i.recruiter_name,
            "applications": db.query(Application).filter(Application.internship_id == i.id).count(),
        })
    return out


# Change the posting's active flag without removing its stored records.
@router.put("/internships/{internship_id}/toggle")
def toggle_internship(internship_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    i = db.query(Internship).filter(Internship.id == internship_id).first()
    if not i:
        raise HTTPException(status_code=404, detail="Internship not found.")
    i.is_active = not i.is_active
    db.commit()
    return {"id": i.id, "is_active": i.is_active}


# Delete a posting selected by the administrator, including configured cascades.
@router.delete("/internships/{internship_id}")
def delete_internship(internship_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    i = db.query(Internship).filter(Internship.id == internship_id).first()
    if not i:
        raise HTTPException(status_code=404, detail="Internship not found.")
    db.delete(i)
    db.commit()
    return {"message": f"Internship '{i.title}' removed."}


# ── Applications feed ────────────────────────────────────────────────────────

# Return a bounded recent application feed with related candidate/job names.
@router.get("/applications")
def list_all_applications(
    limit: int = 100,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    apps = (
        db.query(Application).order_by(Application.applied_at.desc()).limit(min(limit, 500)).all()
    )
    out = []
    for a in apps:
        out.append({
            "id": a.id,
            "student_name": a.student.full_name if a.student else "Unknown",
            "student_email": a.student.user.email if a.student and a.student.user else None,
            "internship_title": a.internship.title if a.internship else "—",
            "company_name": a.internship.company_name if a.internship else "—",
            "status": a.status,
            "applied_at": a.applied_at,
            "has_resume": bool(a.resume_url),
        })
    return out


# ── Activity feed ─────────────────────────────────────────────────────────────

# Combine recent applications, postings, signups and interviews, sort them
# by timestamp, and return a limited feed. This is not a separate audit-log table.
@router.get("/activity")
def recent_activity(limit: int = 40, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Merged, time-sorted feed of the latest platform events."""
    events = []
    for a in db.query(Application).order_by(Application.applied_at.desc()).limit(30).all():
        events.append({
            "type": "application",
            "actor": a.student.full_name if a.student else "Unknown",
            "detail": f"applied for '{a.internship.title if a.internship else '—'}'"
                      + (f" at {a.internship.company_name}" if a.internship else ""),
            "at": a.applied_at,
        })
    for i in db.query(Internship).order_by(Internship.created_at.desc()).limit(20).all():
        events.append({
            "type": "internship",
            "actor": i.recruiter.full_name if i.recruiter else (i.recruiter_name or i.company_name),
            "detail": f"posted '{i.title}' at {i.company_name}",
            "at": i.created_at,
        })
    for u in db.query(User).filter(User.role != "admin").order_by(User.created_at.desc()).limit(20).all():
        name = u.email.split("@")[0].title()
        if u.role == "student" and u.student_profile:
            name = u.student_profile.full_name
        elif u.role == "recruiter" and u.recruiter_profile:
            name = u.recruiter_profile.full_name
        events.append({
            "type": "user",
            "actor": name,
            "detail": f"joined the platform as a {u.role}",
            "at": u.created_at,
        })
    for iv in db.query(Interview).order_by(Interview.created_at.desc()).limit(15).all():
        events.append({
            "type": "interview",
            "actor": iv.recruiter.full_name if iv.recruiter else "A recruiter",
            "detail": f"scheduled an interview for '{iv.internship.title if iv.internship else '—'}'",
            "at": iv.created_at,
        })
    events = [e for e in events if e["at"]]
    events.sort(key=lambda e: e["at"], reverse=True)
    return events[:min(limit, 100)]
