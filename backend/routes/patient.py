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


# ── Helpers ──────────────────────────────────────────────────────────────────

def _patient_to_params(patient) -> dict:
    """Convert Patient model to params dict for severity/transfusion classification."""
    return {
        # CBC / HPLC — use API names; engine maps them to CSV column names
        'hb_level':       patient.hb_level,
        'mcv_level':      patient.mcv_level,
        'mch_level':      patient.mch_level,
        'mchc_level':     patient.mchc_level,
        'rbc_count':      patient.rbc_count,
        'ferritin_level': patient.ferritin_level,
        'rdw_pct':        patient.rdw_pct,
        'weight_kg':      patient.weight_kg,
        'hb_a_pct':       patient.hb_a_pct,
        'hb_a2':          patient.hb_a2,
        'hb_f':           patient.hb_f,
        'age':            patient.age,
        'sex':            patient.gender,
        # Transfusion parameters
        'hb_post_transfusion':           patient.hb_post_transfusion,
        'hb_drop_rate_per_day':          patient.hb_drop_rate_per_day,
        'hb_transfusion_threshold':      patient.hb_transfusion_threshold,
        'days_since_last_transfusion':   patient.days_since_last_transfusion,
        'units_per_session':             patient.units_per_session,
        'avg_transfusion_interval_days': patient.avg_transfusion_interval_days,
    }


def _run_severity_classification(patient):
    """Run severity classification and transfusion prediction on a patient."""
    params = _patient_to_params(patient)

    # Classify severity (rule-based + ML)
    result = classify_severity(params, use_ml=True)

    patient.severity = result.get('consensus_severity', result['rule_severity'])
    patient.severity_score = result.get('confidence', 0.5) if result['ml_severity'] else 0.5

    if patient.severity == 'No Thalassemia':
        patient.urgency_level = None
        patient.days_until_transfusion = None
        patient.next_transfusion_date = None
        return

    # Predict transfusion date
    try:
        days = predict_transfusion_date(params)
        if days is not None:
            patient.days_until_transfusion = days
            from datetime import datetime, timedelta
            next_date = datetime.now() + timedelta(days=days)
            patient.next_transfusion_date = next_date.strftime('%Y-%m-%d')

            if days <= 3:
                patient.urgency_level = 'CRITICAL'
            elif days <= 7:
                patient.urgency_level = 'URGENT'
            elif days <= 14:
                patient.urgency_level = 'SOON'
            else:
                patient.urgency_level = 'SCHEDULED'
        else:
            # Rule-based fallback
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


