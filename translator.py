
import os
import json
import re
import time
from pathlib import Path

import srt
from dotenv import load_dotenv


# =====================================
# CONFIGURATION
# =====================================

BATCH_SIZE = 20


SYSTEM_PROMPT = """
Чи бол мэргэжлийн кино нутагшуулалтын орчуулагч,
Монгол хэлний редактор, кино зохиолын ярианы найруулагч.

ҮНДСЭН ЗОРИЛГО:
Англи эсвэл хятад хэл дээрх киноны яриаг
утга, сэтгэл хөдлөл, дүрийн онцлогийг хадгалсан,
монгол хүний амьд яриа шиг байгалийн хэлээр орчуул.

1. УТГА БА КОНТЕКСТ
- Үг бүрээр шууд орчуулж болохгүй.
- Өгүүлбэрийн цаад санаа, нөхцөл байдал,
  өмнөх болон дараах яриатай нь холбон ойлго.
- Олон утгатай үгийг тухайн киноны нөхцөлд
  хамгийн тохирох утгаар орчуул.
- Хошигнол, ёжлол, далд утга, хэлц үгийг
  монгол хэлний дүйцэх хэллэгээр илэрхийл.
- Эх зохиолд байхгүй үйл явдал, мэдээлэл нэмж болохгүй.

2. БАЙГАЛИЙН МОНГОЛ ХЭЛ
- Монгол хүн бодит амьдрал дээр ингэж ярих уу
  гэдгийг үргэлж бодолц.
- Номын, албаны, хэт бичгийн хэллэгээс зайлсхий.
- Монгол хэлний өгүүлбэрийн зөв бүтэц, үгийн
  дарааллыг ашигла.
- Шаардлагагүй төлөөний үг, давхардсан үг,
  илүүц тайлбарыг хас.
- Эх хэлний өгүүлбэрийн бүтцийг хуулбарлахгүй.
- Утгыг алдагдуулахгүйгээр товч, цэгцтэй найруул.

3. ДҮРИЙН ЯРИАНЫ ОНЦЛОГ
- Дүрүүдийн нас, харилцаа, зан чанар,
  нийгмийн байр суурь, тухайн нөхцөл байдлыг харгалз.
- Найз нөхөд, гэр бүлийнхэн, хосуудын яриаг
  харилцаанд нь тохирсон хэлбэрээр орчуул.
- Дүр бүрийн ярианы хэв маягийг тогтвортой хадгал.
- Хэн ярьж байгаагүйг мэдэхгүй бол дур мэдэн
  хүйс, дүрийн шинж чанар зохиож болохгүй.

4. СЭТГЭЛ ХӨДЛӨЛ
- Уур, гомдол, айдас, баяр баясгалан,
  хайр, эргэлзээ, ёжлол зэрэг өнгө аясыг хадгал.
- Асуулт, тушаал, гуйх, татгалзах, сануулах
  хэлбэрүүдийг зөв ялга.
- Эхэд байхгүй хүчтэй сэтгэл хөдлөл нэмж болохгүй.

5. ХАДМАЛЫН НАЙРУУЛГА
- Дэлгэц дээр хурдан уншихад ойлгомжтой байлга.
- Боломжтой бол богино, цэгцтэй өгүүлбэр ашигла.
- Монгол хэлний цэг тэмдэг, зөв бичих дүрмийг баримтал.
- Эх өгүүлбэрийн цагийн утга, үйл явдлын дарааллыг хадгал.
- Орчуулгыг тайлбар, хаалт, тэмдэглэлээр бүү нэмэгдүүл.

6. ЧАНАРЫН ӨӨРИЙН ШАЛГАЛТ
Орчуулга бүрийн өмнө дараах зүйлийг шалга:
- Эх өгүүлбэрийн жинхэнэ утгыг зөв ойлгосон уу?
- Монгол хүн ингэж ярих нь байгалийн уу?
- Дүрийн сэтгэл хөдлөл зөв хадгалагдсан уу?
- Өмнөх болон дараах яриатай нийцэж байна уу?
- Илүүц үг, тайлбар байна уу?

ГАРАЛТЫН ШААРДЛАГА:
- Зөвхөн одоо орчуулах хадмалын мөрүүдийг орчуул.
- Контекстэд байгаа бусад мөрийг дахин орчуулж болохгүй.
- Оруулсан index дугаарыг өөрчлөхгүй.
- Нэг мөрийг дур мэдэн хувааж, нэгтгэж болохгүй.
- JSON-оос өөр ямар ч тайлбар бүү буцаа.

Зөвхөн дараах бүтэцтэй JSON буцаа:
{
  "translations": [
    {"index": 1, "text": "Монгол орчуулга"}
  ]
}
"""



