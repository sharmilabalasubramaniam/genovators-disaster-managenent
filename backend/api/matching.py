from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.schemas import schemas
from backend.services.matching.matching_engine import run_matching_for_case
from backend.services.notification_service import NotificationService
from backend.models import models

router = APIRouter(prefix="/api/matching", tags=["Matching"])

@router.post("/{vrn_id}/run", response_model=schemas.MatchingResponse)
def run_matching(vrn_id: str, db: Session = Depends(get_db)):
    case = db.query(models.Case).filter(models.Case.vrn_id == vrn_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    candidates = run_matching_for_case(db, case.id)
    if candidates is None:
        raise HTTPException(status_code=400, detail="Cannot run matching on this case")
        
    if candidates and len(candidates) > 0:
        top_score = candidates[0].get("score", 0.0)
        top_vrn = candidates[0].get("record_id", "Unknown")
        NotificationService.notify_match_found(db, case.id, case.vrn_id, top_vrn, top_score)
        
    return {
        "case_id": vrn_id,
        "status": "MATCHING_COMPLETE",
        "candidates": candidates
    }
