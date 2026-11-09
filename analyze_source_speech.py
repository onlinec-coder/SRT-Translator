from __future__ import annotations

import csv
import sys
from pathlib import Path

from faster_whisper import WhisperModel


VIDEO = Path(r"C:\Users\chinzorig\Desktop\Husbands\Husbands.mp4")
OUTPUT = Path(r"C:\Users\chinzorig\Desktop\Husbands\source_speech_60s.csv")
CLIP_START = 0.0
CLIP_END = 60.0
MODEL_SIZE = "tiny.en"


def main() -> int:
    if not VIDEO.is_file():
        print(f"ERROR: Source video not found: {VIDEO}", file=sys.stderr)
        return 1

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    print(f"Source: {VIDEO}")
    print(f"Window: {CLIP_START:.1f}-{CLIP_END:.1f} seconds")
    print(f"Loading Whisper model: {MODEL_SIZE}")
    print("The first run may download the model (about 75 MB).")

    model = WhisperModel(
        MODEL_SIZE,
        device="cpu",
        compute_type="int8",
        cpu_threads=2,
        num_workers=1,
    )

    print("Transcribing original English speech with word timestamps...")
    segments, info = model.transcribe(
        str(VIDEO),
        language="en",
        task="transcribe",
        word_timestamps=True,
        vad_filter=False,
        clip_timestamps=f"{CLIP_START},{CLIP_END}",
        beam_size=1,
        condition_on_previous_text=False,
    )

    rows: list[dict[str, object]] = []
    for segment in segments:
        if not segment.words:
            continue

        for word in segment.words:
            token = word.word.strip()
            if not token:
                continue

            rows.append(
                {
                    "start": round(float(word.start), 3),
                    "end": round(float(word.end), 3),
                    "duration": round(float(word.end - word.start), 3),
                    "word": token,
                    "probability": round(float(word.probability), 3),
                    "segment_start": round(float(segment.start), 3),
                    "segment_end": round(float(segment.end), 3),
                    "segment_text": segment.text.strip(),
                }
            )

    fieldnames = [
        "start",
        "end",
        "duration",
        "word",
        "probability",
        "segment_start",
        "segment_end",
        "segment_text",
    ]

    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print()
    print(f"Detected words: {len(rows)}")
    print(f"Detected language: {info.language}")
    print(f"Language probability: {info.language_probability:.3f}")
    print(f"CSV saved to: {OUTPUT}")
    print()
    print("First 40 recognized words:")
    for row in rows[:40]:
        print(
            f'{row["start"]:7.3f}-{row["end"]:7.3f} '
            f'({row["duration"]:5.3f}s) {row["word"]}'
        )

    if not rows:
        print("WARNING: No words were detected. Check the source audio/video.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
