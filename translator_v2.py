
import os
import re
import json
import time
import hashlib
from pathlib import Path

import srt
from dotenv import load_dotenv
from google import genai


# ==================================================
# SRT TRANSLATOR V2.2 — GEMINI
# ==================================================

VERSION = "2.2"

BATCH_SIZE = 20
CONTEXT_WINDOW = 10
MAX_BATCH_ATTEMPTS = 3

DEFAULT_MODEL = "gemini-2.5-flash"

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "data" / "output"
CHECKPOINT_DIR = BASE_DIR / "data" / "checkpoints"
DEBUG_DIR = BASE_DIR / "data" / "debug"

for directory in (OUTPUT_DIR, CHECKPOINT_DIR, DEBUG_DIR):
    directory.mkdir(parents=True, exist_ok=True)


# ==================================================
# ENVIRONMENT
# ==================================================

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY олдсонгүй. "
        ".env файлаа шалгана уу."
    )

client = genai.Client(api_key=API_KEY)


# ==================================================
# FILE HELPERS
# ==================================================

def sha256_file(path):
    digest = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


def load_srt(path):
    with open(path, "r", encoding="utf-8-sig") as file:
        content = file.read()

    subtitles = list(srt.parse(content))

    if not subtitles:
        raise ValueError("SRT файл хоосон байна.")

    return subtitles


def save_srt(subtitles, path):
    content = srt.compose(subtitles)

    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


# ==================================================
# CHECKPOINT
# ==================================================

def load_checkpoint(path, source_hash):

    if not path.exists():
        print("\nШинэ checkpoint үүсгэнэ.")
        return {}

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    saved_hash = data.get("source_hash")

    if saved_hash != source_hash:
        raise RuntimeError(
            "\nCHECKPOINT SOURCE HASH MISMATCH!\n"
            "Checkpoint-ийн эх файл одоогийн SRT-тэй "
            "таарахгүй байна.\n"
            "Checkpoint-ийг автоматаар өөрчлөхгүй."
        )

    translations = data.get("translations", {})

    # Бүх ID-г string хэлбэрт оруулна.
    translations = {
        str(key): str(value)
        for key, value in translations.items()
    }

    print("\nӨмнөх checkpoint олдлоо.")

    return translations


