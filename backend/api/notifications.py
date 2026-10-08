from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models import models
from backend.schemas import schemas
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.get("/", response_model=List[schemas.NotificationSchema])
def get_notifications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Assuming role is OFFICER for now
    notifications = db.query(models.Notification).order_by(models.Notification.created_at.desc()).offset(skip).limit(limit).all()
    return notifications

@router.get("/unread", response_model=List[schemas.NotificationSchema])
def get_unread_notifications(db: Session = Depends(get_db)):
    notifications = db.query(models.Notification).filter(models.Notification.status == "UNREAD").order_by(models.Notification.created_at.desc()).all()
    return notifications

@router.get("/{notification_id}", response_model=schemas.NotificationSchema)
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.patch("/{notification_id}/read", response_model=schemas.NotificationSchema)
def mark_read(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    notification.status = "READ"
    notification.read_at = datetime.utcnow()
    db.commit()
    db.refresh(notification)
    return notification

@router.patch("/{notification_id}/archive", response_model=schemas.NotificationSchema)
def archive_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.status = "ARCHIVED"
    db.commit()
    db.refresh(notification)
    return notification

@router.patch("/read-all/all")
def mark_all_read(db: Session = Depends(get_db)):
    notifications = db.query(models.Notification).filter(models.Notification.status == "UNREAD").all()
    now = datetime.utcnow()
    for notif in notifications:
        notif.is_read = True
        notif.status = "READ"
        notif.read_at = now
    db.commit()
    return {"status": "success", "marked_read": len(notifications)}

@router.get("/case/{case_id}", response_model=List[schemas.NotificationSchema])
def get_case_notifications(case_id: int, db: Session = Depends(get_db)):
    notifications = db.query(models.Notification).filter(models.Notification.case_id == case_id).order_by(models.Notification.created_at.desc()).all()
    return notifications
