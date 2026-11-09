#!/usr/bin/env python3
"""Match Whisper's original-film word timestamps to the exact English SRT text.

Analysis only: does not generate TTS, edit MP3s, or apply speed changes.
Requires faster-whisper in the dedicated .venv-whisper environment.
"""
from __future__ import annotations

import csv
import difflib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = Path(r"C:\Users\chinzorig\Desktop\Husbands")
VIDEO = BASE / "Husbands.mp4"
AUDIO_DIR = BASE / "vivienne-V32P01-audio"
MANIFEST = AUDIO_DIR / "manifest.json"
SRT = ROOT / "Husbands_ocr_en.srt"
OUT_DIR = BASE / "V32P01_timing_analysis"
OUT_CSV = OUT_DIR / "V32P01_srt_matched_source_windows.csv"
OUT_JSON = OUT_DIR / "V32P01_srt_matched_source_windows.json"
WAV = OUT_DIR / "source_first_60s.wav"

MODEL_SIZE = "tiny.en"
COMPUTE_TYPE = "int8"
SEARCH_MARGIN = 2.0
MIN_MATCH_RATIO = 0.55
TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?|\d+", re.I)


def stop(message: str) -> None:
    raise SystemExit("\nERROR: " + message)


def seconds(value: str) -> float:
    value = value.strip().replace(",", ".")
    h, m, s = value.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def parse_srt(path: Path) -> dict[int, dict]:
    raw = path.read_text(encoding="utf-8-sig")
    cues = {}
    for block in re.split(r"\r?\n\s*\r?\n", raw.strip()):
        lines = block.strip().splitlines()
        if len(lines) < 3 or not lines[0].strip().isdigit():
            continue
        match = re.match(
            r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})",
            lines[1],
        )
        if not match:
            continue
        cues[int(lines[0])] = {
            "start": seconds(match.group(1)),
            "end": seconds(match.group(2)),
            "text": " ".join(line.strip() for line in lines[2:]),
        }
    return cues


def tokens(text: str) -> list[str]:
    return [x.lower() for x in TOKEN_RE.findall(text)]


def best_alignment(expected: list[str], words: list[dict], low: float, high: float):
    candidates = [
        (i, w) for i, w in enumerate(words)
        if w["end"] >= low and w["start"] <= high
    ]
    if not candidates or not expected:
        return None

    # Search contiguous ASR spans near the subtitle window. The SRT wording,
    # not subtitle timing alone, determines which spoken phrase is selected.
    n_expected = len(expected)
    min_len = max(1, int(n_expected * 0.65))
    max_len = min(len(candidates), max(min_len, int(n_expected * 1.45) + 3))
    best = None

    for start_pos in range(len(candidates)):
        for length in range(min_len, max_len + 1):
            end_pos = start_pos + length
            if end_pos > len(candidates):
                break
            span = candidates[start_pos:end_pos]
            # Candidate words must be consecutive in the complete ASR stream.
            if any(span[j][0] + 1 != span[j + 1][0] for j in range(len(span) - 1)):
                continue
            heard = [tokens(x[1]["word"]) for x in span]
            heard = [t for group in heard for t in group]
            if not heard:
                continue
            ratio = difflib.SequenceMatcher(
                None, expected, heard, autojunk=False
            ).ratio()
            first, last = span[0][1], span[-1][1]
            midpoint = (first["start"] + last["end"]) / 2
            # Tie-break toward the subtitle window, without allowing timing
            # proximity to outweigh a clearly better text match.
            cue_mid = (low + high) / 2
            distance_penalty = min(abs(midpoint - cue_mid) / 20.0, 0.08)
            score = ratio - distance_penalty
            if best is None or score > best["score"]:
                best = {
                    "start": first["start"],
                    "end": last["end"],
                    "ratio": ratio,
                    "score": score,
                    "recognized": " ".join(x[1]["word"] for x in span),
                    "word_count": len(span),
                }
    return best


