import json
from pathlib import Path

data = json.loads(
    Path("speaker_results/batch_01.json").read_text(
        encoding="utf-8"
    )
)

for item in data["results"]:

    print(
        f'{item["subtitle_id"]}: '
        f'{item["speaker_name"]} | '
        f'{item["speaker_type"]} | '
        f'{item["confidence"]}'
    )

    print("   Нотолгоо:", item["evidence"])