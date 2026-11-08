#!/usr/bin/env python3
"""Generate a single stronger-but-controlled Vivienne anger comparison clip.

Uses the already accepted voice ID and Eleven v3. Reads the API key from the
environment or local .env without printing or modifying it. Existing output
is reused to avoid duplicate TTS charges.
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
VOICE_ID_DEFAULT = "6Km4T9TrZXIhfMaxglHw"
MODEL_ID = "eleven_v3"
CUE_ID = 736
TEXT = "[angry] Чиний надад өгөхөөр шийдсэн юуг ч хамаагүй хүлээн авах ёстой байсан уу?"
OUT_FILE = OUT_DIR / "vivienne_D3_controlled_angry_cue736.mp3"


def load_env() -> None:
    path = ROOT / ".env"
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        if key.strip() and key.strip() not in os.environ:
            os.environ[key.strip()] = value


def request(api_key: str, url: str, method: str = "GET", body: bytes | None = None):
    headers = {"xi-api-key": api_key, "Accept": "application/json"}
    if body is not None:
        headers.update({"Content-Type": "application/json", "Accept": "audio/mpeg"})
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return response.read(), response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        detail = exc.read(2500).decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs HTTP {exc.code}: {detail}") from exc


def main() -> int:
    load_env()
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", VOICE_ID_DEFAULT).strip()
    if not key:
        print("ERROR: ELEVENLABS_API_KEY missing. No request sent.")
        return 2
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if OUT_FILE.exists():
        print(f"SKIP: {OUT_FILE.name} already exists ({OUT_FILE.stat().st_size:,} bytes).")
        return 0

    voice_url = "https://api.elevenlabs.io/v1/voices/" + urllib.parse.quote(voice_id, safe="")
    try:
        voice_data, _ = request(key, voice_url)
        voice = json.loads(voice_data.decode("utf-8"))
    except Exception as exc:
        print(f"VOICE CHECK FAILED: {exc}")
        print("No TTS request was sent.")
        return 1

    print("Vivienne D3 controlled-angry comparison")
    print(f"Voice: {voice.get('name', 'Vivienne')} ({voice_id})")
    print(f"Model: {MODEL_ID}")
    print("One TTS request will be made; it may consume account credits.")
    payload = json.dumps({"text": TEXT, "model_id": MODEL_ID}, ensure_ascii=False).encode("utf-8")
    url = (
        "https://api.elevenlabs.io/v1/text-to-speech/"
        + urllib.parse.quote(voice_id, safe="")
        + "?"
        + urllib.parse.urlencode({"output_format": "mp3_44100_128"})
    )
    try:
        audio, content_type = request(key, url, "POST", payload)
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
        "speaker_id": "C001",
        "speaker_name": "Vivienne",
        "speaker_role": "character",
        "text": TEXT,
        "voice_id": voice_id,
        "model_id": MODEL_ID,
        "voice_settings": "Same saved defaults as accepted D2; no numerical settings overridden.",
        "direction": "Stronger anger than D2, but keep feminine timbre, controlled delivery, intelligibility; no shouting, harshness, or loss of identity.",
        "bytes": len(audio),
    }
    manifest_path = OUT_DIR / "vivienne_D3_controlled_angry_cue736_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"SUCCESS: Saved {OUT_FILE.name} ({len(audio):,} bytes)")
    print(f"Manifest: {manifest_path}")
    print("Do not commit .env or API keys.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
