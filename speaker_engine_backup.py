import json
from pathlib import Path

import srt


SUBTITLE_FILE = "input.srt"
CHARACTER_FILE = "Husbands_characters_reconciled.json"

SPEAKER_OUTPUT_SCHEMA = {
    "results": [
        {
            "subtitle_id": 1,
            "speaker_id": "C001",
            "speaker_name": "Vivienne",
            "speaker_type": "character",
            "confidence": "high",
            "evidence": "Контекст болон ярианы ээлжээр тогтоосон"
        }
    ]
}

VALID_SPEAKER_TYPES = [
    "character",
    "inner_monologue",
    "narrator",
    "unknown"
]

VALID_CONFIDENCE_LEVELS = [
    "high",
    "medium",
    "low"
]


def load_subtitles(file_path):

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Файл олдсонгүй: {path}"
        )

    content = path.read_text(
        encoding="utf-8-sig"
    )

    subtitles = list(srt.parse(content))

    if not subtitles:
        raise ValueError(
            "SRT файл хоосон байна."
        )

    return subtitles


def load_characters(file_path):

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Файл олдсонгүй: {path}"
        )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    characters = data.get("characters", [])

    if not characters:
        raise ValueError(
            "Дүрийн бүртгэл хоосон байна."
        )

    return characters


def prepare_speaker_data(subtitles, characters):

    character_list = []

    for character in characters:

        character_list.append({
            "id": character["id"],
            "name": character["canonical_name"],
            "aliases": character.get("aliases", []),
            "gender": character.get("gender"),
            "relationships": character.get(
                "relationships", []
            ),
            "speech_style": character.get(
                "speech_style", []
            )
        })

    subtitle_list = []

    for sub in subtitles:

        subtitle_list.append({
            "subtitle_id": sub.index,
            "start": str(sub.start),
            "end": str(sub.end),
            "text": sub.content
        })

    return {
        "characters": character_list,
        "subtitles": subtitle_list
    }
def create_subtitle_batches(
    subtitles,
    batch_size=40,
    context_size=5
):

    batches = []

    for start in range(
        0,
        len(subtitles),
        batch_size
    ):

        end = min(
            start + batch_size,
            len(subtitles)
        )

        context_start = max(
            0,
            start - context_size
        )

        context_end = min(
            len(subtitles),
            end + context_size
        )

        batches.append({
            "batch_number": len(batches) + 1,

            "subtitles": subtitles[start:end],

            "context_before": subtitles[
                context_start:start
            ],

            "context_after": subtitles[
                end:context_end
            ]
        })

    return batches
def build_speaker_prompt(batch, characters):

    return f"""
Чи мэргэжлийн киноны диалог шинжээч.

ҮҮРЭГ:
Доорх хадмал бүрийн яригчийг тодорхойл.

ДҮРҮҮД:
{json.dumps(
    characters,
    ensure_ascii=False,
    indent=2
)}

ӨМНӨХ КОНТЕКСТ:
{json.dumps(
    batch["context_before"],
    ensure_ascii=False,
    indent=2
)}

ШИНЖЛЭХ ХАДМАЛ:
{json.dumps(
    batch["subtitles"],
    ensure_ascii=False,
    indent=2
)}

ДАРААХ КОНТЕКСТ:
{json.dumps(
    batch["context_after"],
    ensure_ascii=False,
    indent=2
)}

ШИНЖИЛГЭЭНИЙ ДҮРЭМ:

1. Нэр дурдагдсан дүрийг шууд яригч гэж бүү үз.
2. Ярианы ээлж, өгүүлбэрийн утга,
   өмнөх болон дараах контекстыг ашигла.
3. Дүрүүдийн харилцааг харгалз.
4. Дүрийн ярианы хэв маягийг харгалз.
5. Дотоод бодлыг inner_monologue гэж ангил.
   Дотоод бодлын эзнийг контекст болон өгүүлэмжээр тогтоо.
   Хэрэв Vivienne өөрийн бодлыг хүүрнэж байвал:
   speaker_id = "C001"
   speaker_name = "Vivienne"
   speaker_type = "inner_monologue".
   Зөвхөн эхний биеэр өгүүлсэн гэдгээр Vivienne гэж таамаглаж болохгүй.
   Эзнийг тогтоох боломжгүй бол speaker_id болон
   speaker_name-ийг null болго.
6. Гаднын хүүрнэлийг narrator гэж ангил.
7. Тодорхойлох боломжгүй бол unknown ашигла.
8. Таамгаар дүрийн ID бүү оноо.
9. Бүх хадмалын subtitle_id-г яг хэвээр хадгал.
10. Нэг ч хадмалыг алгасаж болохгүй.

ЗӨВШӨӨРӨГДСӨН speaker_type:
{VALID_SPEAKER_TYPES}

ЗӨВШӨӨРӨГДСӨН confidence:
{VALID_CONFIDENCE_LEVELS}

ГАРАЛТ:
Зөвхөн JSON буцаа.

Бүтэц:
{json.dumps(
    SPEAKER_OUTPUT_SCHEMA,
    ensure_ascii=False,
    indent=2
)}

speaker_id нь дүрийн бүртгэл дэх ID байна.
speaker_name нь дүрийн canonical нэр байна.
unknown үед speaker_id болон speaker_name хоёулаа null байна.
evidence нь тухайн шийдвэрийн товч нотолгоо байна.
"""
def classify_speaker_confidence(results):

    review = {
        "high": [],
        "medium": [],
        "low": []
    }

    for item in results:

        confidence = item.get("confidence")

        if confidence in review:

            review[confidence].append(item)

    return review
