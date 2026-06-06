"""
Database models using SQLAlchemy
Maps to PostgreSQL RDS tables
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
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
    last_transfusion_date = Column(String(10), nullable=True)
    transfusion_interval_days = Column(Integer, default=28)

    # Medical report data
    hb_level = Column(Float, nullable=True)
    mcv_level = Column(Float, nullable=True)
    mch_level = Column(Float, nullable=True)
    mchc_level = Column(Float, nullable=True)
    ferritin_level = Column(Float, nullable=True)
    hba2_level = Column(Float, nullable=True)
    hbf_level = Column(Float, nullable=True)
    rbc_count = Column(Float, nullable=True)

    # Severity classification
    severity = Column(String(50), nullable=True)
    severity_score = Column(Float, nullable=True)

    # Transfusion prediction
    urgency_window_days = Column(Integer, nullable=True)
    next_transfusion_date = Column(String(10), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

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
            "hba2_level": self.hba2_level,
            "hbf_level": self.hbf_level,
            "rbc_count": self.rbc_count,
            "severity": self.severity,
            "severity_score": self.severity_score,
            "urgency_window_days": self.urgency_window_days,
            "next_transfusion_date": self.next_transfusion_date,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, nullable=False, index=True)

    # Extracted values
    hb = Column(Float, nullable=True)
    hbf = Column(Float, nullable=True)
    hba2 = Column(Float, nullable=True)
    mcv = Column(Float, nullable=True)
    mch = Column(Float, nullable=True)
    mchc = Column(Float, nullable=True)
    rbc = Column(Float, nullable=True)
    ferritin = Column(Float, nullable=True)

    # OCR metadata
    ocr_text = Column(Text, nullable=True)
    extraction_method = Column(String(50), nullable=True)  # "real" or "mock"

    # Analysis results
    severity = Column(String(50), nullable=True)
    severity_score = Column(Float, nullable=True)
    urgency_level = Column(String(50), nullable=True)
    days_until_transfusion = Column(Integer, nullable=True)
    transfusion_date = Column(String(10), nullable=True)
    recommendation = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

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
            "ocr_text": self.ocr_text,
            "extraction_method": self.extraction_method,
            "severity": self.severity,
            "severity_score": self.severity_score,
            "urgency_level": self.urgency_level,
            "days_until_transfusion": self.days_until_transfusion,
            "transfusion_date": self.transfusion_date,
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Donor(Base):
    __tablename__ = "donors"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(50), nullable=False)
    blood_group = Column(String(10), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Availability
    is_active = Column(Boolean, default=True)
    last_donation_date = Column(String(10), nullable=True)
    donation_count = Column(Integer, default=0)
    preferred_contact_method = Column(String(50), default="whatsapp")
    preferred_time = Column(String(50), nullable=True)
    languages = Column(String(255), default="English")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "blood_group": self.blood_group,
            "phone": self.phone,
            "email": self.email,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "is_active": self.is_active,
            "last_donation_date": self.last_donation_date,
            "donation_count": self.donation_count,
            "preferred_contact_method": self.preferred_contact_method,
            "preferred_time": self.preferred_time,
            "languages": self.languages,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
