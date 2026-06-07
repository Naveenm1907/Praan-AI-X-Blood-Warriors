from fastapi import APIRouter, Query
from typing import Optional
from models.blood_bank import ReserveRequest
from engine.inventory import search_blood_banks, reserve_units, get_expiring_stock
import json
import os

router = APIRouter(tags=["blood-bank"])

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load_banks():
    path = os.path.join(DATA_DIR, "seed_data.json")
    with open(path) as f:
        data = json.load(f)
    return data["blood_banks"]


def save_banks(banks):
    path = os.path.join(DATA_DIR, "seed_data.json")
    with open(path) as f:
        data = json.load(f)
    data["blood_banks"] = banks
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


@router.get("")
def list_inventory():
    return load_banks()


@router.get("/search")
def search_inventory(
    blood_group: str = Query(...),
    district: Optional[str] = Query(None),
):
    banks = load_banks()
    return search_blood_banks(banks, blood_group, district)


@router.post("/reserve")
def reserve_blood(req: ReserveRequest):
    banks = load_banks()
    result = reserve_units(banks, req.bank_id, req.blood_group, req.units)
    if result:
        save_banks(banks)
    return result or {"error": "Insufficient stock"}


@router.get("/expiry")
def get_expiry_alerts(days: int = Query(7)):
    banks = load_banks()
    return get_expiring_stock(banks, days)


@router.post("/seed")
def seed_data():
    return {"message": "Blood bank data loaded", "count": len(load_banks())}
