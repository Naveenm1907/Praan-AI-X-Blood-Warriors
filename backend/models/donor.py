from pydantic import BaseModel
from typing import Optional


class Donor(BaseModel):
    donor_id: str
    name: str
    blood_group: str
    phone: str
    language: str
    location: str
    latitude: float
    longitude: float
    last_donation_date: str
    total_donations: int
    total_calls: int
    calls_to_donations_ratio: float
    eligibility_status: str
    readiness_score: Optional[float] = None
    distance_km: Optional[float] = None


class DonorRankRequest(BaseModel):
    patient_id: str
    blood_group: str
    location: str = "Hyderabad"
    latitude: float = 17.385
    longitude: float = 78.4867
    count: int = 20
