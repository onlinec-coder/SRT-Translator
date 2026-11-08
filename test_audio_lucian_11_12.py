import os
import json
from pathlib import Path
from google import genai
from google.genai import types

project = Path(r"C:\Users\chinzorig\SRT-Translator")
audio_path = Path(r"C:\Users\chinzorig\Desktop\Husbands_test_01.wav")

# Load API key without displaying it
env_path = project / ".env"
for line in env_path.read_text(encoding="utf-8").splitlines():
    if line.strip().startswith("GEMINI_API_KEY="):
        os.environ["GEMINI_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")
        break

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in project .env")

if not audio_path.exists():
    raise FileNotFoundError(audio_path)

audio_bytes = audio_path.read_bytes()
client = genai.Client(api_key=api_key)

prompt = """
Analyze the attached 11.5-second movie audio clip.

This is a BLIND ACOUSTIC ANALYSIS.
Do not infer emotions, intentions, personality, or psychological states.
Do not use subtitle meaning to interpret the voice.
Do not guess what the speaker feels.

Analyze ONLY the audible vocal characteristics in these exact intervals.
Times are relative to the beginning of the attached audio:

Cue 11: 8.374–9.749 seconds. Speaker identity: Lucian.
Cue 12: 9.800–10.541 seconds. Speaker identity: Lucian.

The speaker identities are fixed. Do not reconsider or change them.

For each cue, describe:
- loudness: quiet / low / medium / loud
- pitch: relative pitch level and whether it rises, falls, or stays steady
- voice_quality: clear, breathy, hoarse, strained, rough, nasal, resonant, etc.
- rate_and_rhythm: slow / moderate / fast; steady or uneven
- vocal_stability: stable or noticeably wavering
- breathing_and_pauses: only breaths or pauses that are clearly audible
- clearly_audible_features: objective acoustic observations
- uncertain_features: anything that cannot be confidently determined

Then compare cue 11 and cue 12:
- Are they similar or different in loudness?
- Are they similar or different in pitch?
- Are they similar or different in voice quality?
- Is either cue clearly slower, breathier, rougher, or more strained?

Important:
Do not label either cue as sad, angry, happy, cold, confident, hesitant, or any other emotion.
Do not claim breathing, vocal fry, or strain unless clearly audible.
Do not invent details to fill fields.
If something is unclear, explicitly say "unclear".

Return valid JSON only, using this structure:

{
  "cue_11": {
    "loudness": "",
    "pitch": "",
    "voice_quality": "",
    "rate_and_rhythm": "",
    "vocal_stability": "",
    "breathing_and_pauses": "",
    "clearly_audible_features": [],
    "uncertain_features": []
  },
  "cue_12": {
    "loudness": "",
    "pitch": "",
    "voice_quality": "",
    "rate_and_rhythm": "",
    "vocal_stability": "",
    "breathing_and_pauses": "",
    "clearly_audible_features": [],
    "uncertain_features": []
  },
  "comparison": {
    "loudness": "",
    "pitch": "",
    "voice_quality": "",
    "rate_and_rhythm": "",
    "reliable_differences": [],
    "uncertain_differences": []
  }
}
"""

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=[
        prompt,
        types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
    ],
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0
    )
)

result = json.loads(response.text)
print(json.dumps(result, ensure_ascii=False, indent=2))
