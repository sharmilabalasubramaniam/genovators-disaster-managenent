from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models import models
from backend.schemas import schemas
from backend.services.reunification_service import ReunificationService
from backend.api.verification import get_case_id_by_vrn

router = APIRouter(prefix="/api/reunification", tags=["reunification"])

@router.get("/{vrn_id}", response_model=schemas.ReunificationSchema)
def get_reunification_info(vrn_id: str, db: Session = Depends(get_db)):
    case_id = get_case_id_by_vrn(db, vrn_id)
    reunification = ReunificationService.get_reunification(db, case_id)
    
    if not reunification:
        case = db.query(models.Case).filter(models.Case.id == case_id).first()
        if case and case.status == "VERIFIED":
            reunification = ReunificationService.create_or_get_reunification(db, case_id)
        else:
            raise HTTPException(status_code=404, detail="Reunification record not found or case not ready")
            
    return reunification

@router.post("/{vrn_id}/start", response_model=schemas.ReunificationSchema)
def start_reunification(vrn_id: str, request: schemas.ReunificationStartRequest, db: Session = Depends(get_db)):
    case_id = get_case_id_by_vrn(db, vrn_id)
    return ReunificationService.start_reunification(db, case_id, request)

@router.post("/{vrn_id}/complete", response_model=schemas.ReunificationSchema)
def complete_reunification(vrn_id: str, request: schemas.ReunificationCompleteRequest, db: Session = Depends(get_db)):
    case_id = get_case_id_by_vrn(db, vrn_id)
    return ReunificationService.complete_reunification(db, case_id, request)

@router.post("/{vrn_id}/cancel", response_model=schemas.ReunificationSchema)
def cancel_reunification(vrn_id: str, request: schemas.VerificationActionRequest, db: Session = Depends(get_db)):
    case_id = get_case_id_by_vrn(db, vrn_id)
    reason = request.reason or request.notes or "Cancelled"
    return ReunificationService.cancel_reunification(db, case_id, reason)
