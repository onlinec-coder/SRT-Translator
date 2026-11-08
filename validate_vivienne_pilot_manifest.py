#!/usr/bin/env python3
"""Validate the Vivienne pilot manifest against the Mongolian SRT.

Metadata-only validation: this script does not open, decode, play, modify, upload,
or generate any audio. It checks cue IDs, subtitle text, and target durations.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PILOT_DIR = ROOT / "acoustic_comparison_6_results_v2" / "vivienne_production_pilot_01"
MANIFEST = PILOT_DIR / "vivienne_production_pilot_01_manifest.json"
SRT = ROOT / "Husbands_mn_v3.srt"


def timestamp_seconds(value: str) -> float:
    hours, minutes, rest = value.split(":")
    seconds, millis = rest.split(",")
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_srt(path: Path) -> dict[int, dict]:
    raw = path.read_text(encoding="utf-8-sig")
    cues: dict[int, dict] = {}
    for block in re.split(r"\r?\n\s*\r?\n", raw.strip()):
        lines = block.strip().splitlines()
        if len(lines) < 3 or not lines[0].strip().isdigit():
            continue
        match = re.fullmatch(
            r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})",
            lines[1].strip(),
        )
        if not match:
            continue
        cue_id = int(lines[0].strip())
        cues[cue_id] = {
            "start": timestamp_seconds(match.group(1)),
            "end": timestamp_seconds(match.group(2)),
            "text": normalize_text(" ".join(line.strip() for line in lines[2:])),
        }
    return cues


def main() -> int:
    for required in (MANIFEST, SRT):
        if not required.is_file():
            print(f"FAIL: required file not found: {required}")
            return 2

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cues = parse_srt(SRT)
    failures: list[str] = []
    checked = 0

    print("Vivienne pilot manifest validation (metadata only)")
    print("Audio opened/decoded: NO | Audio uploaded: NO | TTS: NO")
    print()

    for clip in manifest.get("clips", []):
        checked += 1
        filename = clip.get("file", "<unnamed>")
        cue_ids = clip.get("cue_ids", [])
        missing = [cue_id for cue_id in cue_ids if cue_id not in cues]
        if not cue_ids:
            failures.append(f"{filename}: cue_ids is empty")
            print(f"FAIL  {filename}: no cue IDs")
            continue
        if missing:
            failures.append(f"{filename}: missing SRT cue IDs {missing}")
            print(f"FAIL  {filename}: missing cue IDs {missing}")
            continue

        actual_text = normalize_text(" ".join(cues[cue_id]["text"] for cue_id in cue_ids))
        expected_text = normalize_text(clip.get("subtitle_text_without_delivery_tags", ""))
        text_ok = actual_text == expected_text

        actual_duration_ms = round(
            (cues[cue_ids[-1]]["end"] - cues[cue_ids[0]]["start"]) * 1000
        )
        expected_duration_ms = clip.get("target_subtitle_window_ms")
        duration_ok = actual_duration_ms == expected_duration_ms

        status = "PASS" if text_ok and duration_ok else "FAIL"
        print(
            f"{status}  {filename} | cues={cue_ids} | "
            f"text={'OK' if text_ok else 'MISMATCH'} | "
            f"duration={actual_duration_ms}ms (manifest={expected_duration_ms}ms)"
        )
        if not text_ok:
            failures.append(
                f"{filename}: subtitle text mismatch; "
                f"manifest={expected_text!r}; SRT={actual_text!r}"
            )
        if not duration_ok:
            failures.append(
                f"{filename}: duration mismatch; "
                f"manifest={expected_duration_ms}; SRT={actual_duration_ms}"
            )

    print()
    print(f"Checked clips: {checked}")
    print(f"Validation failures: {len(failures)}")
    if failures:
        for failure in failures:
            print(" -", failure)
        return 1
    print("RESULT: ALL MANIFEST METADATA CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