def build_speaker_output(subtitles, results):

    assignments = results

    review = classify_speaker_confidence(
        assignments
    )

    return {
        "movie": {
            "subtitle_file": SUBTITLE_FILE,
            "total_subtitles": len(subtitles)
        },
        "assignments": assignments,
        "review": review
    }
def validate_speaker_results(
    ai_response,
    batch_subtitles,
    characters
):

    errors = []

    if not isinstance(ai_response, dict):

        return [
            "AI-ийн хариу JSON object биш байна."
        ]

    results = ai_response.get("results")

    if not isinstance(results, list):

        return [
            "AI-ийн хариунд results жагсаалт алга."
        ]

    valid_speaker_ids = {
        character["id"]
        for character in characters
    }
    speaker_name_by_id = {
        character["id"]: character["canonical_name"]
        for character in characters
    }

    expected_ids = {
        subtitle["subtitle_id"]
        for subtitle in batch_subtitles
    }

    received_ids = []

    for item in results:

        if not isinstance(item, dict):

            errors.append(
                "results дотор буруу бүтэцтэй элемент байна."
            )

            continue

        subtitle_id = item.get("subtitle_id")

        if type(subtitle_id) is not int:

            errors.append(
                f"Буруу subtitle_id: {subtitle_id}"
            )

            continue

        received_ids.append(subtitle_id)

        speaker_id = item.get("speaker_id")

        if speaker_id is not None:

            if not isinstance(speaker_id, str):

                errors.append(
                    f"[{subtitle_id}] speaker_id текст биш байна: "
                    f"{speaker_id}"
                )

            elif speaker_id not in valid_speaker_ids:

                errors.append(
                    f"[{subtitle_id}] Байхгүй дүрийн ID: "
                    f"{speaker_id}"
                )
        if (
            isinstance(speaker_id, str)
            and speaker_id in speaker_name_by_id
        ):

            expected_name = speaker_name_by_id[speaker_id]

            actual_name = item.get("speaker_name")

            if actual_name != expected_name:

                errors.append(
                    f"[{subtitle_id}] Speaker нэр таарахгүй: "
                    f"{speaker_id} нь {expected_name} байх ёстой, "
                    f"харин {actual_name} ирсэн байна."
                )

        speaker_type = item.get("speaker_type")

        if speaker_type not in VALID_SPEAKER_TYPES:

            errors.append(
                f"[{subtitle_id}] Буруу speaker_type: {speaker_type}"
            )

        confidence = item.get("confidence")

        if confidence not in VALID_CONFIDENCE_LEVELS:

            errors.append(
                f"[{subtitle_id}] Буруу confidence: {confidence}"
            )

        if speaker_type == "unknown":

            if speaker_id is not None:

                errors.append(
                    f"[{subtitle_id}] unknown төрөлтэй боловч "
                    "speaker_id оноосон байна."
                )

            if item.get("speaker_name") is not None:

                errors.append(
                    f"[{subtitle_id}] unknown төрөлтэй боловч "
                    "speaker_name оноосон байна."
                )

        if (
            speaker_type in [
                "character",
                "inner_monologue"
            ]
            and speaker_id is None
        ):

            errors.append(
                f"[{subtitle_id}] Дүрийн төрөлтэй боловч speaker_id алга."
            )

    if len(received_ids) != len(set(received_ids)):

        errors.append(
            "Давхардсан subtitle_id байна."
        )

    received_set = set(received_ids)

    missing_ids = expected_ids - received_set
    extra_ids = received_set - expected_ids

    if missing_ids:

        errors.append(
            f"Орхигдсон хадмалын дугаар: {sorted(missing_ids)}"
        )

    if extra_ids:

        errors.append(
            f"Багцад байхгүй хадмалын дугаар: {sorted(extra_ids)}"
        )

    return errors
