"""
Pydantic schemas for patient API request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PatientCreate(BaseModel):
    """Schema for creating a new patient"""
    name: str = Field(..., min_length=1, max_length=200)
    age: int = Field(..., ge=0, le=150)
    gender: Optional[str] = Field(default=None, pattern="^(Male|Female|Other|Not Specified)$")
    blood_group: str = Field(..., pattern="^(A|B|AB|O)[+-]$")
    phone: str = Field(..., min_length=10, max_length=20)
    location: str = Field(..., min_length=1, max_length=200)
    last_transfusion_date: Optional[str] = None
    transfusion_interval_days: int = Field(default=28, ge=1, le=365)

    # Optional blood parameters (can be added manually or via OCR)
    hb_level: Optional[float] = Field(None, ge=0, le=30)
    mcv_level: Optional[float] = Field(None, ge=0, le=200)
    mch_level: Optional[float] = Field(None, ge=0, le=100)
    mchc_level: Optional[float] = Field(None, ge=0, le=100)
    rbc_count: Optional[float] = Field(None, ge=0, le=20)
    wbc_count: Optional[float] = Field(None, ge=0, le=100)
    platelet_count: Optional[float] = Field(None, ge=0, le=1000)
    ferritin_level: Optional[float] = Field(None, ge=0, le=5000)
    hb_a2: Optional[float] = Field(None, ge=0, le=100)
    hb_f: Optional[float] = Field(None, ge=0, le=100)


class PatientUpdate(BaseModel):
    """Schema for updating patient information"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = Field(None, pattern="^(Male|Female|Other)$")
    blood_group: Optional[str] = Field(None, pattern="^(A|B|AB|O)[+-]$")
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    last_transfusion_date: Optional[str] = None
    transfusion_interval_days: Optional[int] = Field(None, ge=1, le=365)
    is_active: Optional[bool] = None


class PatientResponse(BaseModel):
    """Schema for patient response"""
    id: int
    name: str
    age: int
    gender: str
    blood_group: str
    phone: str
    location: str
    last_transfusion_date: Optional[str]
    transfusion_interval_days: int
    hb_level: Optional[float]
    mcv_level: Optional[float]
    mch_level: Optional[float]
    mchc_level: Optional[float]
    rbc_count: Optional[float]
    wbc_count: Optional[float]
    platelet_count: Optional[float]
    ferritin_level: Optional[float]
    hb_a2: Optional[float]
    hb_f: Optional[float]
    severity: Optional[str]
    severity_score: Optional[float]
    urgency_level: Optional[str]
    days_until_transfusion: Optional[int]
    next_transfusion_date: Optional[str]
    ocr_text: Optional[str]
    ocr_confidence: Optional[float]
    created_at: Optional[str]
    updated_at: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class PatientListResponse(BaseModel):
    """Schema for listing patients"""
    patients: list[PatientResponse]
    total: int
    page: int
    per_page: int


class MedicalReportUpload(BaseModel):
    """Schema for manual medical report data entry"""
    hb_level: Optional[float] = None
    mcv_level: Optional[float] = None
    mch_level: Optional[float] = None
    mchc_level: Optional[float] = None
    rbc_count: Optional[float] = None
    wbc_count: Optional[float] = None
    platelet_count: Optional[float] = None
    ferritin_level: Optional[float] = None
    hb_a2: Optional[float] = None
    hb_f: Optional[float] = None
