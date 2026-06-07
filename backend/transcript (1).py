# Fetch transcript + collected info after the call
# Usage: python transcript.py <call_id>

import sys
import json
import urllib.request
import urllib.error

BLAND_API_KEY = "org_4ca8e11fb1c722d736155c856d04db63fd0001c1207102b1ae710151980ca2b6106238ccc6bdb1c1ec3669"

if len(sys.argv) < 2:
    print("Usage: python transcript.py <call_id>")
    sys.exit(1)

call_id = sys.argv[1]

def get_transcript():
    req = urllib.request.Request(
        f"https://api.bland.ai/v1/calls/{call_id}",
        headers={
            "Authorization": BLAND_API_KEY,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    )

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"HTTP Error {e.code}: {e.reason}")
        print("Details:", error_body)
        sys.exit(1)

    print("\n=== CALL SUMMARY ===")
    print("Status:", data.get("status"))
    print("Duration:", data.get("call_length"), "minutes")
    print("Recording:", data.get("recording_url") or "Not available yet")

    print("\n=== TRANSCRIPT ===")
    transcripts = data.get("transcripts")
    if transcripts:
        for t in transcripts:
            print(f"[{t['user']}]: {t['text']}")
    else:
        print("No transcript available yet.")

    print("\n=== COLLECTED INFO (from conversation) ===")
    if data.get("summary"):
        print("Summary:", data["summary"])
    else:
        print("No summary available yet.")

get_transcript()