def main():

    subtitles = load_subtitles(
        SUBTITLE_FILE
    )

    characters = load_characters(
        CHARACTER_FILE
    )

    speaker_data = prepare_speaker_data(
        subtitles,
        characters
    )

    batches = create_subtitle_batches(
        speaker_data["subtitles"],
        batch_size=40,
        context_size=5
    )
    prompt_directory = Path("speaker_prompts")

    prompt_directory.mkdir(
        exist_ok=True
    )

    for index, batch in enumerate(batches, start=1):

        prompt = build_speaker_prompt(
            batch,
            speaker_data["characters"]
        )

        prompt_file = prompt_directory / f"batch_{index:02d}.txt"

        prompt_file.write_text(
            prompt,
            encoding="utf-8"
        )

    print("Бүх багцын Prompt бэлэн боллоо.")
    print("Prompt хавтас:", prompt_directory)
    print("Үүсгэсэн Prompt:", len(batches))

    output_file = "speaker_analysis_input.json"

    result = {
        "characters": speaker_data["characters"],
        "batches": batches
    }

    Path(output_file).write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=4
        ),
        encoding="utf-8"
    )
    speaker_output = build_speaker_output(
        subtitles,
        []
    )

    Path("speaker_assignments.json").write_text(
        json.dumps(
            speaker_output,
            ensure_ascii=False,
            indent=4
        ),
        encoding="utf-8"
    )

    print("Speaker үр дүнгийн файл бэлэн боллоо.")
    print("Файл: speaker_assignments.json")
    print("Нийт хадмал:", len(subtitles))
    print("Нийт дүр:", len(characters))
    print("Нийт багц:", len(batches))
    print("Шинэ файл:", output_file)
def test_speaker_confidence_classification():

    test_results = [
        {
            "subtitle_id": 1,
            "confidence": "high"
        },
        {
            "subtitle_id": 2,
            "confidence": "medium"
        },
        {
            "subtitle_id": 3,
            "confidence": "low"
        },
        {
            "subtitle_id": 4,
            "confidence": "high"
        }
    ]

    classified = classify_speaker_confidence(
        test_results
    )

    assert len(classified["high"]) == 2
    assert len(classified["medium"]) == 1
    assert len(classified["low"]) == 1

    assert classified["high"][0]["subtitle_id"] == 1
    assert classified["medium"][0]["subtitle_id"] == 2
    assert classified["low"][0]["subtitle_id"] == 3

    print("Speaker confidence ангиллын тест: PASS")
def test_subtitle_batch_context():

    test_subtitles = [
        {"subtitle_id": i}
        for i in range(1, 101)
    ]

    batches = create_subtitle_batches(
        test_subtitles,
        batch_size=40,
        context_size=5
    )

    first = batches[0]
    second = batches[1]
    last = batches[-1]

    assert len(batches) == 3

    assert len(first["subtitles"]) == 40
    assert len(first["context_before"]) == 0
    assert len(first["context_after"]) == 5

    assert len(second["subtitles"]) == 40
    assert len(second["context_before"]) == 5
    assert len(second["context_after"]) == 5

    assert len(last["subtitles"]) == 20
    assert len(last["context_before"]) == 5
    assert len(last["context_after"]) == 0

    assert [
        item["subtitle_id"]
        for item in second["context_before"]
    ] == [36, 37, 38, 39, 40]

    assert [
        item["subtitle_id"]
        for item in second["subtitles"]
    ] == list(range(41, 81))

    print("Багцын контекст тест: PASS")
