"""
Patient routes with RDS integration
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import logging

from database import get_db
from models.patient import Patient
from schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    MedicalReportUpload,
)
from engine.severity import rule_severity, ml_severity, classify_severity, predict_transfusion_date
from engine.ocr_parser import OCRParser

logger = logging.getLogger(__name__)
router = APIRouter()


def _patient_to_params(patient) -> dict:
    """Convert Patient model to params dict for severity classification"""
    return {
        'hb_level': patient.hb_level,
        'mcv_level': patient.mcv_level,
        'mch_level': patient.mch_level,
        'mchc_level': patient.mchc_level,
        'rbc_count': patient.rbc_count,
        'ferritin_level': patient.ferritin_level,
        'hb_a2': patient.hb_a2,
        'hb_f': patient.hb_f,
        'age': patient.age,
    }


def _run_severity_classification(patient):
    """Run severity classification and transfusion prediction on a patient"""
    params = _patient_to_params(patient)

    # Classify severity (rule-based + ML)
    result = classify_severity(params, use_ml=True)

    # Use ML severity if available, otherwise rule-based
    if result['ml_severity']:
        patient.severity = result['ml_severity']
        patient.severity_score = result.get('confidence', 0.5)
    else:
        patient.severity = result['rule_severity']
        patient.severity_score = 0.5

    # Predict transfusion date
    try:
        days = predict_transfusion_date(params)
        if days is not None:
            patient.days_until_transfusion = days
            # Calculate next transfusion date
            from datetime import datetime, timedelta
            next_date = datetime.now() + timedelta(days=days)
            patient.next_transfusion_date = next_date.strftime('%Y-%m-%d')

            # Set urgency level based on days
            if days <= 3:
                patient.urgency_level = 'CRITICAL'
            elif days <= 7:
                patient.urgency_level = 'URGENT'
            elif days <= 14:
                patient.urgency_level = 'SOON'
            else:
                patient.urgency_level = 'SCHEDULED'
        else:
            # Use rule-based fallback
            severity = patient.severity or 'Mild'
            if severity in ['Mild', 'No Thalassemia']:
                patient.urgency_level = 'SCHEDULED'
                patient.days_until_transfusion = patient.transfusion_interval_days or 28
            else:
                patient.urgency_level = 'URGENT'
                patient.days_until_transfusion = 7
    except Exception as e:
        logger.warning(f"Transfusion prediction failed: {e}")
        patient.urgency_level = 'SCHEDULED'
        patient.days_until_transfusion = patient.transfusion_interval_days or 28


@router.post("/patients", response_model=PatientResponse, status_code=201)
def create_patient(patient_data: PatientCreate, db: Session = Depends(get_db)):
    """
    Create a new patient in RDS database
    """
    try:
        # Create patient instance
        patient = Patient(
            name=patient_data.name,
            age=patient_data.age,
            gender=patient_data.gender,
            blood_group=patient_data.blood_group,
            phone=patient_data.phone,
            location=patient_data.location,
            last_transfusion_date=patient_data.last_transfusion_date,
            transfusion_interval_days=patient_data.transfusion_interval_days,
            hb_level=patient_data.hb_level,
            mcv_level=patient_data.mcv_level,
            mch_level=patient_data.mch_level,
            mchc_level=patient_data.mchc_level,
            rbc_count=patient_data.rbc_count,
            wbc_count=patient_data.wbc_count,
            platelet_count=patient_data.platelet_count,
            ferritin_level=patient_data.ferritin_level,
            hb_a2=patient_data.hb_a2,
            hb_f=patient_data.hb_f,
        )

        # Classify severity if blood parameters provided
        if any([patient.hb_level, patient.mcv_level, patient.ferritin_level]):
            _run_severity_classification(patient)

        # Save to database
        db.add(patient)
        db.commit()
        db.refresh(patient)

        logger.info(f"Patient created: {patient.id} - {patient.name}")
        return patient.to_dict()

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating patient: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create patient: {str(e)}")


@router.get("/patients", response_model=list[PatientResponse])
def list_patients(
    skip: int = 0,
    limit: int = 100,
    blood_group: Optional[str] = None,
    urgency_level: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List patients with optional filters
    """
    query = db.query(Patient).filter(Patient.is_active == True)

    if blood_group:
        query = query.filter(Patient.blood_group == blood_group)
    if urgency_level:
        query = query.filter(Patient.urgency_level == urgency_level)

    patients = query.order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()
    return [p.to_dict() for p in patients]


