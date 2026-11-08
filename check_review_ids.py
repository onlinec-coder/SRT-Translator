import json
from pathlib import Path
from collections import Counter

files = [
    "assignments_check.json",
    "medium_review_export.json",
    "review_export.json"
]

old_ids = {"C006", "C007", "C015", "C016", "C017", "C018", "C020"}

for filename in files:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    found = Counter()

    def scan(obj):
        if isinstance(obj, dict):
            sid = obj.get("speaker_id")
            if sid in old_ids:
                found[sid] += 1

            for value in obj.values():
                scan(value)

        elif isinstance(obj, list):
            for item in obj:
                scan(item)

    scan(data)

    print(filename)
    print("Хуучин ID:", dict(found))
    print("JSON:", "OK")
    print()

# Үндсэн файл
d = json.load(open("speaker_assignments.json", encoding="utf-8"))
print("Үндсэн оноолт:", len(d["assignments"]))
print("Үндсэн файл JSON: OK")