# -*- coding: utf-8 -*-
"""
Objective Original vs Speech acoustic measurements for Husbands.
Uses only Python standard library; no activation or third-party packages needed.

Input WAVs: Desktop
Output: acoustic_comparison_6_results_v2/objective_measurements.json
          acoustic_comparison_6_results_v2/objective_measurements.csv

Measurements per cue:
- RMS level (dBFS), peak level (dBFS), crest factor
- estimated F0 median and 10th/90th percentiles (autocorrelation; voiced frames only)
- voiced-frame ratio, zero-crossing rate
- frame-to-frame RMS range

F0 is an approximate acoustic estimate, not a voice identity or emotion classifier.
"""

import csv
import json
import math
import statistics
import struct
import wave
from array import array
from pathlib import Path

PROJECT = Path(r"C:\Users\chinzorig\SRT-Translator")
DESKTOP = Path(r"C:\Users\chinzorig\Desktop")
OUTPUT_DIR = PROJECT / "acoustic_comparison_6_results_v2"

SETS = {
    "normal": {
        "original": "Husbands_test_01_normal_original.wav",
        "speech": "Husbands_test_01_normal_speech.wav",
        "cues": {
            66: (0.458, 2.000),
            67: (2.000, 3.666),
            68: (5.300, 6.500),
            69: (6.900, 8.300),
            70: (8.300, 9.900),
        },
    },
    "emotional": {
        "original": "Husbands_test_02_emotional_original.wav",
        "speech": "Husbands_test_02_emotional_speech.wav",
        "cues": {
            698: (0.400, 1.958),
            699: (2.000, 2.958),
            700: (3.200, 4.166),
            701: (5.200, 6.500),
            702: (6.600, 7.749),
        },
    },
    "quiet": {
        "original": "Husbands_test_03_quiet_original.wav",
        "speech": "Husbands_test_03_quiet_speech.wav",
        "cues": {
            9: (1.000, 2.125),
            10: (2.583, 3.600),
            11: (5.374, 6.749),
            12: (6.800, 7.541),
            13: (8.541, 9.800),
            15: (12.600, 13.500),
            16: (13.600, 14.958),
            17: (15.000, 16.374),
            18: (16.500, 18.166),
            19: (18.200, 20.000),
        },
    },
}

TARGET_SR = 8000
FRAME_MS = 30
HOP_MS = 10
MIN_F0 = 65.0
MAX_F0 = 400.0


def read_wav_mono(path):
    with wave.open(str(path), "rb") as wf:
        channels = wf.getnchannels()
        width = wf.getsampwidth()
        sample_rate = wf.getframerate()
        frames = wf.getnframes()
        raw = wf.readframes(frames)

    if width == 1:
        vals = [((b - 128) / 128.0) for b in raw]
    elif width == 2:
        count = len(raw) // 2
        vals_i = struct.unpack("<" + "h" * count, raw)
        vals = [v / 32768.0 for v in vals_i]
    elif width == 3:
        vals = []
        for i in range(0, len(raw) - 2, 3):
            v = raw[i] | (raw[i + 1] << 8) | (raw[i + 2] << 16)
            if v & 0x800000:
                v -= 0x1000000
            vals.append(v / 8388608.0)
    elif width == 4:
        count = len(raw) // 4
        vals_i = struct.unpack("<" + "i" * count, raw)
        vals = [v / 2147483648.0 for v in vals_i]
    else:
        raise ValueError(f"Unsupported PCM sample width: {width} bytes")

    if channels > 1:
        vals = [
            sum(vals[i:i + channels]) / channels
            for i in range(0, len(vals) - channels + 1, channels)
        ]

    # Linear interpolation to a common 8 kHz analysis rate.
    if sample_rate != TARGET_SR:
        new_len = int(len(vals) * TARGET_SR / sample_rate)
        converted = []
        ratio = sample_rate / TARGET_SR
        for j in range(new_len):
            pos = j * ratio
            left = int(pos)
            frac = pos - left
            if left + 1 < len(vals):
                converted.append(vals[left] * (1.0 - frac) + vals[left + 1] * frac)
            elif left < len(vals):
                converted.append(vals[left])
        vals = converted

    return vals, sample_rate, channels, width


