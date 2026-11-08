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

# Зөвхөн Vivienne-ийн cue-үүд
CUE_ROLES = {
    559: "narrator",
    560: "narrator",
    561: "narrator",
    562: "narrator",
    563: "character",
    565: "narrator",
    568: "character",
    569: "character",
    570: "character",
}

if not API_KEY:
    raise SystemExit("ERROR: ELEVENLABS_API_KEY not found in .env")

srt_path = Path("Husbands_mn_v3.srt")
if not srt_path.exists():
    raise SystemExit("ERROR: Husbands_mn_v3.srt not found")

srt_text = srt_path.read_text(encoding="utf-8-sig")
blocks = re.split(r"\r?\n\s*\r?\n", srt_text.strip())

cue_data = {}

for block in blocks:
    lines = block.strip().splitlines()
    if len(lines) < 3 or not lines[0].strip().isdigit():
        continue

    number = int(lines[0].strip())
    if number not in CUE_ROLES:
        continue

    match = re.match(
        r"(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+"
        r"(\d{2}:\d{2}:\d{2},\d{3})",
        lines[1].strip()
    )
    if not match:
        continue

    cue_data[number] = {
        "start": match.group(1),
        "end": match.group(2),
        "text": " ".join(x.strip() for x in lines[2:]).strip()
    }

missing = set(CUE_ROLES) - set(cue_data)
if missing:
    raise SystemExit(f"STOP: Missing cues: {sorted(missing)}")

output_dir = Path("output") / "Vivienne_cues_559_570"
output_dir.mkdir(parents=True, exist_ok=True)

url = (
    f"https://api.elevenlabs.io/v1/text-to-speech/"
    f"{VOICE_ID}?output_format=mp3_44100_128"
)

print("Generating Vivienne cues 559-570")
print("Voice:", VOICE_ID)
print()

success = 0

for number, role in CUE_ROLES.items():
    cue = cue_data[number]

    if role == "narrator":
        text = "[reflective] " + cue["text"]
    else:
        text = cue["text"]

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

    print(f"Cue {number} [{role}] {cue['start']} - {cue['end']}")
    print("Text:", cue["text"])

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            audio = response.read()

        if not audio:
            print("ERROR: Empty audio response")
            continue

        output_file = output_dir / f"Vivienne_{number}.mp3"
        output_file.write_bytes(audio)

        print("SUCCESS:", output_file.name, len(audio), "bytes\n")
        success += 1

    except urllib.error.HTTPError as error:
        print("API ERROR:", error.code)
        print(error.read().decode("utf-8", errors="replace"))
        break
    except Exception as error:
        print("ERROR:", type(error).__name__, str(error))
        break

print(f"\nCompleted: {success}/{len(CUE_ROLES)}")
print("Output:", output_dir.resolve())
