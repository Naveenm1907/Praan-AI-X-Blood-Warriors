from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.donor import DonorRankRequest
from engine.match import rank_donors
from database import get_db
import json
import os

router = APIRouter(tags=["donor"])

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load_donors_from_db(db: Session):
    """Load donors from database"""
    result = db.execute(text("SELECT * FROM donors ORDER BY id"))
    rows = result.fetchall()
    columns = result.keys()

    donors = []
    for row in rows:
        donor = dict(zip(columns, row))
        # Convert database field names to match expected format
        donors.append({
            "donor_id": donor['id'],  # Use Integer ID, not string user_id
            "name": donor.get("user_id", f"Donor {donor['id']}"),
            "blood_group": donor.get("blood_group", "O+"),
            "phone": donor.get("phone", "+91 99999-00000"),
            "language": "English",
            "location": "Hyderabad",
            "latitude": float(donor.get("latitude", 17.385)),
            "longitude": float(donor.get("longitude", 78.4867)),
            "last_donation_date": str(donor.get("last_donation_date", "2025-01-01"))[:10] if donor.get("last_donation_date") else None,
            "total_donations": int(donor.get("donations_till_date", 0) or 0),
            "total_calls": int(donor.get("total_calls", 0) or 0),
            "calls_to_donations_ratio": float(donor.get("calls_to_donations_ratio", 0.5) or 0.5),
            "eligibility_status": donor.get("eligibility_status", "eligible"),
            "user_donation_active_status": donor.get("user_donation_active_status", "Active"),
            "role": donor.get("role", "Emergency Donor"),
            "donor_type": donor.get("donor_type", "Regular Donor"),
            "last_contacted_date": str(donor.get("last_contacted_date", ""))[:10] if donor.get("last_contacted_date") else None,
            "next_eligible_date": str(donor.get("next_eligible_date", ""))[:10] if donor.get("next_eligible_date") else None,
            "inactive_trigger_comment": donor.get("inactive_trigger_comment"),
        })
    return donors


def load_donors_from_json():
    """Fallback: Load donors from JSON"""
    path = os.path.join(DATA_DIR, "seed_data.json")
    with open(path) as f:
        data = json.load(f)
    return data["donors"]


@router.get("/rank")
def rank_donors_for_patient(
    patient_id: int = Query(None),
    blood_group: str = Query(...),
    latitude: float = Query(None),
    longitude: float = Query(None),
    count: int = Query(20),
    db: Session = Depends(get_db),
):
    """Rank donors for a specific patient. Uses patient location if patient_id provided."""
    # If patient_id provided, fetch patient location
    if patient_id:
        from models.patient import Patient
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if patient and patient.location:
            # TODO: Geocode patient location to lat/lng
            # For now use Hyderabad coords as default
            latitude = latitude or 17.385
            longitude = longitude or 78.4867

    # Fallback to default coords if not provided
    latitude = latitude or 17.385
    longitude = longitude or 78.4867

    try:
        donors = load_donors_from_db(db)
        if not donors:
            donors = load_donors_from_json()
    except Exception:
        donors = load_donors_from_json()

    # Get already-assigned donors for other active patients (avoid double-booking)
    assigned_donor_ids = set()
    if patient_id:
        try:
            result = db.execute(text("""
                SELECT dm.donor_id FROM donor_matches dm
                JOIN patients p ON dm.patient_id = p.id
                WHERE p.is_active = true AND dm.patient_id != :pid
            """), {"pid": patient_id})
            assigned_donor_ids = {row[0] for row in result.fetchall()}
        except:
            pass  # Table might not exist yet

    # Rank donors
    ranked = rank_donors(donors, blood_group, latitude, longitude, count * 2)

    # Deprioritize already-assigned donors (move them to end)
    available = [d for d in ranked if d['donor_id'] not in assigned_donor_ids]
    assigned = [d for d in ranked if d['donor_id'] in assigned_donor_ids]

    return available[:count] + assigned[:count-len(available)]


@router.post("/match")
def match_donors(req: DonorRankRequest, db: Session = Depends(get_db)):
    try:
        donors = load_donors_from_db(db)
        if not donors:
            donors = load_donors_from_json()
    except Exception:
        donors = load_donors_from_json()
    return rank_donors(donors, req.blood_group, req.latitude, req.longitude, req.count)


@router.get("/{donor_id}")
def get_donor(donor_id: str, db: Session = Depends(get_db)):
    try:
        donors = load_donors_from_db(db)
        if not donors:
            donors = load_donors_from_json()
    except Exception:
        donors = load_donors_from_json()
    for d in donors:
        if d["donor_id"] == donor_id:
            return d
    raise HTTPException(404, "Donor not found")


@router.get("/")
def list_donors(db: Session = Depends(get_db)):
    try:
        donors = load_donors_from_db(db)
        if not donors:
            donors = load_donors_from_json()
    except Exception:
        donors = load_donors_from_json()
    return {"count": len(donors), "donors": donors}


@router.post("/seed")
def seed_donors(db: Session = Depends(get_db)):
    try:
        donors = load_donors_from_db(db)
        return {"message": "Donor data loaded from database", "count": len(donors)}
    except Exception:
        donors = load_donors_from_json()
        return {"message": "Donor data loaded from JSON (database not available)", "count": len(donors)}
