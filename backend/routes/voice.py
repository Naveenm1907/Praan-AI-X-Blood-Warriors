from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from database.models import Donor as DonorDB  # SQLAlchemy model
from models.donor import Donor  # Pydantic model
from models.call_session import CampaignCreate, Campaign, CallResponse
from engine.bland_ai import create_donor_confirmation_call, get_call_transcript
from models.workflow import Workflow
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["voice"])

campaigns_db: dict[str, dict] = {}
call_tracker: dict[str, dict] = {}  # call_id -> {workflow_id, donor_id}


@router.post("/campaign", response_model=Campaign)
def start_campaign(req: CampaignCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Start Bland AI voice campaign with parallel calling (2 donors at a time)"""
    cid = f"cam{uuid.uuid4().hex[:8]}"

    # Get workflow
    workflow = db.query(Workflow).filter(
        Workflow.patient_id == req.patient_id,
        Workflow.completed_at == None
    ).order_by(Workflow.created_at.desc()).first()

    if not workflow:
        raise HTTPException(404, "No workflow found for this patient")

    # Fetch real donor data from database
    donors = db.query(DonorDB).filter(DonorDB.id.in_(req.donor_ids)).all()
    if len(donors) != len(req.donor_ids):
        found_ids = {d.id for d in donors}
        missing_ids = set(req.donor_ids) - found_ids
        raise HTTPException(404, f"Donors not found in database: {missing_ids}")

    # Build donor map with real phone numbers
    donor_map = {d.id: {"phone": d.phone, "name": d.name} for d in donors}

    # Validate all donors have phone numbers
    for donor_id in req.donor_ids:
        if not donor_map[donor_id]["phone"]:
            raise HTTPException(400, f"Donor {donor_id} has no phone number in database")

    # Initialize campaign
    responses = {}
    for did in req.donor_ids:
        donor_info = donor_map[did]
        responses[did] = {
            "status": "pending",
            "retry_count": 0,
            "phone": donor_info["phone"],
            "name": donor_info["name"],
            "call_id": None,
            "response": None
        }

    campaign = {
        "campaign_id": cid,
        "patient_id": req.patient_id,
        "patient_name": workflow.patient_data.get("name", "Patient"),
        "blood_group": workflow.patient_data.get("blood_group"),
        "workflow_id": workflow.workflow_id,
        "donor_ids": req.donor_ids,
        "status": "calling",
        "responses": responses,
        "language": req.language,
        "target_count": req.target_count,
        "confirmed_count": 0,
        "started_at": datetime.now().isoformat(),
        "max_parallel": 2  # Call 2 donors at a time
    }
    campaigns_db[cid] = campaign

    # Start first batch of calls in background
    background_tasks.add_task(_run_parallel_calls, cid, db)

    return campaign


def _run_parallel_calls(campaign_id: str, db: Session):
    """Run parallel voice calls (2 at a time)"""
    import time

    campaign = campaigns_db.get(campaign_id)
    if not campaign:
        return

    pending_donors = [did for did, resp in campaign["responses"].items() if resp["status"] == "pending"]

    for i in range(0, len(pending_donors), campaign["max_parallel"]):
        batch = pending_donors[i:i + campaign["max_parallel"]]

        # Initiate calls for this batch
        for donor_id in batch:
            donor_info = campaign["responses"][donor_id]
            phone = donor_info["phone"]
            name = donor_info["name"]

            if not phone:
                donor_info["status"] = "no_phone"
                continue

            # Create Bland AI call
            result = create_donor_confirmation_call(
                phone_number=phone,
                patient_name=campaign["patient_name"],
                blood_group=campaign["blood_group"],
                donor_name=name,
                language=campaign["language"]
            )

            if result["status"] == "initiated":
                call_id = result["call_id"]
                donor_info["call_id"] = call_id
                donor_info["status"] = "calling"
                call_tracker[call_id] = {
                    "campaign_id": campaign_id,
                    "donor_id": donor_id,
                    "workflow_id": campaign["workflow_id"]
                }
                logger.info(f"Initiated call {call_id} to {name} ({phone})")
            else:
                donor_info["status"] = "failed"
                donor_info["error"] = result.get("error", "Unknown error")
                logger.error(f"Failed to initiate call to {name}: {result}")
                print(f"CAMPAIGN ERROR for {name} ({phone}): {result}")

        # Wait for batch to complete before starting next batch
        if i + campaign["max_parallel"] < len(pending_donors):
            time.sleep(60)  # Wait 60 seconds between batches


@router.get("/campaign/{campaign_id}")
def get_campaign(campaign_id: str):
    if campaign_id not in campaigns_db:
        from fastapi import HTTPException
        raise HTTPException(404, "Campaign not found")
    return campaigns_db[campaign_id]


@router.post("/call-donor")
async def call_single_donor(request: Request, db: Session = Depends(get_db)):
    """Initiate Bland AI call to a single donor"""
    body = await request.json()
    donor_id = body.get("donor_id")
    patient_name = body.get("patient_name")
    blood_group = body.get("blood_group")
    language = body.get("language", "te")
    workflow_id = body.get("workflow_id")
    patient_id = body.get("patient_id")

    if not all([donor_id, patient_name, blood_group]):
        raise HTTPException(400, f"Missing required fields. Got: donor_id={donor_id}, patient_name={patient_name}, blood_group={blood_group}")

    # Fetch real donor from database
    donor = db.query(DonorDB).filter(DonorDB.id == donor_id).first()
    if not donor:
        raise HTTPException(404, f"Donor {donor_id} not found in database")

    donor_phone = donor.phone
    donor_name = donor.name

    if not donor_phone:
        raise HTTPException(400, f"Donor {donor_id} has no phone number in database")

    # Look up workflow_id from patient if not provided
    if not workflow_id and patient_id:
        wf = db.query(Workflow).filter(
            Workflow.patient_id == str(patient_id),
            Workflow.completed_at == None
        ).order_by(Workflow.created_at.desc()).first()
        if wf:
            workflow_id = wf.workflow_id

    # Initiate call
    result = create_donor_confirmation_call(
        phone_number=donor_phone,
        patient_name=patient_name,
        blood_group=blood_group,
        donor_name=donor_name or f"Donor {donor_id}",
        language=language
    )

    if result["status"] == "initiated":
        call_id = result["call_id"]

        # Track the call
        call_tracker[call_id] = {
            "workflow_id": workflow_id,
            "donor_id": donor_id,
            "patient_id": patient_id
        }

        # Update workflow if found
        if workflow_id:
            workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
            if workflow:
                if not workflow.donor_responses:
                    workflow.donor_responses = []

                donor_resp = next((d for d in workflow.donor_responses if d["donor_id"] == donor_id), None)
                if donor_resp:
                    donor_resp["status"] = "calling"
                    donor_resp["call_id"] = call_id
                else:
                    workflow.donor_responses.append({
                        "donor_id": donor_id,
                        "status": "calling",
                        "call_id": call_id,
                        "phone": donor_phone
                    })

                db.commit()

        return {"status": "success", "call_id": call_id, "message": f"Call initiated to {donor_name}"}
    else:
        raise HTTPException(500, f"Failed to initiate call: {result.get('error')}")


@router.post("/response")
def record_response(campaign_id: str, donor_id: str, response: str):
    if campaign_id not in campaigns_db:
        from fastapi import HTTPException
        raise HTTPException(404, "Campaign not found")
    cam = campaigns_db[campaign_id]
    cam["responses"][donor_id] = {
        "status": response,
        "timestamp": datetime.now().isoformat(),
        "retry_count": cam["responses"].get(donor_id, {}).get("retry_count", 0),
    }
    if response == "confirmed":
        cam["confirmed_count"] += 1
    if cam["confirmed_count"] >= cam["target_count"]:
        cam["status"] = "completed"
        for did in cam["donor_ids"]:
            if cam["responses"][did]["status"] in ("pending", "calling"):
                cam["responses"][did]["status"] = "cancelled"
    return cam


@router.post("/cancel")
def cancel_campaign(campaign_id: str):
    if campaign_id not in campaigns_db:
        from fastapi import HTTPException
        raise HTTPException(404, "Campaign not found")
    cam = campaigns_db[campaign_id]
    cam["status"] = "cancelled"
    cancelled = 0
    for did in cam["donor_ids"]:
        if cam["responses"][did]["status"] in ("pending", "calling"):
            cam["responses"][did]["status"] = "cancelled"
            cancelled += 1
    return {"campaign_id": campaign_id, "cancelled_calls": cancelled}


@router.get("/script")
def get_call_script(language: str = "en-IN", blood_group: str = "O+"):
    scripts = {
        "en-IN": f"Hello, this is an automated call from Blood Warriors. A patient with {blood_group} blood group needs your help this week. Can you donate? Press 1 for yes, or press 2 for no.",
        "hi-IN": f"Namaste, yeh Blood Warriors ki taraf se automated call hai. Ek patient ko {blood_group} blood group ki zaroorat hai. Kya aap donate kar sakte hain? Haan ke liye 1 dabayein.",
        "te-IN": f"Namaskaram, idi Blood Warriors nundi automated call. Oka patient ki {blood_group} blood group avasaram. Meeru donate cheyagalara? Yes ki 1 nokkandi.",
        "ta-IN": f"Vanakkam, idhu Blood Warriors la irundhu automated call. Oru patient ku {blood_group} blood group thevai. Neenga donate pannalama? Yes ku 1 amuthunga.",
    }
    return {"language": language, "script": scripts.get(language, scripts["en-IN"])}


@router.post("/bland/webhook")
async def bland_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Bland AI webhook - receives call completion with transcript
    Auto-parses donor response and updates workflow/campaign
    """
    try:
        payload = await request.json()
        call_id = payload.get("call_id")
        call_status = payload.get("status")
        transcript = payload.get("transcript")

        if not call_id or call_id not in call_tracker:
            logger.warning(f"Unknown call_id: {call_id}")
            return {"status": "ignored"}

        tracker = call_tracker[call_id]
        campaign_id = tracker["campaign_id"]
        donor_id = tracker["donor_id"]
        workflow_id = tracker["workflow_id"]

        # Parse transcript to extract response
        response = _parse_transcript(transcript) if transcript else "no_response"

        # Update campaign
        campaign = campaigns_db.get(campaign_id)
        if campaign and donor_id in campaign["responses"]:
            campaign["responses"][donor_id].update({
                "status": "completed",
                "response": response,
                "call_id": call_id,
                "transcript": transcript,
                "completed_at": datetime.now().isoformat()
            })

            # Update confirmed count
            if response == "confirmed":
                campaign["confirmed_count"] = sum(
                    1 for r in campaign["responses"].values()
                    if r.get("response") == "confirmed"
                )

                # Check if target reached
                if campaign["confirmed_count"] >= campaign["target_count"]:
                    campaign["status"] = "completed"

        # Update workflow in database
        workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
        if workflow:
            if not workflow.donor_responses:
                workflow.donor_responses = {}

            workflow.donor_responses[donor_id] = {
                "response": response,
                "call_id": call_id,
                "transcript": transcript,
                "updated_at": datetime.now().isoformat()
            }
            db.commit()

            logger.info(f"Updated workflow {workflow_id}: donor {donor_id} -> {response}")

        # Clean up tracker
        del call_tracker[call_id]

        return {"status": "ok", "response": response}

    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        raise HTTPException(500, str(e))


def _parse_transcript(transcript: str) -> str:
    """
    Parse transcript to extract donor response.
    Returns: "confirmed", "declined", "callback", or "no_response"
    """
    if not transcript:
        return "no_response"

    transcript_lower = transcript.lower()

    # Confirmation keywords (multilingual)
    confirm_keywords = ["yes", "okay", "ok", "sure", "confirm", "agree",
                       "హౌను", "సరే", "అవును", "हाँ", "ठीक", "जी"]
    decline_keywords = ["no", "nope", "sorry", "can't", "cannot", "busy",
                       "కాదు", "లేదు", "नहीं", "माफ़"]
    callback_keywords = ["later", "call back", "busy now", "not available",
                        "తర్వాత", "తరువాत", "बाद में"]

    # Check for decline first (more specific)
    if any(kw in transcript_lower for kw in decline_keywords):
        return "declined"

    # Check for callback request
    if any(kw in transcript_lower for kw in callback_keywords):
        return "callback"

    # Check for confirmation
    if any(kw in transcript_lower for kw in confirm_keywords):
        return "confirmed"

    return "no_response"
