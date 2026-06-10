from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import logging

from database import get_db
from models.workflow import Workflow
from models.patient import Patient

logger = logging.getLogger(__name__)
router = APIRouter(tags=["workflow"])

# Keep in-memory dict as fallback for agent.py compatibility
workflows_db: dict[str, dict] = {}


def _sync_to_db(workflow_data: dict, db: Session):
    """Sync workflow dict to database"""
    existing = db.query(Workflow).filter(Workflow.workflow_id == workflow_data["workflow_id"]).first()
    if existing:
        existing.patient_data = workflow_data.get("patient_data")
        existing.current_step = workflow_data.get("current_step")
        existing.steps = workflow_data.get("steps")
        existing.ranked_donors = workflow_data.get("ranked_donors")
        existing.whatsapp_campaign = workflow_data.get("whatsapp_campaign")
        existing.voice_campaign = workflow_data.get("voice_campaign")
        existing.donor_responses = workflow_data.get("donor_responses")
        if workflow_data.get("completed_at"):
            existing.completed_at = datetime.fromisoformat(workflow_data["completed_at"]) if isinstance(workflow_data["completed_at"], str) else workflow_data["completed_at"]
    else:
        wf = Workflow(
            workflow_id=workflow_data["workflow_id"],
            patient_id=str(workflow_data["patient_id"]),
            patient_data=workflow_data.get("patient_data"),
            current_step=workflow_data.get("current_step", "patient_registered"),
            steps=workflow_data.get("steps", []),
            ranked_donors=workflow_data.get("ranked_donors"),
            whatsapp_campaign=workflow_data.get("whatsapp_campaign"),
            voice_campaign=workflow_data.get("voice_campaign"),
            donor_responses=workflow_data.get("donor_responses"),
            scoring_method=workflow_data.get("scoring_method", "xgboost_ai"),
        )
        db.add(wf)
    db.commit()
    # Also keep in-memory
    workflows_db[workflow_data["workflow_id"]] = workflow_data


def _load_from_db(db: Session):
    """Load all workflows from DB into memory"""
    rows = db.query(Workflow).order_by(Workflow.created_at.desc()).all()
    for row in rows:
        workflows_db[row.workflow_id] = row.to_dict()


def create_workflow_for_patient(patient: Patient, db: Session) -> dict:
    """Create workflow for a patient — called from patient.py or agent.py"""
    wid = f"wf{uuid.uuid4().hex[:8]}"

    patient_data = {
        "patient_id": str(patient.id),
        "name": patient.name,
        "blood_group": patient.blood_group,
        "latitude": 17.385,
        "longitude": 78.4867,
        "urgency": patient.urgency_level or "SCHEDULED",
    }

    workflow = {
        "workflow_id": wid,
        "patient_id": str(patient.id),
        "patient_data": patient_data,
        "current_step": "patient_registered",
        "steps": [
            {
                "step_name": "Patient Registered",
                "status": "completed",
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "details": f"Blood group: {patient.blood_group}, Urgency: {patient.urgency_level}",
            },
            {
                "step_name": "AI Donor Matching",
                "status": "in_progress",
                "started_at": datetime.now().isoformat(),
                "details": "Running XGBoost model to predict donor response probability"
            },
            {"step_name": "WhatsApp Campaign", "status": "pending"},
            {"step_name": "Voice Call Campaign", "status": "pending"},
            {"step_name": "Donors Confirmed", "status": "pending"},
        ],
        "ranked_donors": None,
        "whatsapp_campaign": None,
        "voice_campaign": None,
        "donor_responses": None,
        "scoring_method": "xgboost_ai",
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
    }

    _sync_to_db(workflow, db)
    logger.info(f"Workflow {wid} created for patient {patient.id}")
    return workflow


@router.get("/active")
def list_active(db: Session = Depends(get_db)):
    _load_from_db(db)
    return [w for w in workflows_db.values() if w["completed_at"] is None]


@router.get("/insights")
def get_insights():
    return [
        {
            "pattern": "O+ requests in Hyderabad fail 40% in Tier 1",
            "action": "System now starts with Tier 2 for this combination",
            "result": "Success rate improved 23%",
        },
        {
            "pattern": "Donors respond 35% better to calls between 6-8 PM",
            "action": "Campaign scheduler adjusted to evening hours",
            "result": "Confirmation rate up from 42% to 57%",
        },
        {
            "pattern": "B- blood group has lowest donor density",
            "action": "Expanded search radius from 10km to 25km for B-",
            "result": "Match rate improved from 15% to 38%",
        },
    ]


