import csv
import json
import re
import shutil
import subprocess
from pathlib import Path

# V32P01 short preview: first 60 seconds of the source film.
# Places all generated Vivienne clips at their original film timestamps.

BASE = Path(r"C:\Users\chinzorig\Desktop\Husbands")
VIDEO = BASE / "Husbands.mp4"
AUDIO_DIR = BASE / "vivienne-V32P01-audio"
MANIFEST = AUDIO_DIR / "manifest.json"

PREVIEW_SECONDS = 60.0
OUTPUT_DIR = BASE / "V32P01_preview"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_VIDEO = OUTPUT_DIR / "Husbands_V32P01_preview.mp4"
OUTPUT_CSV = OUTPUT_DIR / "V32P01_timing_QA.csv"

FFMPEG = shutil.which("ffmpeg.exe") or shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe.exe") or shutil.which("ffprobe")


def fail(message):
    raise SystemExit("\nERROR: " + message)


def timestamp_to_seconds(value):
    value = value.strip().replace(",", ".")
    hours, minutes, seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def parse_source_time(value):
    parts = re.split(r"\s*-->\s*", value)
    if len(parts) != 2:
        fail(f"Invalid source_time in manifest: {value}")
    return timestamp_to_seconds(parts[0]), timestamp_to_seconds(parts[1])


for required in (VIDEO, MANIFEST):
    if not required.is_file():
        fail(f"File not found: {required}")

if not FFMPEG:
    fail("ffmpeg.exe was not found. Check your FFmpeg installation.")

with MANIFEST.open("r", encoding="utf-8") as file:
    manifest = json.load(file)

clips = manifest.get("clips", [])
if len(clips) != 13:
    fail(f"Expected 13 generated clips, found {len(clips)}.")

inputs = ["-i", str(VIDEO)]
filters = []
clip_rows = []
duck_intervals = []

for index, clip in enumerate(clips):
    clip_id = clip["clip_id"]
    audio_path = AUDIO_DIR / f"{clip_id}.mp3"
    if not audio_path.is_file():
        fail(f"Missing audio file: {audio_path}")

    start, target_end = parse_source_time(clip["source_time"])
    target_duration = target_end - start
    actual_duration = float(clip["duration_seconds"])
    actual_end = start + actual_duration

    if start >= PREVIEW_SECONDS:
        fail(f"{clip_id} starts after the {PREVIEW_SECONDS:.0f}-second preview.")

    inputs.extend(["-i", str(audio_path)])
    delay_ms = round(start * 1000)

    filters.append(
        f"[{index + 1}:a]asetpts=PTS-STARTPTS,"
        f"adelay={delay_ms}|{delay_ms},"
        f"atrim=duration={PREVIEW_SECONDS:.3f}[voice{index}]"
    )

    duck_end = min(actual_end, PREVIEW_SECONDS)
    duck_intervals.append(f"between(t,{start:.3f},{duck_end:.3f})")

    clip_rows.append({
        "sequence": clip.get("sequence", index + 1),
        "clip_id": clip_id,
        "start_seconds": round(start, 3),
        "target_end_seconds": round(target_end, 3),
        "target_duration_seconds": round(target_duration, 3),
        "actual_duration_seconds": round(actual_duration, 3),
        "actual_end_seconds": round(actual_end, 3),
        "overrun_seconds": round(actual_duration - target_duration, 3),
        "status": "CHECK" if actual_duration > target_duration + 0.15 else "OK",
    })

# Keep the original film audio, lowering it while the new Vivienne voice is heard.
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
    FFMPEG,
    "-y",
    *inputs,
    "-filter_complex", ";".join(filters),
    "-map", "0:v:0",
    "-map", "[aout]",
    "-t", f"{PREVIEW_SECONDS:.3f}",
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-crf", "23",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-movflags", "+faststart",
    str(OUTPUT_VIDEO),
]

print("\nGenerating the 60-second V32P01 preview...")
print(f"Source video: {VIDEO}")
print(f"Vivienne audio clips: {len(clips)}")
print(f"Preview duration: {PREVIEW_SECONDS:.0f} seconds")
print(f"Output: {OUTPUT_VIDEO}\n")

result = subprocess.run(command)
if result.returncode != 0:
    fail("FFmpeg failed. Review the error above.")

with OUTPUT_CSV.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=clip_rows[0].keys())
    writer.writeheader()
    writer.writerows(clip_rows)

# Verify the exported container duration when ffprobe is available.
if FFPROBE:
    probe = subprocess.run(
        [
            FFPROBE, "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(OUTPUT_VIDEO),
        ],
        capture_output=True,
        text=True,
    )
    if probe.returncode == 0 and probe.stdout.strip():
        exported_duration = float(probe.stdout.strip())
        print(f"Verified output duration: {exported_duration:.3f} seconds")

print("\n========== COMPLETE ==========")
print(f"Preview video: {OUTPUT_VIDEO}")
print(f"Timing QA: {OUTPUT_CSV}")
print("\nClip timing:")
for row in clip_rows:
    print(
        f"{row['clip_id']}: start={row['start_seconds']:.3f}s, "
        f"target={row['target_duration_seconds']:.3f}s, "
        f"audio={row['actual_duration_seconds']:.3f}s, "
        f"overrun={row['overrun_seconds']:+.3f}s [{row['status']}]"
    )
