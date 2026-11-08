#!/usr/bin/env python3
"""Generate four controlled Vivienne ElevenLabs v3 audition clips.

Uses only Python standard-library modules. Reads ELEVENLABS_API_KEY from the
process environment or a local .env file in the project root. Never prints the
API key and never modifies .env.
"""
from __future__ import annotations

import json
import os
import sys
import time
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
        "name": "A_neutral_narration",
        "text": "Тэр хүчээр инээмсэглэв.",
        "purpose": "Neutral narration baseline",
    },
    {
        "name": "B_reflective_narration",
        "text": "[reflective] Түүний хоолой огт чичирсэнгүй.",
        "purpose": "Reflective narration; retain the project's existing tag",
    },
    {
        "name": "C_quiet_inner_monologue",
        "text": "[sad] Би юм хэлэхийг оролдсон ч амнаас минь ганц ч үг гарсангүй.",
        "purpose": "Restrained vulnerable inner monologue; no whisper tag",
    },
    {
        "name": "D_angry_dialogue",
        "text": "[angry] Новшийн амьтан!",
        "purpose": "Firm angry direct dialogue; avoid adding shout tag",
    },
]


def load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE lines without overwriting existing env vars."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


def verify_voice(api_key: str, voice_id: str) -> str:
    url = f"https://api.elevenlabs.io/v1/voices/{urllib.parse.quote(voice_id, safe='')}"
    request = urllib.request.Request(
        url,
        headers={"xi-api-key": api_key, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("name", "(name unavailable)")
    except urllib.error.HTTPError as exc:
        detail = exc.read(3000).decode("utf-8", errors="replace")
        if exc.code == 404:
            raise RuntimeError(
                f"Voice ID '{voice_id}' is not accessible to this API key. "
                "Run list_elevenlabs_voices.py and set ELEVENLABS_VOICE_ID in .env."
            ) from exc
        raise RuntimeError(f"ElevenLabs voice check HTTP {exc.code}: {detail}") from exc


def request_audio(api_key: str, voice_id: str, text: str) -> bytes:
    query = urllib.parse.urlencode({"output_format": OUTPUT_FORMAT})
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{urllib.parse.quote(voice_id, safe='')}?{query}"
    payload = json.dumps(
        {"text": text, "model_id": MODEL_ID},
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            audio = response.read()
            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("audio/"):
                raise RuntimeError(
                    f"Unexpected response type: {content_type}. "
                    f"Response: {audio[:1000].decode('utf-8', errors='replace')}"
                )
            return audio
    except urllib.error.HTTPError as exc:
        detail = exc.read(4000).decode("utf-8", errors="replace")
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

    try:
        voice_name = verify_voice(api_key, voice_id)
    except Exception as exc:
        print(f"VOICE CHECK FAILED: {exc}")
        print("No text-to-speech requests were sent; no generation credits should be consumed.")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "voice_id": voice_id,
        "voice_name": voice_name,
        "model_id": MODEL_ID,
        "output_format": OUTPUT_FORMAT,
        "voice_settings": "Omitted: use the same saved voice defaults for all four requests.",
        "generated_at_local": time.strftime("%Y-%m-%d %H:%M:%S"),
        "clips": [],
    }

    print("Vivienne controlled audition generation")
    print(f"Model: {MODEL_ID}")
    print(f"Voice: {voice_name} ({voice_id})")
    print(f"Output: {OUTPUT_DIR}")
    print("Four API requests will be made. Each request may consume account credits.")

    for index, item in enumerate(AUDITIONS, start=1):
        output_path = OUTPUT_DIR / f"vivienne_{item['name']}.mp3"
        if output_path.exists():
            existing_bytes = output_path.stat().st_size
            print(f"\nSKIP {index}/4: reusing existing {output_path.name} ({existing_bytes:,} bytes)")
            manifest["clips"].append(
                {
                    "file": output_path.name,
                    "purpose": item["purpose"],
                    "text": item["text"],
                    "bytes": existing_bytes,
                    "status": "reused_existing_file",
                }
            )
            continue

        print(f"\nGenerating {index}/4: {item['name']} ...")
        try:
            audio = request_audio(api_key, voice_id, item["text"])
        except Exception as exc:
            print(f"ERROR: {exc}")
            print("Stopped to avoid repeated requests and unexpected credit use.")
            return 1

        if len(audio) < 1000:
            print("ERROR: The returned audio is unexpectedly small; file not saved.")
            return 1

        output_path.write_bytes(audio)
        manifest["clips"].append(
            {
                "file": output_path.name,
                "purpose": item["purpose"],
                "text": item["text"],
                "bytes": len(audio),
            }
        )
        print(f"Saved: {output_path.name} ({len(audio):,} bytes)")

    manifest_path = OUTPUT_DIR / "audition_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("\nSUCCESS: All four audition clips were generated.")
    print(f"Manifest: {manifest_path}")
    print("Do not commit .env or any API key. Review the MP3s by listening.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
