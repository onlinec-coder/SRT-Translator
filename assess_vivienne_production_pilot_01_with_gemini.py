#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Gemini listening QA for the six existing Vivienne pilot MP3s."""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

ROOT = Path(__file__).resolve().parent
PILOT = ROOT / "acoustic_comparison_6_results_v2" / "vivienne_production_pilot_01"
MANIFEST = PILOT / "vivienne_production_pilot_01_manifest.json"
OFFLINE_QA = PILOT / "vivienne_production_pilot_01_qa_report.json"
OUT_JSON = PILOT / "vivienne_production_pilot_01_gemini_assessment.json"
OUT_MD = PILOT / "vivienne_production_pilot_01_gemini_assessment.md"

SYSTEM = (
    "You are a careful professional Mongolian-language dubbing QA listener. "
    "Assess the supplied audio itself, not merely the text. Be candid and conservative. "
    "Do not claim to compare against the original actress because no original reference "
    "recording is supplied. Distinguish subjective judgments from measured facts. "
    "Return only valid JSON."
)

PROMPT = r"""
Listen carefully to this Mongolian voice clip as a production dubbing sample for Vivienne
in the film Husbands.

FILE: {file}
SOURCE MOVIE TIME: {source_time}
SUBTITLE CUES: {cue_ids}
TARGET WINDOW: {target_ms} ms
ACTUAL MP3 DURATION (offline measurement): {duration} seconds

EXPECTED MONGOLIAN TEXT:
{expected}

INTENDED ACTING DIRECTION:
{direction}

Evaluate only what is audible:
1. Best-effort transcript and whether it matches the expected text. Mark uncertainty.
2. Mongolian pronunciation, articulation, intelligibility, natural prosody, stress and phrasing.
3. Whether the acting matches the requested emotion; say too weak, appropriate, or exaggerated.
4. Whether the delivery sounds wooden, synthetic, overacted, or natural, with evidence.
5. Pauses, breaths, and rhythm. Distinguish total file duration from audible speech.
6. Fit to the target window. Do not recommend blindly speeding up if it harms emotion or clarity.
7. Audible voice qualities and consistency. You cannot verify identity against the original actress.

Return exactly one JSON object with this structure:
{{
 "file": "{file}",
 "heard_text": "Best effort; use [unclear] where needed",
 "text_match": "match | minor_difference | major_difference | uncertain",
 "text_match_notes": "Brief evidence",
 "scores": {{
   "pronunciation_clarity": 1,
   "intelligibility": 1,
   "natural_mongolian_prosody": 1,
   "acting_emotion_fit": 1,
   "voice_control": 1,
   "overall_dubbing_quality": 1
 }},
 "emotion_assessment": "Specific judgment against the intended direction",
 "pacing_assessment": "Rhythm and target-window fit",
 "pause_assessment": "Naturalness and effect of pauses",
 "voice_assessment": "Audible qualities; no unsupported identity claims",
 "strengths": ["..."],
 "issues": ["..."],
 "recommendations": ["..."],
 "confidence": "high | medium | low",
 "limitations": ["..."]
}}

Scores are integers 1-5: 1 poor/unusable, 2 weak, 3 acceptable with clear issues,
4 good, 5 excellent. Be conservative and explain scores below 4.
""".strip()


