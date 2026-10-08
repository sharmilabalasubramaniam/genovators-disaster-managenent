from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum, Float
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from backend.database.db import Base

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    OFFICER = "OFFICER"
    FAMILY = "FAMILY"
    HOSPITAL = "HOSPITAL"
    SHELTER = "SHELTER"
    RESCUE = "RESCUE"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=UserRole.FAMILY.value)
    name = Column(String, default="")
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
    photo_url = Column(String, nullable=True)
    
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
    evidence = relationship("Evidence", foreign_keys="[Evidence.case_id]", back_populates="case")
    verifications = relationship("Verification", foreign_keys="[Verification.case_id]", back_populates="case")
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
    source = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    candidate_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("Case", foreign_keys=[case_id], back_populates="evidence")

class Verification(Base):
    __tablename__ = "verifications"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    candidate_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    step = Column(String) # AI Match, Timeline Check, Auth
    status = Column(String) # Pending, Approved, Rejected
    notes = Column(String, nullable=True)
    verified_by = Column(String, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    case = relationship("Case", foreign_keys=[case_id], back_populates="verifications")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    notification_type = Column(String, nullable=True)
    title = Column(String, nullable=True)
    message = Column(String)
    priority = Column(String, default="LOW")
    related_entity_type = Column(String, nullable=True)
    related_entity_id = Column(Integer, nullable=True)
    recipient_role = Column(String, default="OFFICER")
    status = Column(String, default="UNREAD")
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

class MatchResult(Base):
    __tablename__ = "match_results"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    candidate_case_id = Column(Integer, ForeignKey("cases.id"))
    score = Column(Float)
    confidence = Column(String)
    signals = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
