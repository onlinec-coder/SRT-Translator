#!/usr/bin/env python3
"""Generate ElevenLabs-native speed A/B samples for selected V32P01 clips.

Creates 8 new TTS files (4 clips x 2 speeds). Original V32P01 assets are
never modified. Each request reads the voice's saved settings and overrides
only voice_settings.speed for that request.
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

ROOT = Path(__file__).resolve().parent.parent
PREP = ROOT / "acoustic_comparison_6_results_v2" / "VIVIENNE_V3_2_PILOT_01_PREP.json"
OUT = ROOT / "vivienne_tts_output" / "V32P01_SPEED_AB"
VOICE_ID = "6Km4T9TrZXIhfMaxglHw"
MODEL_ID = "eleven_v3"
OUTPUT_FORMAT = "mp3_44100_128"
CONFIRMATION = "GENERATE V32P01 SPEED AB"
TARGET_CLIPS = {
    "V32P01_CUE_0001",
    "V32P01_CUE_0002",
    "V32P01_CUES_0004_0005",
    "V32P01_CUES_0009_0010",
}
SPEEDS = {"A_1.10x": 1.10, "B_1.20x": 1.20}


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


def audio_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=True, capture_output=True, text=True, timeout=30,
    )
    return round(float(result.stdout.strip()), 3)


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
        print("ERROR: voice/model does not match the approved pilot.")
        return 2

    clips_by_id = {clip["clip_id"]: clip for clip in prep["clips"]}
    missing = TARGET_CLIPS - clips_by_id.keys()
    if missing:
        print(f"ERROR: missing target clips: {sorted(missing)}")
        return 2
    selected = [clip for clip in prep["clips"] if clip["clip_id"] in TARGET_CLIPS]
    if len(selected) != 4:
        print(f"ERROR: expected 4 selected clips, found {len(selected)}.")
        return 2

    settings_url = (
        "https://api.elevenlabs.io/v1/voices/"
        + urllib.parse.quote(VOICE_ID, safe="") + "/settings"
    )
    settings_bytes, _ = request(api_key, settings_url)
    saved_settings = json.loads(settings_bytes.decode("utf-8"))
    if not isinstance(saved_settings, dict) or not saved_settings:
        print("ERROR: could not read saved voice settings. No TTS request sent.")
        return 2

    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "title": "Vivienne V32P01 ElevenLabs-native speed A/B",
        "voice_id": VOICE_ID,
        "model_id": MODEL_ID,
        "output_format": OUTPUT_FORMAT,
        "baseline_saved_voice_settings": saved_settings,
        "only_overridden_setting": "voice_settings.speed",
        "speeds": SPEEDS,
        "paid_tts_request_count": len(selected) * len(SPEEDS),
        "original_audio_modified": False,
        "clips": [],
    }

    targets = []
    for variant, speed in SPEEDS.items():
        variant_dir = OUT / variant
        variant_dir.mkdir(parents=True, exist_ok=True)
        for clip in selected:
            target = variant_dir / f"{clip['clip_id']}.mp3"
            if target.exists():
                print(f"ERROR: refusing to overwrite existing file: {target}")
                print("No generation started. Move existing trial files before retrying.")
                return 2
            targets.append((variant, speed, clip, target))

    print(f"Approved speed A/B: {len(targets)} paid TTS requests.")
    print(f"Voice: {VOICE_ID}; model: {MODEL_ID}; output: {OUTPUT_FORMAT}")
    print("Only voice_settings.speed changes; saved voice settings are otherwise preserved.")

    for index, (variant, speed, clip, target) in enumerate(targets, 1):
        request_settings = dict(saved_settings)
        request_settings["speed"] = speed
        payload = json.dumps(
            {
                "text": clip["tts_text"],
                "model_id": MODEL_ID,
                "voice_settings": request_settings,
            },
            ensure_ascii=False,
        ).encode("utf-8")
        query = urllib.parse.urlencode({"output_format": OUTPUT_FORMAT})
        url = (
            "https://api.elevenlabs.io/v1/text-to-speech/"
            + urllib.parse.quote(VOICE_ID, safe="") + "?" + query
        )
        print(f"GENERATE {index}/{len(targets)} {variant} {clip['clip_id']} speed={speed:.2f}")
        try:
            audio, content_type = request(api_key, url, "POST", payload)
        except Exception as exc:
            print(f"FAILED at {variant}/{clip['clip_id']}: {exc}")
            print("Stopped immediately; no subsequent TTS requests will be sent.")
            return 1
        if not content_type.startswith("audio/") or len(audio) < 1000:
            print(f"ERROR: unexpected response {content_type}, {len(audio)} bytes.")
            print("Stopped immediately.")
            return 1

        target.write_bytes(audio)
        try:
            duration = audio_duration(target)
        except Exception as exc:
            print(f"ERROR: audio saved but duration QA failed: {exc}")
            return 1

        manifest["clips"].append({
            "variant": variant,
            "speed": speed,
            "clip_id": clip["clip_id"],
            "cue_ids": clip["cue_ids"],
            "source_time": clip["source_time"],
            "target_window_ms": clip["target_window_ms"],
            "tts_text": clip["tts_text"],
            "delivery_class": clip["delivery_class"],
            "delivery_direction": clip["direction"],
            "bytes": len(audio),
            "duration_seconds": duration,
            "status": "generated",
        })
        print(f"SAVED {target.name} ({len(audio):,} bytes; {duration:.3f}s)")

    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("\nCOMPLETE: 8 ElevenLabs-native speed variants generated.")
    print(f"Output: {OUT}")
    print("Original V32P01 MP3s and source timestamps were not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
