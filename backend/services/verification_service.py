from sqlalchemy.orm import Session
from datetime import datetime
from backend.models import models
from fastapi import HTTPException
import json

EVIDENCE_WEIGHTS = {
    "AI_MATCH": 0.25,
    "NAME": 0.20,
    "LOCATION": 0.15,
    "TIME": 0.10,
    "PHYSICAL": 0.10,
    "ORGANIZATION": 0.10,
    "AGE": 0.10
}

def create_audit_log(db: Session, case_id: int, action: str, performed_by: str = "System"):
    log = models.AuditLog(
        case_id=case_id,
        action=action,
        performed_by=performed_by
    )
    db.add(log)
    db.flush()

def start_verification(db: Session, case_id: int, candidate_case_id: int, user: str = "Authorized Officer"):
    # Check if verification already exists
    existing = db.query(models.Verification).filter(
        models.Verification.case_id == case_id,
        models.Verification.candidate_id == candidate_case_id,
        models.Verification.status.in_(["PENDING", "IN_REVIEW", "MORE_EVIDENCE_REQUIRED"])
    ).first()
    
    if existing:
        return existing
        
    verification = models.Verification(
        case_id=case_id,
        candidate_id=candidate_case_id,
        step="Multi-Factor Verification",
        status="IN_REVIEW"
    )
    db.add(verification)
    
    # MatchResult removed to fix AttributeError
        
    create_audit_log(db, case_id, f"Started verification for candidate {candidate_case_id}", user)
    
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if case:
        case.status = models.CaseStatus.IN_VERIFICATION.value
        
    db.commit()
    db.refresh(verification)
    return verification

def get_verification_status(db: Session, case_id: int):
    verifications = db.query(models.Verification).filter(models.Verification.case_id == case_id).all()
    evidence = db.query(models.Evidence).filter(models.Evidence.case_id == case_id).all()
    
    return {
        "verifications": verifications,
        "evidence": evidence
    }

def add_evidence(db: Session, case_id: int, candidate_case_id: int, ev_data: dict, user: str = "Authorized Officer"):
    ev = models.Evidence(
        case_id=case_id,
        candidate_id=candidate_case_id,
        evidence_type=ev_data["evidence_type"],
        source=ev_data.get("source"),
        url=ev_data.get("url"),
        description=ev_data.get("description", ""),
        status=ev_data.get("status", "PENDING"),
        created_by=user
    )
    db.add(ev)
    create_audit_log(db, case_id, f"Added {ev_data.get('status', 'PENDING')} evidence: {ev_data.get('evidence_type', '')}", user)
    db.commit()
    db.refresh(ev)
    return ev

def request_more_evidence(db: Session, case_id: int, notes: str, user: str = "Authorized Officer"):
    ver = db.query(models.Verification).filter(
        models.Verification.case_id == case_id,
        models.Verification.status == "IN_REVIEW"
    ).first()
    
    if not ver:
        raise HTTPException(status_code=400, detail="No active verification found to request evidence for.")
        
    ver.status = "MORE_EVIDENCE_REQUIRED"
    if notes:
        ver.notes = notes
        
    create_audit_log(db, case_id, f"Requested more evidence. Notes: {notes}", user)
    db.commit()
    return ver

def approve_verification(db: Session, case_id: int, user: str = "Authorized Officer"):
    ver = db.query(models.Verification).filter(
        models.Verification.case_id == case_id,
        models.Verification.status.in_(["IN_REVIEW", "MORE_EVIDENCE_REQUIRED"])
    ).first()
    
    if not ver:
        raise HTTPException(status_code=400, detail="No active verification found to approve.")
        
    ver.status = "VERIFIED"
    ver.verified_by = user
    ver.verified_at = datetime.utcnow()
    
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if case:
        case.status = models.CaseStatus.VERIFIED.value
        
    candidate_case = db.query(models.Case).filter(models.Case.id == ver.candidate_id).first()
    if candidate_case:
        candidate_case.status = models.CaseStatus.VERIFIED.value
        
    create_audit_log(db, case_id, f"Approved candidate verification.", user)
    db.commit()
    return ver

def reject_verification(db: Session, case_id: int, reason: str, user: str = "Authorized Officer"):
    ver = db.query(models.Verification).filter(
        models.Verification.case_id == case_id,
        models.Verification.status.in_(["IN_REVIEW", "MORE_EVIDENCE_REQUIRED"])
    ).first()
    
    if not ver:
        raise HTTPException(status_code=400, detail="No active verification found to reject.")
        
    ver.status = "REJECTED"
    ver.notes = reason
    ver.verified_by = user
    ver.verified_at = datetime.utcnow()
    
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if case:
        case.status = models.CaseStatus.IN_PROGRESS.value # Revert back to matching possible
        
    create_audit_log(db, case_id, f"Rejected candidate verification. Reason: {reason}", user)
    db.commit()
    return ver

def calculate_strength(db: Session, case_id: int, candidate_case_id: int):
    evidence = db.query(models.Evidence).filter(
        models.Evidence.case_id == case_id,
        models.Evidence.candidate_id == candidate_case_id
    ).all()
    
    total_weight = 0.0
    score = 0.0
    conflicts = 0
    factors_supported = 0
    total_factors = 0
    
    # Use latest evidence per type
    latest_evidence = {}
    for ev in evidence:
        latest_evidence[ev.evidence_type] = ev
        
    for ev_type, ev in latest_evidence.items():
        weight = EVIDENCE_WEIGHTS.get(ev_type, 0.05)
        total_weight += weight
        total_factors += 1
        
        if ev.status == "SUPPORTED":
            score += weight
            factors_supported += 1
        elif ev.status == "PARTIAL":
            score += (weight * 0.5)
        elif ev.status == "CONFLICT":
            conflicts += 1
            
    final_score = (score / total_weight) if total_weight > 0 else 0.0
    
    return {
        "strength_score": final_score,
        "conflicts": conflicts,
        "factors_supported": factors_supported,
        "total_factors": total_factors,
        "evidence_list": [
            {
                "id": ev.id,
                "type": ev.evidence_type,
                "status": ev.status,
                "description": ev.description,
                "source": ev.source,
                "url": ev.url,
                "uploaded_at": ev.uploaded_at
            } for ev in latest_evidence.values()
        ]
    }
