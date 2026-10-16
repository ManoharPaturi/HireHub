from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from app.db.database import get_db
from app.db.models import User, Message, Notification, Student, Application, Internship, RecruiterProfile
from app.schemas.schemas import MessageSchema, MessageCreateRequest, MessageContactSchema
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/messages", tags=["Messages"])


def _connected_user_ids(db: Session, current_user: User) -> set:
    """User ids the current user may message: recruiters of internships they
    applied to (for students) or students who applied to their internships
    (for recruiters)."""
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if student:
        ids = set()
        for app in db.query(Application).filter(Application.student_id == student.id).all():
            if app.internship and app.internship.recruiter and app.internship.recruiter.user_id:
                ids.add(app.internship.recruiter.user_id)
        return ids
    rp = db.query(RecruiterProfile).filter(RecruiterProfile.user_id == current_user.id).first()
    if rp:
        internship_ids = [i.id for i in db.query(Internship.id).filter(
            Internship.recruiter_id == rp.id).all()]
        if not internship_ids:
            return set()
        return {
            st.user_id for st in
            db.query(Student).join(Application, Application.student_id == Student.id)
            .filter(Application.internship_id.in_(internship_ids)).all()
            if st.user_id
        }
    return set()


def _last_message(db: Session, me: int, other: int):
    return db.query(Message).filter(
        or_(
            and_(Message.sender_id == me, Message.receiver_id == other),
            and_(Message.sender_id == other, Message.receiver_id == me),
        )
    ).order_by(desc(Message.sent_at)).first()


def _unread_count(db: Session, me: int, other: int) -> int:
    return db.query(Message).filter(
        Message.sender_id == other,
        Message.receiver_id == me,
        Message.is_read == False,  # noqa: E712
    ).count()


@router.get("/contacts", response_model=List[MessageContactSchema])
def get_contacts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """People the current user can message, derived from real applications:
    - student  → recruiters of internships they applied to
    - recruiter → students who applied to their internships
    Enriched with the most recent message preview + unread count."""
    rows: List[MessageContactSchema] = []
    seen = set()

    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if student:
        for app in db.query(Application).filter(Application.student_id == student.id).all():
            internship = app.internship
            if not internship or not internship.recruiter_id:
                continue
            rp = internship.recruiter  # RecruiterProfile
            if not rp or rp.user_id in seen:
                continue
            seen.add(rp.user_id)
            last = _last_message(db, current_user.id, rp.user_id)
            rows.append(MessageContactSchema(
                user_id=rp.user_id, full_name=rp.full_name,
                avatar_url=rp.company_logo, subtitle=f"{rp.designation or 'Recruiter'} · {rp.company_name}",
                internship_id=internship.id, internship_title=internship.title,
                last_message=last.content if last else None,
                last_at=last.sent_at if last else None,
                unread=_unread_count(db, current_user.id, rp.user_id),
            ))
    else:
        rp = db.query(RecruiterProfile).filter(RecruiterProfile.user_id == current_user.id).first()
        if rp:
            # All applications across this recruiter's internships.
            apps = (
                db.query(Application).join(Internship, Application.internship_id == Internship.id)
                .filter(Internship.recruiter_id == rp.id).all()
            )
            for app in apps:
                st = app.student
                if not st or st.user_id in seen:
                    continue
                seen.add(st.user_id)
                last = _last_message(db, current_user.id, st.user_id)
                rows.append(MessageContactSchema(
                    user_id=st.user_id, full_name=st.full_name,
                    avatar_url=st.avatar_url, subtitle=st.university or st.field_of_study or "Student",
                    internship_id=app.internship_id, internship_title=app.internship.title if app.internship else None,
                    last_message=last.content if last else None,
                    last_at=last.sent_at if last else None,
                    unread=_unread_count(db, current_user.id, st.user_id),
                ))

    # Contacts with a recent message first, then most recent activity.
    rows.sort(key=lambda c: (c.last_at is None, -(c.last_at.timestamp() if c.last_at else 0)))
    return rows


@router.get("/unread")
def total_unread(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Total unread messages addressed to the current user (for nav badges)."""
    count = db.query(Message).filter(
        Message.receiver_id == current_user.id,
        Message.is_read == False,  # noqa: E712
    ).count()
    return {"count": count}


@router.get("", response_model=List[MessageSchema])
def get_conversation(other_user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Conversation between the current user and another user, oldest first.
    Messages addressed to me are marked read on open."""
    if other_user_id not in _connected_user_ids(db, current_user):
        raise HTTPException(status_code=403, detail="You can only message users connected through an application.")
    messages = db.query(Message).filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == other_user_id),
            and_(Message.sender_id == other_user_id, Message.receiver_id == current_user.id),
        )
    ).order_by(Message.sent_at.asc()).all()

    changed = False
    for m in messages:
        if m.receiver_id == current_user.id and not m.is_read:
            m.is_read = True
            changed = True
    if changed:
        db.commit()
    return messages


@router.post("", response_model=MessageSchema)
def send_message(payload: MessageCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot send a message to yourself.")
    receiver = db.query(User).filter(User.id == payload.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Recipient not found.")
    # Only allow messaging users connected through a real application.
    if payload.receiver_id not in _connected_user_ids(db, current_user):
        raise HTTPException(status_code=403, detail="You can only message users connected through an application.")
    if not (payload.content or "").strip():
        raise HTTPException(status_code=422, detail="Message content cannot be empty.")

    msg = Message(sender_id=current_user.id, receiver_id=payload.receiver_id, content=payload.content.strip())
    db.add(msg)

    # Surface the message in the recipient's notification bell too.
    sender_name = current_user.email.split("@")[0].title()
    if current_user.role == "recruiter":
        sp = db.query(RecruiterProfile).filter(RecruiterProfile.user_id == current_user.id).first()
        if sp:
            sender_name = sp.full_name
    else:
        st = db.query(Student).filter(Student.user_id == current_user.id).first()
        if st:
            sender_name = st.full_name
    preview = msg.content if len(msg.content) <= 90 else msg.content[:87] + "…"
    db.add(Notification(
        user_id=receiver.id, title=f"New message from {sender_name} 💬",
        message=preview, type="message",
    ))
    db.commit()
    db.refresh(msg)
    return msg
