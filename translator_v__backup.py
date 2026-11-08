
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
    user_prompt
):

    max_retries = 5

    for attempt in range(max_retries):

        try:

            if provider == "openai":

                response = client.responses.create(
                    model=model,
                    instructions=SYSTEM_PROMPT,
                    input=user_prompt
                )

                return response.output_text

            elif provider == "gemini":

                from google.genai import types

                response = client.models.generate_content(
                    model=model,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
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


# =====================================
# TRANSLATION
# =====================================

def translate_batch(
    client,
    provider,
    model,
    subtitles,
    full_context,
    language
):

    target_text = [
        {
            "index": sub.index,
            "text": sub.content
        }
        for sub in subtitles
    ]

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

ОДОО ОРЧУУЛАХ ХАДМАЛ:
Эдгээр мөрийг л орчуулна.
Бусад мөрийг орчуулгын хариунд оруулахгүй.

{json.dumps(
    target_text,
    ensure_ascii=False,
    indent=2
)}

ОРЧУУЛГЫН ЗААВАР:
1. Киноны нийт контексттэй уялдуул.
2. Өмнөх болон дараах ярианы утгыг харгалз.
3. Монгол хүний амьд ярианы хэлээр найруул.
4. Дүрүүдийн харилцаа, сэтгэл хөдлөлийг хадгал.
5. Үгчилсэн орчуулгаас зайлсхий.
6. Index дугаарыг өөрчлөхгүй.
7. Аль ч мөрийг орхигдуулахгүй.
8. Зөвхөн JSON буцаа.
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

    # Багц бүрээр орчуулах
    for start in range(0, total, BATCH_SIZE):

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
            language
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
