from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models import models
from pydantic import BaseModel

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

class DashboardStats(BaseModel):
    active_cases: int
    missing_persons: int
    potential_matches: int
    in_verification: int
    verified: int
    reunification_in_progress: int
    reunited: int
    total_organizations: int
    total_locations: int

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    # Active cases = New, In Progress, In Verification, Verified, Reunification In Progress
    active_statuses = ["New", "In Progress", "In Verification", "Verified", "REUNIFICATION_IN_PROGRESS"]
    active_cases = db.query(models.Case).filter(models.Case.status.in_(active_statuses)).count()
    
    missing_persons = db.query(models.FamilyReport).count()
    
    # Potential matches = Cases with MatchResults where score > threshold, status not in VERIFIED, REUNITED, CANCELLED
    # For now, just count cases that are MATCH_FOUND (handled via Case status perhaps) or just all MatchResults
    # Let's count cases that have status "MATCH_FOUND" if it exists, otherwise count matches.
    potential_matches = db.query(models.MatchResult).count()
    
    in_verification = db.query(models.Case).filter(models.Case.status == "In Verification").count()
    
    verified = db.query(models.Case).filter(models.Case.status == "Verified").count()
    
    reunification_in_progress = db.query(models.Case).filter(models.Case.status == "REUNIFICATION_IN_PROGRESS").count()
    
    reunited = db.query(models.Case).filter(models.Case.status.in_(["Reunified", "REUNITED"])).count()
    
    total_organizations = (db.query(models.HospitalRecord).count() + 
                           db.query(models.ShelterRecord).count() + 
                           db.query(models.RescueRecord).count())
                           
    total_locations = db.query(models.LocationRecord).count()
    
    return {
        "active_cases": active_cases,
        "missing_persons": missing_persons,
        "potential_matches": potential_matches,
        "in_verification": in_verification,
        "verified": verified,
        "reunification_in_progress": reunification_in_progress,
        "reunited": reunited,
        "total_organizations": total_organizations,
        "total_locations": total_locations
    }