def parse_json(text):
    text = (text or "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ValueError("Gemini did not return a JSON object.")
        return json.loads(match.group(0))


def save(results, model, started):
    report = {
        "project": "Husbands",
        "pilot": "Vivienne production pilot 01",
        "assessment_type": "Gemini cloud audio listening assessment",
        "model": model,
        "started_at_utc": started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "clips_expected": 6,
        "clips_assessed": sum(not x.get("error") for x in results),
        "audio_transfer": "Inline audio bytes in six Gemini API requests; Gemini Files API not used.",
        "elevenlabs_requests": 0,
        "audio_modified": False,
        "results": results,
    }
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Vivienne production pilot 01 — Gemini listening assessment",
        "",
        f"- Model: {model}",
        f"- Completed (UTC): {report['completed_at_utc']}",
        f"- Clips assessed: {report['clips_assessed']}/6",
        "- Transfer: inline audio in Gemini requests; Gemini Files API not used.",
        "- ElevenLabs requests: 0; audio modified: no.",
        "",
        "> AI listening assessment, not human studio review. Gemini has no original actress reference recording.",
        "",
    ]
    for x in results:
        lines += [f"## {x['file']}", ""]
        if x.get("error"):
            lines += [f"ERROR: {x['error']}", ""]
            continue
        lines += [
            f"- Heard text: {x.get('heard_text', '')}",
            f"- Text match: {x.get('text_match', 'unknown')}",
            f"- Confidence: {x.get('confidence', 'unknown')}",
            "",
            "| Criterion | Score / 5 |",
            "|---|---:|",
        ]
        for k, label in [
            ("pronunciation_clarity", "Pronunciation clarity"),
            ("intelligibility", "Intelligibility"),
            ("natural_mongolian_prosody", "Natural Mongolian prosody"),
            ("acting_emotion_fit", "Acting / emotion fit"),
            ("voice_control", "Voice control"),
            ("overall_dubbing_quality", "Overall quality"),
        ]:
            lines.append(f"| {label} | {x.get('scores', {}).get(k, '—')} |")
        for k, label in [
            ("text_match_notes", "Text notes"),
            ("emotion_assessment", "Emotion"),
            ("pacing_assessment", "Pacing"),
            ("pause_assessment", "Pauses"),
            ("voice_assessment", "Voice"),
        ]:
            if x.get(k):
                lines += ["", f"**{label}:** {x[k]}"]
        for k, label in [
            ("strengths", "Strengths"),
            ("issues", "Issues"),
            ("recommendations", "Recommendations"),
            ("limitations", "Limitations"),
        ]:
            if x.get(k):
                lines += ["", f"**{label}:**"] + [f"- {v}" for v in x[k]]
        lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--confirm-cloud-upload",
        action="store_true",
        help="Required confirmation: send the six MP3 audio clips to Gemini API.",
    )
    args = parser.parse_args()
    if not args.confirm_cloud_upload:
        print("No audio sent. Re-run with --confirm-cloud-upload when ready.")
        return 2

    load_dotenv(ROOT / ".env")
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY was not found in the local .env file.")
    model = (
        os.getenv("GEMINI_AUDIO_MODEL")
        or os.getenv("GEMINI_MODEL")
        or "gemini-3.5-flash-lite"
    ).strip()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    qa = json.loads(OFFLINE_QA.read_text(encoding="utf-8"))
    qa_by_file = {x["file"]: x for x in qa["clips"]}
    clips = manifest.get("clips", [])
    if len(clips) != 6:
        raise ValueError(f"Expected 6 clips in manifest; found {len(clips)}")

    for c in clips:
        p = PILOT / c["file"]
        if not p.is_file():
            raise FileNotFoundError(f"Missing audio file: {p}")
        if c.get("bytes") and p.stat().st_size != c["bytes"]:
            raise ValueError(f"File size mismatch: {c['file']}")

    print(f"Gemini model: {model}")
    print("Sending exactly six existing MP3s as inline audio, one request per clip.")
    print("No Files API storage, no ElevenLabs calls, no audio edits.")
    print("The API key is read silently from local .env.")
    client = genai.Client(api_key=key)
    started = datetime.now(timezone.utc).isoformat()
    results = []

    for i, c in enumerate(clips, 1):
        name = c["file"]
        q = qa_by_file[name]
        prompt = PROMPT.format(
            file=name,
            source_time=c.get("source_time", "unknown"),
            cue_ids=", ".join(map(str, c.get("cue_ids", []))),
            target_ms=c.get("target_subtitle_window_ms", "unknown"),
            duration=q.get("duration_seconds", "unknown"),
            expected=c.get("subtitle_text_without_delivery_tags", c.get("text_sent_to_tts", "")),
            direction=c.get("delivery_direction", "Not supplied."),
        )
        audio = types.Part.from_bytes(data=(PILOT / name).read_bytes(), mime_type="audio/mpeg")
        print(f"[{i}/6] {name}")
        error = None
        for attempt in range(1, 6):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=[audio, prompt],
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM,
                        response_mime_type="application/json",
                        max_output_tokens=2500,
                    ),
                )
                item = parse_json(response.text)
                item["file"] = name
                results.append(item)
                save(results, model, started)
                print("  OK")
                error = None
                break
            except Exception as exc:
                error = exc
                msg = str(exc).upper()
                temporary = any(s in msg for s in (
                    "503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED",
                    "500", "INTERNAL", "502", "504", "TIMEOUT"
                ))
                if not temporary or attempt == 5:
                    break
                delay = 2 ** attempt
                print(f"  Temporary API error; retrying in {delay}s ({attempt + 1}/5).")
                time.sleep(delay)
        if error is not None:
            results.append({
                "file": name,
                "error": f"{type(error).__name__}: {str(error)[:1200]}",
            })
            save(results, model, started)
            print(f"  FAILED: {type(error).__name__}: {str(error)[:220]}")

    report = save(results, model, started)
    print(f"Finished: {report['clips_assessed']}/6 clips assessed.")
    print(f"JSON: {OUT_JSON}")
    print(f"Markdown: {OUT_MD}")
    print("ElevenLabs requests: 0")
    return 0 if report["clips_assessed"] == 6 else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted. Completed clip results remain saved.")
        raise SystemExit(130)
