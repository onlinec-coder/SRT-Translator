# Gemini Agentic Video Analysis

Энэ хэрэгсэл нь SRT-Translator төслөөс тусдаа, зөвхөн унших зориулалттай видео шинжилгээний workflow юм. Одоо байгаа SRT, дүрийн жагсаалт, speaker assignments, review export файлуудыг өөрчлөхгүй.

## Шаардлага

- google-genai
- python-dotenv (заавал биш, .env уншихад)
- ffmpeg (зөвхөн видеоны хэсэг таслан тест хийхэд)

PowerShell дээр төслийн virtual environment идэвхтэй үед:

    python -m pip install -U google-genai python-dotenv

## API key болон model

Төслийн үндсэн .env файлд API key-гээ хадгална:

    GEMINI_API_KEY=your_key_here
    GEMINI_MODEL=gemini-3.5-flash-lite
    GEMINI_VIDEO_MODEL=gemini-3.8-flash

GEMINI_VIDEO_MODEL тохируулсан бол тэр нь нэн түрүүнд хэрэглэгдэнэ. Дараа нь GEMINI_MODEL, эцэст нь gemini-3.8-flash default болно. API key-г GitHub-д хэзээ ч commit хийж болохгүй.

## Эхний тест: эхний 10 минут

Төслийн root хавтсаас ажиллуул:

    python scripts/movie_agentic_analysis.py "Husbands.mp4" --start 0 --duration 600 --output "movie_analysis_reports/Husbands_test_10min.json"

Энэ үед ffmpeg түр MP4 хэсэг үүсгэнэ. Gemini Files API-д upload хийгээд Agentic горимоор шинжилнэ. Ажил дуусмагц түр local файл болон Gemini upload-ийг устгана. JSON тайлан үлдэнэ.

## Бүтэн кино

Тестийн тайланг шалгасны дараа:

    python scripts/movie_agentic_analysis.py "Husbands.mp4" --output "movie_analysis_reports/Husbands_full.json"

Тайлангийн файл өмнө нь байвал скрипт санамсаргүй overwrite хийхээс хамгаалж зогсоно. Зориудаар солих бол --overwrite нэмнэ.

## Түгээмэл сонголтууд

- --start: хэсгийн эхлэх секунд.
- --duration: хэсгийн урт секундээр.
- --model: Gemini model-ийг command line-аас заах.
- --output: JSON тайлангийн зам.
- --overwrite: өмнөх тайланг зориудаар солих.
- --keep-upload: Gemini-д upload хийсэн файлыг хадгалах.

Тусламж:

    python scripts/movie_agentic_analysis.py --help

## Тайланд юу гарах вэ?

- Scene болон кадрт харагдаж буй хүмүүсийн ажиглалт
- Дуу хоолойн тогтвортой шинж: pitch, timbre, resonance, texture, cadence, accent
- Яриа бүрийн transcript болон utterance-level цаг
- Emotion болон тухайн мөчийн vocal delivery
- Speaker ID болон дүрстэй холбосон нотолгоо
- Lip-sync-ийн төлөв, итгэлцлийн түвшин, тодорхойгүй зүйлс
- Давтагдсан дуу хоолойн continuity ажиглалт
- Монгол дубляж/локализацийн анхаарах зүйлс

Дүрс дээр хүн гарч ирсэн төдийд тухайн хүнийг ярьж байна гэж үзэхгүй. Lip-sync-ийг зөвхөн амны хөдөлгөөн яриатай бодитоор синхрон харагдсан үед confirmed гэж тэмдэглэх ёстой. Дуу хоолойн тогтвортой шинжийг тухайн үеийн сэтгэл хөдлөл, чанга/сул ярианаас салгаж үзнэ.

Скрипт үгийн түвшний timestamp зохиохгүй. Боломжгүй бол utterance-level цаг ашиглана. Гарсан тайланг хүн шалгаж баталгаажуулсны дараа л downstream speaker assignment-д ашиглана.

## Өгөгдлийн хамгаалалт

- Тайлан movie_analysis_reports/ дотор тусдаа JSON файл болно.
- SRT, character JSON, speaker assignments болон review export-д автоматаар нэгтгэхгүй.
- API key-г хэвлэхгүй, тайланд бичихгүй.
- Gemini upload-ийг default байдлаар ажил дуусахад устгана.
- Алдаа гарсан эсвэл JSON буруу бүтэцтэй бол partial report хадгалахгүй.
