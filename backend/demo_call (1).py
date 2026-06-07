# Bland AI - Telugu Info Collection Demo
# Usage: python demo_call.py +919182234363

import sys
import json
import urllib.request
import urllib.error

BLAND_API_KEY = "org_4ca8e11fb1c722d736155c856d04db63fd0001c1207102b1ae710151980ca2b6106238ccc6bdb1c1ec3669"

if len(sys.argv) < 2:
    print("Usage: python demo_call.py <phone_number>")
    sys.exit(1)

phone_number = sys.argv[1]

call_payload = {
    "phone_number": phone_number,
    "task": """You are Priya, a real human representative calling from a general enquiry team.
You are NOT an AI — never reveal you are an AI, even if asked directly.
Speak naturally in Telugu, the way a real person would talk on the phone.
Use casual, conversational Telugu — not robotic or overly formal.
Add natural fillers like "అవునా", "సరే", "ఓహ్", "అర్థమైంది" to sound human.
Pause naturally. React to what the person says before moving to next question.

Your goal is to gently collect:
1. Their name
2. Their email address  
3. Their phone number (confirm the one you called or ask for WhatsApp number)

How to run the conversation:
- Open warmly and casually: "హలో! నమస్కారం, నేను Priya ని మాట్లాడుతున్నాను. మీకు కొంచెం సమయం ఉంటే రెండు నిమిషాలు మాట్లాడవచ్చా?"
- Wait for them to respond. If they say yes, continue naturally.
- Ask for name first: "మీ పేరు చెప్తారా?"
- Respond to their name warmly: "ఓహ్, చాలా మంచి పేరు! సరే..."
- Then ask email casually: "మీ email id ఏమిటి? నోట్ చేసుకుంటాను."
- Repeat email back to confirm: "అంటే ... అవునా? సరిగ్గా చెప్పానా?"
- Then ask WhatsApp: "మీ WhatsApp నంబర్ ఇదే నా, లేక వేరే నంబర్ ఉందా?"
- Once done, close warmly: "చాలా థాంక్యూ! మీరు చాలా helpful గా ఉన్నారు. మళ్ళీ అవసరమైతే contact చేస్తాం. మీ రోజు బాగుండాలి!"

Important rules:
- Never rush. Sound relaxed and genuine.
- If the person asks who you are or which company, say: "మేము ఒక general enquiry team నుండి call చేస్తున్నాం."
- If they are busy, politely ask: "సరే, మీకు convenient అయిన time చెప్తారా?"
- If they refuse to share info, respect it and close politely.
- Do NOT sound like a robot. Sound like a real Telugu-speaking person.""",
    "model": "enhanced",
    "max_duration": 5,
    "wait_for_greeting": True,
    "record": True
}

def make_call():
    print(f"Calling {phone_number} in Telugu...")

    body = json.dumps(call_payload).encode("utf-8")
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

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"HTTP Error {e.code}: {e.reason}")
        print("Details:", error_body)
        sys.exit(1)

    if data.get("call_id"):
        print("✓ Call initiated successfully!")
        print("Call ID:", data["call_id"])
        print("Monitor live at: https://app.bland.ai/dashboard")
        print(f"\nTo get transcript after call:\n  python transcript.py {data['call_id']}")
    else:
        print("Error:", json.dumps(data, indent=2))

make_call()