import json
from pathlib import Path

with open(
    "input.srt",
    "r",
    encoding="utf-8-sig"
) as file:
    subtitles = file.read()

with open(
    "Husbands_characters_merged.json",
    "r",
    encoding="utf-8"
) as file:
    characters = json.load(file)

result = {
    "source_file": "input.srt",
    "subtitle_text": subtitles,
    "characters": characters["characters"]
}

Path("Husbands_reconciliation_input.json").write_text(
    json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ),
    encoding="utf-8"
)

print("Бэлтгэсэн дүр:", len(characters["characters"]))
print("Хадмалын тэмдэгт:", len(subtitles))
print("Файл: Husbands_reconciliation_input.json")