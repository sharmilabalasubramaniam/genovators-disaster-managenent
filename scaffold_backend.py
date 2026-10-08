import os

backend_files = {
    "backend/models/models.py": """from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from backend.database.db import Base

class CaseStatus(str, enum.Enum):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    IN_VERIFICATION = "In Verification"
    VERIFIED = "Verified"
    REUNIFIED = "Reunified"

class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    distinguishing_features = Column(String, nullable=True)
    
    cases = relationship("Case", back_populates="person")

class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, index=True)
    vrn_id = Column(String, unique=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"))
    status = Column(String, default=CaseStatus.NEW.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    person = relationship("Person", back_populates="cases")
    family_reports = relationship("FamilyReport", back_populates="case")
    hospital_records = relationship("HospitalRecord", back_populates="case")
    shelter_records = relationship("ShelterRecord", back_populates="case")
    rescue_records = relationship("RescueRecord", back_populates="case")
    location_records = relationship("LocationRecord", back_populates="case")
    evidence = relationship("Evidence", back_populates="case")
    verifications = relationship("Verification", back_populates="case")
    audit_logs = relationship("AuditLog", back_populates="case")

class FamilyReport(Base):
    __tablename__ = "family_reports"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    reporter_name = Column(String)
    reporter_contact = Column(String)
    relationship_to_person = Column(String)
    reported_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("Case", back_populates="family_reports")

class HospitalRecord(Base):
    __tablename__ = "hospital_records"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    hospital_name = Column(String)
    admission_date = Column(DateTime)
    condition_summary = Column(String)
    
    case = relationship("Case", back_populates="hospital_records")

class ShelterRecord(Base):
    __tablename__ = "shelter_records"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    shelter_name = Column(String)
    check_in_date = Column(DateTime)
    
    case = relationship("Case", back_populates="shelter_records")

class RescueRecord(Base):
    __tablename__ = "rescue_records"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    rescue_team = Column(String)
    rescue_date = Column(DateTime)
    rescue_location = Column(String)
    
    case = relationship("Case", back_populates="rescue_records")

class LocationRecord(Base):
    __tablename__ = "location_records"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    location_type = Column(String) # Last Known, Found, Shelter, Hospital
    address = Column(String)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("Case", back_populates="location_records")

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    evidence_type = Column(String) # Photo, Document, Item
    description = Column(String)
    url = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("Case", back_populates="evidence")

class Verification(Base):
    __tablename__ = "verifications"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    step = Column(String) # AI Match, Timeline Check, Auth
    status = Column(String) # Pending, Approved, Rejected
    verified_by = Column(String, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    case = relationship("Case", back_populates="verifications")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    message = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    action = Column(String)
    performed_by = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("Case", back_populates="audit_logs")
""",
    "backend/schemas/schemas.py": """from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PersonBase(BaseModel):
    first_name: str
    last_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    distinguishing_features: Optional[str] = None

class PersonCreate(PersonBase):
    pass

class Person(PersonBase):
    id: int
    class Config:
        from_attributes = True

class CaseBase(BaseModel):
    status: str

class CaseCreate(CaseBase):
    person: PersonCreate

class CaseUpdate(BaseModel):
    status: Optional[str] = None

class Case(CaseBase):
    id: int
    vrn_id: str
    created_at: datetime
    updated_at: datetime
    person: Person
    class Config:
        from_attributes = True
""",
    "backend/api/cases.py": """from fastapi import APIRouter, Depends, HTTPException
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
    db.commit()
    db.refresh(db_case)
    return db_case

@router.get("/", response_model=List[schemas.Case])
def read_cases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cases = db.query(models.Case).offset(skip).limit(limit).all()
    return cases

@router.get("/{case_id}", response_model=schemas.Case)
def read_case(case_id: int, db: Session = Depends(get_db)):
    db_case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if db_case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return db_case

@router.patch("/{case_id}", response_model=schemas.Case)
def update_case(case_id: int, case: schemas.CaseUpdate, db: Session = Depends(get_db)):
    db_case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if db_case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if case.status:
        db_case.status = case.status
    db.commit()
    db.refresh(db_case)
    return db_case
""",
    "backend/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.db import engine, Base
from backend.api import cases

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Verified Reunification Network API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases.router)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}
""",
    "backend/database/seed.py": """import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy.orm import Session
from backend.database.db import SessionLocal, engine, Base
from backend.models import models
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

def seed_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    statuses = ["New", "In Progress", "In Verification", "Verified", "Reunified"]
    organizations = ["Shelter A", "Hospital B", "Rescue Team 3", "Shelter C", "Hospital C"]
    
    for i in range(5):
        # Create Person
        person = models.Person(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            age=random.randint(5, 75),
            gender=random.choice(["Male", "Female"]),
            distinguishing_features="None"
        )
        db.add(person)
        db.flush()
        
        # Create Case
        vrn_id = f"VRN-{4000 + i}"
        status = random.choice(statuses)
        case = models.Case(
            vrn_id=vrn_id,
            person_id=person.id,
            status=status,
            created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
        )
        db.add(case)
        db.flush()
        
        # Create Family Report
        if random.choice([True, False]):
            fam_report = models.FamilyReport(
                case_id=case.id,
                reporter_name=fake.name(),
                reporter_contact=fake.phone_number(),
                relationship_to_person=random.choice(["Parent", "Sibling", "Spouse"])
            )
            db.add(fam_report)
            
        # Create Location Record
        loc_record = models.LocationRecord(
            case_id=case.id,
            location_type=random.choice(["Shelter", "Hospital", "Rescue"]),
            address=random.choice(organizations)
        )
        db.add(loc_record)
        
        # Create Verification
        ver = models.Verification(
            case_id=case.id,
            step="Timeline & Evidence Check",
            status=random.choice(["Pending", "Approved"])
        )
        db.add(ver)
        
    db.commit()
    print("Database seeded with 5 synthetic cases.")
    db.close()

if __name__ == "__main__":
    seed_data()
""",
    "frontend/src/pages/Cases.jsx": """import React, { useEffect, useState } from 'react';
import { ChevronRight } from 'lucide-react';
import api from '../services/api';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

export default function Cases() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get('/cases')
      .then(res => {
        setCases(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="rounded-2xl bg-white p-6 shadow-sm">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-lg font-bold">All Cases</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-border text-text-muted">
              <th className="pb-4 font-medium">ID</th>
              <th className="pb-4 font-medium">Person</th>
              <th className="pb-4 font-medium">Status</th>
              <th className="pb-4 font-medium">Last Update</th>
              <th className="pb-4"></th>
            </tr>
          </thead>
          <tbody>
            {cases.map((c) => (
              <tr key={c.id} className="border-b border-border hover:bg-gray-50/50">
                <td className="py-4 font-semibold text-primary">{c.vrn_id}</td>
                <td className="py-4">
                  <div className="flex flex-col">
                    <span className="font-semibold text-text-main">{c.person.first_name} {c.person.last_name}</span>
                    <span className="text-xs text-text-muted">{c.person.gender}, {c.person.age}</span>
                  </div>
                </td>
                <td className="py-4">
                  <span className="rounded-full px-3 py-1.5 text-xs font-semibold bg-gray-100">{c.status}</span>
                </td>
                <td className="py-4 text-text-main">
                  {new Date(c.updated_at).toLocaleDateString()}
                </td>
                <td className="py-4 text-right">
                  <ChevronRight className="ml-auto h-4 w-4 cursor-pointer text-text-muted" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
"""
}

for path, content in backend_files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
