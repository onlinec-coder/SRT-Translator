#!/usr/bin/env python3
"""Generate the V3.2-informed Vivienne representative pilot.

Paid requests are blocked unless GENERATE_CONFIRMATION exactly matches
GENERATE V32P01. Uses the approved existing voice and model without settings
overrides. Existing audio files are reused, never overwritten.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREP = ROOT / "acoustic_comparison_6_results_v2" / "VIVIENNE_V3_2_PILOT_01_PREP.json"
OUT = ROOT / "vivienne_tts_output" / "V32P01"
VOICE_ID = "6Km4T9TrZXIhfMaxglHw"
MODEL_ID = "eleven_v3"
OUTPUT_FORMAT = "mp3_44100_128"
CONFIRMATION = "GENERATE V32P01"


def request(api_key: str, url: str, method: str = "GET", body: bytes | None = None):
    headers = {"xi-api-key": api_key, "Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "audio/mpeg"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return response.read(), response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        detail = exc.read(2500).decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc


def audio_duration(path: Path) -> float | None:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            check=True, capture_output=True, text=True, timeout=30,
        )
        return round(float(result.stdout.strip()), 3)
    except Exception:
        return None


def main() -> int:
    if os.environ.get("GENERATE_CONFIRMATION", "") != CONFIRMATION:
        print("BLOCKED: paid TTS requires the exact workflow confirmation.")
        return 2
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY is missing. No TTS request sent.")
        return 2
    if not PREP.is_file():
        print(f"ERROR: preparation file missing: {PREP}")
        return 2

    prep = json.loads(PREP.read_text(encoding="utf-8"))
    if prep.get("status") != "PREPARED — no ElevenLabs TTS requests sent":
        print("ERROR: preparation status is not eligible for generation.")
        return 2
    scope = prep["pilot_scope"]
    if scope["voice_id"] != VOICE_ID or scope["model_id"] != MODEL_ID:
        print("ERROR: voice/model does not match the locked pilot configuration.")
        return 2
    clips = prep["clips"]
    expected = int(scope["tts_request_count"])
    if len(clips) != expected:
        print(f"ERROR: clip count mismatch: expected {expected}, found {len(clips)}.")
        return 2

    OUT.mkdir(parents=True, exist_ok=True)
    voice_url = "https://api.elevenlabs.io/v1/voices/" + urllib.parse.quote(VOICE_ID, safe="")
    voice_bytes, _ = request(api_key, voice_url)
    voice = json.loads(voice_bytes.decode("utf-8"))
    manifest = {
        "pilot": scope,
        "voice_name": voice.get("name"),
        "preparation_file": str(PREP.relative_to(ROOT)),
        "generation_confirmation": CONFIRMATION,
        "clips": [],
    }

    new_requests = sum(not (OUT / f"{clip['clip_id']}.mp3").is_file() for clip in clips)
    print(f"Vivienne V3.2 pilot: {len(clips)} clips; new paid requests remaining: {new_requests}")
    print(f"Voice: {voice.get('name', 'approved Vivienne voice')} ({VOICE_ID})")
    print(f"Model: {MODEL_ID}; output: {OUTPUT_FORMAT}; voice settings: unchanged")

    for index, clip in enumerate(clips, 1):
        target = OUT / f"{clip['clip_id']}.mp3"
        record = {
            "sequence": clip["sequence"],
            "clip_id": clip["clip_id"],
            "cue_ids": clip["cue_ids"],
            "utterance_ids": clip["utterance_ids"],
            "source_time": clip["source_time"],
            "target_window_ms": clip["target_window_ms"],
            "tts_text": clip["tts_text"],
            "delivery_class": clip["delivery_class"],
            "delivery_direction": clip["direction"],
        }
        if target.is_file():
            record.update({
                "status": "reused_existing",
                "bytes": target.stat().st_size,
                "duration_seconds": audio_duration(target),
            })
            print(f"REUSE {index}/{len(clips)} {target.name}")
            manifest["clips"].append(record)
            continue

        payload = json.dumps(
            {"text": clip["tts_text"], "model_id": MODEL_ID},
            ensure_ascii=False,
        ).encode("utf-8")
        query = urllib.parse.urlencode({"output_format": OUTPUT_FORMAT})
        url = (
            "https://api.elevenlabs.io/v1/text-to-speech/"
            + urllib.parse.quote(VOICE_ID, safe="") + "?" + query
        )
        print(f"GENERATE {index}/{len(clips)} {clip['clip_id']} cues={clip['cue_ids']}")
        try:
            audio, content_type = request(api_key, url, "POST", payload)
        except Exception as exc:
            print(f"FAILED at {clip['clip_id']}: {exc}")
            print("Stopped immediately; no subsequent TTS requests will be sent.")
            return 1
        if not content_type.startswith("audio/") or len(audio) < 1000:
            print(f"ERROR: unexpected response {content_type}, {len(audio)} bytes.")
            print("Stopped immediately.")
            return 1
        target.write_bytes(audio)
        record.update({
            "status": "generated",
            "bytes": len(audio),
            "duration_seconds": audio_duration(target),
        })
        manifest["clips"].append(record)
        print(f"SAVED {target.name} ({len(audio):,} bytes)")

    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    generated = sum(x["status"] == "generated" for x in manifest["clips"])
    reused = sum(x["status"] == "reused_existing" for x in manifest["clips"])
    print(f"COMPLETE: {generated} generated, {reused} reused.")
    print("Review every clip against the original film before acceptance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
