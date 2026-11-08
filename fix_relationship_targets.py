
import json
from pathlib import Path

file_path = Path("Husbands_characters_reconciled.json")

with file_path.open("r", encoding="utf-8") as f:
    data = json.load(f)

name_map = {
    "Vivian": "Vivienne",
    "Viviana": "Vivienne",
    "Vivien": "Vivienne",
    "Vivienna": "Vivienne",
    "Arya": "Aria",
    "Alpha Various": "Alpha Valeris",
    "Alpha Valerce": "Alpha Valeris",
    "Alpha Valerius": "Alpha Valeris",
    "Luna Various": "Luna Valerius",
    "Luna Valerce": "Luna Valerius",
}

changes = []

for character in data["characters"]:
    for relationship in character.get("relationships", []):
        old_target = relationship.get("target")

        if old_target in name_map:
            new_target = name_map[old_target]
            relationship["target"] = new_target
            changes.append(
                f"{character['canonical_name']}: "
                f"{old_target} -> {new_target}"
            )

with file_path.open("w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Шинэчилсэн холбоос: {len(changes)}")
for change in changes:
    print(change)

print("Файл хадгалагдлаа:", file_path.name)
