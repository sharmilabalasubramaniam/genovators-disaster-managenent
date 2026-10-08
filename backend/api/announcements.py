from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models import models
from backend.schemas import schemas
from datetime import datetime

router = APIRouter(prefix="/api/announcements", tags=["Announcements"])

@router.get("/")
def get_announcements(db: Session = Depends(get_db)):
    # In a real system, there would be a dedicated Announcement model.
    # For now, we'll derive published announcements from Reunified / Reunification Ready cases.
    cases = db.query(models.Case).filter(
        models.Case.status.in_(["Reunification Ready", "Reunification In Progress", "Reunified"])
    ).order_by(models.Case.updated_at.desc()).all()
    
    announcements = []
    for c in cases:
        announcements.append({
            "id": f"ANN-{c.id}",
            "case_id": c.vrn_id,
            "person_name": f"{c.person.first_name} {c.person.last_name}",
            "status": c.status,
            "date": c.updated_at,
            "details": f"Missing person {c.person.first_name} has been verified and is ready for reunification.",
            "contact": "Contact the local Command Center for more details."
        })
    return announcements

@router.post("/{case_vrn_id}/publish")
def publish_announcement(case_vrn_id: str, db: Session = Depends(get_db)):
    case = db.query(models.Case).filter(models.Case.vrn_id == case_vrn_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if case.status not in ["Verified", "Reunification Ready"]:
        raise HTTPException(status_code=400, detail="Only verified cases can be published.")
        
    # Mark it ready if it's verified
    if case.status == "Verified":
        case.status = "Reunification Ready"
        case.updated_at = datetime.utcnow()
        db.commit()
        
    return {"status": "success", "message": "Announcement published"}
