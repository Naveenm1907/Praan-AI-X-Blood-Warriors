"""
WhatsApp Routes for Blood Warriors
Handles reminders, follow-ups, and reply processing
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import logging

from database import get_db
from engine.whatsapp import (
    schedule_day_before_reminder,
    send_post_call_followup,
    process_whatsapp_reply
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


class ReminderRequest(BaseModel):
    workflow_id: str
    donor_id: str
    phone: str
    patient_name: str
    blood_group: str
    appointment_date: str  # ISO format


class FollowupRequest(BaseModel):
    workflow_id: str
    donor_id: str
    phone: str
    patient_name: str
    blood_group: str
    call_response: str


class WhatsAppReply(BaseModel):
    workflow_id: str
    donor_id: str
    reply_text: str


@router.post("/schedule-reminder")
async def schedule_reminder(request: ReminderRequest, db: Session = Depends(get_db)):
    """
    Schedule day-before WhatsApp reminder for donor appointment.
    """
    try:
        appointment_date = datetime.fromisoformat(request.appointment_date)

        result = schedule_day_before_reminder(
            workflow_id=request.workflow_id,
            donor_id=request.donor_id,
            phone=request.phone,
            patient_name=request.patient_name,
            blood_group=request.blood_group,
            appointment_date=appointment_date,
            db=db
        )

        return {
            "status": "success",
            "message": f"Reminder scheduled for {result['reminder_date']}",
            "data": result
        }

    except Exception as e:
        logger.error(f"Failed to schedule reminder: {e}", exc_info=True)
        raise HTTPException(500, str(e))


@router.post("/send-followup")
async def send_followup(request: FollowupRequest, db: Session = Depends(get_db)):
    """
    Send WhatsApp follow-up after voice call.
    """
    try:
        result = send_post_call_followup(
            workflow_id=request.workflow_id,
            donor_id=request.donor_id,
            phone=request.phone,
            patient_name=request.patient_name,
            blood_group=request.blood_group,
            call_response=request.call_response,
            db=db
        )

        return {
            "status": "success",
            "message": f"Follow-up sent: {request.call_response}",
            "data": result
        }

    except Exception as e:
        logger.error(f"Failed to send follow-up: {e}", exc_info=True)
        raise HTTPException(500, str(e))


@router.post("/reply-webhook")
async def whatsapp_reply_webhook(reply: WhatsAppReply, db: Session = Depends(get_db)):
    """
    Process incoming WhatsApp replies.
    In production, this would be called by WhatsApp Business API webhook.
    """
    try:
        result = process_whatsapp_reply(
            workflow_id=reply.workflow_id,
            donor_id=reply.donor_id,
            reply_text=reply.reply_text,
            db=db
        )

        return {
            "status": "success",
            "message": f"Reply processed: {result['interpreted_response']}",
            "data": result
        }

    except Exception as e:
        logger.error(f"Failed to process reply: {e}", exc_info=True)
        raise HTTPException(500, str(e))


@router.get("/campaign-status/{workflow_id}")
async def get_whatsapp_status(workflow_id: str, db: Session = Depends(get_db)):
    """
    Get WhatsApp campaign status for a workflow.
    """
    from models.workflow import Workflow

    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()

    if not workflow:
        raise HTTPException(404, "Workflow not found")

    # Extract WhatsApp data from donor_responses
    whatsapp_data = {}
    if workflow.donor_responses:
        for donor_id, response in workflow.donor_responses.items():
            whatsapp_data[donor_id] = {
                "reminder": response.get("whatsapp_reminder"),
                "followup": response.get("whatsapp_followup"),
                "reply": response.get("whatsapp_reply")
            }

    return {
        "workflow_id": workflow_id,
        "whatsapp_campaigns": whatsapp_data,
        "total_donors": len(whatsapp_data)
    }
