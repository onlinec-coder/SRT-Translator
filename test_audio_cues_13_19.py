import os
import json
from pathlib import Path
from google import genai
from google.genai import types

project = Path(r"C:\Users\chinzorig\SRT-Translator")
audio_path = Path(r"C:\Users\chinzorig\Desktop\Husbands_test_02.wav")

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
Perform a blind acoustic analysis of the attached audio.

The audio starts at movie time 00:00:29.500.
Analyze only the following fixed subtitle cue intervals.
Do not infer speaker identity. Do not use subtitle text to infer emotion.

Cue 13: 00:00.041 - 00:01.300
Cue 14: 00:01.833 - 00:03.291
Cue 15: 00:04.100 - 00:05.000
Cue 16: 00:05.100 - 00:06.458
Cue 17: 00:06.500 - 00:07.874
Cue 18: 00:08.000 - 00:09.666
Cue 19: 00:09.700 - 00:11.500

Do not classify emotions.
Do not use emotional words such as sad, angry, happy, fearful,
defeated, affectionate, or emotionally heavy.
Do not infer psychological states or character motivations.

Describe only observable acoustic properties for each cue:

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
- quiet delivery with vocal strain;
- background music with vocal properties.

If a cue contains no speech or is masked by music, say so.
Do not invent acoustic details.
Analyze each cue only within its specified interval.

Return valid JSON only, using this structure:

{
  "cue_13": {
    "loudness": "...",
    "pitch": "...",
    "voice_quality": "...",
    "rate_and_rhythm": "...",
    "vocal_stability": "...",
    "breathing_and_pauses": "...",
    "clearly_audible_features": [],
    "uncertain_features": []
  },
  "cue_14": {},
  "cue_15": {},
  "cue_16": {},
  "cue_17": {},
  "cue_18": {},
  "cue_19": {},
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

result = json.loads(response.text)
output = project / "Husbands_acoustic_test_02.json"
output.write_text(
    json.dumps(result, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False, indent=2))
print(f"\nҮр дүн хадгалагдлаа: {output}")
