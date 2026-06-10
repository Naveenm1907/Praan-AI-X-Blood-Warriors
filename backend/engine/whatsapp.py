"""
WhatsApp Integration for Blood Warriors
Handles day-before reminders and post-call follow-ups
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.workflow import Workflow

logger = logging.getLogger(__name__)


def schedule_day_before_reminder(
    workflow_id: str,
    donor_id: str,
    phone: str,
    patient_name: str,
    blood_group: str,
    appointment_date: datetime,
    db: Session
) -> dict:
    """
    Schedule WhatsApp reminder for day before appointment.
    In production, integrate with WhatsApp Business API or Twilio.
    """
    reminder_date = appointment_date - timedelta(days=1)

    message = f"""🩸 Blood Warriors Reminder

Hi! This is a reminder from Blood Warriors.

Patient: {patient_name}
Blood Group: {blood_group}
Appointment: {appointment_date.strftime('%d %b %Y, %I:%M %p')}

Your donation can save lives! 💙

Reply YES to confirm or NO to reschedule.

Thank you for being a hero! 🦸
"""

    # Store reminder in database
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    if workflow:
        if not workflow.donor_responses:
            workflow.donor_responses = {}

        if donor_id not in workflow.donor_responses:
            workflow.donor_responses[donor_id] = {}

        workflow.donor_responses[donor_id].update({
            "whatsapp_reminder": {
                "scheduled_for": reminder_date.isoformat(),
                "appointment_date": appointment_date.isoformat(),
                "message": message,
                "status": "scheduled",
                "phone": phone
            }
        })
        db.commit()

    logger.info(f"Scheduled WhatsApp reminder for {donor_id} at {reminder_date}")

    # In production: Call WhatsApp API here
    # response = send_whatsapp_message(phone, message)

    return {
        "status": "scheduled",
        "reminder_date": reminder_date.isoformat(),
        "message": message
    }


def send_post_call_followup(
    workflow_id: str,
    donor_id: str,
    phone: str,
    patient_name: str,
    blood_group: str,
    call_response: str,
    db: Session
) -> dict:
    """
    Send WhatsApp follow-up after voice call based on response.
    """
    if call_response == "confirmed":
        message = f"""✅ Thank you for confirming!

Patient: {patient_name}
Blood Group: {blood_group}

We'll contact you soon with appointment details.

Your donation will save lives! 💙
"""
    elif call_response == "callback":
        message = f"""📞 Thanks for speaking with us!

We understand you're busy. We'll call you back later.

Patient: {patient_name}
Blood Group: {blood_group}

When you're ready, reply with your preferred time.
"""
    else:
        message = f"""🙏 Thank you for your time.

If you change your mind, please contact us.

Patient: {patient_name}
Blood Group: {blood_group}

Every donation counts! 💙
"""

    # Store follow-up in database
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    if workflow and workflow.donor_responses and donor_id in workflow.donor_responses:
        workflow.donor_responses[donor_id].update({
            "whatsapp_followup": {
                "sent_at": datetime.now().isoformat(),
                "response_type": call_response,
                "message": message,
                "status": "sent",
                "phone": phone
            }
        })
        db.commit()

    logger.info(f"Sent WhatsApp follow-up to {donor_id}: {call_response}")

    # In production: Call WhatsApp API here
    # response = send_whatsapp_message(phone, message)

    return {
        "status": "sent",
        "message": message,
        "response_type": call_response
    }


def process_whatsapp_reply(
    workflow_id: str,
    donor_id: str,
    reply_text: str,
    db: Session
) -> dict:
    """
    Process incoming WhatsApp replies and update workflow status.
    """
    reply_lower = reply_text.lower().strip()

    if any(kw in reply_lower for kw in ["yes", "confirm", "ok", "హౌను", "సరే", "हाँ"]):
        new_status = "confirmed"
    elif any(kw in reply_lower for kw in ["no", "cancel", "కాదు", "नहीं"]):
        new_status = "declined"
    else:
        new_status = "callback"

    # Update workflow
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    if workflow and workflow.donor_responses and donor_id in workflow.donor_responses:
        workflow.donor_responses[donor_id].update({
            "whatsapp_reply": {
                "received_at": datetime.now().isoformat(),
                "reply_text": reply_text,
                "interpreted_as": new_status
            },
            "response": new_status
        })
        db.commit()

        logger.info(f"Processed WhatsApp reply from {donor_id}: '{reply_text}' -> {new_status}")

    return {
        "donor_id": donor_id,
        "interpreted_response": new_status,
        "reply_text": reply_text
    }
