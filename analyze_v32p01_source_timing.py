import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

# Measure the ORIGINAL spoken-word windows for the V32P01 60-second pilot.
# This is an analysis-only step: it does not alter or regenerate any TTS audio.

BASE = Path(r"C:\Users\chinzorig\Desktop\Husbands")
VIDEO = BASE / "Husbands.mp4"
AUDIO_DIR = BASE / "vivienne-V32P01-audio"
MANIFEST = AUDIO_DIR / "manifest.json"
WORK_DIR = BASE / "V32P01_timing_analysis"
WAV_FILE = WORK_DIR / "source_first_60s.wav"
OUTPUT_CSV = WORK_DIR / "V32P01_source_speech_windows.csv"
PREVIEW_SECONDS = 60.0

MODEL_SIZE = "tiny.en"
CUE_MARGIN = 1.25
MAX_WORD_GAP = 0.65

FFMPEG = shutil.which("ffmpeg.exe") or shutil.which("ffmpeg")


def fail(message):
    raise SystemExit("\nERROR: " + message)


def timestamp_to_seconds(value):
    value = value.strip().replace(",", ".")
    hours, minutes, seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def parse_source_time(value):
    parts = value.split("-->")
    if len(parts) != 2:
        fail(f"Invalid source_time: {value}")
    return timestamp_to_seconds(parts[0]), timestamp_to_seconds(parts[1])


for required in (VIDEO, MANIFEST):
    if not required.is_file():
        fail(f"File not found: {required}")

if not FFMPEG:
    fail("ffmpeg.exe was not found.")

try:
    from faster_whisper import WhisperModel
except ImportError:
    fail(
        "faster-whisper is not installed in this Python environment. "
        "Activate the project venv and run: pip install faster-whisper"
    )

WORK_DIR.mkdir(parents=True, exist_ok=True)

with MANIFEST.open("r", encoding="utf-8") as file:
    manifest = json.load(file)

clips = manifest.get("clips", [])
if not clips:
    fail("No clips found in manifest.json.")

print("Extracting the original film audio (first 60 seconds)...")
extract = subprocess.run(
    [
        FFMPEG, "-y", "-i", str(VIDEO),
        "-t", str(PREVIEW_SECONDS),
        "-vn", "-ac", "1", "-ar", "16000",
        "-c:a", "pcm_s16le", str(WAV_FILE),
    ]
)
if extract.returncode != 0 or not WAV_FILE.is_file():
    fail("Could not extract source audio. Check the FFmpeg output above.")

print(f"Loading Whisper model '{MODEL_SIZE}' on CPU (int8)...")
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

print("Transcribing with word-level timestamps. First run may download the small model...")
segments, info = model.transcribe(
    str(WAV_FILE),
    language="en",
    beam_size=1,
    word_timestamps=True,
    vad_filter=True,
)

words = []
for segment in segments:
    for word in (segment.words or []):
        token = (word.word or "").strip()
        if token:
            words.append({
                "start": float(word.start),
                "end": float(word.end),
                "word": token,
            })

if not words:
    fail("Whisper returned no word timestamps. Check the source audio.")

rows = []
for index, clip in enumerate(clips, start=1):
    cue_start, cue_end = parse_source_time(clip["source_time"])
    search_start = max(0.0, cue_start - CUE_MARGIN)
    search_end = min(PREVIEW_SECONDS, cue_end + CUE_MARGIN)

    nearby = [
        word for word in words
        if word["end"] >= search_start and word["start"] <= search_end
    ]

    if not nearby:
        rows.append({
            "sequence": clip.get("sequence", index),
            "clip_id": clip["clip_id"],
            "cue_start": round(cue_start, 3),
            "cue_end": round(cue_end, 3),
            "cue_duration": round(cue_end - cue_start, 3),
            "source_speech_start": "",
            "source_speech_end": "",
            "source_speech_duration": "",
            "recognized_words": "",
            "generated_audio_duration": round(float(clip["duration_seconds"]), 3),
            "suggested_atempo": "",
            "status": "NO_WORDS_FOUND_CHECK_MANUALLY",
        })
        continue

    # Split nearby words into utterance groups when the gap is substantial.
    groups = []
    current = [nearby[0]]
    for word in nearby[1:]:
        if word["start"] - current[-1]["end"] <= MAX_WORD_GAP:
            current.append(word)
        else:
            groups.append(current)
            current = [word]
    groups.append(current)

    cue_mid = (cue_start + cue_end) / 2
    # Prefer the group centered nearest this cue, with overlap as a tie-breaker.
    def group_score(group):
        start = group[0]["start"]
        end = group[-1]["end"]
        midpoint_distance = abs(((start + end) / 2) - cue_mid)
        overlap = max(0.0, min(end, cue_end) - max(start, cue_start))
        return (midpoint_distance - overlap * 0.5)

    chosen = min(groups, key=group_score)
    speech_start = chosen[0]["start"]
    speech_end = chosen[-1]["end"]
    speech_duration = max(0.05, speech_end - speech_start)
    generated_duration = float(clip["duration_seconds"])
    raw_atempo = generated_duration / speech_duration

    # Report a conservative suggestion only. Never apply speed changes automatically.
    suggested_atempo = min(1.25, max(0.90, raw_atempo))
    status = "REVIEW"
    if raw_atempo > 1.25:
        status = "WOULD_NEED_OVER_1_25X_REVIEW_TEXT_OR_TIMING"
    elif raw_atempo < 0.90:
        status = "GENERATED_SHORTER_THAN_SOURCE_REVIEW"

    rows.append({
        "sequence": clip.get("sequence", index),
        "clip_id": clip["clip_id"],
        "cue_start": round(cue_start, 3),
        "cue_end": round(cue_end, 3),
        "cue_duration": round(cue_end - cue_start, 3),
        "source_speech_start": round(speech_start, 3),
        "source_speech_end": round(speech_end, 3),
        "source_speech_duration": round(speech_duration, 3),
        "recognized_words": " ".join(word["word"] for word in chosen),
        "generated_audio_duration": round(generated_duration, 3),
        "suggested_atempo": round(suggested_atempo, 3),
        "status": status,
    })

with OUTPUT_CSV.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\n========== SOURCE TIMING ANALYSIS COMPLETE ==========")
print(f"Detected language: {info.language} ({info.language_probability:.2f})")
print(f"Word timestamps: {len(words)}")
print(f"CSV report: {OUTPUT_CSV}")
print("\nReview each row's recognized_words and source_speech_start/end.")
print("Whisper timestamps are estimates; correct any mismatched phrase manually.")
print("No TTS was generated and no audio was sped up.")
for row in rows:
    print(
        f"{row['clip_id']}: "
        f"source={row['source_speech_start']}–{row['source_speech_end']} "
        f"({row['source_speech_duration']}s), "
        f"generated={row['generated_audio_duration']}s, "
        f"atempo suggestion={row['suggested_atempo']} "
        f"[{row['status']}]"
    )
