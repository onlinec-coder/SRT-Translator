#!/usr/bin/env python3
"""Build a local 10-minute Vivienne dubbing preview from existing MP3 clips.

This script makes no TTS/API requests. It places each existing clip at the
start time recorded in the manifest, mixes overlaps (without truncating them),
copies the source video stream, and intentionally omits the source audio.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_VIDEO = Path(r"C:\Users\chinzorig\Desktop\Husbands\Husbands.mp4")
DEFAULT_AUDIO_DIR = Path(
    r"C:\Users\chinzorig\Desktop\Husbands\vivienne-10min-speed-1.10"
)
DEFAULT_OUTPUT = Path(
    r"C:\Users\chinzorig\Desktop\Husbands\Husbands_Vivienne_10min_test.mp4"
)
EXPECTED_CLIPS = 214


def parse_timestamp(value: str) -> float:
    """Parse the start of an SRT timestamp or a full SRT time range."""
    start = value.split("-->", 1)[0].strip().replace(",", ".")
    parts = start.split(":")
    if len(parts) != 3:
        raise ValueError(f"Invalid SRT timestamp: {value!r}")
    hours, minutes, seconds = parts
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def locate_manifest(audio_dir: Path, explicit: Path | None) -> Path:
    if explicit is not None:
        path = explicit if explicit.is_absolute() else audio_dir / explicit
        if not path.is_file():
            raise FileNotFoundError(f"Manifest not found: {path}")
        return path

    candidates = sorted(audio_dir.glob("*.json"))
    if len(candidates) != 1:
        raise RuntimeError(
            f"Expected exactly one JSON manifest in {audio_dir}; "
            f"found {len(candidates)}. Pass --manifest explicitly."
        )
    return candidates[0]


def load_clips(manifest_path: Path, audio_dir: Path, duration: float) -> list[dict[str, Any]]:
    data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    clips = data.get("clips")
    if not isinstance(clips, list) or len(clips) != EXPECTED_CLIPS:
        count = len(clips) if isinstance(clips, list) else "missing"
        raise RuntimeError(f"Expected {EXPECTED_CLIPS} clips in manifest; found {count}.")

    prepared: list[dict[str, Any]] = []
    seen_ids: set[int] = set()
    for item in clips:
        cue_id = int(item["cue_id"])
        if cue_id in seen_ids:
            raise RuntimeError(f"Duplicate cue_id in manifest: {cue_id}")
        seen_ids.add(cue_id)

        filename = str(item["filename"])
        # Only allow a plain filename; never accept paths escaping audio_dir.
        if Path(filename).name != filename:
            raise RuntimeError(f"Unsafe audio filename in manifest: {filename!r}")
        audio_path = audio_dir / filename
        if not audio_path.is_file():
            raise FileNotFoundError(f"Audio clip missing for cue {cue_id}: {audio_path}")

        timestamp = item.get("source_timestamp") or item.get("timestamp")
        if not timestamp:
            raise RuntimeError(f"Cue {cue_id} has no source timestamp.")
        start = parse_timestamp(str(timestamp))
        if start < 0 or start >= duration:
            raise RuntimeError(
                f"Cue {cue_id} starts outside the {duration:g}-second preview: {start:.3f}s"
            )
        prepared.append({"cue_id": cue_id, "start": start, "path": audio_path})

    return sorted(prepared, key=lambda clip: (clip["start"], clip["cue_id"]))


def run_ffmpeg(command: list[str]) -> None:
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg exited with code {result.returncode}.")


def render_audio_batch(
    ffmpeg: str,
    clips: list[dict[str, Any]],
    batch_output: Path,
    duration: float,
) -> None:
    """Render a small batch; absolute timeline delays are retained in every batch."""
    command = [ffmpeg, "-hide_banner", "-y"]
    filters: list[str] = []
    labels: list[str] = []

    for index, clip in enumerate(clips):
        command.extend(["-i", str(clip["path"])])
        label = f"clip{index}"
        delay_ms = round(clip["start"] * 1000)
        filters.append(
            f"[{index}:a]"
            f"aformat=sample_rates=44100:channel_layouts=stereo,"
            f"adelay={delay_ms}:all=1"
            f"[{label}]"
        )
        labels.append(f"[{label}]")

    filters.append(
        "".join(labels)
        + f"amix=inputs={len(clips)}:duration=longest:dropout_transition=0:normalize=0,"
        + "alimiter=limit=0.95,"
        + f"atrim=duration={duration:g},asetpts=PTS-STARTPTS[mix]"
    )
    command.extend(
        [
            "-filter_complex", ";".join(filters),
            "-map", "[mix]",
            "-t", str(duration),
            "-c:a", "aac", "-b:a", "192k",
            "-ar", "44100", "-ac", "2",
            "-movflags", "+faststart",
            str(batch_output),
        ]
    )
    run_ffmpeg(command)


def build_final_command(
    ffmpeg: str,
    video: Path,
    batch_files: list[Path],
    output: Path,
    duration: float,
) -> list[str]:
    """Mix temporary batch tracks with video; source audio is deliberately unmapped."""
    command = [ffmpeg, "-hide_banner", "-y", "-i", str(video)]
    for batch_file in batch_files:
        command.extend(["-i", str(batch_file)])

    labels = "".join(f"[{index + 1}:a]" for index in range(len(batch_files)))
    graph = (
        labels
        + f"amix=inputs={len(batch_files)}:duration=longest:dropout_transition=0:normalize=0,"
        + "alimiter=limit=0.95,"
        + f"atrim=duration={duration:g},asetpts=PTS-STARTPTS[mix]"
    )
    command.extend(
        [
            "-filter_complex", graph,
            "-map", "0:v:0", "-map", "[mix]",
            "-t", str(duration),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-ar", "44100", "-ac", "2",
            "-movflags", "+faststart",
            str(output),
        ]
    )
    return command


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mix 214 existing Vivienne MP3 clips onto the first 10 minutes of a video."
    )
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--audio-dir", type=Path, default=DEFAULT_AUDIO_DIR)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--duration", type=float, default=600.0)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    video = args.video.expanduser().resolve()
    audio_dir = args.audio_dir.expanduser().resolve()
    output = args.output.expanduser().resolve()

    if not video.is_file():
        print(f"ERROR: source video not found: {video}", file=sys.stderr)
        return 2
    if not audio_dir.is_dir():
        print(f"ERROR: audio folder not found: {audio_dir}", file=sys.stderr)
        return 2
    if args.duration <= 0:
        print("ERROR: --duration must be greater than zero.", file=sys.stderr)
        return 2
    if output.exists() and not args.overwrite:
        print(
            f"ERROR: output already exists: {output}\n"
            "Choose another --output path or pass --overwrite.",
            file=sys.stderr,
        )
        return 2

    ffmpeg = shutil.which("ffmpeg.exe") or shutil.which("ffmpeg")
    if not ffmpeg:
        print("ERROR: ffmpeg.exe was not found on PATH.", file=sys.stderr)
        return 2

    try:
        manifest = locate_manifest(audio_dir, args.manifest)
        clips = load_clips(manifest, audio_dir, args.duration)
        output.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="vivienne_preview_") as temp_dir:
            temp_path = Path(temp_dir)
            temporary_output = temp_path / "preview_output.mp4"
            batch_size = 20
            batches = [
                clips[index:index + batch_size]
                for index in range(0, len(clips), batch_size)
            ]
            batch_files: list[Path] = []

            print(f"Source video : {video}")
            print(f"Audio folder : {audio_dir}")
            print(f"Manifest     : {manifest}")
            print(f"Existing MP3 : {len(clips)}")
            print(f"Duration     : {args.duration:g} seconds")
            print(f"Audio batches: {len(batches)} (up to {batch_size} clips each)")
            print("Source audio : excluded")
            print("Video stream : copied (not re-encoded)")
            print("Overlaps     : mixed, not truncated")
            print("\nRendering audio batches...")

            for batch_number, batch in enumerate(batches, start=1):
                batch_output = temp_path / f"vivienne_batch_{batch_number:02d}.m4a"
                print(f"  Batch {batch_number}/{len(batches)}: {len(batch)} clips")
                render_audio_batch(ffmpeg, batch, batch_output, args.duration)
                batch_files.append(batch_output)

            print("\nCombining batches with source video...")
            run_ffmpeg(
                build_final_command(
                    ffmpeg, video, batch_files, temporary_output, args.duration
                )
            )

            if not temporary_output.is_file() or temporary_output.stat().st_size == 0:
                raise RuntimeError("FFmpeg completed but the temporary output is missing or empty.")
            # Move into place only after the complete MP4 has been produced successfully.
            shutil.move(str(temporary_output), str(output))

        if not output.is_file() or output.stat().st_size == 0:
            print("ERROR: FFmpeg returned success but output is missing/empty.", file=sys.stderr)
            return 1

        print("\nSUCCESS")
        print(f"Output: {output}")
        print(f"Size  : {output.stat().st_size / (1024 * 1024):.1f} MB")
        return 0

    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
