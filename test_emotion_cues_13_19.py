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
Analyze the emotional expression and vocal delivery in the attached audio.

The audio starts at movie time 00:00:29.500.
Analyze only these fixed cue intervals:

Cue 13: 00:00.041 - 00:01.300
Cue 14: 00:01.833 - 00:03.291
Cue 15: 00:04.100 - 00:05.000
Cue 16: 00:05.100 - 00:06.458
Cue 17: 00:06.500 - 00:07.874
Cue 18: 00:08.000 - 00:09.666
Cue 19: 00:09.700 - 00:11.500

IMPORTANT RULES:

1. Judge only what is audibly expressed by the voice.
2. Do not infer emotion from words, sentence meaning, plot, or presumed character situation.
3. Do not assume that loudness means anger or that fast speech means excitement.
4. Do not assume that low pitch means sadness.
5. Separate emotion from vocal tone and delivery.
6. If emotion is not clearly audible, use "unclear" rather than guessing.
7. Neutral is valid when no distinct emotional expression is audible.
8. Do not force every cue to have a different emotion.
9. Confidence must reflect the strength of audible evidence. Do not automatically use high confidence.
10. If music or another sound masks the voice, state that limitation.

Use these emotion labels only:
neutral, sadness, anger, happiness, fear, disgust, surprise, unclear.

For each cue return:

- emotion: one allowed label
- vocal_tone: observable voice quality
- delivery: how the line is spoken
- intensity: low, medium, high, or unclear
- pace: slow, moderate, fast, or unclear
- audible_evidence: specific audible evidence, not interpretation of words
- confidence: high, medium, or low

Do not use visual information.

Return valid JSON only:

{
  "cue_13": {
    "emotion": "unclear",
    "vocal_tone": "...",
    "delivery": "...",
    "intensity": "unclear",
    "pace": "unclear",
    "audible_evidence": [],
    "confidence": "low"
  },
  "cue_14": {},
  "cue_15": {},
  "cue_16": {},
  "cue_17": {},
  "cue_18": {},
  "cue_19": {},
  "comparison": {
    "consistent_features": [],
    "meaningful_changes": [],
    "limitations": []
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

output = project / "Husbands_emotion_test_02.json"
output.write_text(
    json.dumps(result, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False, indent=2))
print(f"\nҮр дүн хадгалагдлаа: {output}")