def percentile(values, p):
    if not values:
        return None
    ordered = sorted(values)
    pos = (len(ordered) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    frac = pos - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def estimate_pitch(frame):
    # Remove DC and apply a Hann window.
    n = len(frame)
    mean = sum(frame) / n
    x = [(frame[i] - mean) * (0.5 - 0.5 * math.cos(2 * math.pi * i / (n - 1)))
         for i in range(n)]
    energy = sum(v * v for v in x)
    if energy < 1e-7:
        return None

    min_lag = int(TARGET_SR / MAX_F0)
    max_lag = min(int(TARGET_SR / MIN_F0), n - 2)
    correlations = []
    for lag in range(min_lag, max_lag + 1):
        corr = 0.0
        for i in range(n - lag):
            corr += x[i] * x[i + lag]
        correlations.append((lag, corr / energy))

    best_lag, best_corr = max(correlations, key=lambda pair: pair[1])
    if best_corr < 0.28:
        return None

    # Parabolic interpolation around the correlation maximum.
    idx = best_lag - min_lag
    if 0 < idx < len(correlations) - 1:
        y0 = correlations[idx - 1][1]
        y1 = correlations[idx][1]
        y2 = correlations[idx + 1][1]
        denom = y0 - 2 * y1 + y2
        offset = 0.5 * (y0 - y2) / denom if abs(denom) > 1e-12 else 0.0
    else:
        offset = 0.0
    refined_lag = best_lag + max(-0.5, min(0.5, offset))
    return TARGET_SR / refined_lag


def analyze_segment(samples, start_s, end_s):
    start = max(0, int(start_s * TARGET_SR))
    end = min(len(samples), int(end_s * TARGET_SR))
    segment = samples[start:end]
    if len(segment) < int(0.08 * TARGET_SR):
        raise ValueError("Cue segment is too short or outside the WAV duration")

    peak = max(abs(v) for v in segment)
    rms = math.sqrt(sum(v * v for v in segment) / len(segment))
    rms_db = 20 * math.log10(max(rms, 1e-12))
    peak_db = 20 * math.log10(max(peak, 1e-12))
    crest = peak_db - rms_db

    frame_len = int(TARGET_SR * FRAME_MS / 1000)
    hop = int(TARGET_SR * HOP_MS / 1000)
    pitches = []
    frame_rms_db = []
    zcr_values = []
    for offset in range(0, len(segment) - frame_len + 1, hop):
        frame = segment[offset:offset + frame_len]
        frms = math.sqrt(sum(v * v for v in frame) / len(frame))
        frame_rms_db.append(20 * math.log10(max(frms, 1e-12)))
        crossings = sum(
            1 for a, b in zip(frame, frame[1:])
            if (a < 0 <= b) or (a >= 0 > b)
        )
        zcr_values.append(crossings / (len(frame) - 1))
        pitch = estimate_pitch(frame)
        if pitch is not None:
            pitches.append(pitch)

    return {
        "duration_s": round(len(segment) / TARGET_SR, 3),
        "rms_dbfs": round(rms_db, 2),
        "peak_dbfs": round(peak_db, 2),
        "crest_factor_db": round(crest, 2),
        "f0_median_hz": round(statistics.median(pitches), 1) if pitches else None,
        "f0_p10_hz": round(percentile(pitches, 0.10), 1) if pitches else None,
        "f0_p90_hz": round(percentile(pitches, 0.90), 1) if pitches else None,
        "voiced_frame_ratio": round(len(pitches) / max(1, len(frame_rms_db)), 3),
        "zero_crossing_rate": round(statistics.mean(zcr_values), 4) if zcr_values else None,
        "frame_rms_p10_dbfs": round(percentile(frame_rms_db, 0.10), 2) if frame_rms_db else None,
        "frame_rms_p90_dbfs": round(percentile(frame_rms_db, 0.90), 2) if frame_rms_db else None,
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_results = {
        "method": {
            "sample_rate_hz": TARGET_SR,
            "frame_ms": FRAME_MS,
            "hop_ms": HOP_MS,
            "pitch_method": "windowed autocorrelation; approximate F0",
            "note": "Measurements include any background audio inside each cue; interpret RMS and ZCR cautiously.",
        },
        "sets": {},
    }
    csv_rows = []

    for set_name, spec in SETS.items():
        all_results["sets"][set_name] = {}
        for version in ("original", "speech"):
            filename = spec[version]
            path = DESKTOP / filename
            if not path.exists():
                raise FileNotFoundError(f"Audio file not found: {path}")
            samples, source_sr, channels, width = read_wav_mono(path)
            print(f"\n{set_name}/{version}: {filename}")
            print(f"  source={source_sr} Hz, channels={channels}, sample_width={width * 8}-bit")

            cue_results = {}
            for cue_id, (start_s, end_s) in spec["cues"].items():
                metrics = analyze_segment(samples, start_s, end_s)
                cue_results[str(cue_id)] = metrics
                row = {
                    "set": set_name,
                    "version": version,
                    "cue": cue_id,
                    "start_s": start_s,
                    "end_s": end_s,
                    **metrics,
                }
                csv_rows.append(row)
                print(
                    f"  Cue {cue_id}: RMS {metrics['rms_dbfs']} dBFS | "
                    f"F0 {metrics['f0_median_hz']} Hz | "
                    f"voiced {metrics['voiced_frame_ratio']}"
                )
            all_results["sets"][set_name][version] = {
                "file": filename,
                "source_sample_rate_hz": source_sr,
                "channels": channels,
                "sample_width_bits": width * 8,
                "cues": cue_results,
            }

        # Add direct paired differences: Speech minus Original.
        comparisons = {}
        for cue_id in spec["cues"]:
            o = all_results["sets"][set_name]["original"]["cues"][str(cue_id)]
            s = all_results["sets"][set_name]["speech"]["cues"][str(cue_id)]
            comparisons[str(cue_id)] = {
                "speech_minus_original_rms_db": round(s["rms_dbfs"] - o["rms_dbfs"], 2),
                "speech_minus_original_peak_db": round(s["peak_dbfs"] - o["peak_dbfs"], 2),
                "speech_minus_original_f0_hz": (
                    round(s["f0_median_hz"] - o["f0_median_hz"], 1)
                    if s["f0_median_hz"] is not None and o["f0_median_hz"] is not None
                    else None
                ),
                "speech_minus_original_crest_db": round(s["crest_factor_db"] - o["crest_factor_db"], 2),
            }
        all_results["sets"][set_name]["paired_differences_speech_minus_original"] = comparisons

    json_path = OUTPUT_DIR / "objective_measurements.json"
    csv_path = OUTPUT_DIR / "objective_measurements.csv"
    json_path.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    print("\n" + "=" * 60)
    print("DONE — objective acoustic measurements complete")
    print(f"JSON: {json_path}")
    print(f"CSV:  {csv_path}")
    print("No existing analysis JSON files were modified.")


if __name__ == "__main__":
    main()