def save_checkpoint(path, source_hash, translations):

    data = {
        "version": VERSION,
        "model": MODEL,
        "source_hash": source_hash,
        "translations": translations,
        "updated_at": time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    temp_path = path.with_suffix(".tmp")

    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    temp_path.replace(path)


# ==================================================
# DEBUG
# ==================================================

def save_debug_response(batch, attempt, raw_text, error):

    first_id = batch[0]["id"]
    last_id = batch[-1]["id"]

    debug_path = DEBUG_DIR / (
        f"gemini_error_{first_id}_{last_id}_"
        f"attempt_{attempt}.txt"
    )

    with open(debug_path, "w", encoding="utf-8") as file:

        file.write("BATCH INFORMATION\n")
        file.write(f"FIRST ID: {first_id}\n")
        file.write(f"LAST ID: {last_id}\n")
        file.write(f"ATTEMPT: {attempt}\n\n")

        file.write("ERROR\n")
        file.write(str(error))
        file.write("\n\n")

        file.write("RAW GEMINI RESPONSE\n")
        file.write(str(raw_text))

    print("\nDEBUG FILE:", debug_path)


# ==================================================
# JSON HELPERS
# ==================================================

def clean_json_response(text):

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return text.strip()


# ==================================================
# TRANSLATION PROMPT
# ==================================================


def build_prompt(context, batch):

    context_text = "\n".join(
        f'{item["id"]}: {item["text"]}'
        for item in context
    )

    batch_text = "\n".join(
        f'{item["id"]}: {item["text"]}'
        for item in batch
    )

    return f"""
Чи бол киноны хадмал орчуулгын мэргэжлийн орчуулагч.

ҮНДСЭН ДААЛГАВАР:

Англи хэл дээрх киноны хадмалыг монгол хэл рүү
утга төгөлдөр, байгалийн, ярианы хэллэгтэй орчуул.

ОРЧУУЛГЫН ЗАРЧИМ:

1. Эх өгүүлбэрийн үндсэн утга, санаа, агуулгыг бүрэн хадгал.
2. Монгол хүний өдөр тутмын ярианд байгалийн сонсогдохоор орчуул.
3. Үгчлэн орчуулахын оронд эх өгүүлбэрийн утгыг зөв илэрхийл.
4. Киноны нөхцөл байдал, харилцаа, үйл явдлын уялдааг харгалз.
5. Дүрүүдийн сэтгэл хөдлөл, уур амьсгал, ярианы өнгө аясыг хадгал.
6. Хадмалын уншихад хялбар, товч, ойлгомжтой байдлыг эрхэмлэ.
7. Эхэд байхгүй мэдээлэл, тайлбар, санаа нэмж болохгүй.
8. Утга агуулсан үг, өгүүлбэрийг орхиж болохгүй.
9. Орчуулгын тайлбар, тэмдэглэл, нэмэлт тайлбар бүү оруул.
10. Хоёр өөр subtitle-ийн агуулгыг нэгтгэж болохгүй.
11. Subtitle бүрийг тус тусад нь орчуул.
12. Эх subtitle-ийн ID дугаарыг яг хэвээр хадгал.
13. Дүрийн нэр, газар усны нэр, тусгай нэршлийг дур мэдэн өөрчилж болохгүй.
14. Монгол хэлний зөв бичих дүрэм, өгүүлбэрийн найруулгыг баримтал.
15. Эх өгүүлбэрийн утга тодорхойгүй бол таамгаар шинэ утга зохиохгүй.

ДҮРИЙН НЭРС:

- Lucian
- Luna Valeris
- Alpha Valeris
- Chief Elder Laurent
- Vivienne
- Morgana
- Aria
- Royal Seer
- Lance
- Luke

НЭРИЙН ОНЦГОЙ ДҮРЭМ:

Lucian гэдэг нэр зөв.
Lucien гэж өөрчилж болохгүй.

КОНТЕКСТ:

Доорх subtitle-ууд нь зөвхөн тухайн ярианы
утга, нөхцөл байдлыг ойлгоход зориулагдсан.
Эдгээрийг дахин орчуулахгүй.

{context_text}

ОРЧУУЛАХ SUBTITLE-УУД:

{batch_text}

ХАРИУНЫ ФОРМАТ:

Зөвхөн хүчинтэй JSON массив буцаа.

Жишээ:

[
  {{
    "id": 201,
    "text": "Монгол орчуулга"
  }},
  {{
    "id": 202,
    "text": "Монгол орчуулга"
  }}
]

JSON БУЦААХДАА ДАРААХ ДҮРМИЙГ БАРИМТАЛ:

1. Хүсэлтэд өгөгдсөн бүх ID-д орчуулга буцаа.
2. Ямар ч ID-г орхиж болохгүй.
3. Нэг ID-г давхардуулж болохгүй.
4. Эх ID дугаарыг өөрчилж болохгүй.
5. JSON-ийн синтаксийг бүрэн зөв бич.
6. Текст доторх давхар хашилтыг JSON дүрмийн дагуу escape хий.
7. JSON-ийн гадна Markdown, тайлбар, нэмэлт текст бүү оруул.
8. "text" талбар бүр зөвхөн монгол орчуулга агуулсан байна.
"""



# ==================================================
# GEMINI REQUEST
# ==================================================

def translate_batch(context, batch, attempt):

    prompt = build_prompt(context, batch)

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": 0.2,
        }
    )

    raw_text = response.text or ""

    if not raw_text.strip():

        save_debug_response(
            batch,
            attempt,
            raw_text,
            "Gemini хоосон хариу буцаалаа."
        )

        raise ValueError(
            "Gemini хоосон хариу буцаалаа."
        )

    cleaned_text = clean_json_response(raw_text)

    try:

        result = json.loads(cleaned_text)

    except json.JSONDecodeError as error:

        save_debug_response(
            batch,
            attempt,
            raw_text,
            error
        )

        raise ValueError(
            f"Gemini JSON формат буруу байна: {error}"
        )

    if not isinstance(result, list):

        save_debug_response(
            batch,
            attempt,
            raw_text,
            "JSON array биш байна."
        )

        raise ValueError(
            "Gemini JSON array буцаасангүй."
        )

    expected_ids = [
        int(item["id"])
        for item in batch
    ]

    received = {}

    for item in result:

        if not isinstance(item, dict):
            raise ValueError(
                "JSON дотор object биш элемент байна."
            )

        if "id" not in item or "text" not in item:
            raise ValueError(
                "JSON дотор id эсвэл text талбар алга."
            )

        cue_id = int(item["id"])

        translated_text = item["text"]

        if not isinstance(translated_text, str):
            raise ValueError(
                f"Cue {cue_id}: text string биш байна."
            )

        translated_text = translated_text.strip()

        if not translated_text:
            raise ValueError(
                f"Cue {cue_id}: орчуулга хоосон байна."
            )

        if cue_id in received:
            raise ValueError(
                f"Давхардсан cue ID: {cue_id}"
            )

        received[cue_id] = translated_text

    received_ids = set(received.keys())
    expected_id_set = set(expected_ids)

    if received_ids != expected_id_set:

        missing = sorted(
            expected_id_set - received_ids
        )

        unexpected = sorted(
            received_ids - expected_id_set
        )

        raise ValueError(
            "Cue ID зөрүүтэй байна. "
            f"Missing: {missing}; "
            f"Unexpected: {unexpected}"
        )

    return received