# =====================================
# SRT FUNCTIONS
# =====================================

def load_subtitles(file_path):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Файл олдсонгүй: {path}"
        )

    content = path.read_text(encoding="utf-8-sig")
    subtitles = list(srt.parse(content))

    if not subtitles:
        raise ValueError("SRT файл хоосон байна.")

    return subtitles


def save_subtitles(subtitles, output_file):
    content = srt.compose(subtitles)

    Path(output_file).write_text(
        content,
        encoding="utf-8-sig"
    )


def build_full_context(subtitles):
    lines = []

    for sub in subtitles:
        text = " ".join(sub.content.split())

        lines.append(
            f"[{sub.index}] {text}"
        )

    return "\n".join(lines)
def load_speaker_context(input_file):

    base_dir = Path(input_file).parent

    assignments_file = (
        base_dir / "speaker_assignments.json"
    )

    characters_file = (
        base_dir / "Husbands_characters_reconciled.json"
    )

    if not assignments_file.exists():
        raise FileNotFoundError(
            f"Яригчийн оноолтын файл олдсонгүй: {assignments_file}"
        )

    if not characters_file.exists():
        raise FileNotFoundError(
            f"Дүрийн бүртгэлийн файл олдсонгүй: {characters_file}"
        )

    with assignments_file.open("r", encoding="utf-8") as f:
        assignments_data = json.load(f)

    with characters_file.open("r", encoding="utf-8") as f:
        characters_data = json.load(f)

    character_map = {
        character["id"]: character
        for character in characters_data["characters"]
    }

    speaker_map = {}

    for item in assignments_data["assignments"]:

        speaker_id = item["speaker_id"]
        character = character_map.get(speaker_id, {})

        speaker_map[item["subtitle_id"]] = {
            "speaker_id": speaker_id,
            "speaker_name": item["speaker_name"],
            "speaker_type": item["speaker_type"],
            "confidence": item["confidence"],
            "canonical_name": character.get(
                "canonical_name",
                item["speaker_name"]
            ),
            "gender": character.get("gender"),
            "speech_style": character.get("speech_style", [])
        }

    return speaker_map

# =====================================
# JSON PARSER
# =====================================

def extract_json(text):
    if not text:
        raise ValueError("AI хоосон хариулт буцаалаа.")

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return json.loads(text)


# =====================================
# AI PROVIDERS
# =====================================

def create_ai_client(provider, api_key):

    if provider == "openai":
        from openai import OpenAI

        return OpenAI(api_key=api_key)

    elif provider == "gemini":
        from google import genai

        return genai.Client(api_key=api_key)

    else:
        raise ValueError(
            f"Дэмжигдээгүй provider: {provider}"
        )



