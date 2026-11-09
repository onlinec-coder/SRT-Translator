import csv
import json
import shutil
import subprocess
from pathlib import Path

# Creates two comparison previews from existing V32P01 MP3 files.
# Original MP3s are never modified. No TTS/API calls are made.

BASE = Path(r"C:\Users\chinzorig\Desktop\Husbands")
VIDEO = BASE / "Husbands.mp4"
AUDIO_DIR = BASE / "vivienne-V32P01-audio"
MANIFEST = AUDIO_DIR / "manifest.json"
OUTPUT_DIR = BASE / "V32P01_speed_trials"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PREVIEW_SECONDS = 60.0
TARGET_CLIPS = {
    "V32P01_CUE_0001",
    "V32P01_CUE_0002",
    "V32P01_CUES_0004_0005",
    "V32P01_CUES_0009_0010",
}
SPEEDS = {
    "A_1.15x": 1.15,
    "B_1.25x": 1.25,
}

FFMPEG = shutil.which("ffmpeg.exe") or shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe.exe") or shutil.which("ffprobe")


def fail(message):
    raise SystemExit("\nERROR: " + message)


def timestamp_to_seconds(value):
    value = value.strip().replace(",", ".")
    hours, minutes, seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def parse_source_time(value):
    parts = value.split("-->")
    if len(parts) != 2:
        fail(f"Invalid source_time in manifest: {value}")
    return timestamp_to_seconds(parts[0]), timestamp_to_seconds(parts[1])


for required in (VIDEO, MANIFEST):
    if not required.is_file():
        fail(f"File not found: {required}")
if not FFMPEG:
    fail("ffmpeg.exe was not found. Check FFmpeg installation.")

with MANIFEST.open("r", encoding="utf-8") as file:
    manifest = json.load(file)

clips = manifest.get("clips", [])
if len(clips) != 13:
    fail(f"Expected 13 manifest clips, found {len(clips)}.")

for clip in clips:
    audio_path = AUDIO_DIR / f"{clip['clip_id']}.mp3"
    if not audio_path.is_file():
        fail(f"Missing original MP3: {audio_path}")

found_targets = {c["clip_id"] for c in clips} & TARGET_CLIPS
if found_targets != TARGET_CLIPS:
    fail(f"Manifest is missing target clips: {sorted(TARGET_CLIPS - found_targets)}")

report_rows = []

for variant, speed in SPEEDS.items():
    output_video = OUTPUT_DIR / f"Husbands_V32P01_speed_{variant}.mp4"
    output_csv = OUTPUT_DIR / f"V32P01_speed_{variant}_QA.csv"

    # Input 0 is the source film; inputs 1..13 are the original generated clips.
    inputs = ["-i", str(VIDEO)]
    filters = []
    duck_intervals = []
    variant_rows = []

    for index, clip in enumerate(clips):
        clip_id = clip["clip_id"]
        audio_path = AUDIO_DIR / f"{clip_id}.mp3"
        inputs.extend(["-i", str(audio_path)])

        start, target_end = parse_source_time(clip["source_time"])
        source_duration = target_end - start
        original_duration = float(clip["duration_seconds"])
        applied_speed = speed if clip_id in TARGET_CLIPS else 1.0
        expected_duration = original_duration / applied_speed

        audio_filter = f"[{index + 1}:a]asetpts=PTS-STARTPTS"
        if applied_speed != 1.0:
            audio_filter += f",atempo={applied_speed:.3f}"
        audio_filter += (
            f",adelay={round(start * 1000)}|{round(start * 1000)},"
            f"atrim=duration={PREVIEW_SECONDS:.3f}[voice{index}]"
        )
        filters.append(audio_filter)

        duck_end = min(start + expected_duration, PREVIEW_SECONDS)
        duck_intervals.append(f"between(t,{start:.3f},{duck_end:.3f})")

        row = {
            "variant": variant,
            "clip_id": clip_id,
            "changed": "YES" if clip_id in TARGET_CLIPS else "NO",
            "atempo": f"{applied_speed:.3f}",
            "source_start": round(start, 3),
            "source_speech_window_seconds": round(source_duration, 3),
            "original_audio_seconds": round(original_duration, 3),
            "trial_audio_seconds": round(expected_duration, 3),
            "trial_overrun_vs_window_seconds": round(expected_duration - source_duration, 3),
        }
        variant_rows.append(row)
        report_rows.append(row)

    duck_expression = "+".join(duck_intervals)
    filters.append(
        f"[0:a]atrim=duration={PREVIEW_SECONDS:.3f},"
        f"asetpts=PTS-STARTPTS,"
        f"volume=0.20:enable='{duck_expression}'[original]"
    )

    mix_inputs = "[original]" + "".join(
        f"[voice{index}]" for index in range(len(clips))
    )
    filters.append(
        f"{mix_inputs}amix=inputs={len(clips) + 1}:"
        f"duration=longest:dropout_transition=0:normalize=0,"
        f"alimiter=limit=0.95,atrim=duration={PREVIEW_SECONDS:.3f}[aout]"
    )

    command = [
        FFMPEG, "-y", *inputs,
        "-filter_complex", ";".join(filters),
        "-map", "0:v:0", "-map", "[aout]",
        "-t", f"{PREVIEW_SECONDS:.3f}",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(output_video),
    ]

    print(f"\nBuilding {variant} comparison preview...")
    print("Changed clips:", ", ".join(sorted(TARGET_CLIPS)))
    result = subprocess.run(command)
    if result.returncode != 0:
        fail(f"FFmpeg failed while creating {variant}.")

    with output_csv.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=variant_rows[0].keys())
        writer.writeheader()
        writer.writerows(variant_rows)

    if FFPROBE:
        probe = subprocess.run(
            [
                FFPROBE, "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(output_video),
            ],
            capture_output=True, text=True,
        )
        if probe.returncode == 0 and probe.stdout.strip():
            print(f"Verified duration: {float(probe.stdout.strip()):.3f}s")

    print(f"Video: {output_video}")
    print(f"QA: {output_csv}")

summary_path = OUTPUT_DIR / "V32P01_speed_trial_summary.csv"
with summary_path.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=report_rows[0].keys())
    writer.writeheader()
    writer.writerows(report_rows)

print("\n========== SPEED TRIALS COMPLETE ==========")
print(f"Output folder: {OUTPUT_DIR}")
print("A = 1.15x; B = 1.25x on the four selected clips.")
print("All other clips remain at original speed.")
print("Original MP3 files were not modified.")
print("No TTS or paid API calls were made.")
