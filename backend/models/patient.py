from pydantic import BaseModel
from typing import Optional
from datetime import date


class PatientCreate(BaseModel):
    name: str
    age: int
    blood_group: str
    location: str = "Hyderabad"
    latitude: float = 17.385
    longitude: float = 78.4867
    last_transfusion_date: str
    cycle_length_days: int = 21


class PatientResponse(PatientCreate):
    patient_id: str
    hb_level: Optional[float] = None
    ferritin_level: Optional[float] = None
    mcv_level: Optional[float] = None
    urgency_window_days: Optional[int] = None
    created_at: str


class UrgencyResult(BaseModel):
    patient_id: str
    urgency_window_days: int
    priority: str
    hb_level: Optional[float]
    ferritin_level: Optional[float]
    mcv_level: Optional[float]
    next_transfusion_date: str


class OCRResult(BaseModel):
    hb: float
    mcv: float
    ferritin: float
    mch: float
