
import json
from pathlib import Path
from collections import Counter

# Шаардлагатай файлууд
FILES = [
    "Husbands_characters_reconciled.json",
    "speaker_analysis_input.json",
    "speaker_assignments.json",
    "assignments_check.json",
    "medium_review_export.json",
    "review_export.json",
]

# 1. Файлууд байгаа эсэх
for filename in FILES:
    if not Path(filename).exists():
        raise FileNotFoundError(f"Файл олдсонгүй: {filename}")

def load_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

data = {filename: load_json(filename) for filename in FILES}

# 2. Үндсэн дүрийн бүртгэл
registry = data["Husbands_characters_reconciled.json"]
characters = registry["characters"]

def get_character_id(c):
    return c.get("id") or c.get("character_id") or c.get("speaker_id")

def get_character_name(c):
    return c.get("canonical_name") or c.get("name")

canonical = {}
for c in characters:
    cid = get_character_id(c)
    name = get_character_name(c)
    if cid:
        canonical[cid] = name

registry_ids = set(canonical)
registry_duplicates = [
    cid for cid, count in Counter(
        get_character_id(c) for c in characters
    ).items()
    if cid and count > 1
]

print("\n=== 1. ҮНДСЭН ДҮРИЙН БҮРТГЭЛ ===")
print("Дүрийн тоо:", len(characters))
print("ID-ийн тоо:", len(registry_ids))
print("Давхардсан ID:", registry_duplicates)
print("ID / нэр:", canonical)

# 3. Analysis characters
analysis = data["speaker_analysis_input.json"]
analysis_characters = analysis["characters"]
analysis_ids = {
    get_character_id(c) for c in analysis_characters
    if get_character_id(c)
}

print("\n=== 2. ANALYSIS БҮРТГЭЛ ===")
print("Дүрийн тоо:", len(analysis_characters))
print("Batch-ийн тоо:", len(analysis.get("batches", [])))
print("Үндсэн бүртгэлд байхгүй ID:", sorted(analysis_ids - registry_ids))
print("Analysis-д байхгүй ID:", sorted(registry_ids - analysis_ids))

# 4. Бүх объект дотроос speaker_id бүртгэл цуглуулах
def collect_speakers(obj, result):
    if isinstance(obj, dict):
        if "speaker_id" in obj:
            result.append(obj)

        for value in obj.values():
            collect_speakers(value, result)

    elif isinstance(obj, list):
        for item in obj:
            collect_speakers(item, result)

def check_file(filename, obj):
    records = []
    collect_speakers(obj, records)

    ids = Counter()
    unknown = []
    name_errors = []

    for record in records:
        sid = record.get("speaker_id")
        name = record.get("speaker_name")

        if sid:
            ids[sid] += 1

            if sid not in registry_ids:
                unknown.append((sid, name))

            elif name and name != canonical[sid]:
                name_errors.append(
                    (sid, name, canonical[sid])
                )

    print(f"\n=== {filename} ===")
    print("Speaker бүртгэл:", len(records))
    print("ID-ийн тоо:", len(ids))
    print("Бүртгэлгүй ID:", unknown)
    print("Нэрийн зөрүү:", name_errors)

    return len(records), unknown, name_errors

# 5. Файл тус бүрийн шалгалт
results = {}

for filename in FILES[2:]:
    results[filename] = check_file(filename, data[filename])

# 6. Үндсэн оноолтын тоо
main = data["speaker_assignments.json"]
assignment_count = len(main.get("assignments", []))

print("\n=== 3. ҮНДСЭН ОНООЛТ ===")
print("Нийт оноолт:", assignment_count)
print("Review бүртгэл:", len(main.get("review", [])))

# 7. Эцсийн дүгнэлт
all_unknown = sum(len(r[1]) for r in results.values())
all_name_errors = sum(len(r[2]) for r in results.values())

print("\n=== ЭЦСИЙН ДҮГНЭЛТ ===")
print("Давхардсан дүрийн ID:", len(registry_duplicates))
print("Бүртгэлгүй speaker ID:", all_unknown)
print("Нэрийн зөрүү:", all_name_errors)

if (
    not registry_duplicates
    and not (analysis_ids - registry_ids)
    and not (registry_ids - analysis_ids)
    and all_unknown == 0
    and all_name_errors == 0
    and assignment_count == 908
):
    print("\nБҮХ ШАЛГАЛТ АМЖИЛТТАЙ.")
else:
    print("\nАНХААР: Дээрх зөрүүтэй мөрүүдийг шалгах шаардлагатай.")
