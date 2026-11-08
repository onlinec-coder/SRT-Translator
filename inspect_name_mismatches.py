
import json

files = [
    "speaker_assignments.json",
    "assignments_check.json",
    "medium_review_export.json",
    "review_export.json",
]

with open("Husbands_characters_reconciled.json", encoding="utf-8") as f:
    registry = json.load(f)

canonical = {
    c.get("id") or c.get("character_id") or c.get("speaker_id"):
    c.get("canonical_name") or c.get("name")
    for c in registry["characters"]
}

def scan(obj, filename):
    if isinstance(obj, dict):
        sid = obj.get("speaker_id")
        name = obj.get("speaker_name")

        if sid in canonical and name and name != canonical[sid]:
            print(
                f"{filename} | "
                f"Subtitle: {obj.get('subtitle_id', obj.get('id', '?'))} | "
                f"{sid} | {name} -> {canonical[sid]}"
            )

        for value in obj.values():
            scan(value, filename)

    elif isinstance(obj, list):
        for item in obj:
            scan(item, filename)

for filename in files:
    with open(filename, encoding="utf-8") as f:
        data = json.load(f)

    scan(data, filename)
