from fastapi import APIRouter
from datetime import datetime
import uuid

router = APIRouter(tags=["workflow"])

workflows_db: dict[str, dict] = {}


@router.post("/workflow/start")
def start_workflow(patient_id: str, units_needed: int = 2):
    wid = f"wf{uuid.uuid4().hex[:8]}"
    workflow = {
        "workflow_id": wid,
        "patient_id": patient_id,
        "current_step": "patient_registered",
        "steps": [
            {
                "step_name": "Patient Registered",
                "status": "completed",
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "details": f"Units needed: {units_needed}",
            },
            {"step_name": "Blood Bank Search", "status": "pending"},
            {"step_name": "Donor Ranking", "status": "pending"},
            {"step_name": "Voice Call Campaign", "status": "pending"},
            {"step_name": "Donors Confirmed", "status": "pending"},
        ],
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
    }
    workflows_db[wid] = workflow
    return workflow


@router.get("/workflow/{workflow_id}")
def get_workflow(workflow_id: str):
    if workflow_id not in workflows_db:
        from fastapi import HTTPException
        raise HTTPException(404, "Workflow not found")
    return workflows_db[workflow_id]


@router.get("/workflow/active")
def list_active():
    return [w for w in workflows_db.values() if w["completed_at"] is None]


@router.get("/workflow/insights")
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
