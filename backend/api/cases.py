from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models import models
from backend.schemas import schemas
from typing import List

router = APIRouter(prefix="/api/cases", tags=["cases"])

@router.post("/", response_model=schemas.Case)
def create_case(case: schemas.CaseCreate, db: Session = Depends(get_db)):
    # Create person
    db_person = models.Person(**case.person.dict())
    db.add(db_person)
    db.flush() # get person.id
    
    # generate next vrn_id
    last_case = db.query(models.Case).order_by(models.Case.id.desc()).first()
    next_num = 1000 if not last_case else int(last_case.vrn_id.split("-")[1]) + 1
    vrn_id = f"VRN-{next_num}"
    
    db_case = models.Case(vrn_id=vrn_id, person_id=db_person.id, status=case.status)
    db.add(db_case)
    db.flush()

    if case.family_report:
        db_family_report = models.FamilyReport(**case.family_report, case_id=db_case.id)
        db.add(db_family_report)
    
    if case.hospital_record:
        db_hospital = models.HospitalRecord(**case.hospital_record, case_id=db_case.id)
        db.add(db_hospital)

    if case.shelter_record:
        db_shelter = models.ShelterRecord(**case.shelter_record, case_id=db_case.id)
        db.add(db_shelter)
        
    if case.rescue_record:
        db_rescue = models.RescueRecord(**case.rescue_record, case_id=db_case.id)
        db.add(db_rescue)

    if case.location:
        db_location = models.LocationRecord(**case.location, case_id=db_case.id)
        db.add(db_location)

    db.commit()
    db.refresh(db_case)
    return db_case

@router.get("/", response_model=List[schemas.Case])
def read_cases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cases = db.query(models.Case).offset(skip).limit(limit).all()
    return cases

def get_case_by_identifier(identifier: str, db: Session) -> models.Case:
    if str(identifier).startswith("VRN-"):
        case = db.query(models.Case).filter(models.Case.vrn_id == identifier).first()
    else:
        try:
            case_id_int = int(identifier)
            case = db.query(models.Case).filter(models.Case.id == case_id_int).first()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid identifier format")
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.get("/{identifier}", response_model=schemas.Case)
def read_case(identifier: str, db: Session = Depends(get_db)):
    return get_case_by_identifier(identifier, db)

@router.patch("/{identifier}", response_model=schemas.Case)
def update_case(identifier: str, case: schemas.CaseUpdate, db: Session = Depends(get_db)):
    db_case = get_case_by_identifier(identifier, db)
    
    if case.status:
        db_case.status = case.status
    if case.photo_url:
        db_case.person.photo_url = case.photo_url
        
    db.commit()
    db.refresh(db_case)
    return db_case
