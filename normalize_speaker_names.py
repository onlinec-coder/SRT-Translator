
import json
import shutil
from pathlib import Path

files = [
    "speaker_assignments.json",
    "review_export.json"
]

name_map = {
    ("C012", "Alpha Various"): "Alpha Valeris",
    ("C013", "Luna Various"): "Luna Valerius"
}

# Эхлээд бүх файл байгаа эсэх, нөөц файл давхардсан эсэхийг шалгана
for filename in files:
    path = Path(filename)
    if not path.exists():
        raise FileNotFoundError(f"Файл олдсонгүй: {filename}")

    backup = path.with_name(path.stem + "_before_name_update.json")
    if backup.exists():
        raise FileExistsError(f"Нөөц файл аль хэдийн байна: {backup}")

# JSON файлуудыг уншина
data_by_file = {}

for filename in files:
    with open(filename, "r", encoding="utf-8") as f:
        data_by_file[filename] = json.load(f)

def update_names(obj, changes):
    if isinstance(obj, dict):
        sid = obj.get("speaker_id")
        old_name = obj.get("speaker_name")

        key = (sid, old_name)

        if key in name_map:
            obj["speaker_name"] = name_map[key]
            changes[key] = changes.get(key, 0) + 1

        for value in obj.values():
            update_names(value, changes)

    elif isinstance(obj, list):
        for item in obj:
            update_names(item, changes)

# Нөөц үүсгээд шинэчилнэ
for filename, data in data_by_file.items():
    path = Path(filename)
    backup = path.with_name(path.stem + "_before_name_update.json")

    shutil.copy2(path, backup)

    changes = {}
    update_names(data, changes)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nФайл: {filename}")
    print("Нөөц:", backup.name)
    print("Шинэчлэлт:", changes)
    print("Нийт:", sum(changes.values()))

print("\nНэршлийн шинэчлэлт дууслаа.")
