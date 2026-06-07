from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Task(Base):
    """Blood Warrior task - assigned to contact donors for a patient"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    warrior_id = Column(Integer, nullable=True)  # Assigned warrior (null = unassigned)
    assigned_donors = Column(JSON, nullable=False)  # [{donor_id, score, contacted, response}]
    urgency = Column(String(20), nullable=False)  # CRITICAL, URGENT, SOON, SCHEDULED
    status = Column(String(20), nullable=False, default="pending")  # pending, in_progress, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "warrior_id": self.warrior_id,
            "assigned_donors": self.assigned_donors,
            "urgency": self.urgency,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class AgentRun(Base):
    """Log of autonomous agent runs"""
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_date = Column(DateTime(timezone=True), nullable=False)
    patients_processed = Column(Integer, default=0)
    workflows_created = Column(Integer, default=0)
    tasks_created = Column(Integer, default=0)
    campaigns_started = Column(Integer, default=0)
    status = Column(String(20), nullable=False)  # success, failed, partial
    report = Column(JSON, nullable=True)  # Detailed report
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "run_date": self.run_date.isoformat() if self.run_date else None,
            "patients_processed": self.patients_processed,
            "workflows_created": self.workflows_created,
            "tasks_created": self.tasks_created,
            "campaigns_started": self.campaigns_started,
            "status": self.status,
            "report": self.report,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
