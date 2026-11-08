#!/usr/bin/env python3
"""Generate one softer, more restrained Vivienne angry-dialogue comparison.

Uses the same ElevenLabs voice and model as the accepted baseline. Makes one
TTS request after checking voice access. Reads the API key from the process
environment or local .env; never prints or modifies secrets.
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
OUTPUT_FILE = OUTPUT_DIR / "vivienne_D2_soft_feminine_angry.mp3"
MANIFEST_FILE = OUTPUT_DIR / "vivienne_D2_soft_feminine_angry_manifest.json"
DEFAULT_VOICE_ID = "6Km4T9TrZXIhfMaxglHw"
MODEL_ID = "eleven_v3"
OUTPUT_FORMAT = "mp3_44100_128"
TEXT = "[frustrated] Новшийн амьтан!"


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
        return 2

    if OUTPUT_FILE.exists():
        print(f"SKIP: {OUTPUT_FILE.name} already exists ({OUTPUT_FILE.stat().st_size:,} bytes).")
        print("Move or rename that file locally only if you intentionally want to regenerate it.")
        return 0

    voice_url = f"https://api.elevenlabs.io/v1/voices/{urllib.parse.quote(voice_id, safe='')}"
    try:
        voice_bytes, _ = api_request(api_key, voice_url)
        voice_info = json.loads(voice_bytes.decode("utf-8"))
    except Exception as exc:
        print(f"VOICE CHECK FAILED: {exc}")
        print("No text-to-speech request was sent.")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    query = urllib.parse.urlencode({"output_format": OUTPUT_FORMAT})
    tts_url = (
        f"https://api.elevenlabs.io/v1/text-to-speech/"
        f"{urllib.parse.quote(voice_id, safe='')}?{query}"
    )
    payload = json.dumps({"text": TEXT, "model_id": MODEL_ID}, ensure_ascii=False).encode("utf-8")

    print("Vivienne softer angry-dialogue audition")
    print(f"Voice: {voice_info.get('name', '(name unavailable)')} ({voice_id})")
    print(f"Model: {MODEL_ID}")
    print("Direction: controlled frustration; softer attack, less harshness, no shouting.")
    print("One TTS API request will be made and may consume account credits.")
    try:
        audio, content_type = api_request(api_key, tts_url, method="POST", payload=payload)
    except Exception as exc:
        print(f"GENERATION FAILED: {exc}")
        return 1

    if not content_type.startswith("audio/") or len(audio) < 1000:
        print(f"ERROR: Unexpected audio response ({content_type}, {len(audio)} bytes).")
        return 1

    OUTPUT_FILE.write_bytes(audio)
    manifest = {
        "voice_id": voice_id,
        "voice_name": voice_info.get("name"),
        "model_id": MODEL_ID,
        "output_format": OUTPUT_FORMAT,
        "voice_settings": "Same saved voice defaults as the original D audition.",
        "text": TEXT,
        "purpose": "Softer, more feminine-sounding and restrained angry delivery; frustration rather than explosive anger.",
        "bytes": len(audio),
        "file": OUTPUT_FILE.name,
    }
    MANIFEST_FILE.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"SUCCESS: Saved {OUTPUT_FILE.name} ({len(audio):,} bytes)")
    print(f"Manifest: {MANIFEST_FILE}")
    print("Do not commit .env or any API key. Compare this clip with the original D clip by listening.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
