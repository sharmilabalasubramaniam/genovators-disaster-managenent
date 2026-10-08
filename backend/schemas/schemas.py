from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PersonBase(BaseModel):
    first_name: str
    last_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    distinguishing_features: Optional[str] = None
    photo_url: Optional[str] = None

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
    family_report: Optional[dict] = None
    hospital_record: Optional[dict] = None
    shelter_record: Optional[dict] = None
    rescue_record: Optional[dict] = None
    location: Optional[dict] = None

class CaseUpdate(BaseModel):
    status: Optional[str] = None

class FamilyReportBase(BaseModel):
    reporter_name: str
    reporter_contact: Optional[str] = None
    relationship_to_person: Optional[str] = None

class FamilyReport(FamilyReportBase):
    id: int
    case_id: int
    class Config:
        from_attributes = True

class HospitalRecordBase(BaseModel):
    hospital_name: str
    condition_summary: Optional[str] = None

class HospitalRecord(HospitalRecordBase):
    id: int
    case_id: int
    class Config:
        from_attributes = True

class ShelterRecordBase(BaseModel):
    shelter_name: str

class ShelterRecord(ShelterRecordBase):
    id: int
    case_id: int
    class Config:
        from_attributes = True

class LocationRecordBase(BaseModel):
    location_type: str
    address: str

class LocationRecord(LocationRecordBase):
    id: int
    case_id: int
    class Config:
        from_attributes = True

class RescueRecordBase(BaseModel):
    rescue_team: str
    rescue_location: Optional[str] = None

class RescueRecord(RescueRecordBase):
    id: int
    case_id: int
    class Config:
        from_attributes = True

class VerificationStartRequest(BaseModel):
    candidate_vrn_id: str

class EvidenceCreate(BaseModel):
    candidate_vrn_id: str
    evidence_type: str
    description: str
    url: Optional[str] = None

class VerificationActionRequest(BaseModel):
    reason: Optional[str] = None
    notes: Optional[str] = None

class MatchingResponse(BaseModel):
    case_id: str
    status: str
    candidates: List[dict]

class NotificationSchema(BaseModel):
    id: int
    case_id: Optional[int] = None
    notification_type: Optional[str] = None
    title: Optional[str] = None
    message: str
    priority: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    recipient_role: Optional[str] = None
    status: Optional[str] = None
    is_read: bool
    created_at: datetime
    class Config:
        from_attributes = True

class ReunificationSchema(BaseModel):
    id: int
    case_id: int
    status: str
    class Config:
        from_attributes = True

class ReunificationStartRequest(BaseModel):
    candidate_vrn_id: str

class ReunificationCompleteRequest(BaseModel):
    notes: Optional[str] = None


class Case(CaseBase):
    id: int
    vrn_id: str
    created_at: datetime
    updated_at: datetime
    person: Person
    family_reports: List[FamilyReport] = []
    hospital_records: List[HospitalRecord] = []
    shelter_records: List[ShelterRecord] = []
    rescue_records: List[RescueRecord] = []
    location_records: List[LocationRecord] = []
    class Config:
        from_attributes = True
