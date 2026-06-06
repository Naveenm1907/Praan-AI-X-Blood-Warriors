from pydantic import BaseModel
from typing import Dict, List, Optional


class CallResponse(BaseModel):
    status: str
    timestamp: Optional[str] = None
    retry_count: int = 0


class CampaignCreate(BaseModel):
    patient_id: str
    donor_ids: List[str]
    language: str = "en-IN"
    target_count: int = 5


class Campaign(BaseModel):
    campaign_id: str
    patient_id: str
    donor_ids: List[str]
    status: str
    responses: Dict[str, CallResponse]
    language: str
    target_count: int
    confirmed_count: int
    started_at: str
