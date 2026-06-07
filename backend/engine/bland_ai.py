"""
Bland AI Voice Calling Integration
Parallel donor confirmation calls with auto-transcript parsing
"""
import json
import urllib.request
import urllib.error
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

BLAND_API_KEY = "org_64aeaa9ac14e978c9cdcd19b58fa17eb772217f6c7d93b5eaf97ca9571aa30fd86aa0952e126486bda6c69"


def create_donor_confirmation_call(
    phone_number: str,
    patient_name: str,
    blood_group: str,
    donor_name: str,
    language: str = "te"
) -> dict:
    """
    Initiate Bland AI call to confirm donor availability.
    Returns: {"call_id": "...", "status": "initiated"}
    """

    # Normalize phone number - add + if missing
    if phone_number and not phone_number.startswith('+'):
        phone_number = '+' + phone_number

    # Telugu script (default)
    task_script = f"""You are Priya, a real human representative calling from Blood Warriors.
You are NOT an AI — never reveal you are an AI, even if asked directly.
Speak naturally in Telugu, the way a real person would talk on the phone.
Use casual, conversational Telugu — not robotic or overly formal.
Add natural fillers like "అవునా", "సరే", "ఓహ్", "అర్థమైంది" to sound human.
Pause naturally. React to what the person says before moving to next question.

Your goal is to confirm if {donor_name} can donate blood for patient {patient_name} (Blood Group: {blood_group}).

How to run the conversation:
- Open warmly: "హలో! నమస్కారం, నేను Priya ని మాట్లాడుతున్నాను Blood Warriors నుండి. మీరు {donor_name} అవునా?"
- Wait for confirmation. If yes, continue:
- Explain briefly: "ఒక patient కి {blood_group} blood group అవసరం. మీరు donate చేయగలరా?"
- Listen to their response. If they say yes, confirm: "చాలా థాంక్యూ! మీరు confirm చేసారు కదా, సరిగ్గా అర్థమైందా?"
- If they decline or unsure, ask politely: "సరే, మీకు ఎప్పుడు convenient అవుతుంది?"
- Close warmly: "మీ సహాయానికి చాలా ధన్యవాదాలు! మళ్ళీ contact చేస్తాం. మీ రోజు బాగుండాలి!"

Important rules:
- Never rush. Sound relaxed and genuine.
- If they ask which organization, say: "Blood Warriors - ఒక blood donation coordination platform."
- If they are busy, politely ask: "సరే, మీకు convenient అయిన time చెప్తారా?"
- If they refuse, respect it and close politely.
- Do NOT sound like a robot. Sound like a real Telugu-speaking person.
- Key phrases to listen for:
  - CONFIRMED: "అవును", "చేస్తాను", "ok", "sure", "yes"
  - DECLINED: "కాదు", "చేయను", "no", "cannot", "busy"
  - UNCERTAIN: "తర్వాత", "later", "think", "maybe"
"""

    # English script (fallback)
    if language == "en":
        task_script = f"""You are Priya, calling from Blood Warriors.
Speak naturally, conversationally.

Goal: Confirm if {donor_name} can donate blood for patient {patient_name} (Blood Group: {blood_group}).

Conversation flow:
- Open: "Hello! This is Priya from Blood Warriors. Am I speaking with {donor_name}?"
- If yes: "Great! We have a patient who needs {blood_group} blood. Would you be able to donate this week?"
- Listen carefully. If they say yes: "Wonderful! Just to confirm - you're available to donate, correct?"
- If they decline: "I understand. Would a different time work better for you?"
- Close: "Thank you so much for your time! We'll be in touch. Have a great day!"

Key phrases:
- CONFIRMED: "yes", "sure", "I can", "available", "okay"
- DECLINED: "no", "can't", "busy", "not available"
- UNCERTAIN: "maybe", "later", "let me think", "not sure"
"""

    payload = {
        "phone_number": phone_number,
        "task": task_script,
        "model": "enhanced",
        "max_duration": 3,  # Keep calls short (3 min max)
        "wait_for_greeting": True,
        "record": True
    }

    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "https://api.bland.ai/v1/calls",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": BLAND_API_KEY,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            method="POST"
        )

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("call_id"):
            logger.info(f"Bland AI call initiated: {data['call_id']} to {phone_number}")
            return {
                "call_id": data["call_id"],
                "status": "initiated",
                "phone_number": phone_number
            }
        else:
            logger.error(f"Bland AI call failed: {data}")
            return {"call_id": None, "status": "failed", "error": str(data)}

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        logger.error(f"Bland AI HTTP error {e.code}: {error_body}")
        print(f"BLAND AI ERROR: HTTP {e.code} - {error_body}")
        return {"call_id": None, "status": "failed", "error": f"HTTP {e.code}: {error_body}"}
    except Exception as e:
        logger.error(f"Bland AI exception: {e}")
        print(f"BLAND AI EXCEPTION: {e}")
        return {"call_id": None, "status": "failed", "error": str(e)}


def get_call_transcript(call_id: str) -> dict:
    """
    Fetch transcript and parse response from Bland AI.
    Returns: {"status": "confirmed|declined|uncertain", "transcript": [...], "summary": "..."}
    """
    try:
        req = urllib.request.Request(
            f"https://api.bland.ai/v1/calls/{call_id}",
            headers={"Authorization": BLAND_API_KEY}
        )

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))

        # Parse response from transcript
        transcripts = data.get("transcripts", [])
        summary = data.get("summary", "")

        # Determine status based on keywords
        status = _parse_donor_response(transcripts, summary)

        return {
            "call_id": call_id,
            "status": status,
            "call_status": data.get("status"),
            "duration": data.get("call_length"),
            "transcripts": transcripts,
            "summary": summary,
            "recording_url": data.get("recording_url")
        }

    except Exception as e:
        logger.error(f"Failed to get transcript for {call_id}: {e}")
        return {"call_id": call_id, "status": "error", "error": str(e)}


def _parse_donor_response(transcripts: list, summary: str) -> str:
    """
    Parse transcript to determine donor response.
    Returns: "confirmed", "declined", "uncertain", or "no_response"
    """
    # Combine all text
    full_text = " ".join([t.get("text", "").lower() for t in transcripts])
    summary_lower = summary.lower() if summary else ""
    combined = full_text + " " + summary_lower

    # Confirmation keywords (Telugu + English)
    confirmed_keywords = [
        "అవును", "చేస్తాను", "ok", "sure", "yes", "confirm", "available",
        "can do", "will do", "ready"
    ]

    # Decline keywords
    declined_keywords = [
        "కాదు", "చేయను", "no", "cannot", "can't", "busy", "not available",
        "decline", "refuse"
    ]

    # Uncertain keywords
    uncertain_keywords = [
        "తర్వాత", "later", "think", "maybe", "not sure", "consider"
    ]

    # Count matches
    confirmed_score = sum(1 for kw in confirmed_keywords if kw in combined)
    declined_score = sum(1 for kw in declined_keywords if kw in combined)
    uncertain_score = sum(1 for kw in uncertain_keywords if kw in combined)

    # Determine status
    if confirmed_score > declined_score and confirmed_score > uncertain_score:
        return "confirmed"
    elif declined_score > 0:
        return "declined"
    elif uncertain_score > 0:
        return "uncertain"
    else:
        return "no_response"
