"""
Test Bland AI API key validity
"""
import urllib.request
import json

# Replace with your API key from https://app.bland.ai
API_KEY = "YOUR_API_KEY_HERE"

# Test with a simple call
payload = {
    "phone_number": "+15555555555",
    "task": "Hello, this is a test call.",
    "model": "enhanced",
    "max_duration": 3,
    "wait_for_greeting": True,
    "record": True
}

req = urllib.request.Request(
    "https://api.bland.ai/v1/calls",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "Authorization": API_KEY,
        "User-Agent": "Mozilla/5.0"
    }
)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        print("SUCCESS - API key is valid!")
        print(f"Call ID: {data.get('call_id')}")
except urllib.error.HTTPError as e:
    error = e.read().decode("utf-8")
    print(f"FAILED - HTTP {e.code}")
    print(f"Error: {error}")
    if e.code == 403:
        print("\nACTION REQUIRED:")
        print("1. Go to https://app.bland.ai")
        print("2. Get your API key")
        print("3. Update backend/engine/bland_ai.py line 13")
except Exception as e:
    print(f"ERROR: {e}")
