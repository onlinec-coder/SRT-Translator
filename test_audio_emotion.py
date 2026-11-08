import os
import json
from pathlib import Path
from google import genai
from google.genai import types

project = Path(r"C:\Users\chinzorig\SRT-Translator")
audio_path = Path(r"C:\Users\chinzorig\Desktop\Husbands_test_01.wav")

for line in (project / ".env").read_text(encoding="utf-8-sig").splitlines():
    line = line.strip()
    if line.startswith("GEMINI_API_KEY="):
        value = line.split("=", 1)[1].strip().strip('"').strip("'")
        if value:
            os.environ["GEMINI_API_KEY"] = value
        break

if not os.environ.get("GEMINI_API_KEY"):
    raise RuntimeError("GEMINI_API_KEY олдсонгүй.")

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

prompt = """
Perform a blind acoustic analysis of the attached audio.

The audio starts at movie time 00:00:18.000.
Speaker identities and timestamps are fixed.

Cue 9:  00:04.000 - 00:05.125 | Vivienne
Cue 10: 00:05.583 - 00:06.600 | Vivienne

Analyze only these two cues. Do not infer speaker identity.

IMPORTANT:
Do not classify emotions.
Do not use emotional words such as sad, angry, happy, fearful,
defeated, affectionate, or emotionally heavy.
Do not infer psychological states or character motivations.

Describe only observable acoustic properties:

1. Relative loudness.
2. Pitch level and whether pitch rises or falls.
3. Voice quality: clear, breathy, raspy, hoarse, creaky,
   strained, pressed, or other.
4. Speaking rate and rhythm.
5. Stability of the voice.
6. Audible inhalation, exhalation, vocal fry, or pauses.
7. Whether these properties are clearly audible or uncertain.

Do not confuse:
- low loudness with breathiness;
- slow speech with hesitation;
- vocal fry with an audible breath;
- quiet delivery with vocal strain.

Return valid JSON only:

{
  "cue_9": {
    "loudness": "...",
    "pitch": "...",
    "voice_quality": "...",
    "rate_and_rhythm": "...",
    "vocal_stability": "...",
    "breathing_and_pauses": "...",
    "clearly_audible_features": [],
    "uncertain_features": []
  },
  "cue_10": {
    "loudness": "...",
    "pitch": "...",
    "voice_quality": "...",
    "rate_and_rhythm": "...",
    "vocal_stability": "...",
    "breathing_and_pauses": "...",
    "clearly_audible_features": [],
    "uncertain_features": []
  },
  "comparison": {
    "similarities": [],
    "differences": []
  }
}
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

print(json.dumps(json.loads(response.text), ensure_ascii=False, indent=2))
