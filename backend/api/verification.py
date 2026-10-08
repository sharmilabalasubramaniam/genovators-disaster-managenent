from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.schemas import schemas
from backend.services import verification_service
from backend.services.notification_service import NotificationService
from backend.models import models

router = APIRouter(prefix="/api/verification", tags=["verification"])

def get_case_id_by_vrn(db: Session, vrn_id: str) -> int:
    case = db.query(models.Case).filter(models.Case.vrn_id == vrn_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case.id

@router.post("/{vrn_id}/start")
def start_verification(vrn_id: str, request: schemas.VerificationStartRequest, db: Session = Depends(get_db)):
    case_id = get_case_id_by_vrn(db, vrn_id)
    candidate_case_id = get_case_id_by_vrn(db, request.candidate_vrn_id)
    
    ver = verification_service.start_verification(db, case_id, candidate_case_id)
    NotificationService.notify_verification_started(db, case_id, vrn_id)
    return {"status": "success", "verification_id": ver.id}

@router.get("/{vrn_id}/candidate/{candidate_vrn_id}")
def get_verification(vrn_id: str, candidate_vrn_id: str, db: Session = Depends(get_db)):
    case_id = get_case_id_by_vrn(db, vrn_id)
    candidate_case_id = get_case_id_by_vrn(db, candidate_vrn_id)
    
    ver = db.query(models.Verification).filter(
        models.Verification.case_id == case_id,
        models.Verification.candidate_id == candidate_case_id
    ).order_by(models.Verification.id.desc()).first()
    
    if not ver:
        return {"status": "NOT_STARTED"}
        
    strength = verification_service.calculate_strength(db, case_id, candidate_case_id)
    
    # fetch the models to get photo URLs
    family_case = db.query(models.Case).filter(models.Case.id == case_id).first()
    candidate_case = db.query(models.Case).filter(models.Case.id == candidate_case_id).first()
    
    return {
        "status": ver.status,
        "verification_id": ver.id,
        "step": ver.step,
        "notes": ver.notes,
        "strength": strength,
        "case_photo_url": family_case.person.photo_url if family_case and family_case.person else None,
        "candidate_photo_url": candidate_case.person.photo_url if candidate_case and candidate_case.person else None
    }

@router.post("/{vrn_id}/evidence")
def add_evidence(vrn_id: str, request: schemas.EvidenceCreate, db: Session = Depends(get_db)):
    case_id = get_case_id_by_vrn(db, vrn_id)
    candidate_case_id = get_case_id_by_vrn(db, request.candidate_vrn_id)
    
    ev_data = request.model_dump()
    verification_service.add_evidence(db, case_id, candidate_case_id, ev_data)
    
    return {"status": "success"}

@router.post("/{vrn_id}/request-evidence")
def request_more_evidence(vrn_id: str, request: schemas.VerificationActionRequest, db: Session = Depends(get_db)):
    case_id = get_case_id_by_vrn(db, vrn_id)
    ver = verification_service.request_more_evidence(db, case_id, request.notes)
    NotificationService.notify_evidence_requested(db, case_id, vrn_id)
    return {"status": "success", "verification_status": ver.status}

@router.post("/{vrn_id}/approve")
def approve_verification(vrn_id: str, db: Session = Depends(get_db)):
    case_id = get_case_id_by_vrn(db, vrn_id)
    ver = verification_service.approve_verification(db, case_id)
    NotificationService.notify_case_verified(db, case_id, vrn_id)
    return {"status": "success", "verification_status": ver.status}

@router.post("/{vrn_id}/reject")
def reject_verification(vrn_id: str, request: schemas.VerificationActionRequest, db: Session = Depends(get_db)):
    case_id = get_case_id_by_vrn(db, vrn_id)
    if not request.reason:
        raise HTTPException(status_code=400, detail="Reason is required to reject.")
    ver = verification_service.reject_verification(db, case_id, request.reason)
    NotificationService.notify_case_rejected(db, case_id, vrn_id)
    return {"status": "success", "verification_status": ver.status}
