from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from database import Base


class Workflow(Base):
    """Persistent workflow storage"""
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String(50), unique=True, nullable=False, index=True)
    patient_id = Column(String(50), nullable=False, index=True)
    patient_data = Column(JSON, nullable=True)
    current_step = Column(String(100), nullable=False, default="patient_registered")
    steps = Column(JSON, nullable=False)
    ranked_donors = Column(JSON, nullable=True)
    whatsapp_campaign = Column(JSON, nullable=True)
    voice_campaign = Column(JSON, nullable=True)
    donor_responses = Column(JSON, nullable=True)
    scoring_method = Column(String(50), nullable=True, default="xgboost_ai")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self):
        return {
            "workflow_id": self.workflow_id,
            "patient_id": self.patient_id,
            "patient_data": self.patient_data,
            "current_step": self.current_step,
            "steps": self.steps,
            "ranked_donors": self.ranked_donors,
            "whatsapp_campaign": self.whatsapp_campaign,
            "voice_campaign": self.voice_campaign,
            "donor_responses": self.donor_responses,
            "scoring_method": self.scoring_method,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
