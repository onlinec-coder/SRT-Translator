import os
import json
from pathlib import Path
from google import genai
from google.genai import types

project = Path(r"C:\Users\chinzorig\SRT-Translator")
audio_path = Path(r"C:\Users\chinzorig\Desktop\Husbands_test_04.wav")

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
Analyze the emotional expression and vocal delivery in the attached audio.

The audio starts at movie time 00:00:52.500.
Analyze only these exact intervals:

Cue 25: 00:00.291 - 00:01.666
Cue 26: 00:02.291 - 00:04.500
Cue 27: 00:07.100 - 00:08.041
Cue 28: 00:09.500 - 00:11.000
Cue 29: 00:11.000 - 00:12.874

IMPORTANT:
- Judge emotion ONLY from audible vocal expression.
- Do not infer emotion from the meaning of the spoken words.
- Do not use subtitles, plot, character identity, or visual information.
- Do not assume that narration is automatically sad.
- Neutral is a valid result.
- If emotion is not clearly distinguishable, use "unclear".
- Do not force an emotion for every cue.
- Distinguish emotion from delivery and vocal tone.
- Do not treat breathiness, low volume, or a falling pitch alone as proof of sadness.
- Do not treat loudness alone as proof of anger.
- Evaluate each cue independently, while considering the surrounding voice for continuity.

For each cue return:
- emotion: neutral, sadness, anger, fear, joy, disgust, surprise, or unclear
- emotion_evidence: audible vocal evidence only
- vocal_tone: short description of the audible tone
- delivery: normal, soft, whispered, shouted, strained, hesitant, breathy, deliberate, or other observable delivery
- intensity: low, medium, or high
- pace: slow, moderate, or fast
- confidence: low, medium, or high

Use "high" confidence only when the vocal evidence is unmistakable.
Do not invent breaths, pauses, crying, or other vocal events.

Return valid JSON only, with keys cue_25 through cue_29 and a comparison object.
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

output = project / "Husbands_emotion_test_04.json"
output.write_text(
    json.dumps(result, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False, indent=2))
print(f"\nҮр дүн хадгалагдлаа: {output}")
