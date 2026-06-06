from fastapi import APIRouter, UploadFile, File
from models.patient import PatientCreate, PatientResponse, UrgencyResult, OCRResult
from engine.predict import calculate_urgency_window
import uuid
from datetime import datetime

router = APIRouter(tags=["patient"])

patients_db: dict[str, dict] = {}


@router.post("/patient", response_model=PatientResponse)
def create_patient(patient: PatientCreate):
    pid = f"p{uuid.uuid4().hex[:8]}"
    urgency = calculate_urgency_window(
        patient.last_transfusion_date, patient.cycle_length_days
    )
    data = {
        "patient_id": pid,
        **patient.model_dump(),
        "urgency_window_days": urgency["urgency_window_days"],
        "created_at": datetime.now().strftime("%Y-%m-%d"),
    }
    patients_db[pid] = data
    return data


@router.get("/patient", response_model=list[PatientResponse])
def list_patients():
    return list(patients_db.values())


@router.get("/patient/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str):
    if patient_id not in patients_db:
        from fastapi import HTTPException
        raise HTTPException(404, "Patient not found")
    return patients_db[patient_id]


@router.post("/patient/{patient_id}/report", response_model=OCRResult)
async def upload_report(patient_id: str, file: UploadFile = File(...)):
    import random
    result = {
        "hb": round(5 + random.random() * 5, 1),
        "mcv": int(55 + random.random() * 30),
        "ferritin": int(5 + random.random() * 50),
        "mch": round(18 + random.random() * 12, 1),
    }
    if patient_id in patients_db:
        patients_db[patient_id]["hb_level"] = result["hb"]
        patients_db[patient_id]["ferritin_level"] = result["ferritin"]
        patients_db[patient_id]["mcv_level"] = result["mcv"]
        urgency = calculate_urgency_window(
            patients_db[patient_id]["last_transfusion_date"],
            patients_db[patient_id]["cycle_length_days"],
            result["hb"],
            result["ferritin"],
        )
        patients_db[patient_id]["urgency_window_days"] = urgency["urgency_window_days"]
    return result


@router.get("/patient/{patient_id}/urgency", response_model=UrgencyResult)
def get_urgency(patient_id: str):
    if patient_id not in patients_db:
        from fastapi import HTTPException
        raise HTTPException(404, "Patient not found")
    p = patients_db[patient_id]
    result = calculate_urgency_window(
        p["last_transfusion_date"],
        p["cycle_length_days"],
        p.get("hb_level"),
        p.get("ferritin_level"),
    )
    return {
        "patient_id": patient_id,
        **result,
        "hb_level": p.get("hb_level"),
        "ferritin_level": p.get("ferritin_level"),
        "mcv_level": p.get("mcv_level"),
    }