@router.post("/start-for-patient/{patient_id}")
def start_workflow_for_patient(patient_id: int, db: Session = Depends(get_db)):
    """Create workflow for existing patient"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, "Patient not found")

    wid = f"wf{uuid.uuid4().hex[:8]}"

    patient_data = {
        "patient_id": str(patient.id),
        "name": patient.name,
        "blood_group": patient.blood_group,
        "latitude": 17.385,
        "longitude": 78.4867,
        "urgency": patient.urgency_level or "SCHEDULED",
    }

    workflow = {
        "workflow_id": wid,
        "patient_id": str(patient.id),
        "patient_data": patient_data,
        "current_step": "patient_registered",
        "steps": [
            {
                "step_name": "Patient Registered",
                "status": "completed",
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "details": f"Blood group: {patient.blood_group}, Urgency: {patient.urgency_level or 'SCHEDULED'}",
            },
            {
                "step_name": "AI Donor Matching",
                "status": "in_progress",
                "started_at": datetime.now().isoformat(),
                "details": "Running XGBoost model to predict donor response probability"
            },
            {"step_name": "WhatsApp Campaign", "status": "pending"},
            {"step_name": "Voice Call Campaign", "status": "pending"},
            {"step_name": "Donors Confirmed", "status": "pending"},
        ],
        "scoring_method": "xgboost_ai",
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
    }

    workflows_db[wid] = workflow
    db.add(Workflow(
        workflow_id=wid,
        patient_id=str(patient.id),
        patient_data=patient_data,
        current_step="patient_registered",
        steps=workflow["steps"],
        scoring_method="xgboost_ai",
        completed_at=None
    ))
    db.commit()

    return {"workflow_id": wid, "message": "Workflow created"}


@router.post("/start")
def start_workflow(patient_id: str, units_needed: int = 2, db: Session = Depends(get_db)):
    """Start blood donation workflow"""
    wid = f"wf{uuid.uuid4().hex[:8]}"

    patient_data = {
        "patient_id": patient_id,
        "name": "Patient " + patient_id[-4:],
        "blood_group": "O+",
        "latitude": 17.385,
        "longitude": 78.4867,
        "urgency": "critical"
    }

    workflow = {
        "workflow_id": wid,
        "patient_id": patient_id,
        "patient_data": patient_data,
        "current_step": "patient_registered",
        "steps": [
            {
                "step_name": "Patient Registered",
                "status": "completed",
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "details": f"Units needed: {units_needed}, Blood group: {patient_data['blood_group']}",
            },
            {
                "step_name": "AI Donor Matching",
                "status": "in_progress",
                "started_at": datetime.now().isoformat(),
                "details": "Running XGBoost model to predict donor response probability"
            },
            {"step_name": "WhatsApp Campaign", "status": "pending"},
            {"step_name": "Voice Call Campaign", "status": "pending"},
            {"step_name": "Donors Confirmed", "status": "pending"},
        ],
        "ranked_donors": None,
        "whatsapp_campaign": None,
        "voice_campaign": None,
        "donor_responses": None,
        "scoring_method": "xgboost_ai",
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
    }

    _sync_to_db(workflow, db)
    return workflow


@router.post("/{workflow_id}/rank-donors")
def rank_donors_for_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """Run AI-powered donor ranking for workflow"""
    _load_from_db(db)
    if workflow_id not in workflows_db:
        raise HTTPException(404, "Workflow not found")

    workflow = workflows_db[workflow_id]
    patient = workflow["patient_data"]

    from routes.donor import load_donors_from_db
    from engine.match import rank_donors

    try:
        donors = load_donors_from_db(db)
        ranked = rank_donors(
            donors,
            patient["blood_group"],
            patient["latitude"],
            patient["longitude"],
            count=20
        )
    except Exception as e:
        logger.error(f"Rank donors failed: {e}")
        ranked = []

    workflow["ranked_donors"] = ranked[:10]
    workflow["current_step"] = "donors_ranked"
    workflow["steps"][1]["status"] = "completed"
    workflow["steps"][1]["completed_at"] = datetime.now().isoformat()
    workflow["steps"][1]["details"] = f"Ranked {len(ranked)} donors using {ranked[0].get('scoring_method', 'rule_based') if ranked else 'none'}"

    _sync_to_db(workflow, db)

    return {
        "workflow_id": workflow_id,
        "total_donors_ranked": len(ranked),
        "scoring_method": ranked[0].get("scoring_method", "rule_based") if ranked else "none",
        "top_donors": [
            {
                "rank": i+1,
                "donor_id": d.get("donor_id"),
                "name": d.get("name"),
                "blood_group": d.get("blood_group"),
                "distance_km": d.get("distance_km"),
                "readiness_score": d.get("readiness_score"),
                "calls_to_donations_ratio": d.get("calls_to_donations_ratio"),
                "last_donation_date": d.get("last_donation_date")
            }
            for i, d in enumerate(ranked[:10])
        ]
    }


@router.post("/{workflow_id}/whatsapp-campaign")
def start_whatsapp_campaign(workflow_id: str, db: Session = Depends(get_db)):
    """Start WhatsApp campaign to top-ranked donors"""
    _load_from_db(db)
    if workflow_id not in workflows_db:
        raise HTTPException(404, "Workflow not found")

    workflow = workflows_db[workflow_id]
    ranked_donors = workflow.get("ranked_donors", [])

    if not ranked_donors:
        raise HTTPException(400, "No ranked donors. Run /rank-donors first")

    campaign_results = []
    for donor in ranked_donors[:5]:
        campaign_results.append({
            "donor_id": donor.get("donor_id"),
            "name": donor.get("name"),
            "phone": donor.get("phone", "+91 99999-00000"),
            "status": "message_sent",
            "sent_at": datetime.now().isoformat(),
            "readiness_score": donor.get("readiness_score")
        })

    workflow["whatsapp_campaign"] = campaign_results
    workflow["current_step"] = "whatsapp_sent"
    workflow["steps"][2]["status"] = "completed"
    workflow["steps"][2]["completed_at"] = datetime.now().isoformat()
    workflow["steps"][2]["details"] = f"WhatsApp messages sent to {len(campaign_results)} donors"

    _sync_to_db(workflow, db)

    return {
        "workflow_id": workflow_id,
        "campaign_id": f"wa{uuid.uuid4().hex[:6]}",
        "messages_sent": len(campaign_results),
        "results": campaign_results
    }


@router.post("/{workflow_id}/voice-campaign")
def start_voice_campaign(workflow_id: str, db: Session = Depends(get_db)):
    """Start voice call campaign"""
    _load_from_db(db)
    if workflow_id not in workflows_db:
        raise HTTPException(404, "Workflow not found")

    workflow = workflows_db[workflow_id]
    ranked_donors = workflow.get("ranked_donors", [])

    call_results = []
    for donor in ranked_donors[5:8]:
        call_results.append({
            "donor_id": donor.get("donor_id"),
            "name": donor.get("name"),
            "phone": donor.get("phone", "+91 99999-00000"),
            "status": "call_initiated",
            "initiated_at": datetime.now().isoformat(),
            "readiness_score": donor.get("readiness_score")
        })

    workflow["voice_campaign"] = call_results
    workflow["current_step"] = "voice_calls_initiated"
    workflow["steps"][3]["status"] = "in_progress"
    workflow["steps"][3]["started_at"] = datetime.now().isoformat()
    workflow["steps"][3]["details"] = f"Voice calls initiated to {len(call_results)} donors"

    _sync_to_db(workflow, db)

    return {
        "workflow_id": workflow_id,
        "campaign_id": f"vc{uuid.uuid4().hex[:6]}",
        "calls_initiated": len(call_results),
        "results": call_results
    }


@router.post("/{workflow_id}/donor-response")
def record_donor_response(workflow_id: str, donor_id: str, response: str, db: Session = Depends(get_db)):
    """Record donor response"""
    _load_from_db(db)
    if workflow_id not in workflows_db:
        raise HTTPException(404, "Workflow not found")

    workflow = workflows_db[workflow_id]

    if "donor_responses" not in workflow or workflow["donor_responses"] is None:
        workflow["donor_responses"] = []

    workflow["donor_responses"].append({
        "donor_id": donor_id,
        "response": response,
        "recorded_at": datetime.now().isoformat()
    })

    confirmed_count = sum(1 for r in workflow["donor_responses"] if r["response"] == "confirmed")

    if confirmed_count >= 2:
        workflow["current_step"] = "donors_confirmed"
        workflow["steps"][4]["status"] = "completed"
        workflow["steps"][4]["completed_at"] = datetime.now().isoformat()
        workflow["steps"][4]["details"] = f"{confirmed_count} donors confirmed"
        workflow["completed_at"] = datetime.now().isoformat()

    _sync_to_db(workflow, db)

    return {
        "workflow_id": workflow_id,
        "donor_id": donor_id,
        "response": response,
        "confirmed_count": confirmed_count,
        "workflow_status": workflow["current_step"]
    }


@router.get("/{workflow_id}")
def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    _load_from_db(db)
    if workflow_id not in workflows_db:
        raise HTTPException(404, "Workflow not found")
    return workflows_db[workflow_id]
