import os
import json
from pathlib import Path
from google import genai
from google.genai import types

project = Path(r"C:\Users\chinzorig\SRT-Translator")
audio_path = Path(r"C:\Users\chinzorig\Desktop\Husbands_test_03.wav")

for line in (project / ".env").read_text(encoding="utf-8-sig").splitlines():
    line = line.strip()
    if line.startswith("GEMINI_API_KEY="):
        value = line.split("=", 1)[1].strip().strip('"').strip("'")
        if value:
            os.environ["GEMINI_API_KEY"] = value
        break

if not os.environ.get("GEMINI_API_KEY"):
    raise RuntimeError("GEMINI_API_KEY олдсонгүй.")

if not audio_path.exists():
    raise FileNotFoundError(audio_path)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

prompt = """
Analyze the acoustic properties of the voice in the attached audio.

The audio starts at movie time 00:00:41.000.
Analyze only these exact intervals:

Cue 20: 00:01.000 - 00:02.749
Cue 21: 00:04.600 - 00:06.166
Cue 22: 00:06.800 - 00:07.400
Cue 23: 00:07.600 - 00:08.800
Cue 24: 00:09.600 - 00:10.400

Do NOT infer emotion or meaning from the words.
Do NOT use subtitles, character identities, plot, or visual information.

For each cue, report only audible acoustic properties:

- loudness: low, moderate, moderate-high, or high
- pitch: approximate range and contour
- voice_quality: clear, breathy, raspy, strained, pressed, dry, or other observable quality
- rate_and_rhythm: slow, moderate, fast, measured, uneven, etc.
- vocal_stability: stable or unstable, with evidence
- breathing_and_pauses: only sounds clearly audible inside the cue
- clearly_audible_features: specific observable features
- uncertain_features: anything that cannot be determined reliably

Do not describe a pause or breath outside the specified cue interval.
Do not invent breaths, vocal fry, or emotional qualities.
If a cue is too short to assess, say so.

Return valid JSON only, using cue_20 through cue_24 and a comparison object.
"""

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=[
        prompt,
        types.Part.from_bytes(
            data=audio_path.read_bytes(),
            mime_type="audio/wav"
        )
    ],
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0
    )
)

result = json.loads(response.text)

output = project / "Husbands_acoustic_test_03.json"
output.write_text(
    json.dumps(result, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False, indent=2))
print(f"\nҮр дүн хадгалагдлаа: {output}")
