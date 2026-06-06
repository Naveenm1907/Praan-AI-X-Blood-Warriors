from pydantic import BaseModel
from typing import Dict, List


class BloodInventory(BaseModel):
    units_available: int
    expiry_date: str
    reserved_count: int


class BloodBank(BaseModel):
    bank_id: str
    name: str
    district: str
    state: str
    contact_phone: str
    inventory: Dict[str, BloodInventory]


class ReserveRequest(BaseModel):
    bank_id: str
    blood_group: str
    units: int


class ExpiryAlert(BaseModel):
    bank_id: str
    bank_name: str
    district: str
    blood_group: str
    units_available: int
    days_until_expiry: int
