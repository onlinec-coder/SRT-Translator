
import os
import re
import json
import urllib.request
import urllib.error
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = "6Km4T9TrZXIhfMaxglHw"
MODEL_ID = "eleven_v3"

SRT_URL = (
    "https://raw.githubusercontent.com/onlinec-coder/"
    "speaker-engine-review/refs/heads/main/Husbands_mn_v3.srt"
)

TARGET_CUES = range(550, 559)

if not API_KEY:
    raise SystemExit("ERROR: API key not found in .env")

print("Downloading SRT from GitHub...")

request = urllib.request.Request(
    SRT_URL,
    headers={"User-Agent": "Mozilla/5.0"}
)

with urllib.request.urlopen(request, timeout=30) as response:
    srt_text = response.read().decode("utf-8-sig")

blocks = re.split(r"\r?\n\s*\r?\n", srt_text.strip())
cue_data = {}

for block in blocks:
    lines = block.strip().splitlines()

    if len(lines) < 3 or not lines[0].strip().isdigit():
        continue

    cue_number = int(lines[0].strip())

    if cue_number not in TARGET_CUES:
        continue

    timing = lines[1].strip()
    match = re.match(
        r"(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+"
        r"(\d{2}:\d{2}:\d{2},\d{3})",
        timing
    )

    if not match:
        continue

    text = " ".join(line.strip() for line in lines[2:]).strip()

    cue_data[cue_number] = {
        "start": match.group(1),
        "end": match.group(2),
        "text": text
    }

missing = set(TARGET_CUES) - set(cue_data)

if missing:
    raise SystemExit(f"STOP: Missing cues: {sorted(missing)}")

output_dir = Path("output") / "Vivienne_cues_550_558"
output_dir.mkdir(parents=True, exist_ok=True)

url = (
    f"https://api.elevenlabs.io/v1/text-to-speech/"
    f"{VOICE_ID}?output_format=mp3_44100_128"
)

print("\nGenerating 9 separate audio files...\n")

for cue_number in TARGET_CUES:
    cue = cue_data[cue_number]

    # Keep the approved reflective narration style.
    text = "[reflective] " + cue["text"]

    payload = {
        "text": text,
        "model_id": MODEL_ID
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        },
        method="POST"
    )

    print(f"Cue {cue_number}: {cue['start']} - {cue['end']}")
    print("Text:", cue["text"])

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            audio = response.read()

        if not audio:
            print("ERROR: Empty audio response. Skipping.")
            continue

        output_file = output_dir / f"Vivienne_{cue_number}.mp3"
        output_file.write_bytes(audio)

        print("SUCCESS:", output_file.name, "-", len(audio), "bytes\n")

    except urllib.error.HTTPError as error:
        print("API ERROR:", error.code)
        print(error.read().decode("utf-8", errors="replace"))
        break

    except Exception as error:
        print("ERROR:", type(error).__name__, str(error))
        break

print("\nFinished.")
print("Output folder:", output_dir.resolve())
