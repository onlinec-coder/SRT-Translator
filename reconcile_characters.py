
import json
from pathlib import Path


INPUT_FILE = "Husbands_reconciliation_input.json"
MAPPING_FILE = "character_mapping.json"
OUTPUT_FILE = "Husbands_characters_reconciled.json"


def unique_items(items):

    result = []
    seen = set()

    for item in items:

        key = json.dumps(
            item,
            ensure_ascii=False,
            sort_keys=True
        )

        if key not in seen:
            seen.add(key)
            result.append(item)

    return result


def merge_character_records(records, mapping):

    character_map = {
        character["id"]: character
        for character in records
    }

    excluded_ids = {
        item["character_id"]
        for item in mapping.get(
            "exclude_from_characters", []
        )
    }

    merged_groups = mapping.get(
        "merge_candidates", []
    )

    consumed_ids = set(excluded_ids)

    result = []

    for group in merged_groups:

        ids = group["character_ids"]

        group_records = [
            character_map[character_id]
            for character_id in ids
            if character_id in character_map
        ]

        if len(group_records) != len(ids):
            raise ValueError(
                f"Дүрийн ID олдсонгүй: {ids}"
            )

        genders = {
            character["gender"]
            for character in group_records
            if character.get("gender") is not None
        }

        if len(genders) > 1:
            raise ValueError(
                f"Хүйсийн зөрчилтэй дүрүүд: {ids}"
            )

        base = group_records[0]

        names = []
        aliases = list(group.get("aliases", []))

        relationships = []
        speech_style = []
        evidence = []

        for character in group_records:

            names.extend(character.get("names") or [])
            aliases.extend(character.get("aliases") or [])

            relationships.extend(
                character.get("relationships") or []
            )

            speech_style.extend(
                character.get("speech_style") or []
            )

            evidence.extend(
                character.get("evidence") or []
            )

        canonical_name = group["canonical_name"]

        all_names = unique_items(names + aliases)

        final_aliases = [
            name
            for name in all_names
            if name != canonical_name
        ]

        result.append({
            "id": ids[0],
            "canonical_name": canonical_name,
            "aliases": final_aliases,
            "gender": base.get("gender"),
            "relationships": unique_items(relationships),
            "speech_style": unique_items(speech_style),
            "evidence": unique_items(evidence),
            "confidence": "high",
            "source_ids": ids
        })

        consumed_ids.update(ids)

    for character in records:

        character_id = character["id"]

        if character_id in consumed_ids:
            continue

        result.append({
            "id": character_id,
            "canonical_name": (
                character.get("names") or [None]
            )[0],
                        "aliases": (
                []
                if character_id == "C008"
                else character.get("aliases") or []
            ),
            "gender": character.get("gender"),
            "relationships": character.get("relationships") or [],
            "speech_style": character.get("speech_style") or [],
            "evidence": character.get("evidence") or [],
            "confidence": character.get("confidence", "low"),
            "source_ids": [character_id]
        })

    return result


def main():

    data = json.loads(
        Path(INPUT_FILE).read_text(
            encoding="utf-8"
        )
    )

    mapping = json.loads(
        Path(MAPPING_FILE).read_text(
            encoding="utf-8"
        )
    )
    characters = data.get("characters", [])

    # Дүр бүрт тогтвортой ID оноох
    for index, character in enumerate(
        characters,
        start=1
    ):
        character["id"] = f"C{index:03d}"

    reconciled = merge_character_records(
        characters,
        mapping
    )
    

    result = {
        "characters": reconciled,
        "review_required": mapping.get(
            "review_required", []
        ),
        "unresolved": mapping.get(
            "unresolved", []
        ),
        "notes": [
            "Зөвхөн merge_candidates доторх дүрүүдийг нэгтгэсэн.",
            "review_required дүрүүдийг тусад нь үлдээсэн.",
            "exclude_from_characters доторх бүртгэлийг хассан."
        ]
    }

    Path(OUTPUT_FILE).write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=4
        ),
        encoding="utf-8"
    )

    print("Эх бүртгэл:", len(characters))
    print("Нэгтгэсэн бүртгэл:", len(reconciled))
    print("Шинэ файл:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
