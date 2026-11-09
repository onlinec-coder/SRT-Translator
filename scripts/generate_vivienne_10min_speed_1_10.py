#!/usr/bin/env python3
"""Generate the explicitly authorized 10-minute Vivienne TTS test at ElevenLabs speed 1.10."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREP = ROOT / "acoustic_comparison_6_results_v2" / "VIVIENNE_10MIN_SPEED_1_10_PREP_V1.json"
OUT = ROOT / "vivienne_tts_output" / "VIVIENNE_10MIN_SPEED_1_10"
VOICE_ID = "6Km4T9TrZXIhfMaxglHw"
MODEL_ID = "eleven_v3"
OUTPUT_FORMAT = "mp3_44100_128"
EXPECTED_REQUESTS = 214
SPEED = 1.10
AUTHORIZATION_PHRASE = "AUTHORIZE 10MIN VIVIENNE TTS 214 REQUESTS"


def api_request(api_key: str, url: str, method: str = "GET", body: bytes | None = None):
    headers = {"xi-api-key": api_key, "Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "audio/mpeg"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=240) as response:
            return response.read(), response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        detail = exc.read(3000).decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc


def parse_start(timestamp: str) -> float:
    start = timestamp.split("-->")[0].strip().replace(",", ".")
    h, m, s = start.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def duration_seconds(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=True, capture_output=True, text=True, timeout=30,
    )
    return round(float(result.stdout.strip()), 3)


def write_manifest(manifest: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    if not PREP.is_file():
        print(f"BLOCKED: preparation file missing: {PREP}")
        return 2
    prep = json.loads(PREP.read_text(encoding="utf-8"))
    scope = prep.get("pilot_scope", {})
    auth = prep.get("authorization", {})
    if prep.get("status") != "AUTHORIZED — user approved 214 paid ElevenLabs TTS requests":
        print("BLOCKED: preparation status is not explicitly authorized.")
        return 2
    if auth.get("approved_by_user") is not True or auth.get("approved_request_count") != EXPECTED_REQUESTS:
        print("BLOCKED: explicit authorization record missing or request count mismatch.")
        return 2
    if scope.get("tts_request_count") != EXPECTED_REQUESTS or scope.get("baseline_speed") != SPEED:
        print("BLOCKED: expected request count or speed mismatch.")
        return 2
    if scope.get("voice_id") != VOICE_ID or scope.get("model_id") != MODEL_ID:
        print("BLOCKED: voice or model mismatch.")
        return 2
    clips = prep.get("clips", [])
    if len(clips) != EXPECTED_REQUESTS:
        print(f"BLOCKED: expected {EXPECTED_REQUESTS} cues, found {len(clips)}.")
        return 2
    ids = [clip.get("cue_id") for clip in clips]
    if len(set(ids)) != EXPECTED_REQUESTS:
        print("BLOCKED: duplicate or missing cue IDs.")
        return 2
    if any(c.get("speaker_id") != "C001" or not c.get("tts_text") for c in clips):
        print("BLOCKED: non-Vivienne or empty-text cue found.")
        return 2
    if any(parse_start(c["timestamp"]) >= 600 for c in clips):
        print("BLOCKED: a cue starts outside the first 10 minutes.")
        return 2
    if clips != sorted(clips, key=lambda c: parse_start(c["timestamp"])):
        print("BLOCKED: cue order is not chronological.")
        return 2
    if any(c.get("emotion_tag") for c in clips):
        print("BLOCKED: unexpected emotion tags require separate review.")
        return 2
    if OUT.exists() and any(OUT.iterdir()):
        print(f"BLOCKED: output directory already contains files: {OUT}")
        return 2
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY is missing; no TTS request sent.")
        return 2

    settings_url = "https://api.elevenlabs.io/v1/voices/" + urllib.parse.quote(VOICE_ID, safe="") + "/settings"
    settings_bytes, _ = api_request(api_key, settings_url)
    saved_settings = json.loads(settings_bytes.decode("utf-8"))
    if not isinstance(saved_settings, dict) or not saved_settings:
        print("ERROR: could not read saved ElevenLabs voice settings; no TTS request sent.")
        return 2

    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "title": "Husbands — Vivienne first 10-minute TTS test",
        "status": "IN_PROGRESS",
        "authorization_phrase": AUTHORIZATION_PHRASE,
        "authorized_request_count": EXPECTED_REQUESTS,
        "voice_id": VOICE_ID,
        "model_id": MODEL_ID,
        "output_format": OUTPUT_FORMAT,
        "speed": SPEED,
        "baseline_saved_voice_settings": saved_settings,
        "only_overridden_setting": "voice_settings.speed",
        "source_window": scope.get("film_window"),
        "generated_count": 0,
        "failed_at": None,
        "original_audio_modified": False,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "clips": [],
    }
    print(f"AUTHORIZED: {EXPECTED_REQUESTS} separate TTS requests; speed={SPEED:.2f}.")
    print("Only voice_settings.speed is overridden; all other saved voice settings are preserved.")
    for index, clip in enumerate(clips, 1):
        cue_id = int(clip["cue_id"])
        filename = f"VIVIENNE_10MIN_CUE_{cue_id:04d}.mp3"
        target = OUT / filename
        if target.exists():
            manifest["status"] = "STOPPED — output collision"
            manifest["failed_at"] = {"cue_id": cue_id, "reason": "output file already exists"}
            write_manifest(manifest)
            print(f"STOPPED: refusing to overwrite {target}")
            return 1

        request_settings = dict(saved_settings)
        request_settings["speed"] = SPEED
        payload = json.dumps(
            {"text": clip["tts_text"], "model_id": MODEL_ID, "voice_settings": request_settings},
            ensure_ascii=False,
        ).encode("utf-8")
        query = urllib.parse.urlencode({"output_format": OUTPUT_FORMAT})
        url = "https://api.elevenlabs.io/v1/text-to-speech/" + urllib.parse.quote(VOICE_ID, safe="") + "?" + query
        print(f"GENERATE {index}/{EXPECTED_REQUESTS}: cue {cue_id} speed={SPEED:.2f}", flush=True)
        try:
            audio, content_type = api_request(api_key, url, "POST", payload)
        except Exception as exc:
            manifest["status"] = "PARTIAL — stopped on first API error"
            manifest["failed_at"] = {"cue_id": cue_id, "error": str(exc)}
            write_manifest(manifest)
            print(f"STOPPED at cue {cue_id}: {exc}")
            return 1
        if not content_type.startswith("audio/") or len(audio) < 1000:
            manifest["status"] = "PARTIAL — unexpected API response"
            manifest["failed_at"] = {"cue_id": cue_id, "content_type": content_type, "bytes": len(audio)}
            write_manifest(manifest)
            print(f"STOPPED: unexpected response for cue {cue_id}: {content_type}, {len(audio)} bytes")
            return 1
        target.write_bytes(audio)
        try:
            actual_duration = duration_seconds(target)
        except Exception as exc:
            manifest["status"] = "PARTIAL — duration QA failed"
            manifest["failed_at"] = {"cue_id": cue_id, "error": str(exc), "audio_saved": True}
            write_manifest(manifest)
            print(f"STOPPED: cue {cue_id} saved but duration QA failed: {exc}")
            return 1

        manifest["clips"].append({
            "cue_id": cue_id,
            "batch_id": clip.get("batch_id"),
            "source_timestamp": clip["timestamp"],
            "tts_text": clip["tts_text"],
            "delivery_class": clip.get("delivery_class"),
            "direction": clip.get("direction"),
            "filename": filename,
            "bytes": len(audio),
            "duration_seconds": actual_duration,
            "status": "generated",
        })
        manifest["generated_count"] = len(manifest["clips"])
        manifest["status"] = "IN_PROGRESS"
        write_manifest(manifest)
        print(f"SAVED cue {cue_id}: {actual_duration:.3f}s ({len(audio):,} bytes)", flush=True)
        time.sleep(0.15)

    manifest["status"] = "COMPLETE"
    manifest["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_manifest(manifest)
    print(f"COMPLETE: {manifest['generated_count']}/{EXPECTED_REQUESTS} MP3 files.")
    print(f"Output: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
