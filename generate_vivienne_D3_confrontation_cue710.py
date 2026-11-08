#!/usr/bin/env python3
"""Generate a single Vivienne D3 confrontation audition for verified cue 710.

Keeps the approved Vivienne voice/model and saved defaults. Reads the API key
from the local environment or .env; never prints or modifies secrets.
Existing output is reused to avoid duplicate TTS charges.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "acoustic_comparison_6_results_v2" / "vivienne_elevenlabs_auditions"
DEFAULT_VOICE_ID = "6Km4T9TrZXIhfMaxglHw"
MODEL_ID = "eleven_v3"
OUTPUT_FORMAT = "mp3_44100_128"
CUE_ID = 710
TEXT = "[angry] Одоо бүр надаас тайлбар нэхэж байна уу?"
OUT_FILE = OUT_DIR / "vivienne_D3_confrontation_cue710.mp3"
MANIFEST_FILE = OUT_DIR / "vivienne_D3_confrontation_cue710_manifest.json"


def load_env() -> None:
    path = ROOT / ".env"
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def api_request(api_key: str, url: str, method: str = "GET", body: bytes | None = None):
    headers = {"xi-api-key": api_key, "Accept": "application/json"}
    if body is not None:
        headers.update({"Content-Type": "application/json", "Accept": "audio/mpeg"})
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return response.read(), response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        detail = exc.read(2500).decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs HTTP {exc.code}: {detail}") from exc


def main() -> int:
    load_env()
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID).strip()
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY missing. No request sent.")
        return 2

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if OUT_FILE.is_file():
        print(f"SKIP: {OUT_FILE.name} already exists ({OUT_FILE.stat().st_size:,} bytes).")
        return 0

    voice_url = "https://api.elevenlabs.io/v1/voices/" + urllib.parse.quote(voice_id, safe="")
    try:
        voice_bytes, _ = api_request(api_key, voice_url)
        voice = json.loads(voice_bytes.decode("utf-8"))
    except Exception as exc:
        print(f"VOICE CHECK FAILED: {exc}")
        print("No TTS request was sent.")
        return 1

    print("Vivienne D3 confrontation audition")
    print(f"Voice: {voice.get('name', 'Vivienne')} ({voice_id})")
    print(f"Model: {MODEL_ID}")
    print("One TTS request will be made; it may consume account credits.")
    payload = json.dumps({"text": TEXT, "model_id": MODEL_ID}, ensure_ascii=False).encode("utf-8")
    url = (
        "https://api.elevenlabs.io/v1/text-to-speech/"
        + urllib.parse.quote(voice_id, safe="")
        + "?"
        + urllib.parse.urlencode({"output_format": OUTPUT_FORMAT})
    )
    try:
        audio, content_type = api_request(api_key, url, "POST", payload)
    except Exception as exc:
        print(f"TTS FAILED: {exc}")
        return 1

    if not content_type.startswith("audio/") or len(audio) < 1000:
        print(f"ERROR: Unexpected response ({content_type}, {len(audio)} bytes).")
        return 1

    OUT_FILE.write_bytes(audio)
    manifest = {
        "file": OUT_FILE.name,
        "cue_id": CUE_ID,
        "start_end": "00:22:34.800–00:22:36.791",
        "speaker_id": "C001",
        "speaker_name": "Vivienne",
        "speaker_role": "character",
        "text": TEXT,
        "voice_id": voice_id,
        "model_id": MODEL_ID,
        "voice_settings": "Same saved defaults as accepted D3; no numerical settings overridden.",
        "direction": "Clearly angry and confrontational, with controlled feminine timbre and intelligible articulation; no shouting, harshness, or loss of Vivienne identity.",
        "bytes": len(audio),
    }
    MANIFEST_FILE.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"SUCCESS: Saved {OUT_FILE.name} ({len(audio):,} bytes)")
    print(f"Manifest: {MANIFEST_FILE}")
    print("Do not commit .env or API keys.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
