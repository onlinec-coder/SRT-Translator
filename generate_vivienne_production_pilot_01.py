#!/usr/bin/env python3
"""Generate the approved six-clip Vivienne production pilot.

Repository scope: onlinec-coder/SRT-Translator only.
Uses the already accepted Vivienne voice ID and Eleven v3 model.
Does not override any numerical voice settings, speed, stability, similarity,
style, or pitch. Reads the API key from the environment or local .env.
Existing clips are reused; the script stops on the first failed TTS request.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "acoustic_comparison_6_results_v2" / "vivienne_production_pilot_01"
VOICE_ID = "6Km4T9TrZXIhfMaxglHw"
MODEL_ID = "eleven_v3"
OUTPUT_FORMAT = "mp3_44100_128"

# Text is joined only where the original verified cues form one continuous
# sentence/thought. All wording is copied from Husbands_mn_v3.srt.
CLIPS = [
    {
        "file": "pilot_01_cue427_hurt_disappointed.mp3",
        "cue_ids": [427],
        "time": "00:13:19.166–00:13:20.583",
        "target_ms": 1417,
        "role": "direct_dialogue",
        "tagged_text": "[whispers] Тэр чамайг огт мэддэггүй юм байна.",
        "plain_text": "Тэр чамайг огт мэддэггүй юм байна.",
        "direction": (
            "Hurt and broken trust with slight disgust; lowered, close to a whisper "
            "but still clearly articulated. Do not turn it into anger."
        ),
    },
    {
        "file": "pilot_02_cues430-434_hurt_realization.mp3",
        "cue_ids": [430, 431, 432, 433, 434],
        "time": "00:13:24.600–00:13:30.000",
        "target_ms": 5400,
        "role": "direct_dialogue",
        "tagged_text": (
            "[whispers] Тэр ерөөсөө мэддэггүй байсан юм. "
            "Тэгэхээр энэ олон жилийн турш, баяр ёслол бүрээр, "
            "сүргийн найр бүрээр тэр надтай уулзахаар ирдэггүй байжээ."
        ),
        "plain_text": (
            "Тэр ерөөсөө мэддэггүй байсан юм. "
            "Тэгэхээр энэ олон жилийн турш, баяр ёслол бүрээр, "
            "сүргийн найр бүрээр тэр надтай уулзахаар ирдэггүй байжээ."
        ),
        "direction": (
            "Continue the same hurt, loss of trust, and slight disgust as cue 427. "
            "Low, intimate, near-whisper delivery, but keep words intelligible. "
            "Treat all five cues as one connected thought; do not insert artificial "
            "pauses at the subtitle boundaries."
        ),
    },
    {
        "file": "pilot_03_cues776-778_assertive_explanation.mp3",
        "cue_ids": [776, 777, 778],
        "time": "00:24:36.791–00:24:42.125",
        "target_ms": 5334,
        "role": "direct_dialogue",
        "tagged_text": (
            "Хоёр хоногийн өмнө энэ гэрт ирсэн эмэгтэй би биш. "
            "Тэр үед би Колдвеллийн харшид оройн хоол идэж байсан. "
            "Ахлах ахлагч Лорант эхнэрийнхээ хамт байсан юм."
        ),
        "plain_text": (
            "Хоёр хоногийн өмнө энэ гэрт ирсэн эмэгтэй би биш. "
            "Тэр үед би Колдвеллийн харшид оройн хоол идэж байсан. "
            "Ахлах ахлагч Лорант эхнэрийнхээ хамт байсан юм."
        ),
        "direction": (
            "Calm, self-confident, evidence-led explanation. Clear factual articulation "
            "and contrastive emphasis only where meaning requires it. No anger, sarcasm, "
            "or theatrical force."
        ),
    },
    {
        "file": "pilot_04_cue758_firm_correction.mp3",
        "cue_ids": [758],
        "time": "00:23:55.800–00:23:56.958",
        "target_ms": 1158,
        "role": "direct_dialogue",
        "tagged_text": "Та хүнээ андуурчээ.",
        "plain_text": "Та хүнээ андуурчээ.",
        "direction": (
            "Calm and self-confident correction, firm resolve with slight displeasure. "
            "Not angry and not sarcastic."
        ),
    },
    {
        "file": "pilot_05_cue963_disgusted_refusal.mp3",
        "cue_ids": [963],
        "time": "00:30:08.800–00:30:09.791",
        "target_ms": 991,
        "role": "direct_dialogue",
        "tagged_text": "[disgusted] Ингэж болохгүй.",
        "plain_text": "Ингэж болохгүй.",
        "direction": (
            "Disgust with slight controlled anger; decisive refusal. Keep the voice "
            "feminine and controlled. No shouting or harsh aggression."
        ),
    },
    {
        "file": "pilot_06_cues1203-1205_natural_resolution.mp3",
        "cue_ids": [1203, 1204, 1205],
        "time": "00:37:24.541–00:37:27.583",
        "target_ms": 3042,
        "role": "direct_dialogue",
        "tagged_text": (
            "Тохирлоо. Гэхдээ энэ удаа бид хоёулаа аз жаргалтай болно."
        ),
        "plain_text": (
            "Тохирлоо. Гэхдээ энэ удаа бид хоёулаа аз жаргалтай болно."
        ),
        "direction": (
            "Ordinary, natural Vivienne voice. Calm and sincere; do not add conspicuous "
            "joy, heightened hope, uncertainty, or theatrical happiness."
        ),
    },
]


def load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


def api_request(api_key: str, url: str, method: str = "GET", payload: bytes | None = None):
    headers = {"xi-api-key": api_key, "Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "audio/mpeg"
    request = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return response.read(), response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        detail = exc.read(2500).decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc


def main() -> int:
    load_env_file(ROOT / ".env")
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    configured_voice = os.environ.get("ELEVENLABS_VOICE_ID", "").strip()

    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY missing. No request sent.")
        return 2
    if configured_voice and configured_voice != VOICE_ID:
        print("ERROR: ELEVENLABS_VOICE_ID does not match the approved Vivienne voice.")
        print("No request sent. The script will not silently use a different voice.")
        return 2

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT_DIR / "vivienne_production_pilot_01_manifest.json"

    voice_url = "https://api.elevenlabs.io/v1/voices/" + urllib.parse.quote(VOICE_ID, safe="")
    try:
        voice_bytes, _ = api_request(api_key, voice_url)
        voice_info = json.loads(voice_bytes.decode("utf-8"))
    except Exception as exc:
        print(f"VOICE ACCESS CHECK FAILED: {exc}")
        print("No TTS requests were sent.")
        return 1

    existing = sum((OUT_DIR / item["file"]).is_file() for item in CLIPS)
    pending = len(CLIPS) - existing
    print("Vivienne — six-clip production pilot")
    print(f"Voice: {voice_info.get('name', 'Vivienne')} ({VOICE_ID})")
    print(f"Model: {MODEL_ID}")
    print("Numerical voice settings: unchanged / omitted")
    print(f"New TTS requests remaining: {pending} (maximum 6)")
    print(f"Output directory: {OUT_DIR}")

    manifest = {
        "project": "Husbands",
        "pilot": "Vivienne production pilot 01",
        "voice_id": VOICE_ID,
        "voice_name": voice_info.get("name"),
        "model_id": MODEL_ID,
        "output_format": OUTPUT_FORMAT,
        "voice_settings": "Not supplied; use the existing saved voice defaults.",
        "speed_pitch_stability_similarity_style": "No overrides.",
        "clips": [],
    }

    for index, item in enumerate(CLIPS, 1):
        output_path = OUT_DIR / item["file"]
        record = {
            "file": item["file"],
            "cue_ids": item["cue_ids"],
            "source_time": item["time"],
            "target_subtitle_window_ms": item["target_ms"],
            "speaker_id": "C001",
            "speaker_name": "Vivienne",
            "speaker_role": item["role"],
            "text_sent_to_tts": item["tagged_text"],
            "subtitle_text_without_delivery_tags": item["plain_text"],
            "delivery_direction": item["direction"],
        }

        if output_path.is_file():
            record.update({
                "status": "reused_existing_file",
                "bytes": output_path.stat().st_size,
            })
            print(f"SKIP {index}/6: {output_path.name} already exists.")
            manifest["clips"].append(record)
            continue

        print(f"Generating {index}/6: cues {','.join(map(str, item['cue_ids']))}")
        body = json.dumps(
            {"text": item["tagged_text"], "model_id": MODEL_ID},
            ensure_ascii=False,
        ).encode("utf-8")
        query = urllib.parse.urlencode({"output_format": OUTPUT_FORMAT})
        tts_url = (
            "https://api.elevenlabs.io/v1/text-to-speech/"
            + urllib.parse.quote(VOICE_ID, safe="")
            + "?"
            + query
        )
        try:
            audio, content_type = api_request(api_key, tts_url, "POST", body)
        except Exception as exc:
            print(f"TTS FAILED on clip {index}/6: {exc}")
            print("Stopped immediately; no further credits will be used by this run.")
            return 1

        if not content_type.startswith("audio/") or len(audio) < 1000:
            print(f"ERROR: Unexpected response ({content_type}, {len(audio)} bytes).")
            print("Stopped; no further TTS requests will be sent.")
            return 1

        output_path.write_bytes(audio)
        record.update({"status": "generated", "bytes": len(audio)})
        manifest["clips"].append(record)
        print(f"Saved {output_path.name} ({len(audio):,} bytes)")

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    generated = sum(c["status"] == "generated" for c in manifest["clips"])
    reused = sum(c["status"] == "reused_existing_file" for c in manifest["clips"])
    print(f"COMPLETE: {generated} generated, {reused} reused.")
    print(f"Manifest: {manifest_path}")
    print("Keep .env and API keys private; do not commit them.")
    print("Listen to each clip against its original film passage before accepting.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