def call_ai(
    client,
    provider,
    model,
    user_prompt,
    system_prompt=None
):

    max_retries = 5

    active_system_prompt = system_prompt or SYSTEM_PROMPT

    for attempt in range(max_retries):

        try:

            if provider == "openai":

                response = client.responses.create(
                    model=model,
                    instructions=active_system_prompt,
                    input=user_prompt
                )

                return response.output_text

            elif provider == "gemini":

                from google.genai import types

                response = client.models.generate_content(
                    model=model,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=active_system_prompt,
                        response_mime_type="application/json",
                        temperature=0.2
                    )
                )

                return response.text

            raise ValueError("Provider буруу байна.")

        except Exception as error:

            error_text = str(error)

            temporary_errors = [
                "503",
                "UNAVAILABLE",
                "429",
                "RESOURCE_EXHAUSTED",
                "500",
                "INTERNAL",
                "502",
                "504"
            ]

            is_temporary = any(
                code in error_text
                for code in temporary_errors
            )

            if not is_temporary:
                raise

            if attempt == max_retries - 1:
                raise

            wait_seconds = 2 ** (attempt + 1)

            print(
                f"\nТүр алдаа гарлаа: {error_text[:150]}"
            )

            print(
                f"{wait_seconds} секунд хүлээгээд "
                f"дахин оролдоно... "
                f"({attempt + 1}/{max_retries})"
            )

            time.sleep(wait_seconds)


CHARACTER_ANALYSIS_PROMPT = """
Чи киноны зохиолын шинжээч, дүрийн редактор.

Үүрэг:
Киноны бүх хадмал текстийг шинжилж, текстэд
үндэслэн танигдах дүрүүдийн мэдээллийг гарга.

Дүрэм:
- Зөвхөн текстээр нотлогдох мэдээллийг ашигла.
- Нэр нь дурдагдсан хүнийг заавал ярьж буй дүр гэж үзэж болохгүй.
- Яригч тодорхойгүй бол таамаглаж нэр оноож болохгүй.
- Хүйс тодорхойгүй бол null ашигла.
- Харилцаа нотлогдоогүй бол хоосон жагсаалт ашигла.
- Зан чанар, харилцааг зохиож болохгүй.
- Нотолгоог хадмалын индексээр заа.
- Эргэлзээтэй мэдээлэлд low confidence өг.

Зөвхөн хүчинтэй JSON буцаа.
Markdown болон нэмэлт тайлбар бүү оруул.
"""


def analyze_characters(
    client,
    provider,
    model,
    subtitles,
    language
):

    subtitles_per_chunk = 100

    chunks = [
        subtitles[i:i + subtitles_per_chunk]
        for i in range(
            0,
            len(subtitles),
            subtitles_per_chunk
        )
    ]

    all_characters = []
    all_notes = []

    for i, chunk in enumerate(chunks):

        chunk_context = "\n".join(
            f"[{sub.index}] {' '.join(sub.content.split())}"
            for sub in chunk
        )

        print(
            f"\nДүр шинжилж байна: "
            f"{i + 1}/{len(chunks)}"
        )
        prompt = f"""
Киноны эх хэл: {language}

Доорх хадмалын хэсгээс нотолгоотой
дүрүүдийн мэдээллийг гарга.

JSON бүтэц:

{{
    "characters": [
        {{
            "names": [],
            "aliases": [],
            "gender": null,
            "relationships": [],
            "speech_style": [],
            "evidence": [],
            "confidence": "low"
        }}
    ],
    "notes": []
}}

ДҮР ТАНИХ ДҮРЭМ:

- Зөвхөн хадмалын текстээр нотлогдох мэдээллийг ашигла.
- Нэр нь дурдагдсан хүнийг заавал ярьж буй дүр гэж үзэж болохгүй.
- Нэг хүний нэр өөр өөр бичигдсэн байж болохыг анхаар.
  Жишээ нь: Aria / Arya.
- Нэрийн бичлэг төстэй байна гэдэг нь
  заавал нэг хүн гэсэн үг биш.
- Хоёр нэр нэг хүнийг зааж байгааг
  текстийн нөхцөл, харилцаа, үйл явдлаар нотолж чадвал
  нэг дүрийн names эсвэл aliases хэсэгт оруул.
- Нэг хүн гэдэг нь тодорхойгүй бол тусдаа дүрээр үлдээ.
- Буруу танигдсан эсвэл утгагүй нэрийг
  бодит дүрийн нэр гэж шууд бүү үз.
- Хүйс тодорхойгүй бол null.
- Харилцаа нотлогдоогүй бол хоосон жагсаалт.
- Зан чанар, харилцаа, нэр зохиож болохгүй.
- Нотолгооны хадмалын индексийг evidence-д хадгал.
- Эргэлзээтэй мэдээлэлд low confidence өг.
- Зөвхөн энэ хэсэгт байгаа нотолгоог ашигла.
- Зөвхөн хүчинтэй JSON буцаа.

ХАДМАЛ:

{chunk_context}
"""
        

        response_text = call_ai(
            client,
            provider,
            model,
            prompt,
            system_prompt=CHARACTER_ANALYSIS_PROMPT
        )

        result = extract_json(response_text)

        all_characters.extend(
            result.get("characters", [])
        )

        all_notes.extend(
            result.get("notes", [])
        )
    merged_characters = merge_characters(
        all_characters
    )

    print(
        f"\nНэгтгэсний дараах дүрийн тоо: "
        f"{len(merged_characters)}"
    )

    return {
        "characters": merged_characters,
        "notes": all_notes
    }