# ==================================================
# MAIN
# ==================================================

def main():

    print("=" * 50)
    print("          SRT TRANSLATOR V2.2")
    print("=" * 50)

    source_input = input(
        "\nSRT файлын бүтэн зам: "
    ).strip().strip('"')

    source_path = Path(source_input)

    if not source_path.exists():
        raise FileNotFoundError(
            f"SRT файл олдсонгүй: {source_path}"
        )

    subtitles = load_srt(source_path)

    source_hash = sha256_file(source_path)

    file_stem = source_path.stem

    output_path = (
        OUTPUT_DIR / f"{file_stem}_mn.srt"
    )

    checkpoint_path = (
        CHECKPOINT_DIR /
        f"{file_stem}_checkpoint.json"
    )

    translations = load_checkpoint(
        checkpoint_path,
        source_hash
    )

    total = len(subtitles)

    print("\nSOURCE CUES:", total)
    print("MODEL:", MODEL)
    print("CHECKPOINT TRANSLATIONS:", len(translations))

    # ==================================================
    # TRANSLATION LOOP
    # ==================================================

    for start in range(0, total, BATCH_SIZE):

        batch_subtitles = subtitles[
            start:start + BATCH_SIZE
        ]

        batch = [
            {
                "id": subtitle.index,
                "text": subtitle.content
            }
            for subtitle in batch_subtitles
        ]

        pending_batch = [
            item
            for item in batch
            if str(item["id"]) not in translations
        ]

        if not pending_batch:
            continue

        context_start = max(
            0,
            start - CONTEXT_WINDOW
        )

        context_subtitles = subtitles[
            context_start:start
        ]

        context = [
            {
                "id": subtitle.index,
                "text": subtitle.content
            }
            for subtitle in context_subtitles
        ]

        print(
            f"\nTRANSLATING CUES "
            f"{batch[0]['id']} - {batch[-1]['id']}"
        )

        print(
            "PENDING:",
            len(pending_batch)
        )

        success = False

        for attempt in range(
            1,
            MAX_BATCH_ATTEMPTS + 1
        ):

            try:

                result = translate_batch(
                    context,
                    pending_batch,
                    attempt
                )

                # Зөвхөн бүх шалгалт амжилттай
                # болсон тохиолдолд checkpoint-д бичнэ.

                for cue_id, translated_text in result.items():

                    translations[str(cue_id)] = (
                        translated_text
                    )

                save_checkpoint(
                    checkpoint_path,
                    source_hash,
                    translations
                )

                print(
                    f"SUCCESS: {len(result)} "
                    "subtitles translated."
                )

                success = True
                break

            except Exception as error:

                print(
                    f"ATTEMPT {attempt} FAILED: {error}"
                )

                if attempt < MAX_BATCH_ATTEMPTS:

                    wait_seconds = attempt * 3

                    print(
                        f"Retrying in {wait_seconds} seconds..."
                    )

                    time.sleep(wait_seconds)

        if not success:

            save_checkpoint(
                checkpoint_path,
                source_hash,
                translations
            )

            raise RuntimeError(
                f"\nCue {batch[0]['id']}-"
                f"{batch[-1]['id']} орчуулга амжилтгүй.\n"
                "Checkpoint хадгалагдсан.\n"
                "Алдааны дэлгэрэнгүй мэдээллийг "
                "data/debug хавтаснаас шалгана уу."
            )

        time.sleep(1)

    # ==================================================
    # VERIFY ALL TRANSLATIONS
    # ==================================================

    missing = []

    for subtitle in subtitles:

        cue_id = str(subtitle.index)

        if cue_id not in translations:
            missing.append(subtitle.index)

    if missing:

        raise RuntimeError(
            "Орчуулга дутуу cue байна: "
            f"{missing}"
        )

    # ==================================================
    # BUILD FINAL SRT
    # ==================================================

    for subtitle in subtitles:

        cue_id = str(subtitle.index)

        subtitle.content = translations[cue_id]

    save_srt(
        subtitles,
        output_path
    )

    print("\n" + "=" * 50)
    print("TRANSLATION COMPLETED")
    print("=" * 50)

    print("OUTPUT:", output_path)
    print("TOTAL CUES:", total)
    print("TRANSLATED:", len(translations))
    print("MODEL:", MODEL)


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:
        print("\nUser interrupted translation.")

    except Exception as error:
        print("\nFATAL ERROR:")
        print(error)
        raise
