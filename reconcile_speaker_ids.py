
import json
from pathlib import Path

file_path = Path("speaker_assignments.json")

with file_path.open("r", encoding="utf-8") as f:
    data = json.load(f)

id_map = {
    "C015": "C014",
    "C017": "C014",
}

name_map = {
    "C014": "Chief Elder Laurent",
}

changes = []

for item in data["assignments"]:
    old_id = item.get("speaker_id")

    if old_id in id_map:
        new_id = id_map[old_id]
        old_name = item.get("speaker_name")

        item["speaker_id"] = new_id
        item["speaker_name"] = name_map[new_id]

        changes.append(
            f"Subtitle {item['subtitle_id']}: "
            f"{old_id}/{old_name} -> "
            f"{new_id}/{name_map[new_id]}"
        )

# Review хэсгийг assignments-тай ижил шинэчлэнэ.
for category, items in data.get("review", {}).items():
    if isinstance(items, list):
        for item in items:
            old_id = item.get("speaker_id")

            if old_id in id_map:
                new_id = id_map[old_id]
                item["speaker_id"] = new_id
                item["speaker_name"] = name_map[new_id]

with file_path.open("w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Шинэчилсэн мөр:", len(changes))
for change in changes:
    print(change)

print("JSON хадгалагдлаа.")