def unique_items(items):

    result = []
    seen = set()

    for item in items:

        if isinstance(item, (dict, list)):
            key = json.dumps(
                item,
                ensure_ascii=False,
                sort_keys=True
            )
        else:
            key = str(item)

        if key not in seen:
            seen.add(key)
            result.append(item)

    return result
def merge_characters(characters):

    merged = []
    def get_identifiers(character):

        names = character.get("names") or []

        return {
            name.strip().casefold()
            for name in names
            if isinstance(name, str) and name.strip()
        }
    

    for character in characters:

        identifiers = get_identifiers(character)

        match = None

        for existing in merged:

            existing_identifiers = get_identifiers(existing)
            same_name = bool(
                identifiers & existing_identifiers
            )

            existing_gender = existing.get("gender")
            current_gender = character.get("gender")

            gender_conflict = (
                existing_gender is not None
                and current_gender is not None
                and existing_gender != current_gender
            )

            if same_name and not gender_conflict:
                match = existing
                break
           

        if match is None:

            merged.append({
                "names": list(character.get("names") or []),
                "aliases": list(character.get("aliases") or []),
                "gender": character.get("gender"),
                "relationships": list(character.get("relationships") or []),
                "speech_style": list(character.get("speech_style") or []),
                "evidence": list(character.get("evidence") or []),
                "confidence": character.get("confidence", "low")
            })

            continue

        for field in [
            "names",
            "aliases",
            "relationships",
            "speech_style",
            "evidence"
        ]:
            combined = (
                match.get(field, [])
                + (character.get(field) or [])
            )

            match[field] = unique_items(combined)
            

        if match.get("gender") is None:
            match["gender"] = character.get("gender")

        confidence_order = {
            "low": 1,
            "medium": 2,
            "high": 3
        }

        if confidence_order.get(
            character.get("confidence"), 0
        ) > confidence_order.get(
            match.get("confidence"), 0
        ):
            match["confidence"] = character.get("confidence")

    return merged
# =====================================
# TRANSLATION
# =====================================