@router.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Get patient by ID
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient.to_dict()


@router.put("/patients/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
):
    """
    Update patient information
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Update fields
    update_data = patient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    # Reclassify severity if blood parameters changed
    if any([
        "hb_level" in update_data,
        "mcv_level" in update_data,
        "ferritin_level" in update_data,
    ]):
        _run_severity_classification(patient)

    db.commit()
    db.refresh(patient)
    logger.info(f"Patient updated: {patient.id}")
    return patient.to_dict()


@router.delete("/patients/{patient_id}", status_code=204)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Soft delete patient (set is_active = False)
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient.is_active = False
    db.commit()
    logger.info(f"Patient deleted (soft): {patient.id}")
    return None


@router.post("/patients/{patient_id}/medical-report")
async def upload_medical_report(
    patient_id: int,
    file: Optional[UploadFile] = File(None),
    hb_level: Optional[float] = Form(None),
    mcv_level: Optional[float] = Form(None),
    mch_level: Optional[float] = Form(None),
    mchc_level: Optional[float] = Form(None),
    rbc_count: Optional[float] = Form(None),
    wbc_count: Optional[float] = Form(None),
    platelet_count: Optional[float] = Form(None),
    ferritin_level: Optional[float] = Form(None),
    hb_a2: Optional[float] = Form(None),
    hb_f: Optional[float] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Upload medical report image (OCR) or manually enter blood parameters
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    try:
        # Process OCR if file uploaded
        if file:
            ocr_parser = OCRParser()
            ocr_result = await ocr_parser.parse_report(file)

            # Update patient with OCR results
            if ocr_result.get("hb_level"):
                patient.hb_level = ocr_result["hb_level"]
            if ocr_result.get("mcv_level"):
                patient.mcv_level = ocr_result["mcv_level"]
            if ocr_result.get("mch_level"):
                patient.mch_level = ocr_result["mch_level"]
            if ocr_result.get("mchc_level"):
                patient.mchc_level = ocr_result["mchc_level"]
            if ocr_result.get("rbc_count"):
                patient.rbc_count = ocr_result["rbc_count"]
            if ocr_result.get("ferritin_level"):
                patient.ferritin_level = ocr_result["ferritin_level"]

            # Store OCR metadata
            patient.ocr_text = ocr_result.get("raw_text")
            patient.ocr_confidence = ocr_result.get("confidence_score")

        # Manual entry overrides
        if hb_level is not None:
            patient.hb_level = hb_level
        if mcv_level is not None:
            patient.mcv_level = mcv_level
        if mch_level is not None:
            patient.mch_level = mch_level
        if mchc_level is not None:
            patient.mchc_level = mchc_level
        if rbc_count is not None:
            patient.rbc_count = rbc_count
        if wbc_count is not None:
            patient.wbc_count = wbc_count
        if platelet_count is not None:
            patient.platelet_count = platelet_count
        if ferritin_level is not None:
            patient.ferritin_level = ferritin_level
        if hb_a2 is not None:
            patient.hb_a2 = hb_a2
        if hb_f is not None:
            patient.hb_f = hb_f

        # Classify severity
        _run_severity_classification(patient)

        db.commit()
        db.refresh(patient)

        logger.info(f"Medical report processed for patient {patient.id}")
        return {
            "message": "Medical report processed successfully",
            "patient": patient.to_dict(),
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error processing medical report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process medical report: {str(e)}",
        )


@router.get("/patients/{patient_id}/analysis")
def get_patient_analysis(patient_id: int, db: Session = Depends(get_db)):
    """
    Get detailed analysis for a patient including severity breakdown
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    params = _patient_to_params(patient)

    # Get severity classification with probabilities
    result = classify_severity(params, use_ml=True)

    # Get transfusion prediction
    days = predict_transfusion_date(params)

    return {
        "patient": patient.to_dict(),
        "analysis": {
            "rule_severity": result['rule_severity'],
            "ml_severity": result['ml_severity'],
            "confidence": result['confidence'],
            "probabilities": result.get('probabilities', {}),
            "method": result['method'],
        },
        "transfusion_days": days,
    }
