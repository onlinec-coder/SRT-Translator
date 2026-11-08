#!/usr/bin/env python3
"""Generate the explicitly approved Vivienne VIV_01 cue audio set.

No retries: an interrupted/ambiguous request must be reviewed before rerunning,
to avoid duplicate paid generations. Each successful cue is saved immediately.
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

ROOT = Path(__file__).resolve().parents[1]
PREP = ROOT / "acoustic_comparison_6_results_v2" / "VIVIENNE_BATCH_01_TTS_PREP_V1.json"
OUT = ROOT / "vivienne_tts_output" / "VIV_01"
VOICE_ID = "6Km4T9TrZXIhfMaxglHw"
MODEL_ID = "eleven_v3"
OUTPUT_FORMAT = "mp3_44100_128"
EXPECTED_CUES = 32
EXPECTED_CHARACTERS = 894


def request_audio(api_key: str, text: str) -> bytes:
    query = urllib.parse.urlencode({"output_format": OUTPUT_FORMAT})
    url = (
        "https://api.elevenlabs.io/v1/text-to-speech/"
        + urllib.parse.quote(VOICE_ID, safe="")
        + "?"
        + query
    )
    payload = json.dumps({"text": text, "model_id": MODEL_ID}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
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
        with urllib.request.urlopen(req, timeout=180) as response:
            data = response.read()
            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("audio/") or len(data) < 1000:
                raise RuntimeError(f"Unexpected response: type={content_type}, bytes={len(data)}")
            return data
    except urllib.error.HTTPError as exc:
        detail = exc.read(3000).decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error; request outcome may be uncertain: {exc.reason}") from exc


def main() -> int:
    if os.environ.get("GENERATE_CONFIRMATION") != "GENERATE VIV_01":
        print("STOP: confirmation input must be exactly 'GENERATE VIV_01'.")
        return 2
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        print("STOP: GitHub Actions secret ELEVENLABS_API_KEY is missing.")
        return 2
    if not PREP.is_file():
        print(f"STOP: preparation file not found: {PREP}")
        return 2

    data = json.loads(PREP.read_text(encoding="utf-8"))
    cues = data.get("cues", [])
    if data.get("batch_id") != "VIV_01" or len(cues) != EXPECTED_CUES:
        print("STOP: batch identity or cue count does not match the reviewed VIV_01 plan.")
        return 2
    if data.get("voice", {}).get("voice_id") != VOICE_ID:
        print("STOP: voice ID differs from the approved Vivienne voice.")
        return 2
    if data.get("voice", {}).get("model_id") != MODEL_ID:
        print("STOP: model differs from the approved Eleven v3 model.")
        return 2
    if any(c.get("emotion_tag") for c in cues):
        print("STOP: VIV_01 unexpectedly contains emotion tags; review required.")
        return 2

    total_chars = sum(len(c["tts_text"]) for c in cues)
    if total_chars != EXPECTED_CHARACTERS:
        print(f"STOP: expected {EXPECTED_CHARACTERS} text characters, found {total_chars}.")
        return 2

    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / "manifest.json"
    manifest = {
        "batch_id": "VIV_01",
        "voice_id": VOICE_ID,
        "model_id": MODEL_ID,
        "output_format": OUTPUT_FORMAT,
        "voice_settings": "Omitted, matching the project's prior accepted audition request pattern; no numeric overrides.",
        "expected_cue_count": EXPECTED_CUES,
        "expected_text_characters": EXPECTED_CHARACTERS,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "in_progress",
        "cues": [],
    }
    print(f"Validated {len(cues)} cues / {total_chars} text characters.")
    print("Sending one TTS request per cue; no automatic retries.")

    for index, cue in enumerate(cues, 1):
        cue_id = int(cue["cue_id"])
        out_file = OUT / f"cue_{cue_id:04d}.mp3"
        if out_file.exists():
            print(f"STOP: output already exists ({out_file.name}); refusing to overwrite or double-charge.")
            return 3
        print(f"Generating {index}/{len(cues)} — cue {cue_id}")
        try:
            audio = request_audio(api_key, cue["tts_text"])
        except Exception as exc:
            manifest["status"] = "failed_or_ambiguous"
            manifest["failed_at_cue_id"] = cue_id
            manifest["error"] = str(exc)
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"STOPPED at cue {cue_id}: {exc}")
            print("No automatic retry was attempted. Review billing/history before any rerun.")
            return 1
        out_file.write_bytes(audio)
        manifest["cues"].append({
            "cue_id": cue_id,
            "timestamp": cue["timestamp"],
            "file": out_file.name,
            "characters": len(cue["tts_text"]),
            "bytes": len(audio),
        })
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Saved {out_file.name} ({len(audio)} bytes)")

    manifest["status"] = "complete"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"SUCCESS: {len(manifest['cues'])} cue files generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
