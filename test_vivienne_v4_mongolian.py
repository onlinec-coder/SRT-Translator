@'
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

PROJECT = Path(r"C:\Users\chinzorig\SRT-Translator")
load_dotenv(PROJECT / ".env")

API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not API_KEY:
    raise RuntimeError("ELEVENLABS_API_KEY олдсонгүй")

VOICE_ID = "6Km4T9TrZXIhfMaxglHw"
text = "[reflective] Намайг ярьж дуусахад өрөөнд нам гүм болов. Тэр ширээн дээрх хагас идсэн бялуу руу удаан ширтлээ."

url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128"

response = requests.post(
    url,
    headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
    json={"text": text, "model_id": "eleven_v3"},
    timeout=120
)
response.raise_for_status()

out = PROJECT / "output" / "Vivienne_cues_559_570"
out.mkdir(parents=True, exist_ok=True)

path = out / "Vivienne_test_without_name.mp3"
path.write_bytes(response.content)
print(f"Saved: {path}")
'@ | .\.venv\Scripts\python.exe -

text = "[reflective] Намайг ярьж дуусахад өрөөнд нам гүм болов. Тэр ширээн дээрх хагас идсэн бялуу руу удаан ширтлээ."