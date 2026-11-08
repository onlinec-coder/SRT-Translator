
import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = "t9cfscnpanqv8SAN8rHS"

if not api_key:
    print("ERROR: API key not found in .env")
    raise SystemExit(1)

url = f"https://api.elevenlabs.io/v1/voices/{voice_id}"

request = urllib.request.Request(
    url,
    headers={"xi-api-key": api_key},
    method="GET"
)

try:
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
        print("API CONNECTION: SUCCESS")
        print("Voice access: SUCCESS")
        print("Voice name:", data.get("name", "Unknown"))

except urllib.error.HTTPError as error:
    print("API ERROR:", error.code)
    print("Check API key permissions and voice access.")

except Exception as error:
    print("CONNECTION ERROR:", type(error).__name__)
