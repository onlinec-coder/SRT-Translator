
import json
import shutil
from pathlib import Path
from datetime import datetime
import os

# This script and JSON file must be in the same folder.
folder = Path(__file__).resolve().parent
json_path = folder / "medium_review_export.json"

# subtitle_id: (speaker_id, speaker_name, speaker_type)
decisions = {
    28:  ("C001", "Vivienne", "character"),
    31:  ("C001", "Vivienne", "character"),
    163: ("C002", "Lucian", "inner_monologue"),
    164: ("C002", "Lucian", "inner_monologue"),
    199: ("C002", "Lucian", "character"),
    200: ("C002", "Lucian", "character"),
    349: ("C009", "Lance Laurent", "character"),
    350: ("C009", "Lance Laurent", "character"),
    356: ("C001", "Vivienne", "character"),
    365: ("C001", "Vivienne", "inner_monologue"),
    366: ("C001", "Vivienne", "inner_monologue"),
    377: ("C008", "Morgana", "character"),
    378: ("C008", "Morgana", "character"),
    379: ("C001", "Vivienne", "character"),
    387: ("C008", "Morgana", "character"),
    458: ("C003", "Aria", "character"),
    459: ("C001", "Vivienne", "character"),
    460: ("C001", "Vivienne", "narration"),
    728: ("C005", "Narrator", "narrator"),
    770: ("C015", "Chief Elder Laurent", "character"),
    846: ("C001", "Vivienne", "character"),
    850: ("C003", "Aria", "character"),
    851: ("C003", "Aria", "character"),
    852: ("C003", "Aria", "character"),
    853: ("C003", "Aria", "character"),
    854: ("C001", "Vivienne", "character"),
    855: ("C001", "Vivienne", "character"),
    857: ("C001", "Vivienne", "character"),
}

try:
    # Check file exists
    if not json_path.exists():
        raise FileNotFoundError(
            f"Cannot find file: {json_path}"
        )

    # Read JSON
    with json_path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    # Validate structure
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object.")

    assignments = data.get("assignments")

    if not isinstance(assignments, list):
        raise ValueError("Missing assignments array.")

    if data.get("count") != 28 or len(assignments) != 28:
        raise ValueError(
            f"Expected 28 assignments, found {len(assignments)}."
        )

    # Validate subtitle IDs
    existing_ids = {
        item.get("subtitle_id")
        for item in assignments
    }

    expected_ids = set(decisions.keys())

    if existing_ids != expected_ids:
        missing = expected_ids - existing_ids
        unexpected = existing_ids - expected_ids
        raise ValueError(
            f"ID mismatch. Missing: {sorted(missing)}, "
            f"Unexpected: {sorted(unexpected)}"
        )

    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = folder / (
        f"medium_review_export_{timestamp}.bak"
    )
    shutil.copy2(json_path, backup_path)

    # Apply reviewed decisions
    for item in assignments:
        subtitle_id = item["subtitle_id"]

        speaker_id, speaker_name, speaker_type = (
            decisions[subtitle_id]
        )

        item["speaker_id"] = speaker_id
        item["speaker_name"] = speaker_name
        item["speaker_type"] = speaker_type
        item["confidence"] = "high"
        item["evidence"] = (
            "Видео шалгалтаар хэрэглэгч баталгаажуулсан."
        )

    # Write temporary file first
    temp_path = json_path.with_suffix(".tmp")

    with temp_path.open("w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )
        f.write("\n")

    # Replace original file
    os.replace(temp_path, json_path)

    # Verify saved JSON
    with json_path.open("r", encoding="utf-8") as f:
        verified = json.load(f)

    assert len(verified["assignments"]) == 28

    print("SUCCESS: JSON updated.")
    print(f"Updated assignments: {len(decisions)}")
    print(f"Original backup: {backup_path.name}")
    print(f"Updated file: {json_path.name}")

except Exception as e:
    print("ERROR:", e)
    print("Original JSON was not intentionally overwritten.")
