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

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

prompt = """
Analyze emotional expression and vocal delivery using ONLY audible voice characteristics.

The audio starts at movie time 00:00:41.000.
Analyze these intervals:

Cue 20: 00:01.000 - 00:02.749
Cue 21: 00:04.600 - 00:06.166
Cue 22: 00:06.800 - 00:07.400
Cue 23: 00:07.600 - 00:08.800
Cue 24: 00:09.600 - 00:10.400

STRICT RULES:
- Do not infer emotion from words or sentence meaning.
- Do not use plot, character identity, subtitles, or visual information.
- Do not equate low volume with sadness.
- Do not equate slow speech with sadness.
- Do not equate controlled speech with neutrality automatically.
- Neutral is valid if no distinct emotion is audible.
- Use unclear if the voice does not provide enough evidence.
- Separate emotion from vocal tone and delivery.
- Confidence must reflect actual audible evidence, not certainty of the model.

Allowed emotion labels:
neutral, sadness, anger, happiness, fear, disgust, surprise, unclear.

For each cue return:
emotion
vocal_tone
delivery
intensity: low, medium, high, unclear
pace: slow, moderate, fast, unclear
audible_evidence: array of specific audible observations
alternative_interpretation: short explanation if ambiguous, otherwise null
confidence: low, medium, high

Do not use visual information.
Return valid JSON only with cue_20 through cue_24 and a comparison object.
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

output = project / "Husbands_emotion_test_03.json"
output.write_text(
    json.dumps(result, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False, indent=2))
print(f"\nҮр дүн хадгалагдлаа: {output}")