def _apply_patient_data(patient: Patient, data):
    """Apply PatientCreate/PatientUpdate fields to a Patient ORM object."""
    fields = [
        # Basic
        'name', 'age', 'gender', 'blood_group', 'phone', 'location',
        'last_transfusion_date', 'transfusion_interval_days',
        # CBC / HPLC
        'hb_level', 'mcv_level', 'mch_level', 'mchc_level', 'rbc_count',
        'wbc_count', 'platelet_count', 'ferritin_level', 'rdw_pct',
        'weight_kg', 'hb_a_pct', 'hb_a2', 'hb_f',
        # Transfusion
        'hb_post_transfusion', 'hb_drop_rate_per_day', 'hb_transfusion_threshold',
        'days_since_last_transfusion', 'units_per_session',
        'avg_transfusion_interval_days',
    ]
    if hasattr(data, 'model_dump'):
        data_dict = data.model_dump(exclude_unset=True)
    else:
        data_dict = {f: getattr(data, f, None) for f in fields}

    for field in fields:
        if field in data_dict:
            setattr(patient, field, data_dict[field])


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/patients", response_model=PatientResponse, status_code=201)
def create_patient(patient_data: PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient in RDS database"""
    try:
        patient = Patient()
        _apply_patient_data(patient, patient_data)

        # Classify severity if any blood parameter provided
        if any([patient.hb_level, patient.mcv_level, patient.ferritin_level,
                patient.hb_a2, patient.hb_f]):
            _run_severity_classification(patient)

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
    """List patients with optional filters"""
    query = db.query(Patient).filter(Patient.is_active == True)

    if blood_group:
        query = query.filter(Patient.blood_group == blood_group)
    if urgency_level:
        query = query.filter(Patient.urgency_level == urgency_level)

    patients = query.order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()
    return [p.to_dict() for p in patients]


@router.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Get patient by ID"""
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
    """Update patient information"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    update_data = patient_data.model_dump(exclude_unset=True)
    _apply_patient_data(patient, patient_data)

    # Reclassify if any blood/transfusion parameter changed
    reclassify_keys = {
        'hb_level', 'mcv_level', 'mch_level', 'mchc_level', 'rbc_count',
        'ferritin_level', 'rdw_pct', 'hb_a_pct', 'hb_a2', 'hb_f',
        'hb_post_transfusion', 'hb_drop_rate_per_day',
        'hb_transfusion_threshold', 'days_since_last_transfusion',
        'units_per_session', 'avg_transfusion_interval_days',
    }
    if any(k in update_data for k in reclassify_keys):
        _run_severity_classification(patient)

    db.commit()
    db.refresh(patient)
    logger.info(f"Patient updated: {patient.id}")
    return patient.to_dict()


@router.delete("/patients/{patient_id}", status_code=204)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """Soft delete patient (set is_active = False)"""
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
    # CBC / HPLC
    hb_level:       Optional[float] = Form(None),
    mcv_level:      Optional[float] = Form(None),
    mch_level:      Optional[float] = Form(None),
    mchc_level:     Optional[float] = Form(None),
    rbc_count:      Optional[float] = Form(None),
    wbc_count:      Optional[float] = Form(None),
    platelet_count: Optional[float] = Form(None),
    ferritin_level: Optional[float] = Form(None),
    rdw_pct:        Optional[float] = Form(None),
    weight_kg:      Optional[float] = Form(None),
    hb_a_pct:       Optional[float] = Form(None),
    hb_a2:          Optional[float] = Form(None),
    hb_f:           Optional[float] = Form(None),
    # Transfusion parameters
    hb_post_transfusion:           Optional[float] = Form(None),
    hb_drop_rate_per_day:          Optional[float] = Form(None),
    hb_transfusion_threshold:      Optional[float] = Form(None),
    days_since_last_transfusion:   Optional[int]   = Form(None),
    units_per_session:             Optional[float] = Form(None),
    avg_transfusion_interval_days: Optional[float] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Upload medical report image (OCR) or manually enter blood parameters.
    Also accepts transfusion-specific parameters.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    try:
        # Process OCR if file uploaded
        if file:
            ocr_parser = OCRParser()
            ocr_result = await ocr_parser.parse_report(file)

            ocr_field_map = {
                'hb_level':       'hb_level',
                'mcv_level':      'mcv_level',
                'mch_level':      'mch_level',
                'mchc_level':     'mchc_level',
                'rbc_count':      'rbc_count',
                'ferritin_level': 'ferritin_level',
                'rdw_pct':        'rdw_pct',
                'platelet_count': 'platelet_count',
                'wbc_count':      'wbc_count',
                'hb_a_pct':       'hb_a_pct',
                'hb_a2':          'hb_a2',
                'hb_f':           'hb_f',
            }
            for ocr_key, model_attr in ocr_field_map.items():
                if ocr_result.get(ocr_key):
                    setattr(patient, model_attr, ocr_result[ocr_key])

            patient.ocr_text = ocr_result.get("raw_text")
            patient.ocr_confidence = ocr_result.get("confidence_score")

        # Manual entry (overrides OCR when both provided)
        manual_fields = {
            'hb_level':                    hb_level,
            'mcv_level':                   mcv_level,
            'mch_level':                   mch_level,
            'mchc_level':                  mchc_level,
            'rbc_count':                   rbc_count,
            'wbc_count':                   wbc_count,
            'platelet_count':              platelet_count,
            'ferritin_level':              ferritin_level,
            'rdw_pct':                     rdw_pct,
            'weight_kg':                   weight_kg,
            'hb_a_pct':                    hb_a_pct,
            'hb_a2':                       hb_a2,
            'hb_f':                        hb_f,
            'hb_post_transfusion':         hb_post_transfusion,
            'hb_drop_rate_per_day':        hb_drop_rate_per_day,
            'hb_transfusion_threshold':    hb_transfusion_threshold,
            'days_since_last_transfusion': days_since_last_transfusion,
            'units_per_session':           units_per_session,
            'avg_transfusion_interval_days': avg_transfusion_interval_days,
        }
        for attr, value in manual_fields.items():
            if value is not None:
                setattr(patient, attr, value)

        # Classify severity + predict transfusion date
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


@router.post("/patients/{patient_id}/transfusion-info")
def update_transfusion_info(
    patient_id: int,
    hb_post_transfusion:           Optional[float] = None,
    hb_drop_rate_per_day:          Optional[float] = None,
    hb_transfusion_threshold:      Optional[float] = None,
    days_since_last_transfusion:   Optional[int]   = None,
    units_per_session:             Optional[float] = None,
    avg_transfusion_interval_days: Optional[float] = None,
    last_transfusion_date:         Optional[str]   = None,
    db: Session = Depends(get_db),
):
    """
    Dedicated endpoint to record post-transfusion measurements and update
    transfusion scheduling parameters. Triggers ML re-prediction.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    tf_fields = {
        'hb_post_transfusion':           hb_post_transfusion,
        'hb_drop_rate_per_day':          hb_drop_rate_per_day,
        'hb_transfusion_threshold':      hb_transfusion_threshold,
        'days_since_last_transfusion':   days_since_last_transfusion,
        'units_per_session':             units_per_session,
        'avg_transfusion_interval_days': avg_transfusion_interval_days,
        'last_transfusion_date':         last_transfusion_date,
    }
    for attr, value in tf_fields.items():
        if value is not None:
            setattr(patient, attr, value)

    # Re-run ML with updated transfusion data
    _run_severity_classification(patient)

    db.commit()
    db.refresh(patient)

    logger.info(f"Transfusion info updated for patient {patient.id}")
    return {
        "message": "Transfusion info updated",
        "patient": patient.to_dict(),
    }


@router.get("/patients/{patient_id}/analysis")
def get_patient_analysis(patient_id: int, db: Session = Depends(get_db)):
    """Get detailed analysis for a patient including severity breakdown"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    params = _patient_to_params(patient)

    result = classify_severity(params, use_ml=True)
    days = predict_transfusion_date(params)

    return {
        "patient": patient.to_dict(),
        "analysis": {
            "rule_severity":  result['rule_severity'],
            "ml_severity":    result['ml_severity'],
            "confidence":     result['confidence'],
            "probabilities":  result.get('probabilities', {}),
            "method":         result['method'],
        },
        "transfusion_days": days,
    }
