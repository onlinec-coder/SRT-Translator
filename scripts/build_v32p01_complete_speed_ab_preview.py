#!/usr/bin/env python3
"""Build complete V32P01 A/B previews using all 13 original clips.

For each variant, only the four selected utterances are replaced by their
ElevenLabs-native speed trial. The other nine original MP3s are retained.
No TTS/API requests are made by this script.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:\Users\chinzorig\Desktop\Husbands")
VIDEO_DEFAULT = BASE / "Husbands.mp4"
ORIGINAL_DEFAULT = BASE / "vivienne-V32P01-audio"
SPEED_AB_DEFAULT = BASE / "vivienne-V32P01-elevenlabs-speed-ab"
OUTPUT_DEFAULT = BASE / "V32P01_AB_preview"
PREVIEW_SECONDS = 60.0

TARGET_CLIPS = {
    "V32P01_CUE_0001",
    "V32P01_CUE_0002",
    "V32P01_CUES_0004_0005",
    "V32P01_CUES_0009_0010",
}
VARIANTS = ("A_1.10x", "B_1.20x")


def fail(message: str) -> None:
    raise SystemExit("\nERROR: " + message)


def timestamp_to_seconds(value: str) -> float:
    value = value.strip().replace(",", ".")
    hours, minutes, seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def parse_source_time(value: str) -> tuple[float, float]:
    parts = value.split("-->")
    if len(parts) != 2:
        fail(f"Invalid source_time: {value}")
    return timestamp_to_seconds(parts[0]), timestamp_to_seconds(parts[1])


def probe_duration(ffprobe: str, path: Path) -> float:
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=True, capture_output=True, text=True, timeout=30,
    )
    return round(float(result.stdout.strip()), 3)


def build_variant(
    variant: str,
    video: Path,
    original_dir: Path,
    speed_dir: Path,
    output_dir: Path,
    original_manifest: dict,
    speed_manifest: dict,
    ffmpeg: str,
    ffprobe: str,
    cue2_start: float,
) -> None:
    variant_dir = speed_dir / variant
    speed_records = {
        row["clip_id"]: row
        for row in speed_manifest.get("clips", [])
        if row.get("variant") == variant
    }
    original_clips = original_manifest.get("clips", [])
    if len(original_clips) != 13:
        fail(f"Expected 13 original clips, found {len(original_clips)}.")
    if set(speed_records) != TARGET_CLIPS:
        fail(
            f"{variant}: expected exactly four speed clips "
            f"{sorted(TARGET_CLIPS)}, found {sorted(speed_records)}."
        )

    inputs = ["-i", str(video)]
    filters: list[str] = []
    clip_rows: list[dict] = []
    duck_intervals: list[str] = []

    # Sort by source time to keep the voice timeline deterministic.
    ordered = sorted(
        original_clips,
        key=lambda row: parse_source_time(row["source_time"])[0],
    )

    for index, original in enumerate(ordered):
        clip_id = original["clip_id"]
        source_path = original_dir / f"{clip_id}.mp3"
        if not source_path.is_file():
            fail(f"Missing original audio: {source_path}")

        chosen_path = source_path
        source_label = "original_1.00x"
        if clip_id in TARGET_CLIPS:
            chosen_path = variant_dir / f"{clip_id}.mp3"
            source_label = variant
            if not chosen_path.is_file():
                fail(f"Missing speed-trial audio: {chosen_path}")

        start, target_end = parse_source_time(original["source_time"])
        # The first sentence must finish before cue 0002 begins. This small
        # manual offset preserves the previously agreed 100 ms gap.
        if clip_id == "V32P01_CUE_0002":
            start = max(start, cue2_start)
        # Prevent the original 0018 and 0019 voice clips from overlapping.
        if clip_id == "V32P01_CUE_0019":
            start = max(start, 39.50)

        duration = probe_duration(ffprobe, chosen_path)
        actual_end = start + duration
        if start >= PREVIEW_SECONDS:
            fail(f"{clip_id} starts outside the preview window.")

        inputs.extend(["-i", str(chosen_path)])
        delay_ms = round(start * 1000)
        filters.append(
            f"[{index + 1}:a]asetpts=PTS-STARTPTS,"
            f"adelay={delay_ms}|{delay_ms},"
            f"atrim=duration={PREVIEW_SECONDS:.3f}[voice{index}]"
        )
        duck_end = min(actual_end, PREVIEW_SECONDS)
        duck_intervals.append(f"between(t,{start:.3f},{duck_end:.3f})")

        clip_rows.append({
            "sequence": original.get("sequence", index + 1),
            "clip_id": clip_id,
            "audio_source": source_label,
            "start_seconds": round(start, 3),
            "original_start_seconds": round(
                parse_source_time(original["source_time"])[0], 3
            ),
            "target_end_seconds": round(target_end, 3),
            "target_duration_seconds": round(target_end - start, 3),
            "actual_duration_seconds": duration,
            "actual_end_seconds": round(actual_end, 3),
            "overrun_seconds": round(actual_end - target_end, 3),
            "status": "CHECK" if actual_end > target_end + 0.15 else "OK",
        })

    # Report actual voice-to-voice gaps separately from subtitle-window overruns.
    for row_index, row in enumerate(clip_rows):
        if row_index + 1 < len(clip_rows):
            next_start = clip_rows[row_index + 1]["start_seconds"]
            gap = round(next_start - row["actual_end_seconds"], 3)
            row["next_start_seconds"] = next_start
            row["gap_after_seconds"] = gap
            row["timeline_status"] = (
                "OVERLAP" if gap < -0.02 else
                "TIGHT" if gap < 0.05 else "OK"
            )
        else:
            row["next_start_seconds"] = ""
            row["gap_after_seconds"] = ""
            row["timeline_status"] = "END"

    duck_expression = "+".join(duck_intervals)
    filters.append(
        f"[0:a]atrim=duration={PREVIEW_SECONDS:.3f},"
        f"asetpts=PTS-STARTPTS,"
        f"volume=0.20:enable='{duck_expression}'[original]"
    )
    mix_inputs = "[original]" + "".join(
        f"[voice{index}]" for index in range(len(ordered))
    )
    filters.append(
        f"{mix_inputs}amix=inputs={len(ordered) + 1}:"
        f"duration=longest:dropout_transition=0:normalize=0,"
        f"alimiter=limit=0.95,atrim=duration={PREVIEW_SECONDS:.3f}[aout]"
    )

    output_video = output_dir / f"V32P01_AB_{variant}.mp4"
    output_csv = output_dir / f"V32P01_AB_{variant}_timing_QA.csv"
    command = [
        ffmpeg, "-y", *inputs,
        "-filter_complex", ";".join(filters),
        "-map", "0:v:0", "-map", "[aout]",
        "-t", f"{PREVIEW_SECONDS:.3f}",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", str(output_video),
    ]

    print(f"\nBuilding {variant}: {len(ordered)} total voice clips")
    print(f"  Speed replacements: {len(speed_records)}")
    print(f"  Original clips retained: {len(ordered) - len(speed_records)}")
    print(f"  Cue 0002 start: {cue2_start:.3f}s")
    result = subprocess.run(command)
    if result.returncode != 0:
        fail(f"FFmpeg failed while building {variant}.")

    with output_csv.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=clip_rows[0].keys())
        writer.writeheader()
        writer.writerows(clip_rows)

    exported = probe_duration(ffprobe, output_video)
    if abs(exported - PREVIEW_SECONDS) > 0.25:
        fail(f"Unexpected preview duration for {variant}: {exported:.3f}s")
    print(f"COMPLETE: {output_video}")
    print(f"QA CSV: {output_csv}")
    print(f"Verified video duration: {exported:.3f}s")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, default=VIDEO_DEFAULT)
    parser.add_argument("--original-dir", type=Path, default=ORIGINAL_DEFAULT)
    parser.add_argument("--speed-ab-dir", type=Path, default=SPEED_AB_DEFAULT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DEFAULT)
    parser.add_argument(
        "--cue2-start", type=float, default=11.94,
        help="Absolute video timestamp for cue 0002; default leaves at least "
             "20 ms after the 1.20x cue 0001 audio and 100 ms after 1.10x.",
    )
    args = parser.parse_args()

    ffmpeg = shutil.which("ffmpeg.exe") or shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe.exe") or shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        fail("ffmpeg.exe and ffprobe.exe must be available on PATH.")
    for path in (args.video, args.original_dir / "manifest.json",
                 args.speed_ab_dir / "manifest.json"):
        if not path.is_file():
            fail(f"Required file not found: {path}")

    original_manifest = json.loads(
        (args.original_dir / "manifest.json").read_text(encoding="utf-8")
    )
    speed_manifest = json.loads(
        (args.speed_ab_dir / "manifest.json").read_text(encoding="utf-8")
    )
    if speed_manifest.get("paid_tts_request_count") != 8:
        fail("Speed A/B manifest does not confirm the expected 8 existing trials.")
    if speed_manifest.get("original_audio_modified") is not False:
        fail("Speed A/B manifest does not confirm originals were preserved.")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("V32P01 complete A/B preview builder")
    print("No ElevenLabs requests will be made.")
    print("Each preview contains all 13 clips: 4 speed trials + 9 originals.")
    for variant in VARIANTS:
        build_variant(
            variant, args.video, args.original_dir, args.speed_ab_dir,
            args.output_dir, original_manifest, speed_manifest,
            ffmpeg, ffprobe, args.cue2_start,
        )
    print("\nBOTH A/B PREVIEWS BUILT SUCCESSFULLY.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
