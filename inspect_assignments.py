import json
import srt

from pathlib import Path
from translator import (
    load_subtitles,
    load_speaker_context
)

input_file = "input.srt"

subtitles = load_subtitles(input_file)
speaker_map = load_speaker_context(input_file)

batch = subtitles[:20]

target_text = []

for sub in batch:

    speaker = speaker_map.get(sub.index, {})

    target_text.append({
        "index": sub.index,
        "text": sub.content,
        "speaker": {
            "id": speaker.get("speaker_id"),
            "name": speaker.get("canonical_name"),
            "type": speaker.get("speaker_type"),
            "confidence": speaker.get("confidence"),
            "gender": speaker.get("gender"),
            "speech_style": speaker.get("speech_style", [])
        }
    })

output_file = Path("translation_test_input.json")

output_file.write_text(
    json.dumps(
        {"translations_input": target_text},
        ensure_ascii=False,
        indent=2
    ),
    encoding="utf-8"
)

print("Туршилтын мөр:", len(target_text))
print("Файл:", output_file)
print("\nЭхний 3 мөр:")

for item in target_text[:3]:
    print(json.dumps(item, ensure_ascii=False, indent=2))