def translate_batch(
    client,
    provider,
    model,
    subtitles,
    full_context,
    language,
    characters,
    speaker_map
):

    target_text = []

    for sub in subtitles:

        speaker = speaker_map.get(sub.index, {})

        target_text.append({
            "index": sub.index,
            "text": sub.content,
            "speaker": {
                "id": speaker.get("speaker_id"),
                "name": speaker.get("canonical_name"),
                "type": speaker.get("speaker_type"),
                "confidence": speaker.get("confidence"),
                "gender": speaker.get("gender"),
                "speech_style": speaker.get("speech_style", [])
            }
        })

    language_name = {
        "en": "Англи хэл",
        "zh": "Хятад хэл"
    }[language]

    user_prompt = f"""
ЭХ ХЭЛ: {language_name}
ЗОРИЛТОТ ХЭЛ: Монгол хэл

КИНОНЫ НИЙТ ЯРИАНЫ КОНТЕКСТ:
Доорх бүх мөрийг киноны үйл явдал,
дүрүүдийн харилцаа, нэр томьёог ойлгоход ашигла.

{full_context}

ДҮРҮҮДИЙН МЭДЭЭЛЭЛ:
Доорх мэдээллийг дүрүүдийн нэр, харилцаа,
ярианы хэв маягийг ойлгоход ашигла.

{json.dumps(
    characters,
    ensure_ascii=False,
    indent=2
)}

ОДОО ОРЧУУЛАХ ХАДМАЛ:
Эдгээр мөрийг л орчуулна.
Бусад мөрийг орчуулгын хариунд оруулахгүй.

{json.dumps(
    target_text,
    ensure_ascii=False,
    indent=2
)}

ЯРИГЧИЙН МЭДЭЭЛЛИЙГ АШИГЛАХ ДҮРЭМ:

1. Одоо орчуулах мөр бүрийн speaker мэдээллийг анхаарч унш.
2. speaker.id болон speaker.name нь тухайн мөрийн яригчийг тодорхойлно.
3. speaker.type нь ярианы хэлбэрийг тодорхойлно:
   - inner_monologue: дүрийн дотоод бодол, өөртөө хэлж буй үг.
   - narrator: гаднын хүүрнэл.
   - character: дүрийн шууд яриа.
4. inner_monologue мөрийг бусдад хандаж ярьж байгаа мэт орчуулж болохгүй.
5. narrator мөрийг дүрийн шууд яриа мэт орчуулж болохгүй.
6. Дүрийн speech_style мэдээллийг тухайн дүрийн ярианы өнгө аясыг хадгалахад ашигла.
7. confidence нь low эсвэл medium бол дүрийн талаар нэмэлт таамаглал бүү хий.
8. Хүйс тодорхойгүй бол хүйсээр нь ялгасан хэллэгийг дур мэдэн бүү хэрэглэ.
9. Дүрийн хэв маягийг хэтрүүлж, эхэд байхгүй зан чанар, сэтгэл хөдлөл нэмж болохгүй.
10. speaker мэдээлэл байхгүй бол дүрийг таамаглаж болохгүй.

ОРЧУУЛГЫН ЗААВАР:
1. Киноны нийт контексттэй уялдуул.
2. Өмнөх болон дараах ярианы утгыг харгалз.
3. Монгол хүний амьд ярианы хэлээр найруул.
4. Дүрүүдийн харилцаа, сэтгэл хөдлөлийг хадгал.
5. Үгчилсэн орчуулгаас зайлсхий.
6. Index дугаарыг өөрчлөхгүй.
7. Аль ч мөрийг орхигдуулахгүй.
8. Нэг мөрийг дур мэдэн хувааж, нэгтгэж болохгүй.
9. Зөвхөн JSON буцаа.
"""

    raw_result = call_ai(
        client,
        provider,
        model,
        user_prompt
    )

    result = extract_json(raw_result)

    if "translations" not in result:
        raise ValueError(
            "AI хариултад translations талбар алга."
        )

    translations = result["translations"]

    expected_ids = {
        sub.index for sub in subtitles
    }

    received_ids = [
        item["index"] for item in translations
    ]

    if len(received_ids) != len(expected_ids):
        raise ValueError(
            "AI дутуу эсвэл давхар мөр буцаасан."
        )

    if set(received_ids) != expected_ids:
        raise ValueError(
            "AI хадмалын index дугаарыг өөрчилсөн."
        )

    translated_map = {}

    for item in translations:

        if not isinstance(item.get("text"), str):
            raise ValueError(
                "Орчуулгын текст буруу форматтай."
            )

        translated_map[item["index"]] = (
            item["text"].strip()
        )

    return translated_map


# =====================================
# MAIN TRANSLATOR
# =====================================

