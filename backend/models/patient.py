from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Numeric
from sqlalchemy.sql import func
from database import Base

class Patient(Base):
    __tablename__ = "patients"

    # Basic info
    id = Column(Integer, primary_key=True, index=True)
    patient_code = Column(String(20), nullable=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    sex = Column(String(5), nullable=True)
    gender = Column(String, nullable=False, default="Not Specified")
    weight_kg = Column(Numeric(5, 1), nullable=True)
    blood_group = Column(String(10), nullable=False, index=True)
    phone = Column(String(15), nullable=True)
    location = Column(String, nullable=True, default="Hyderabad")

    # Medical info
    spleen_enlargement = Column(String(20), nullable=True)
    last_transfusion_date = Column(String(20), nullable=True)
    transfusion_interval_days = Column(Integer, default=28)

    # Blood parameters (from OCR, manual entry, or seed data)
    hb_level = Column(Float, nullable=True)
    rbc_count = Column(Float, nullable=True)
    mcv_level = Column(Float, nullable=True)
    mch_level = Column(Float, nullable=True)
    mchc_level = Column(Float, nullable=True)
    rdw_pct = Column(Numeric(5, 1), nullable=True)
    ferritin_level = Column(Float, nullable=True)
    hb_a_pct = Column(Numeric(5, 1), nullable=True)
    hb_a2 = Column(Float, nullable=True)
    hb_f = Column(Float, nullable=True)
    mentzer_index = Column(Numeric(6, 2), nullable=True)
    wbc_count = Column(Float, nullable=True)
    platelet_count = Column(Float, nullable=True)

    # Transfusion history
    hb_post_transfusion = Column(Numeric(4, 1), nullable=True)
    hb_drop_rate_per_day = Column(Numeric(6, 4), nullable=True)
    hb_transfusion_threshold = Column(Numeric(4, 1), nullable=True)
    days_since_last_transfusion = Column(Integer, nullable=True)
    units_per_session = Column(Numeric(3, 1), nullable=True)
    avg_transfusion_interval_days = Column(Integer, nullable=True)
    days_until_next_transfusion = Column(Integer, nullable=True)

    # Severity classification
    severity = Column(String(50), nullable=True, index=True)
    severity_score = Column(Float, nullable=True)

    # Transfusion prediction
    urgency_level = Column(String(50), nullable=True, index=True)
    days_until_transfusion = Column(Integer, nullable=True)
    next_transfusion_date = Column(String(20), nullable=True)

    # OCR metadata
    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Status
    is_active = Column(Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_code": self.patient_code,
            "name": self.name,
            "age": self.age,
            "sex": self.sex,
            "gender": self.gender,
            "weight_kg": float(self.weight_kg) if self.weight_kg else None,
            "blood_group": self.blood_group,
            "phone": self.phone,
            "location": self.location,
            "spleen_enlargement": self.spleen_enlargement,
            "last_transfusion_date": self.last_transfusion_date,
            "transfusion_interval_days": self.transfusion_interval_days,
            "hb_level": self.hb_level,
            "rbc_count": self.rbc_count,
            "mcv_level": self.mcv_level,
            "mch_level": self.mch_level,
            "mchc_level": self.mchc_level,
            "rdw_pct": float(self.rdw_pct) if self.rdw_pct else None,
            "ferritin_level": self.ferritin_level,
            "hb_a_pct": float(self.hb_a_pct) if self.hb_a_pct else None,
            "hb_a2": self.hb_a2,
            "hb_f": self.hb_f,
            "mentzer_index": float(self.mentzer_index) if self.mentzer_index else None,
            "wbc_count": self.wbc_count,
            "platelet_count": self.platelet_count,
            "hb_post_transfusion": float(self.hb_post_transfusion) if self.hb_post_transfusion else None,
            "hb_drop_rate_per_day": float(self.hb_drop_rate_per_day) if self.hb_drop_rate_per_day else None,
            "hb_transfusion_threshold": float(self.hb_transfusion_threshold) if self.hb_transfusion_threshold else None,
            "days_since_last_transfusion": self.days_since_last_transfusion,
            "units_per_session": float(self.units_per_session) if self.units_per_session else None,
            "avg_transfusion_interval_days": self.avg_transfusion_interval_days,
            "days_until_next_transfusion": self.days_until_next_transfusion,
            "severity": self.severity,
            "severity_score": self.severity_score,
            "urgency_level": self.urgency_level,
            "days_until_transfusion": self.days_until_transfusion,
            "next_transfusion_date": self.next_transfusion_date,
            "ocr_text": self.ocr_text,
            "ocr_confidence": self.ocr_confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
        }
