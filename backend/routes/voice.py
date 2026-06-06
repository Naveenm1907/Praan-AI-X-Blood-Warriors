from fastapi import APIRouter
from models.call_session import CampaignCreate, Campaign, CallResponse
import uuid
from datetime import datetime

router = APIRouter(tags=["voice"])

campaigns_db: dict[str, dict] = {}


@router.post("/voice/campaign", response_model=Campaign)
def start_campaign(req: CampaignCreate):
    cid = f"cam{uuid.uuid4().hex[:8]}"
    responses = {did: {"status": "pending", "retry_count": 0} for did in req.donor_ids}
    campaign = {
        "campaign_id": cid,
        "patient_id": req.patient_id,
        "donor_ids": req.donor_ids,
        "status": "calling",
        "responses": responses,
        "language": req.language,
        "target_count": req.target_count,
        "confirmed_count": 0,
        "started_at": datetime.now().isoformat(),
    }
    campaigns_db[cid] = campaign
    return campaign


@router.get("/voice/campaign/{campaign_id}")
def get_campaign(campaign_id: str):
    if campaign_id not in campaigns_db:
        from fastapi import HTTPException
        raise HTTPException(404, "Campaign not found")
    return campaigns_db[campaign_id]


@router.post("/voice/response")
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


@router.post("/voice/cancel")
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


@router.get("/voice/script")
def get_call_script(language: str = "en-IN", blood_group: str = "O+"):
    scripts = {
        "en-IN": f"Hello, this is an automated call from Blood Warriors. A patient with {blood_group} blood group needs your help this week. Can you donate? Press 1 for yes, or press 2 for no.",
        "hi-IN": f"Namaste, yeh Blood Warriors ki taraf se automated call hai. Ek patient ko {blood_group} blood group ki zaroorat hai. Kya aap donate kar sakte hain? Haan ke liye 1 dabayein.",
        "te-IN": f"Namaskaram, idi Blood Warriors nundi automated call. Oka patient ki {blood_group} blood group avasaram. Meeru donate cheyagalara? Yes ki 1 nokkandi.",
        "ta-IN": f"Vanakkam, idhu Blood Warriors la irundhu automated call. Oru patient ku {blood_group} blood group thevai. Neenga donate pannalama? Yes ku 1 amuthunga.",
    }
    return {"language": language, "script": scripts.get(language, scripts["en-IN"])}
