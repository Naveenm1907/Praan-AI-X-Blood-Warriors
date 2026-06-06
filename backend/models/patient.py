from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from database import Base


class Patient(Base):
    __tablename__ = "patients"

    # Basic info
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    blood_group = Column(String(10), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    location = Column(String, nullable=False)

    # Medical info
    last_transfusion_date = Column(String(20), nullable=True)
    transfusion_interval_days = Column(Integer, default=28)

    # Blood parameters (from OCR or manual entry)
    hb_level = Column(Float, nullable=True)
    mcv_level = Column(Float, nullable=True)
    mch_level = Column(Float, nullable=True)
    mchc_level = Column(Float, nullable=True)
    rbc_count = Column(Float, nullable=True)
    wbc_count = Column(Float, nullable=True)
    platelet_count = Column(Float, nullable=True)
    ferritin_level = Column(Float, nullable=True)
    hb_a2 = Column(Float, nullable=True)
    hb_f = Column(Float, nullable=True)

    # Severity classification
    severity = Column(String(50), nullable=True)
    severity_score = Column(Float, nullable=True)

    # Transfusion prediction
    urgency_level = Column(String(50), nullable=True)
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
            "rbc_count": self.rbc_count,
            "wbc_count": self.wbc_count,
            "platelet_count": self.platelet_count,
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
            "is_active": self.is_active,
        }
