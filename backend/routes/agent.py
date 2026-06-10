from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from engine.agent import PRAANAgent
from models.task import AgentRun
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["agent"])


@router.post("/run-daily")
def run_daily_agent_cycle(
    auto_contact: bool = False,
    db: Session = Depends(get_db)
):
    """
    Trigger autonomous daily cycle.
    - Finds urgent patients (transfusion within 7 days)
    - AI ranks donors for each patient
    - Creates workflows + warrior tasks
    - Optionally auto-starts contact campaigns
    """
    try:
        agent = PRAANAgent(db)
        report = agent.run_daily_cycle(auto_contact=auto_contact)
        return {
            "status": "success",
            "message": f"Processed {report['patients_processed']} patients",
            "report": report,
        }
    except Exception as e:
        logger.error(f"Agent run failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent run failed: {str(e)}")


@router.get("/status")
def get_agent_status(db: Session = Depends(get_db)):
    """Get status of last agent run"""
    agent = PRAANAgent(db)
    return agent.get_last_run_status()


@router.get("/history")
def get_agent_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get agent run history"""
    runs = db.query(AgentRun).order_by(AgentRun.created_at.desc()).limit(limit).all()
    return [run.to_dict() for run in runs]


@router.post("/process-patient/{patient_id}")
def process_single_patient(
    patient_id: int,
    auto_contact: bool = False,
    db: Session = Depends(get_db)
):
    """
    Process a single patient (triggered when URGENT/CRITICAL patient registers)
    """
    from models.patient import Patient

    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Only process if urgent
    if patient.urgency_level not in ["CRITICAL", "URGENT", "SOON"]:
        return {
            "status": "skipped",
            "message": f"Patient urgency is {patient.urgency_level}, not urgent enough for auto-processing"
        }

    try:
        agent = PRAANAgent(db)
        workflow_id = agent._create_workflow(patient)
        ranked_donors = agent._ai_rank_donors(patient)
        agent._assign_donors_to_workflow(workflow_id, ranked_donors[:10])
        task = agent._create_warrior_task(patient, ranked_donors[:10])

        campaign_id = None
        if auto_contact and len(ranked_donors) > 0:
            campaign_id = agent._auto_start_campaign(workflow_id)

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "task_id": task.id,
            "donors_assigned": min(10, len(ranked_donors)),
            "campaign_started": campaign_id is not None,
            "campaign_id": campaign_id,
        }
    except Exception as e:
        logger.error(f"Failed to process patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process patient: {str(e)}")
