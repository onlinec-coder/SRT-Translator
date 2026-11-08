import json
from pathlib import Path

analysis_path = Path("speaker_analysis_input.json")
reconciled_path = Path("Husbands_characters_reconciled.json")

# Хоёр файлыг унших
with analysis_path.open("r", encoding="utf-8") as f:
    analysis = json.load(f)

with reconciled_path.open("r", encoding="utf-8") as f:
    reconciled = json.load(f)

# Шинэчилсэн дүрүүдийг авах
new_characters = []

for character in reconciled["characters"]:
    new_characters.append({
        "id": character["id"],
        "name": character["canonical_name"],
        "aliases": character.get("aliases", []),
        "gender": character.get("gender"),
        "relationships": character.get("relationships", []),
        "speech_style": character.get("speech_style", [])
    })

# Зөвхөн characters хэсгийг шинэчлэх
analysis["characters"] = new_characters

# Бусад хэсгийг хэвээр хадгалж файлд бичих
with analysis_path.open("w", encoding="utf-8") as f:
    json.dump(analysis, f, ensure_ascii=False, indent=2)

print("Шинэчилсэн дүрийн тоо:", len(new_characters))
print("Batch-ийн тоо:", len(analysis["batches"]))
print("C021 байгаа эсэх:", any(x["id"] == "C021" for x in new_characters))
print("C022 байгаа эсэх:", any(x["id"] == "C022" for x in new_characters))
print("JSON хадгалагдлаа.")