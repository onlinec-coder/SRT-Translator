
import json
from pathlib import Path

source = Path("speaker_assignments.json")
output = Path("medium_review_export.json")

data = json.loads(source.read_text(encoding="utf-8-sig"))
medium = data["review"]["medium"]

result = {
    "count": len(medium),
    "assignments": medium
}

output.write_text(
    json.dumps(result, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("Medium бичлэг:", len(medium))
print("Экспортолсон файл:", output)
