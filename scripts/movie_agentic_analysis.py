from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google import genai
except ImportError:
    genai = None


PROMPT = """You are performing a careful audiovisual analysis of a film segment for
professional subtitle localization and character-specific dubbing.

Analyze the actual audio and visual evidence. Do not provide only a plot summary.
Return ONLY one valid JSON object with these exact top-level keys:
analysis_scope, scenes, speakers, utterances, speaker_continuity,
localization_notes, unresolved_questions.

SCENES:
- Divide the segment into meaningful scenes/shots or continuous dramatic beats.
- Include scene_id, start_time, end_time, setting, visual_description.
- Describe visible people with stable temporary IDs when identity is uncertain.
- Record actions and relevant mouth visibility/synchronization evidence.

SPEAKERS:
- Identify every distinct audible voice, not just the narrator.
- Create a stable speaker_id for each distinct voice (SPK_001, SPK_002, ...).
- Include stable_voice_profile and associated_visible_person_id.
- Distinguish voice identity from delivery style. The same person remains the
  same speaker across scenes even when emotion, volume, or delivery changes.
- Do not create a new speaker merely because the voice becomes emotional.
- Do not assume a visible person is speaking simply because they are on screen.

UTTERANCES:
- Transcribe EVERY audible spoken utterance in chronological order, including
  dialogue, narration, voice-over, inner monologue, brief interjections, and
  clearly audible off-screen speech.
- Do not omit dialogue after the opening line or summarize multiple lines.
- Each utterance must include: utterance_id, speaker_id, visible_person_id,
  start_time, end_time, verbatim_transcript, emotion, vocal_delivery,
  lip_sync_status, confidence, continuity_notes, localization_notes,
  unresolved_questions.
- Use timestamps in seconds from the beginning of the supplied segment.
- Keep one utterance per continuous turn/line where possible. Do not invent
  word-level timestamps.
- If speech is audible but the speaker cannot be identified, use an unknown
  speaker ID and explain why. Never force an attribution.
- If a line is narration or inner monologue, label that role in continuity_notes
  or localization_notes; do not automatically treat it as a separate person.
- Mark lip_sync_status as confirmed only when synchronized mouth movement is
  actually visible. Otherwise use not_visible, off_screen, voice_over, or
  uncertain as appropriate.

CONTINUITY AND ACCURACY:
- Track recurring voices across the whole segment in speaker_continuity.
- Link a visible person to a speaker only when supported by lip movement,
  synchronized turn-taking, or other direct audiovisual evidence.
- Keep character names uncertain unless spoken or otherwise clearly established.
- Never invent dialogue, names, relationships, emotions, or events.
- Use confidence values from 0.0 to 1.0 and explain low-confidence decisions.
- If the audio is unclear, mark it as unclear instead of fabricating a transcript.
- Check the entire supplied timeline before finalizing. Do not stop after the
  first utterance or return a single sample line when more speech is present.

The analysis_scope should state the actual segment start/end and any limitations.
The final JSON must be complete and machine-readable, with arrays for scenes,
speakers, utterances, and speaker_continuity."""


def elapsed_text(seconds: float) -> str:
    seconds = max(0, int(seconds))
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def run_with_heartbeat(label, function, interval=3):
    """Run a blocking SDK call while keeping the user informed."""
    started = time.monotonic()
    print(label, flush=True)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(function)
        while True:
            try:
                result = future.result(timeout=interval)
                break
            except FutureTimeout:
                if future.done():
                    # The worker itself raised TimeoutError; surface that error.
                    result = future.result()
                    break
                print(
                    f"  ...still working | elapsed {elapsed_text(time.monotonic() - started)}",
                    flush=True,
                )
    print(f"  Completed | elapsed {elapsed_text(time.monotonic() - started)}", flush=True)
    return result


def state_name(value) -> str:
    state = getattr(value, "state", None)
    return getattr(state, "name", str(state or "UNKNOWN")).upper()


