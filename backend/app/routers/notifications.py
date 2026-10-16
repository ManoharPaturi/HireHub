# Stored notification API. Notifications belong to a user account rather than
# to a browser session, and is_read persists whether that account opened an alert.

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Notification
from app.schemas.schemas import NotificationSchema
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

# Filter by the signed-in user ID so each bell shows only its own alerts.
@router.get("", response_model=List[NotificationSchema])
def get_user_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()


# Match the notification ID and owner together, then persist its read flag.
@router.put("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    db.commit()
    return {"message": "Notification marked as read."}
