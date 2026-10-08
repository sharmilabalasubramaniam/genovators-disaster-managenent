from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models import models
from backend.schemas import schemas
from typing import List, Dict, Any
from .cases import get_case_by_identifier

router = APIRouter(prefix="/api/locations", tags=["locations"])

@router.get("/case/{case_id}")
def get_case_locations(case_id: str, db: Session = Depends(get_db)):
    db_case = get_case_by_identifier(case_id, db)
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    locations = db.query(models.LocationRecord).filter(
        models.LocationRecord.case_id == db_case.id
    ).order_by(models.LocationRecord.recorded_at.asc()).all()
    
    result = []
    for loc in locations:
        result.append({
            "type": loc.location_type,
            "name": getattr(loc, 'location_name', loc.address),
            "latitude": getattr(loc, 'latitude', 28.6139), # Defaulting to India if none
            "longitude": getattr(loc, 'longitude', 77.2090),
            "timestamp": loc.recorded_at,
            "source": getattr(loc, 'source', "System")
        })
        
    return {
        "case_id": db_case.vrn_id,
        "locations": result
    }

@router.get("/")
def get_all_locations(db: Session = Depends(get_db)):
    locations = db.query(models.LocationRecord).join(models.Case).order_by(models.LocationRecord.recorded_at.desc()).all()
    
    result = []
    for loc in locations:
        lat = getattr(loc, 'latitude', 28.6139)
        lon = getattr(loc, 'longitude', 77.2090)
        if lat is not None and lon is not None:
            result.append({
                "case_id": loc.case.vrn_id,
                "type": loc.location_type,
                "name": getattr(loc, 'location_name', loc.address),
                "latitude": lat,
                "longitude": lon,
                "timestamp": loc.recorded_at,
                "source": getattr(loc, 'source', "System"),
                "status": loc.case.status
            })
            
    return result
