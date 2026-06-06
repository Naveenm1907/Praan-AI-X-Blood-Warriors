from fastapi import APIRouter, Query
from models.donor import DonorRankRequest
from engine.match import rank_donors
import json
import os

router = APIRouter(tags=["donor"])

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load_donors():
    path = os.path.join(DATA_DIR, "seed_data.json")
    with open(path) as f:
        data = json.load(f)
    return data["donors"]


@router.get("/donor/rank")
def rank_donors_for_patient(
    blood_group: str = Query(...),
    latitude: float = Query(17.385),
    longitude: float = Query(78.4867),
    count: int = Query(20),
):
    donors = load_donors()
    return rank_donors(donors, blood_group, latitude, longitude, count)


@router.post("/donor/match")
def match_donors(req: DonorRankRequest):
    donors = load_donors()
    return rank_donors(donors, req.blood_group, req.latitude, req.longitude, req.count)


@router.get("/donor/{donor_id}")
def get_donor(donor_id: str):
    donors = load_donors()
    for d in donors:
        if d["donor_id"] == donor_id:
            return d
    from fastapi import HTTPException
    raise HTTPException(404, "Donor not found")


@router.post("/donor/seed")
def seed_donors():
    return {"message": "Donor data loaded", "count": len(load_donors())}