def main() -> int:
    for path in (VIDEO, MANIFEST, SRT):
        if not path.is_file():
            stop(f"Required file not found: {path}")
    ffmpeg = shutil.which("ffmpeg.exe") or shutil.which("ffmpeg")
    if not ffmpeg:
        stop("ffmpeg.exe not found in PATH.")

    try:
        from faster_whisper import WhisperModel
    except Exception as exc:
        stop(
            "faster-whisper is unavailable in this Python environment. "
            "Run this script with .venv-whisper\\Scripts\\python.exe. "
            f"Import error: {exc!r}"
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cues = parse_srt(SRT)

    if not WAV.is_file():
        print("Extracting first 60 seconds of source audio...")
        result = subprocess.run([
            ffmpeg, "-y", "-i", str(VIDEO), "-t", "60",
            "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(WAV)
        ])
        if result.returncode:
            stop("FFmpeg could not extract source audio.")

    print(f"Loading Whisper {MODEL_SIZE} on CPU int8...")
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type=COMPUTE_TYPE)
    print("Transcribing original film with word timestamps...")
    segments, info = model.transcribe(
        str(WAV), language="en", beam_size=3, word_timestamps=True,
        vad_filter=False, condition_on_previous_text=False
    )
    words = []
    for segment in segments:
        for word in segment.words or []:
            value = (word.word or "").strip()
            if value:
                words.append({
                    "word": value,
                    "start": float(word.start),
                    "end": float(word.end),
                })

    rows = []
    for clip in manifest.get("clips", []):
        cue_ids = clip.get("cue_ids", [])
        missing = [cid for cid in cue_ids if cid not in cues]
        if missing:
            rows.append({
                "sequence": clip.get("sequence"),
                "clip_id": clip.get("clip_id"),
                "cue_ids": ",".join(map(str, cue_ids)),
                "status": f"MISSING_SRT_CUES:{missing}",
            })
            continue

        selected = [cues[cid] for cid in cue_ids]
        expected_text = " ".join(c["text"] for c in selected)
        expected_tokens = tokens(expected_text)
        cue_start = min(c["start"] for c in selected)
        cue_end = max(c["end"] for c in selected)
        alignment = best_alignment(
            expected_tokens, words,
            max(0.0, cue_start - SEARCH_MARGIN),
            min(60.0, cue_end + SEARCH_MARGIN),
        )

        generated = float(clip["duration_seconds"])
        if not alignment:
            rows.append({
                "sequence": clip.get("sequence"),
                "clip_id": clip.get("clip_id"),
                "cue_ids": ",".join(map(str, cue_ids)),
                "srt_text": expected_text,
                "generated_duration": generated,
                "status": "NO_TEXT_MATCH",
            })
            continue

        source_duration = max(0.01, alignment["end"] - alignment["start"])
        ratio = alignment["ratio"]
        raw_atempo = generated / source_duration
        if ratio < MIN_MATCH_RATIO:
            status = "LOW_TEXT_MATCH_MANUAL_REVIEW"
            suggested = ""
        elif raw_atempo > 1.25:
            status = "GENERATED_LONGER_THAN_SOURCE_REVIEW"
            suggested = round(min(raw_atempo, 1.25), 3)
        elif raw_atempo < 0.90:
            status = "GENERATED_SHORTER_THAN_SOURCE_REVIEW"
            suggested = round(max(raw_atempo, 0.90), 3)
        else:
            status = "TEXT_MATCHED_REVIEW"
            suggested = round(raw_atempo, 3)

        rows.append({
            "sequence": clip.get("sequence"),
            "clip_id": clip.get("clip_id"),
            "cue_ids": ",".join(map(str, cue_ids)),
            "cue_start": round(cue_start, 3),
            "cue_end": round(cue_end, 3),
            "cue_window_duration": round(cue_end - cue_start, 3),
            "source_speech_start": round(alignment["start"], 3),
            "source_speech_end": round(alignment["end"], 3),
            "source_speech_duration": round(source_duration, 3),
            "srt_text": expected_text,
            "whisper_matched_text": alignment["recognized"],
            "text_match_ratio": round(ratio, 3),
            "generated_duration": round(generated, 3),
            "raw_required_atempo": round(raw_atempo, 3),
            "conservative_atempo_reference": suggested,
            "status": status,
        })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with OUT_CSV.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    report = {
        "method": "English SRT text matched against Whisper word timestamps",
        "detected_language": info.language,
        "language_probability": round(info.language_probability, 3),
        "asr_word_count": len(words),
        "warning": (
            "Whisper timestamps and fuzzy text matching are estimates. "
            "Review matched text and confidence before changing playback speed. "
            "No TTS/audio changes were made."
        ),
        "clips": rows,
    }
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nSOURCE TIMING / SRT MATCH COMPLETE")
    print(f"Language: {info.language} ({info.language_probability:.2f})")
    print(f"Whisper words: {len(words)}")
    print(f"CSV: {OUT_CSV}")
    print(f"JSON: {OUT_JSON}")
    for row in rows:
        print(
            f"{row.get('clip_id')}: "
            f"{row.get('source_speech_start', 'n/a')}–"
            f"{row.get('source_speech_end', 'n/a')} "
            f"match={row.get('text_match_ratio', 'n/a')} "
            f"generated={row.get('generated_duration', 'n/a')} "
            f"atempo={row.get('conservative_atempo_reference', 'n/a')} "
            f"[{row.get('status')}]"
        )
    print("\nNo TTS was generated and no MP3 was modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
