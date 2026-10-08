from sqlalchemy.orm import Session
from backend.models import models
from backend.schemas import schemas
from datetime import datetime
from fastapi import HTTPException

class ReunificationService:
    @staticmethod
    def get_reunification(db: Session, case_id: int):
        return db.query(models.Reunification).filter(models.Reunification.case_id == case_id).first()

    @staticmethod
    def create_or_get_reunification(db: Session, case_id: int):
        reunification = ReunificationService.get_reunification(db, case_id)
        if not reunification:
            reunification = models.Reunification(
                case_id=case_id,
                status="REUNIFICATION_READY"
            )
            db.add(reunification)
            db.commit()
            db.refresh(reunification)
        return reunification

    @staticmethod
    def start_reunification(db: Session, case_id: int, request: schemas.ReunificationStartRequest):
        case = db.query(models.Case).filter(models.Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        if case.status != "Verified" and case.status != "Reunification Ready":
            raise HTTPException(status_code=400, detail=f"Cannot start reunification for case in {case.status} state")

        reunification = ReunificationService.create_or_get_reunification(db, case_id)
        
        reunification.status = "IN_PROGRESS"
        reunification.meeting_location = request.meeting_location
        reunification.family_contact = request.family_contact
        reunification.officer_in_charge = request.officer_in_charge
        reunification.notes = request.notes
        reunification.scheduled_time = request.scheduled_time
        case.status = "Reunification In Progress"
        
        db.commit()
        db.refresh(reunification)
        
        from backend.services.notification_service import NotificationService
        NotificationService.create_notification(db, case.id, "REUNIFICATION_STARTED", "Reunification Started", f"Reunification in progress for VRN: {case.vrn_id}.", "HIGH")
        
        return reunification

    @staticmethod
    def complete_reunification(db: Session, case_id: int, request: schemas.ReunificationCompleteRequest):
        case = db.query(models.Case).filter(models.Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        reunification = ReunificationService.get_reunification(db, case_id)
        if not reunification:
            raise HTTPException(status_code=404, detail="Reunification record not found")
            
        reunification.status = "REUNITED"
        if request.notes:
            reunification.notes = (reunification.notes or "") + "\n\nCompletion notes: " + request.notes
        reunification.completed_time = datetime.utcnow()
        
        case.status = "Reunified"
        
        db.commit()
        db.refresh(reunification)
        
        from backend.services.notification_service import NotificationService
        NotificationService.create_notification(db, case.id, "REUNITED", "Case Reunited", f"Successfully reunited for VRN: {case.vrn_id}.", "HIGH")
        
        return reunification

    @staticmethod
    def cancel_reunification(db: Session, case_id: int, reason: str):
        case = db.query(models.Case).filter(models.Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
            
        reunification = ReunificationService.get_reunification(db, case_id)
        if not reunification:
            raise HTTPException(status_code=404, detail="Reunification record not found")
            
        reunification.status = "CANCELLED"
        reunification.notes = (reunification.notes or "") + f"\n\nCANCELLED. Reason: {reason}"
        
        case.status = "Verified" # Revert to Verified
        
        db.commit()
        db.refresh(reunification)
        
        from backend.services.notification_service import NotificationService
        NotificationService.create_notification(db, case.id, "REUNIFICATION_CANCELLED", "Reunification Cancelled", f"Reunification cancelled for VRN: {case.vrn_id}.", "HIGH")
        
        return reunification