def main():
    p = argparse.ArgumentParser(
        description="Analyze a film segment with Gemini Agentic Video Analysis."
    )
    p.add_argument("video", type=Path)
    p.add_argument("--output", type=Path, default=Path("movie_analysis_reports/movie_analysis.json"))
    p.add_argument("--model")
    p.add_argument("--start", type=float, default=0)
    p.add_argument("--duration", type=float)
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--keep-upload", action="store_true")
    p.add_argument("--poll-interval", type=float, default=5,
                   help="Seconds between Gemini status checks (default: 5).")
    p.add_argument("--file-timeout", type=float, default=900,
                   help="Maximum seconds to wait for video processing (default: 900).")
    p.add_argument("--analysis-timeout", type=float, default=3600,
                   help="Maximum seconds to wait for Agentic Analysis (default: 3600).")
    a = p.parse_args()

    video = a.video.resolve()
    output = a.output.resolve()
    if a.start < 0 or (a.duration is not None and a.duration <= 0):
        raise SystemExit("--start must be >= 0 and --duration must be > 0.")
    if a.poll_interval <= 0 or a.file_timeout <= 0 or a.analysis_timeout <= 0:
        raise SystemExit("Polling interval and timeout values must be > 0.")
    if not video.is_file():
        raise SystemExit(f"Video not found: {video}")
    if output.exists() and not a.overwrite:
        raise SystemExit("Report exists; pass --overwrite to replace it.")
    if genai is None:
        raise SystemExit("Install google-genai and python-dotenv.")
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is missing.")

    model = (
        a.model
        or os.getenv("GEMINI_VIDEO_MODEL")
        or os.getenv("GEMINI_MODEL")
        or "gemini-3.8-flash"
    )
    temp_path = None
    uploaded = None
    client = genai.Client(api_key=key)

    try:
        source = video
        if a.start or a.duration:
            import shutil
            import subprocess
            import tempfile

            print("\n[1/7] Preparing requested video segment", flush=True)
            ffmpeg = shutil.which("ffmpeg") or (
                str(Path("ffmpeg.exe").resolve()) if Path("ffmpeg.exe").exists() else None
            )
            if not ffmpeg:
                raise RuntimeError("ffmpeg is required for segment mode.")
            f = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            temp_path = Path(f.name)
            f.close()
            cmd = [
                ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                "-ss", str(a.start), "-i", str(video),
            ]
            if a.duration:
                cmd += ["-t", str(a.duration)]
            cmd += ["-c", "copy", str(temp_path)]
            run_with_heartbeat(
                "  Cutting video segment with FFmpeg...",
                lambda: subprocess.run(cmd, check=True, capture_output=True, text=True),
            )
            source = temp_path
            print(f"  Segment ready: start={a.start:.2f}s, duration={a.duration or 'to end'}", flush=True)
        else:
            print("\n[1/7] Using the full source video", flush=True)

        print("\n[2/7] Uploading video to Gemini Files API", flush=True)
        print("  Upload progress percentage is not exposed by this SDK; showing elapsed time.", flush=True)
        uploaded = run_with_heartbeat(
            f"  Sending {source.name} ({source.stat().st_size / (1024 * 1024):.1f} MB)...",
            lambda: client.files.upload(file=str(source)),
            interval=3,
        )
        print(f"  Gemini file created: {uploaded.name}", flush=True)

        print("\n[3/7] Waiting for Gemini to prepare the video", flush=True)
        file_started = time.monotonic()
        deadline = file_started + a.file_timeout
        last_state = None
        while True:
            state = state_name(uploaded)
            elapsed = time.monotonic() - file_started
            if state == "ACTIVE":
                print(
                    f"  Video is ACTIVE and ready | total processing time {elapsed_text(elapsed)}",
                    flush=True,
                )
                break
            if state == "FAILED":
                detail = getattr(uploaded, "error", None)
                raise RuntimeError(f"Gemini video processing failed: {detail or 'No error details'}")
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Gemini video processing timed out after {elapsed_text(elapsed)} "
                    f"(last state: {state})."
                )
            if state != last_state:
                print(f"  State changed: {state} | elapsed {elapsed_text(elapsed)}", flush=True)
                last_state = state
            else:
                print(
                    f"  Still preparing video: {state} | elapsed {elapsed_text(elapsed)} "
                    f"| checking again in {a.poll_interval:g}s",
                    flush=True,
                )
            time.sleep(a.poll_interval)
            uploaded = client.files.get(name=uploaded.name)

        print("\n[4/7] Starting Gemini Agentic Video Analysis", flush=True)
        print(f"  Model: {model}", flush=True)
        print("  Task: inspect the timeline, identify voices, transcribe utterances, and track continuity.", flush=True)
        interaction_input = [
            {
                "type": "video",
                "uri": uploaded.uri,
                "mime_type": getattr(uploaded, "mime_type", None) or "video/mp4",
                "processing": "agentic",
            },
            {"type": "text", "text": PROMPT},
        ]
        try:
            interaction = client.interactions.create(
                model=model,
                input=interaction_input,
                background=True,
            )
            background_mode = True
        except Exception as background_error:
            # Some model/API combinations may not accept background execution.
            # Fall back to a synchronous request, but keep the console alive with
            # an elapsed-time heartbeat instead of appearing frozen.
            print(
                f"  Background mode unavailable ({background_error}). "
                "Falling back to monitored synchronous mode.",
                flush=True,
            )
            interaction = run_with_heartbeat(
                "  Gemini is running Agentic Analysis synchronously...",
                lambda: client.interactions.create(
                    model=model,
                    input=interaction_input,
                ),
                interval=a.poll_interval,
            )
            background_mode = False

        interaction_id = getattr(interaction, "id", None)
        if not interaction_id and not getattr(interaction, "output_text", None):
            raise RuntimeError("Gemini returned neither an interaction ID nor output_text.")
        if background_mode:
            print(f"  Background analysis started. Interaction ID: {interaction_id}", flush=True)

        print("\n[5/7] Monitoring Agentic Analysis", flush=True)
        if background_mode and not getattr(interaction, "output_text", None):
            analysis_started = time.monotonic()
            analysis_deadline = analysis_started + a.analysis_timeout
            last_status = None
            while True:
                interaction = client.interactions.get(id=interaction_id)
                status = str(getattr(interaction, "status", "unknown")).lower()
                elapsed = time.monotonic() - analysis_started

                if status == "completed":
                    print(
                        f"  Agentic Analysis completed | elapsed {elapsed_text(elapsed)}",
                        flush=True,
                    )
                    break
                if status in {"failed", "cancelled", "canceled", "requires_action"}:
                    detail = getattr(interaction, "error", None)
                    raise RuntimeError(
                        f"Agentic Analysis ended with status '{status}': "
                        f"{detail or 'No additional error details'}"
                    )
                if time.monotonic() >= analysis_deadline:
                    raise TimeoutError(
                        f"Agentic Analysis timed out after {elapsed_text(elapsed)}. "
                        f"Interaction ID: {interaction_id}"
                    )
                if status != last_status:
                    print(f"  Analysis status: {status} | elapsed {elapsed_text(elapsed)}", flush=True)
                    last_status = status
                else:
                    print(
                        f"  Gemini is still analyzing the video | status={status} "
                        f"| elapsed {elapsed_text(elapsed)} "
                        f"| next update in {a.poll_interval:g}s",
                        flush=True,
                    )
                time.sleep(a.poll_interval)
        else:
            print("  Synchronous Agentic Analysis returned its result.", flush=True)

        print("\n[6/7] Retrieving and validating Gemini's result", flush=True)
        raw = getattr(interaction, "output_text", None)
        if not raw:
            raise RuntimeError("Gemini marked the interaction completed but returned no output_text.")
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()
        data = json.loads(cleaned)
        required = [
            "analysis_scope", "scenes", "speakers", "utterances",
            "speaker_continuity", "localization_notes", "unresolved_questions",
        ]
        if not isinstance(data, dict) or any(k not in data for k in required):
            raise RuntimeError("Response JSON is missing required fields.")
        for key_name in ("scenes", "speakers", "utterances", "speaker_continuity"):
            if not isinstance(data[key_name], list):
                raise RuntimeError(f"Response field '{key_name}' must be a JSON array.")

        data["_metadata"] = {
            "source_file": video.name,
            "source_start_seconds": a.start,
            "duration_seconds": a.duration,
            "model": model,
            "processing": "agentic",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "interaction_id": interaction_id,
            "note": "Separate report; existing project data is not modified.",
        }

        print("\n[7/7] Saving analysis report", flush=True)
        output.parent.mkdir(parents=True, exist_ok=True)
        tmp = output.with_name(output.name + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, output)

        print("\nSUCCESS: Agentic video analysis finished.", flush=True)
        print(f"  Scenes: {len(data['scenes'])}", flush=True)
        print(f"  Speakers: {len(data['speakers'])}", flush=True)
        print(f"  Utterances: {len(data['utterances'])}", flush=True)
        print(f"  Report: {output}", flush=True)

    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)
        if uploaded is not None and not a.keep_upload:
            print("\nCleaning up temporary Gemini upload...", flush=True)
            try:
                client.files.delete(name=uploaded.name)
                print("  Temporary upload deleted.", flush=True)
            except Exception as e:
                print(f"  Upload cleanup warning: {e}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
