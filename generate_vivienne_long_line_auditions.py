#!/usr/bin/env python3
"""Generate longer-line Vivienne auditions for consistency and Mongolian delivery QA.

Uses the accepted Vivienne voice ID, Eleven v3, and saved voice defaults.
Reads ELEVENLABS_API_KEY from the environment or local .env; never prints or
modifies secrets. Existing output files are reused to avoid duplicate charges.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "acoustic_comparison_6_results_v2" / "vivienne_elevenlabs_auditions"
DEFAULT_VOICE_ID = "6Km4T9TrZXIhfMaxglHw"
MODEL_ID = "eleven_v3"
OUTPUT_FORMAT = "mp3_44100_128"

AUDITIONS = [
    {
        "name": "long_A_neutral_narration_cue153",
        "cue_id": 153,
        "role": "narrator",
        "text": "Тэр гараа өвдгөн дээрээ зөрүүлэн тавьж, огт хөдөлгөөнгүй суусаар байв.",
        "direction": "Neutral conversational narration; calm, clear, natural pace; no added sadness or theatrical emphasis.",
    },
    {
        "name": "long_B_reflective_narration_cue502",
        "cue_id": 502,
        "role": "narrator",
        "text": "[reflective] Бид үгээ гүйцээж амжаагүй байхад ээж гэрээнүүдийг гаргаж ирсэн байлаа.",
        "direction": "Reflective narration; thoughtful and measured, but not artificially slow; same recognizable voice as neutral.",
    },
    {
        "name": "long_C_quiet_inner_monologue_cue293",
        "cue_id": 293,
        "role": "inner_monologue",
        "text": "[sad] Эсвэл би тодорхой зааж хэлж чадахаар ямар нэгэн зүйл хийгээгүй.",
        "direction": "Quiet, vulnerable inner monologue; contained emotion, softer vocal force, subtle breathiness; not whispered.",
    },
    {
        "name": "long_D2_soft_angry_dialogue_cue736",
        "cue_id": 736,
        "role": "character",
        "text": "[frustrated] Чиний надад өгөхөөр шийдсэн юуг ч хамаагүй хүлээн авах ёстой байсан уу?",
        "direction": "Feminine controlled frustration; softer attack, firm intention and clear articulation; no harshness or shouting.",
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
        detail = exc.read(3000).decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc


def main() -> int:
    load_env_file(ROOT / ".env")
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID).strip()
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY was not found in environment or project .env")
        print("The script does not create, print, or modify API keys.")
        return 2

    voice_url = f"https://api.elevenlabs.io/v1/voices/{urllib.parse.quote(voice_id, safe='')}"
    try:
        voice_bytes, _ = api_request(api_key, voice_url)
        voice_info = json.loads(voice_bytes.decode("utf-8"))
    except Exception as exc:
        print(f"VOICE CHECK FAILED: {exc}")
        print("No text-to-speech requests were sent.")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = OUTPUT_DIR / "vivienne_long_line_auditions_manifest.json"
    manifest = {
        "voice_id": voice_id,
        "voice_name": voice_info.get("name"),
        "model_id": MODEL_ID,
        "output_format": OUTPUT_FORMAT,
        "voice_settings": "Omitted; same saved voice defaults as accepted A/B/C/D2 auditions.",
        "clips": [],
    }

    print("Vivienne longer-line consistency audition")
    print(f"Voice: {voice_info.get('name', '(name unavailable)')} ({voice_id})")
    print(f"Model: {MODEL_ID}")
    print(f"Output: {OUTPUT_DIR}")
    print("Up to four TTS requests will be made; existing clips are reused.")

    for index, item in enumerate(AUDITIONS, 1):
        output_path = OUTPUT_DIR / f"vivienne_{item['name']}.mp3"
        record = {
            "file": output_path.name,
            "cue_id": item["cue_id"],
            "speaker_role": item["role"],
            "text": item["text"],
            "direction": item["direction"],
        }
        if output_path.exists():
            record.update({"bytes": output_path.stat().st_size, "status": "reused_existing_file"})
            print(f"SKIP {index}/4: {output_path.name} already exists ({output_path.stat().st_size:,} bytes)")
            manifest["clips"].append(record)
            continue

        print(f"\nGenerating {index}/4: {item['name']} (cue {item['cue_id']})")
        payload = json.dumps(
            {"text": item["text"], "model_id": MODEL_ID},
            ensure_ascii=False,
        ).encode("utf-8")
        query = urllib.parse.urlencode({"output_format": OUTPUT_FORMAT})
        tts_url = (
            "https://api.elevenlabs.io/v1/text-to-speech/"
            f"{urllib.parse.quote(voice_id, safe='')}?{query}"
        )
        try:
            audio, content_type = api_request(api_key, tts_url, method="POST", payload=payload)
        except Exception as exc:
            print(f"GENERATION FAILED: {exc}")
            print("Stopped to avoid repeated requests and unexpected credit use.")
            return 1

        if not content_type.startswith("audio/") or len(audio) < 1000:
            print(f"ERROR: Unexpected audio response ({content_type}, {len(audio)} bytes).")
            return 1

        output_path.write_bytes(audio)
        record.update({"bytes": len(audio), "status": "generated"})
        manifest["clips"].append(record)
        print(f"Saved: {output_path.name} ({len(audio):,} bytes)")

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nManifest: {manifest_path}")
    print("Do not commit .env or any API key.")
    print("Listen to all four clips for natural Mongolian pronunciation, phrasing, and consistent Vivienne identity.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
