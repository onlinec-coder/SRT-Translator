import json
import shutil
from pathlib import Path

files = [
    "assignments_check.json",
    "medium_review_export.json",
    "review_export.json"
]

id_map = {
    "C006": ("C003", "Aria"),
    "C015": ("C014", "Chief Elder Laurent"),
    "C017": ("C014", "Chief Elder Laurent")
}

# Эхлээд бүх файлыг шалгаж уншина
data_by_file = {}

for filename in files:
    path = Path(filename)

    if not path.exists():
        raise FileNotFoundError(f"Файл олдсонгүй: {filename}")

    with path.open("r", encoding="utf-8") as f:
        data_by_file[filename] = json.load(f)

# Нөөц файлууд давхардаж байгаа эсэхийг шалгана
for filename in files:
    backup = Path(filename.replace(".json", "_before_id_update.json"))

    if backup.exists():
        raise FileExistsError(f"Нөөц файл аль хэдийн байна: {backup}")

# Нөөц хуулбар үүсгэнэ
for filename in files:
    backup = filename.replace(".json", "_before_id_update.json")
    shutil.copy2(filename, backup)
    print("Нөөц:", backup)

# Бүх түвшний бүртгэлийг шинэчилнэ
def update_ids(obj, changes):
    if isinstance(obj, dict):
        old_id = obj.get("speaker_id")

        if old_id in id_map:
            new_id, new_name = id_map[old_id]

            obj["speaker_id"] = new_id
            obj["speaker_name"] = new_name

            changes[old_id] = changes.get(old_id, 0) + 1

        for value in obj.values():
            update_ids(value, changes)

    elif isinstance(obj, list):
        for item in obj:
            update_ids(item, changes)


# Файлуудыг шинэчилж хадгална
for filename, data in data_by_file.items():
    changes = {}
    update_ids(data, changes)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\nФайл:", filename)
    print("Шинэчлэл:", changes)
    print("Нийт:", sum(changes.values()))

print("\nБүх review файл шинэчлэгдлээ.")