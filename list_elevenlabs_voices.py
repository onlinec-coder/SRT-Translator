#!/usr/bin/env python3
"""List voices accessible to the ElevenLabs API key in the local .env."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


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


def get_json(api_key: str, url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"xi-api-key": api_key, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read(3000).decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs HTTP {exc.code}: {detail}") from exc


def main() -> int:
    load_env_file(ROOT / ".env")
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY was not found in environment or project .env")
        return 2

    url = "https://api.elevenlabs.io/v1/voices?page_size=100"
    found = 0
    page = 1
    try:
        while url:
            data = get_json(api_key, url)
            voices = data.get("voices", [])
            for voice in voices:
                found += 1
                labels = voice.get("labels") or {}
                print(
                    f"{voice.get('name', '(unnamed)')}\n"
                    f"  voice_id: {voice.get('voice_id', '')}\n"
                    f"  category: {voice.get('category', '')}\n"
                    f"  labels: {json.dumps(labels, ensure_ascii=False)}"
                )
            token = data.get("next_page_token")
            if not token:
                break
            url = "https://api.elevenlabs.io/v1/voices?" + urllib.parse.urlencode(
                {"page_size": 100, "next_page_token": token}
            )
            page += 1
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"\nTotal accessible voices: {found}")
    print("Copy the exact voice_id for the intended Vivienne voice.")
    print("Do not share or commit your API key.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
