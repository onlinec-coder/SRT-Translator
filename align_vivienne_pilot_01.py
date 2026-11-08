#!/usr/bin/env python3
"""Local word-timestamp diagnostic for the six existing Vivienne pilot MP3s.

Uses faster-whisper locally (CPU, multilingual tiny model by default).
No audio upload, no TTS calls, and no audio edits.
Word timestamps are approximate ASR timestamps, not studio-grade forced alignment.
"""
from __future__ import annotations
import json, re, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PILOT = ROOT / "acoustic_comparison_6_results_v2" / "vivienne_production_pilot_01"
MANIFEST = PILOT / "vivienne_production_pilot_01_manifest.json"
SRT = ROOT / "Husbands_mn_v3.srt"
OUT_JSON = PILOT / "vivienne_production_pilot_01_word_alignment.json"
OUT_MD = PILOT / "vivienne_production_pilot_01_word_alignment.md"
MODEL_SIZE = "tiny"  # multilingual; CPU-friendly starting point
COMPUTE_TYPE = "int8"

def parse_time(value: str) -> float:
    h, m, rest = value.split(":")
    s, ms = rest.split(",")
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000

def read_srt(path: Path):
    raw = path.read_text(encoding="utf-8-sig")
    cues = {}
    for block in re.split(r"\r?\n\s*\r?\n", raw.strip()):
        lines = block.strip().splitlines()
        if len(lines) < 3 or not lines[0].strip().isdigit():
            continue
        m = re.match(r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", lines[1])
        if not m:
            continue
        cues[int(lines[0])] = {"start":parse_time(m.group(1)), "end":parse_time(m.group(2)),
                               "text":" ".join(x.strip() for x in lines[2:])}
    return cues

def fmt(sec):
    ms = round(sec*1000)
    return f"{ms//60000:02d}:{(ms//1000)%60:02d}.{ms%1000:03d}"

def main():
    try:
        from faster_whisper import WhisperModel
    except Exception as e:
        print("faster-whisper is not installed in this Python environment.")
        print("Install command: .venv\\Scripts\\python.exe -m pip install faster-whisper")
        print("Import error:", repr(e))
        return 2
    for p in (MANIFEST, SRT):
        if not p.is_file():
            print("Missing required file:", p)
            return 2
    ffmpeg = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if not ffmpeg:
        print("ffmpeg/ffmpeg.exe not found in PATH.")
        return 2

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    srt_cues = read_srt(SRT)
    print(f"Loading Whisper model '{MODEL_SIZE}' on CPU (first run may download model files)...")
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type=COMPUTE_TYPE)
    results, errors = [], []

    for clip in manifest.get("clips", []):
        name = clip["file"]
        audio = PILOT / name
        if not audio.is_file():
            errors.append({"file":name,"error":"MP3 file missing"})
            continue
        cue_ids = clip.get("cue_ids", [])
        missing = [cid for cid in cue_ids if cid not in srt_cues]
        if missing:
            errors.append({"file":name,"error":f"SRT cue IDs missing: {missing}"})
            continue
        base = min(srt_cues[cid]["start"] for cid in cue_ids)
        cue_windows = []
        for cid in cue_ids:
            c = srt_cues[cid]
            cue_windows.append({"cue_id":cid,"start":round(c["start"]-base,3),
                                "end":round(c["end"]-base,3),"text":c["text"]})
        print("Transcribing/alignment timestamps:", name)
        segments, info = model.transcribe(str(audio), language="mn", beam_size=3,
                                           word_timestamps=True, vad_filter=False,
                                           condition_on_previous_text=False)
        words = []
        for seg in segments:
            for w in (seg.words or []):
                words.append({"word":w.word.strip(),"start":round(float(w.start),3),
                              "end":round(float(w.end),3),
                              "probability":round(float(w.probability),3) if w.probability is not None else None})
        cue_rows = []
        for cue in cue_windows:
            assigned = []
            for w in words:
                overlap = max(0.0, min(w["end"],cue["end"])-max(w["start"],cue["start"]))
                if overlap > 0:
                    assigned.append({**w,"overlap_seconds":round(overlap,3)})
            cue_rows.append({**cue,"recognized_words":assigned,
                             "recognized_text":" ".join(x["word"] for x in assigned)})
        results.append({
            "file":name,"cue_ids":cue_ids,"audio_duration_seconds":round(float(info.duration),3),
            "language_detected":info.language,"language_probability":round(float(info.language_probability),3),
            "subtitle_text":clip.get("subtitle_text_without_delivery_tags",""),
            "cue_windows_relative_to_audio":cue_windows,
            "asr_words_relative_to_audio":words,"cue_level_overlap_diagnostic":cue_rows,
            "warning":"Whisper ASR word timestamps are approximate. Low-confidence or missing words require listening; this is not forced alignment."
        })

    report = {"project":"Husbands","pilot":"Vivienne production pilot 01",
              "generated_at":datetime.now(timezone.utc).isoformat(),
              "model":MODEL_SIZE,"device":"cpu","compute_type":COMPUTE_TYPE,
              "audio_source":"existing local MP3s only","network_audio_uploads":0,
              "tts_requests":0,"audio_edits":0,"clips_analyzed":len(results),
              "errors":errors,"clips":results}
    OUT_JSON.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# Vivienne pilot 01 — local word timestamp diagnostic","",
           f"Generated: {report['generated_at']}","",
           "**Method:** faster-whisper multilingual tiny, CPU int8, word timestamps.",
           "**Privacy/scope:** existing local MP3s only; no audio upload, no TTS, no audio edits.",
           "**Limit:** ASR word timestamps are approximate, not forced alignment or a human listening judgment.","",
           "| Clip | Audio | ASR words | SRT cue windows |","|---|---:|---:|---:|"]
    for x in results:
        lines.append(f"| {x['file']} | {x['audio_duration_seconds']:.2f}s | {len(x['asr_words_relative_to_audio'])} | {len(x['cue_windows_relative_to_audio'])} |")
    for x in results:
        lines += ["",f"## {x['file']}","",
                  f"- Detected language: {x['language_detected']} (p={x['language_probability']})",
                  f"- Expected: {x['subtitle_text']}","",
                  "| Cue | Target window (audio-relative) | Words overlapping window |",
                  "|---:|---:|---|"]
        for c in x["cue_level_overlap_diagnostic"]:
            win=f"{fmt(c['start'])}–{fmt(c['end'])}"
            words=" ".join(w["word"] for w in c["recognized_words"]) or "(none recognized)"
            lines.append(f"| {c['cue_id']} | {win} | {words} |")
        lines += ["","**Recognized word timestamps:**",
                  "| Word | Start | End | Probability |","|---|---:|---:|---:|"]
        for w in x["asr_words_relative_to_audio"]:
            lines.append(f"| {w['word']} | {fmt(w['start'])} | {fmt(w['end'])} | {w['probability']} |")
    if errors:
        lines += ["","## Errors",""]+[f"- {e['file']}: {e['error']}" for e in errors]
    OUT_MD.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"Completed: {len(results)}/{len(manifest.get('clips',[]))} clips")
    print("JSON:",OUT_JSON)
    print("Markdown:",OUT_MD)
    print("Audio uploads: 0 | TTS requests: 0 | Audio edits: 0")
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
