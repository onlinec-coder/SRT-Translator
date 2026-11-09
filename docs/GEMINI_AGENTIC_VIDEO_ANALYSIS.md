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

## V3 — Chunked audiovisual analysis for dubbing

V3 нь урт бичлэгийг жижиг хэсгүүдэд хувааж, хэсэг бүрийг тусдаа Agentic Video хүсэлтээр шинжилнэ. Ингэснээр нэг 10 минутын хүсэлтэд ердөө 1–2 utterance буцаах зэрэг хэт товч хариуны эрсдэлийг бууруулна.

### V3-ийн шинэ өгөгдөл

- Бүх сонсогдох яриаг utterance бүрээр тусад нь бүртгэхийг шаардсан.
- Emotion: primary/secondary, intensity 1–5, confidence.
- Vocal delivery: mode, volume, pace, texture, sigh/sob/laugh/gasp зэрэг voice action.
- Lip-sync: status, visual evidence, confidence.
- Visual context: scene, visible people, action, shot context.
- Dubbing direction: target emotion, intensity, pitch direction, pace, volume, texture, breath/pause notes.
- Pause before/after, non-speech audio events.
- Дүрийн каталогийн canonical name, aliases, character ID-г боломжтой үед ашиглана.
- Хэсэг бүрийн utterance тоо болон хоосон хэсгийн warning-ийг quality_checks-д хадгална.

Narration болон Vivienne-ийн inner monologue нь Husbands-ийн dubbing-д нэг Vivienne voice identity (C001) хэвээр. Харин speech_role ялгаатай байна. Тодорхой бус дүрийг хүчээр оноохгүй.

### V3 туршилт — эхний 10 минут

Төслийн root хавтсанд:

    git pull
    python -m py_compile scripts/movie_agentic_analysis.py

Дараа нь 60 секундийн хэсгүүдээр 10 минутыг турш:

    python scripts/movie_agentic_analysis.py "C:\Users\chinzorig\Desktop\Husbands\Husbands.mp4" --start 0 --duration 600 --chunk-duration 60 --model "gemini-3.5-flash-lite" --output "movie_analysis_reports/Husbands_test_10min_v3.json"

Энэ нь 10 тусдаа chunk хүсэлт үүсгэнэ. Chunk бүрийн upload, Gemini file processing, Agentic Analysis, үр дүнгийн тоо болон cleanup явцыг console дээр харуулна. Хүсэлт бүрийн timestamp-ийг эх киноны абсолют секунд рүү шилжүүлж нэг JSON тайланд нэгтгэнэ.

### Chunk хэмжээ өөрчлөх

- Default: 60 секунд.
- --chunk-duration 90: 90 секундийн хэсэг.
- --chunk-duration 120: 2 минутын хэсэг.
- --chunk-duration 0: нэг бүхэл хүсэлт (V2 шиг нэг хүсэлтээр боловсруулах; бүрэн transcript-ийн эрсдэл өндөр).

Хэсэг тус бүр тусдаа Gemini хүсэлт тул API usage болон processing хугацаа нэмэгдэнэ. 10 минутын туршилтын чанарыг шалгахаас өмнө бүтэн киног ажиллуулахгүй.

### Чухал хамгаалалт

- V3 зөвхөн тусдаа JSON тайлан үүсгэнэ.
- SRT, character catalog, 1,213 гар шалгасан speaker assignments, review exports-д өөрчлөлт оруулахгүй.
- Chunk бүрийн speaker ID-г автоматаар нэгтгэхдээ зөвхөн баттай character_id таарсан тохиолдолд нэг voice identity гэж үзнэ. Тодорхойгүй speaker-үүдийг хүчээр нэгтгэхгүй.
- quality_checks.warnings болон unresolved_questions-ийг заавал шалгана.
- AI-ийн emotion болон dubbing direction нь санал болгосон шинжилгээ; хүнээр сонсож баталгаажуулсны дараа л production dubbing-д ашиглана.