def translate_srt(input_file, language):

    load_dotenv()

    provider = os.getenv(
        "AI_PROVIDER",
        "gemini"
    ).strip().lower()

    if provider == "openai":

        api_key = os.getenv("OPENAI_API_KEY")

        model = os.getenv(
            "OPENAI_MODEL",
            "gpt-5.5"
        )

    elif provider == "gemini":

        api_key = os.getenv("GEMINI_API_KEY")

        model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        )

    else:
        raise ValueError(
            "AI_PROVIDER нь openai эсвэл gemini байх ёстой."
        )

    if not api_key:
        raise ValueError(
            f"{provider.upper()} API түлхүүр олдсонгүй."
        )

    print(f"\nProvider: {provider.upper()}")
    print(f"Model: {model}")

    client = create_ai_client(
        provider,
        api_key
    )

    subtitles = load_subtitles(input_file)

    total = len(subtitles)

    print(f"\nНийт хадмал: {total}")

        # Киноны бүх ярианы контекст
    full_context = build_full_context(subtitles)
        # Хадмал бүрийн яригчийн мэдээллийг ачаалах
    speaker_map = load_speaker_context(input_file)

    print(
        f"Яригчийн мэдээлэл ачаалагдлаа: "
        f"{len(speaker_map)} мөр"
    )

    # Дүрүүдийг автоматаар шинжлэх
    print("\nКиноны дүрүүдийг шинжилж байна...")

    characters = analyze_characters(
        client,
        provider,
        model,
        subtitles,
        language
    )

    print(
        f"Танигдсан дүрүүд: "
        f"{len(characters.get('characters', []))}"
    )
    # Нэгтгэсэн дүрийн мэдээллийг тусдаа JSON файлд хадгалах
    character_file = (
        Path(input_file).with_name(
            Path(input_file).stem + "_characters_merged.json"
        )
    )

    character_file.write_text(
        json.dumps(
            characters,
            ensure_ascii=False,
            indent=4
        ),
        encoding="utf-8"
    )
   

    print(f"Дүрийн мэдээлэл хадгалагдлаа: {character_file}")
    print("\n========== ТАНИГДСАН ДҮРҮҮД ==========")

    for number, character in enumerate(
        characters.get("characters", []),
        start=1
    ):

        names = ", ".join(
            character.get("names") or []
        )

        aliases = ", ".join(
            character.get("aliases") or []
        )

        print(f"{number}. {names}")

        if aliases:
            print(f"   Өөр нэр: {aliases}")

        print(
            f"   Хүйс: {character.get('gender')}"
        )

        print(
            f"   Итгэлцэл: {character.get('confidence')}"
        )

    print("======================================\n")    

    

    # Багц бүрээр орчуулах
    # Багц бүрээр орчуулах
    for start in range(0, min(total, 20), BATCH_SIZE):

        batch = subtitles[
            start:start + BATCH_SIZE
        ]

        print(
            f"\nОрчуулж байна: "
            f"{start + 1}–{start + len(batch)} / {total}"
        )

        translated = translate_batch(
            client,
            provider,
            model,
            batch,
            full_context,
            language,
            characters,
            speaker_map
        )

        # Зөвхөн текст солих
        # Цагийн код өөрчлөгдөхгүй
        for sub in batch:
            sub.content = translated[sub.index]

    output_file = (
        Path(input_file).with_name(
            Path(input_file).stem + "_mn.srt"
        )
    )

    save_subtitles(
        subtitles,
        output_file
    )

    print("\nОРЧУУЛГА ДУУСЛАА!")
    print(f"Гарах файл: {output_file}")


# =====================================
# APPLICATION
# =====================================

def main():

    print("=" * 40)
    print("       SRT TRANSLATOR V1")
    print("=" * 40)

    input_file = input(
        "\nSRT файлын зам: "
    ).strip().strip('"')

    print("\nЭх хэл сонго:")
    print("1. Англи")
    print("2. Хятад")

    choice = input(
        "Сонголт (1/2): "
    ).strip()

    if choice == "1":
        language = "en"

    elif choice == "2":
        language = "zh"

    else:
        print("Буруу сонголт.")
        return

    try:
        translate_srt(
            input_file,
            language
        )

    except Exception as error:
        print(f"\nАЛДАА: {error}")


if __name__ == "__main__":
    main()
