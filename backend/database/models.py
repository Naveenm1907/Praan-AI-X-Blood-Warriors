"""
SQLAlchemy database models for PRAAN AI
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey, JSON, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(50), nullable=False)
    blood_group = Column(String(10), nullable=False)
    phone = Column(String(20), nullable=False)
    location = Column(String(255), nullable=False)
    last_transfusion_date = Column(String(20), nullable=True)
    transfusion_interval_days = Column(Integer, default=28)

    # Medical report extracted values
    hb_level = Column(Float, nullable=True)
    mcv_level = Column(Float, nullable=True)
    mch_level = Column(Float, nullable=True)
    mchc_level = Column(Float, nullable=True)
    ferritin_level = Column(Float, nullable=True)
    hb_a2 = Column(Float, nullable=True)
    hb_f = Column(Float, nullable=True)

    # Severity and urgency
    severity = Column(String(50), nullable=True)
    severity_score = Column(Integer, nullable=True)
    urgency_level = Column(String(50), nullable=True)
    days_until_transfusion = Column(Integer, nullable=True)
    next_transfusion_date = Column(String(20), nullable=True)

    # OCR metadata
    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    medical_reports = relationship("MedicalReport", back_populates="patient", cascade="all, delete-orphan")
    transfusion_requests = relationship("TransfusionRequest", back_populates="patient", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "blood_group": self.blood_group,
            "phone": self.phone,
            "location": self.location,
            "last_transfusion_date": self.last_transfusion_date,
            "transfusion_interval_days": self.transfusion_interval_days,
            "hb_level": self.hb_level,
            "mcv_level": self.mcv_level,
            "mch_level": self.mch_level,
            "mchc_level": self.mchc_level,
            "ferritin_level": self.ferritin_level,
            "hb_a2": self.hb_a2,
            "hb_f": self.hb_f,
            "severity": self.severity,
            "severity_score": self.severity_score,
            "urgency_level": self.urgency_level,
            "days_until_transfusion": self.days_until_transfusion,
            "next_transfusion_date": self.next_transfusion_date,
            "ocr_text": self.ocr_text,
            "ocr_confidence": self.ocr_confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)

    # Extracted values
    hb = Column(Float, nullable=True)
    hbf = Column(Float, nullable=True)
    hba2 = Column(Float, nullable=True)
    mcv = Column(Float, nullable=True)
    mch = Column(Float, nullable=True)
    mchc = Column(Float, nullable=True)
    rbc = Column(Float, nullable=True)
    ferritin = Column(Float, nullable=True)

    # OCR details
    raw_text = Column(Text, nullable=True)
    extraction_method = Column(String(50), nullable=True)  # "mock", "textract", "manual"
    confidence_score = Column(Float, nullable=True)

    # Analysis results
    severity = Column(String(50), nullable=True)
    severity_score = Column(Float, nullable=True)
    urgency_level = Column(String(50), nullable=True)
    days_until_transfusion = Column(Integer, nullable=True)
    estimated_transfusion_date = Column(String(20), nullable=True)
    recommendation = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="medical_reports")

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "hb": self.hb,
            "hbf": self.hbf,
            "hba2": self.hba2,
            "mcv": self.mcv,
            "mch": self.mch,
            "mchc": self.mchc,
            "rbc": self.rbc,
            "ferritin": self.ferritin,
            "raw_text": self.raw_text,
            "extraction_method": self.extraction_method,
            "confidence_score": self.confidence_score,
            "severity": self.severity,
            "severity_score": self.severity_score,
            "urgency_level": self.urgency_level,
            "days_until_transfusion": self.days_until_transfusion,
            "estimated_transfusion_date": self.estimated_transfusion_date,
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Donor(Base):
    __tablename__ = "donors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=True, index=True)
    bridge_id = Column(String(255), nullable=True)
    role = Column(String(255), nullable=True)
    role_status = Column(Boolean, nullable=True)
    bridge_status = Column(Boolean, nullable=True)
    blood_group = Column(String(10), nullable=True)
    gender = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)
    latitude = Column(Numeric(10, 6), nullable=True)
    longitude = Column(Numeric(10, 6), nullable=True)
    donor_type = Column(String(255), nullable=True)
    last_contacted_date = Column(Date, nullable=True)
    last_donation_date = Column(Date, nullable=True)
    next_eligible_date = Column(Date, nullable=True)
    donations_till_date = Column(Integer, nullable=True)
    eligibility_status = Column(String(50), nullable=True)
    cycle_of_donations = Column(Integer, nullable=True)
    total_calls = Column(Integer, nullable=True)
    frequency_in_days = Column(Integer, nullable=True)
    status_of_bridge = Column(Boolean, nullable=True)
    status = Column(String(50), nullable=True)
    donated_earlier = Column(Boolean, nullable=True)
    last_bridge_donation_date = Column(Date, nullable=True)
    calls_to_donations_ratio = Column(Numeric(10, 4), nullable=True)
    user_donation_active_status = Column(String(50), nullable=True)
    inactive_trigger_comment = Column(Text, nullable=True)
    registration_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    transfusion_requests = relationship("TransfusionRequest", back_populates="donor", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "bridge_id": self.bridge_id,
            "role": self.role,
            "role_status": self.role_status,
            "bridge_status": self.bridge_status,
            "blood_group": self.blood_group,
            "gender": self.gender,
            "phone": self.phone,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
            "donor_type": self.donor_type,
            "last_contacted_date": self.last_contacted_date.isoformat() if self.last_contacted_date else None,
            "last_donation_date": self.last_donation_date.isoformat() if self.last_donation_date else None,
            "next_eligible_date": self.next_eligible_date.isoformat() if self.next_eligible_date else None,
            "donations_till_date": self.donations_till_date,
            "eligibility_status": self.eligibility_status,
            "cycle_of_donations": self.cycle_of_donations,
            "total_calls": self.total_calls,
            "frequency_in_days": self.frequency_in_days,
            "status_of_bridge": self.status_of_bridge,
            "status": self.status,
            "donated_earlier": self.donated_earlier,
            "last_bridge_donation_date": self.last_bridge_donation_date.isoformat() if self.last_bridge_donation_date else None,
            "calls_to_donations_ratio": float(self.calls_to_donations_ratio) if self.calls_to_donations_ratio else None,
            "user_donation_active_status": self.user_donation_active_status,
            "inactive_trigger_comment": self.inactive_trigger_comment,
            "registration_date": self.registration_date.isoformat() if self.registration_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TransfusionRequest(Base):
    __tablename__ = "transfusion_requests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    donor_id = Column(Integer, ForeignKey("donors.id"), nullable=False)
    blood_bank_id = Column(String, nullable=True)
    status = Column(String(50), default="pending")  # pending, matched, contacted, confirmed, completed, cancelled
    units_required = Column(Integer, default=1)
    urgency_level = Column(String(50), nullable=True)

    # Communication tracking
    whatsapp_sent = Column(Boolean, default=False)
    whatsapp_response = Column(String(50), nullable=True)
    call_made = Column(Boolean, default=False)
    call_response = Column(String(50), nullable=True)
    call_duration = Column(Integer, nullable=True)  # in seconds

    # AI call details
    ai_call_transcript = Column(Text, nullable=True)
    ai_call_sentiment = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="transfusion_requests")
    donor = relationship("Donor", back_populates="transfusion_requests")

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "donor_id": self.donor_id,
            "blood_bank_id": self.blood_bank_id,
            "status": self.status,
            "units_required": self.units_required,
            "urgency_level": self.urgency_level,
            "whatsapp_sent": self.whatsapp_sent,
            "whatsapp_response": self.whatsapp_response,
            "call_made": self.call_made,
            "call_response": self.call_response,
            "call_duration": self.call_duration,
            "ai_call_transcript": self.ai_call_transcript,
            "ai_call_sentiment": self.ai_call_sentiment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