def test_speaker_name_validation():

    test_characters = [
        {
            "id": "C001",
            "canonical_name": "Vivienne"
        }
    ]

    test_subtitles = [
        {"subtitle_id": 1}
    ]

    correct_response = {
        "results": [
            {
                "subtitle_id": 1,
                "speaker_id": "C001",
                "speaker_name": "Vivienne",
                "speaker_type": "character",
                "confidence": "high",
                "evidence": "Тест"
            }
        ]
    }

    wrong_response = {
        "results": [
            {
                "subtitle_id": 1,
                "speaker_id": "C001",
                "speaker_name": "Lucian",
                "speaker_type": "character",
                "confidence": "high",
                "evidence": "Тест"
            }
        ]
    }
    invalid_type_response = {
        "results": [
            {
                "subtitle_id": 1,
                "speaker_id": "C001",
                "speaker_name": "Vivienne",
                "speaker_type": "dialogue",
                "confidence": "high",
                "evidence": "Тест"
            }
        ]
    }
    invalid_confidence_response = {
        "results": [
            {
                "subtitle_id": 1,
                "speaker_id": "C001",
                "speaker_name": "Vivienne",
                "speaker_type": "character",
                "confidence": "very_high",
                "evidence": "Тест"
            }
        ]
    }
    invalid_unknown_response = {
        "results": [
            {
                "subtitle_id": 1,
                "speaker_id": "C001",
                "speaker_name": "Vivienne",
                "speaker_type": "unknown",
                "confidence": "low",
                "evidence": "Тест"
            }
        ]
    }

    invalid_unknown_errors = validate_speaker_results(
        invalid_unknown_response,
        test_subtitles,
        test_characters
    )

    print(
        "Unknown speaker тест:",
        "PASS" if (
            any(
                "unknown төрөлтэй боловч speaker_id" in error
                for error in invalid_unknown_errors
            )
            and any(
                "unknown төрөлтэй боловч speaker_name" in error
                for error in invalid_unknown_errors
            )
        ) else "FAIL"
    )
    correct_unknown_response = {
        "results": [
            {
                "subtitle_id": 1,
                "speaker_id": None,
                "speaker_name": None,
                "speaker_type": "unknown",
                "confidence": "low",
                "evidence": "Яригчийг тогтоох боломжгүй"
            }
        ]
    }

    correct_unknown_errors = validate_speaker_results(
        correct_unknown_response,
        test_subtitles,
        test_characters
    )

    print(
        "Зөв unknown тест:",
        "PASS" if not correct_unknown_errors else "FAIL"
    )
    invalid_confidence_errors = validate_speaker_results(
        invalid_confidence_response,
        test_subtitles,
        test_characters
    )

    print(
        "Буруу confidence тест:",
        "PASS" if any(
            "Буруу confidence" in error
            for error in invalid_confidence_errors
        ) else "FAIL"
    )

    invalid_type_errors = validate_speaker_results(
        invalid_type_response,
        test_subtitles,
        test_characters
    )

    print(
        "Буруу speaker_type тест:",
        "PASS" if any(
            "Буруу speaker_type" in error
            for error in invalid_type_errors
        ) else "FAIL"
    )
    duplicate_response = {
        "results": [
            correct_response["results"][0],
            correct_response["results"][0]
        ]
    }
    extra_response = {
        "results": [
            correct_response["results"][0],
            {
                "subtitle_id": 2,
                "speaker_id": "C001",
                "speaker_name": "Vivienne",
                "speaker_type": "character",
                "confidence": "high",
                "evidence": "Тест"
            }
        ]
    }

    extra_errors = validate_speaker_results(
        extra_response,
        test_subtitles,
        test_characters
    )

    print(
        "Илүүдэл хадмалын тест:",
        "PASS" if any(
            "Багцад байхгүй хадмалын дугаар" in error
            for error in extra_errors
        ) else "FAIL"
    )
    missing_response = {
        "results": []
    }

    missing_errors = validate_speaker_results(
        missing_response,
        test_subtitles,
        test_characters
    )

    print(
        "Дутуу хадмалын тест:",
        "PASS" if any(
            "Орхигдсон хадмалын дугаар" in error
            for error in missing_errors
        ) else "FAIL"
    )

    duplicate_errors = validate_speaker_results(
        duplicate_response,
        test_subtitles,
        test_characters
    )

    print(
        "Давхардсан хадмалын тест:",
        "PASS" if any(
            "Давхардсан subtitle_id" in error
            for error in duplicate_errors
        ) else "FAIL"
    )

    correct_errors = validate_speaker_results(
        correct_response,
        test_subtitles,
        test_characters
    )

    wrong_errors = validate_speaker_results(
        wrong_response,
        test_subtitles,
        test_characters
    )

    print("Зөв нэрийн тест:", "PASS" if not correct_errors else "FAIL")
    print("Буруу нэрийн тест:", "PASS" if wrong_errors else "FAIL")

    if wrong_errors:
        for error in wrong_errors:
            print(error)
if __name__ == "__main__":
    test_speaker_name_validation()
    test_subtitle_batch_context()
    test_speaker_confidence_classification()
    main()

   