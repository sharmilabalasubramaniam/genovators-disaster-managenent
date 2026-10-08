from typing import Optional

from pydantic import BaseModel, Field


class PersonRecord(BaseModel):
    record_id: str
    source_type: str  # RESCUE | HOSPITAL | SHELTER | FAMILY
    name: Optional[str] = None
    partial_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    clothing: Optional[str] = None
    physical_description: Optional[str] = None
    location: Optional[str] = None
    origin_location: Optional[str] = None  # where the person was found / transferred from
    timestamp: Optional[str] = None  # "YYYY-MM-DD HH:MM"
    medical_condition: Optional[str] = None


class IdentityClusterRequest(BaseModel):
    record_ids: list[str] = Field(min_length=2)


class VerificationRequest(BaseModel):
    cluster_id: str
    verified_name: str = Field(min_length=1)
    officer_name: str = Field(min_length=1)
    notes: Optional[str] = None
