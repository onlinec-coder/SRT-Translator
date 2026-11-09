from __future__ import annotations
import argparse
import json
import os
import sys
import time
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

PROMPT = """Analyze audio and video frames for localization. Return only valid JSON.
Include scenes, visible people, stable voice profiles, every utterance with
timestamps, verbatim transcript, emotion, vocal delivery, speaker ID, visible
person ID, lip-sync status, confidence, continuity notes, localization notes,
and unresolved questions. Never infer the speaker from plot or appearance.
Confirm lip sync only when synchronized mouth movement is visible. Separate
stable voice traits from temporary delivery. Do not invent words, names,
relationships, or precise word timestamps. Use uncertainty where evidence
is insufficient. Times are seconds from the supplied segment start.
Return a JSON object with keys: analysis_scope, scenes, speakers, utterances,
speaker_continuity, localization_notes, unresolved_questions."""

def main():
    p = argparse.ArgumentParser()
    p.add_argument("video", type=Path)
    p.add_argument("--output", type=Path, default=Path("movie_analysis_reports/movie_analysis.json"))
    p.add_argument("--model")
    p.add_argument("--start", type=float, default=0)
    p.add_argument("--duration", type=float)
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--keep-upload", action="store_true")
    a = p.parse_args()
    video = a.video.resolve()
    output = a.output.resolve()
    if a.start < 0 or (a.duration is not None and a.duration <= 0):
        raise SystemExit("--start must be >= 0 and --duration must be > 0.")
    if not video.is_file():
        raise SystemExit(f"Video not found: {video}")
    if output.exists() and not a.overwrite:
        raise SystemExit("Report exists; pass --overwrite to replace it.")
    if genai is None:
        raise SystemExit("Install google-genai and python-dotenv.")
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is missing.")
    model = a.model or os.getenv("GEMINI_VIDEO_MODEL") or os.getenv("GEMINI_MODEL") or "gemini-3.8-flash"
    temp_path = None
    uploaded = None
    client = genai.Client(api_key=key)
    try:
        source = video
        if a.start or a.duration:
            import shutil, subprocess, tempfile
            ffmpeg = shutil.which("ffmpeg") or (str(Path("ffmpeg.exe").resolve()) if Path("ffmpeg.exe").exists() else None)
            if not ffmpeg:
                raise RuntimeError("ffmpeg is required for segment mode.")
            f = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            temp_path = Path(f.name)
            f.close()
            cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(a.start), "-i", str(video)]
            if a.duration:
                cmd += ["-t", str(a.duration)]
            cmd += ["-c", "copy", str(temp_path)]
            subprocess.run(cmd, check=True)
            source = temp_path
        print("Uploading video...", flush=True)
        uploaded = client.files.upload(file=str(source))
        deadline = time.monotonic() + 900
        while "ACTIVE" not in getattr(getattr(uploaded, "state", None), "name", str(getattr(uploaded, "state", ""))).upper():
            state = getattr(getattr(uploaded, "state", None), "name", str(getattr(uploaded, "state", ""))).upper()
            print("File state:", state, flush=True)
            if "FAILED" in state or time.monotonic() > deadline:
                raise RuntimeError("Video processing failed or timed out.")
            time.sleep(5)
            uploaded = client.files.get(name=uploaded.name)
        response = client.interactions.create(model=model, input=[
            {"type":"video", "uri":uploaded.uri, "mime_type":getattr(uploaded,"mime_type",None) or "video/mp4", "processing":"agentic"},
            {"type":"text", "text":PROMPT}
        ])
        raw = getattr(response, "output_text", None)
        if not raw:
            raise RuntimeError("No output_text returned by Gemini.")
        data = json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())
        required = ["analysis_scope","scenes","speakers","utterances","speaker_continuity","localization_notes","unresolved_questions"]
        if not isinstance(data, dict) or any(k not in data for k in required):
            raise RuntimeError("Response JSON is missing required fields.")
        data["_metadata"] = {"source_file":video.name,"source_start_seconds":a.start,"duration_seconds":a.duration,"model":model,"processing":"agentic","generated_at_utc":datetime.now(timezone.utc).isoformat(),"interaction_id":getattr(response,"id",None),"note":"Separate report; existing project data is not modified."}
        output.parent.mkdir(parents=True, exist_ok=True)
        tmp = output.with_name(output.name + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, output)
        print("Saved:", output)
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)
        if uploaded is not None and not a.keep_upload:
            try:
                client.files.delete(name=uploaded.name)
            except Exception as e:
                print("Upload cleanup warning:", e, file=sys.stderr)

if __name__ == "__main__":
    main()
