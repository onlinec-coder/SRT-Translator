from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
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


PROMPT_TEMPLATE = """You are an expert audiovisual localization analyst preparing production metadata
for character-specific dubbing. Analyze ONLY the supplied video segment's actual audio
and visible images. Do not rely on external subtitles, plot assumptions, or invented
dialogue. The segment is one part of a longer film.

KNOWN CHARACTER CATALOG (use canonical spelling and IDs only when evidence supports
the match; aliases help recognize names but are NOT separate characters):
{character_catalog}

SPECIAL IDENTITY RULE FOR THIS FILM:
Narration and Vivienne's inner monologue use the SAME dubbing voice identity,
Vivienne (character_id C001). Keep their speech_role labels distinct, but do not
create a separate Narrator voice identity. Do not apply this rule to unrelated voices.

Return ONLY valid JSON with these top-level keys:
analysis_scope, scenes, speakers, utterances, speaker_continuity, audio_events,
localization_notes, unresolved_questions.

1) COMPLETE AUDIO TRANSCRIPTION — HIGHEST PRIORITY
- Listen through the ENTIRE segment from first to last second.
- Transcribe EVERY audible spoken line, not a plot summary or sample.
- Include dialogue, narration, inner monologue, off-screen speech, interjections,
  short reactions, and overlapping speech when intelligible.
- Never merge two different speakers into one utterance. Split at speaker changes.
- Keep consecutive lines separate when there is a meaningful pause, speaker change,
  emotion change, or dubbing-relevant delivery change.
- Preserve exact audible wording. Do not use on-screen subtitles as a substitute
  for listening. If a word is unclear, mark only that span as [unclear].
- Do not invent speech during silence, music, or sound effects.
- Use utterance-level start_time and end_time in seconds relative to this segment.
  Do not fabricate word-level timestamps.
- If the segment contains many lines, return all of them. Completeness is more
  important than a short response. Do not stop after the first or second utterance.

2) SPEAKERS AND CHARACTER MATCHING
- Create a stable speaker_id within this segment (SPK_001, SPK_002, ...).
- Include character_id, character_name, identity_confidence, and associated_visible_person_id.
- Match a known character from the catalog only when voice, spoken name, direct
  audiovisual evidence, or strong continuity supports it. Otherwise character_id
  and character_name must be null and identity_confidence low.
- Do not confuse a character being visible with that character being the speaker.
- Do not split one voice into multiple speakers just because emotion or volume changes.
- Describe stable voice identity only: perceived pitch range, timbre, resonance,
  texture, cadence, accent only if clearly audible, and distinctive traits.
- Do not infer a real person's age. If useful, describe only perceived vocal maturity
  (e.g. youthful-sounding / mature-sounding) with confidence.
- For this film, narration and Vivienne inner monologue map to the same voice identity
  and character_id C001 when the voice evidence supports it.

3) EACH UTTERANCE — REQUIRED STRUCTURE
Every utterance object must contain:
utterance_id, speaker_id, character_id, character_name, speech_role,
start_time, end_time, verbatim_transcript,
emotion, vocal_delivery, lip_sync, visual_context, dubbing_direction,
pause_before_ms, pause_after_ms, confidence, continuity_notes,
localization_notes, unresolved_questions.

emotion object:
- primary: one concise label (neutral, sadness, anger, fear, joy, disgust,
  surprise, affection, embarrassment, confidence, uncertainty, sarcasm, etc.)
- secondary: optional label or null
- intensity_1_to_5: 1 means subtle, 5 means very strong
- confidence: 0.0 to 1.0
- Use neutral when no clearly audible emotional coloring exists. Do not over-interpret.

vocal_delivery object:
- mode: conversational, narration, whisper, shout, cry, laugh, sing, breathless,
  strained, robotic, or other evidence-based label
- volume: soft, normal, loud, variable, or unknown
- pace: slow, measured, normal, fast, variable, or unknown
- texture: e.g. trembling, breathy, hoarse, pressed, smooth, clipped, or neutral
- voice_action: optional short evidence-based description (sigh, sob, chuckle, gasp)

lip_sync object:
- status: confirmed, likely, not_visible, off_screen, voice_over, uncertain
- evidence: short description of what is actually visible
- confidence: 0.0 to 1.0
Only use confirmed when synchronized mouth movement is clearly visible.

visual_context object:
- scene_id, visible_person_ids, visible_action, shot_context
- use empty/null values when the evidence is unavailable.

dubbing_direction object:
- target_emotion, intensity_1_to_5, pitch_direction, pace, volume, texture,
  breath_and_pause_notes
- These are practical performance directions, not a new interpretation of dialogue.
- Keep directions consistent with audible performance and intended meaning.

4) SCENES AND VISUAL EVIDENCE
- Include scene_id, start_time, end_time, setting, visual_description,
  visible_people (temporary person IDs, description, actions, confidence).
- Keep times relative to this segment.
- Describe actions relevant to who is speaking, emotional context, and dubbing.
- Do not identify a visible person by character name without evidence.

5) AUDIO EVENTS AND TIMING
- Record meaningful non-speech events that affect dubbing: music changes,
  impacts, gasps, sighs, laughter, crying, silence after a line, overlapping voices.
- Include event_type, start_time, end_time, description, relevance_to_dubbing.
- Estimate pause_before_ms and pause_after_ms only when reasonably clear; otherwise null.
- Do not invent precise speech rate or word timings.

6) CONTINUITY AND UNCERTAINTY
- speaker_continuity should describe repeated voice evidence WITHIN this segment.
- Do not claim cross-segment identity; this is a short segment of a longer film.
- Clearly list unresolved speaker/character/lip-sync/transcription questions.
- Confidence must reflect evidence, not certainty of the story.
- If speech is audible but the speaker is unknown, preserve the utterance with
  speaker_id such as SPK_UNKNOWN and explain the uncertainty.

analysis_scope must include segment_start_seconds, segment_end_seconds,
and limitations. Output all arrays even if empty. Return one complete JSON object."""


def elapsed_text(seconds: float) -> str:
    seconds = max(0, int(seconds))
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:02d}:{secs:02d}"


def heartbeat(label, function, interval=3):
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
                    result = future.result()
                    break
                print(f"  ...ажиллаж байна | өнгөрсөн хугацаа {elapsed_text(time.monotonic() - started)}", flush=True)
    print(f"  Дууслаа | {elapsed_text(time.monotonic() - started)}", flush=True)
    return result


def get_state(file_obj):
    value = getattr(file_obj, "state", None)
    return str(getattr(value, "name", None) or getattr(value, "value", None) or value or "UNKNOWN").upper()


def get_interaction_status(interaction):
    value = getattr(interaction, "status", "unknown")
    return str(getattr(value, "value", None) or getattr(value, "name", None) or value).lower()


def get_media_tools():
    ffmpeg = shutil.which("ffmpeg") or (str(Path("ffmpeg.exe").resolve()) if Path("ffmpeg.exe").exists() else None)
    ffprobe = shutil.which("ffprobe") or (str(Path("ffprobe.exe").resolve()) if Path("ffprobe.exe").exists() else None)
    if not ffmpeg or not ffprobe:
        raise RuntimeError("Chunk analysis requires both ffmpeg and ffprobe to be available.")
    return ffmpeg, ffprobe


def probe_duration(ffprobe, video):
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        check=True, capture_output=True, text=True
    )
    return float(result.stdout.strip())


def load_character_catalog(path):
    if not path or not path.is_file():
        print("  Character catalog not found; known-character matching will be disabled.", flush=True)
        return []
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    items = data.get("characters", [])
    catalog = []
    for item in items:
        if item.get("canonical_name") == "Narrator":
            continue
        catalog.append({
            "id": item.get("id"),
            "canonical_name": item.get("canonical_name"),
            "aliases": item.get("aliases", []),
            "gender": item.get("gender"),
            "speech_style": item.get("speech_style", []),
        })
    return catalog


def extract_json(raw):
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    return json.loads(cleaned)


def run_agentic_for_chunk(client, source, model, prompt, args, chunk_index, total_chunks):
    uploaded = None
    try:
        print(f"\n  [Chunk {chunk_index}/{total_chunks}] Uploading {source.name} "
              f"({source.stat().st_size / (1024 * 1024):.1f} MB)", flush=True)
        uploaded = heartbeat(
            "    Gemini Files API руу илгээж байна...",
            lambda: client.files.upload(file=str(source)),
            interval=3
        )
        print(f"    File ID: {uploaded.name}", flush=True)

        print("    Gemini видео файлыг бэлтгэж байна...", flush=True)
        started = time.monotonic()
        deadline = started + args.file_timeout
        last_state = None
        while True:
            state = get_state(uploaded)
            elapsed = time.monotonic() - started
            if state == "ACTIVE":
                print(f"    ACTIVE | бэлтгэл дууслаа ({elapsed_text(elapsed)})", flush=True)
                break
            if state == "FAILED":
                raise RuntimeError(f"Gemini file processing failed: {getattr(uploaded, 'error', None)}")
            if elapsed >= args.file_timeout:
                raise TimeoutError(f"File processing timed out; last state={state}")
            if state != last_state:
                print(f"    Төлөв: {state} | {elapsed_text(elapsed)}", flush=True)
                last_state = state
            else:
                print(f"    {state} хэвээр | {elapsed_text(elapsed)} | дараагийн шалгалт {args.poll_interval:g}s", flush=True)
            time.sleep(args.poll_interval)
            uploaded = client.files.get(name=uploaded.name)

        video_input = {
            "type": "video",
            "uri": uploaded.uri,
            "mime_type": getattr(uploaded, "mime_type", None) or "video/mp4",
            "processing": "agentic",
        }
        interaction_input = [video_input, {"type": "text", "text": prompt}]

        print("    Agentic Analysis эхлүүлж байна...", flush=True)
        try:
            interaction = client.interactions.create(
                model=model, input=interaction_input, background=True
            )
            background = True
        except Exception as error:
            print(f"    Background горим боломжгүй: {error}", flush=True)
            interaction = heartbeat(
                "    Gemini synchronous analysis ажиллаж байна...",
                lambda: client.interactions.create(model=model, input=interaction_input),
                interval=args.poll_interval
            )
            background = False

        interaction_id = getattr(interaction, "id", None)
        if background and interaction_id and not getattr(interaction, "output_text", None):
            started = time.monotonic()
            deadline = started + args.analysis_timeout
            last_status = None
            while True:
                interaction = client.interactions.get(id=interaction_id)
                status = get_interaction_status(interaction)
                elapsed = time.monotonic() - started
                if status == "completed":
                    print(f"    Analysis completed | {elapsed_text(elapsed)}", flush=True)
                    break
                if status in {"failed", "cancelled", "canceled", "requires_action"}:
                    raise RuntimeError(f"Agentic Analysis status={status}; error={getattr(interaction, 'error', None)}")
                if elapsed >= args.analysis_timeout:
                    raise TimeoutError(f"Agentic Analysis timed out after {elapsed_text(elapsed)}")
                if status != last_status:
                    print(f"    Analysis төлөв: {status} | {elapsed_text(elapsed)}", flush=True)
                    last_status = status
                else:
                    print(f"    Gemini шинжилж байна | {elapsed_text(elapsed)}", flush=True)
                time.sleep(args.poll_interval)

        raw = getattr(interaction, "output_text", None)
        if not raw:
            raise RuntimeError("Gemini returned no output_text.")
        data = extract_json(raw)
        required = ["analysis_scope", "scenes", "speakers", "utterances",
                    "speaker_continuity", "audio_events", "localization_notes",
                    "unresolved_questions"]
        if not isinstance(data, dict) or any(key not in data for key in required):
            raise ValueError("Gemini JSON is missing one or more required V3 fields.")
        for key in ("scenes", "speakers", "utterances", "speaker_continuity", "audio_events"):
            if not isinstance(data[key], list):
                raise ValueError(f"V3 field '{key}' must be an array.")
        return data, interaction_id
    finally:
        if uploaded is not None and not args.keep_upload:
            try:
                client.files.delete(name=uploaded.name)
                print("    Түр upload файлыг устгалаа.", flush=True)
            except Exception as error:
                print(f"    Upload cleanup warning: {error}", file=sys.stderr, flush=True)


def offset_time(value, offset):
    if isinstance(value, (int, float)):
        return round(float(value) + offset, 3)
    return value


def main():
    parser = argparse.ArgumentParser(description="Chunked Gemini Agentic audiovisual analysis for dubbing metadata.")
    parser.add_argument("video", type=Path)
    parser.add_argument("--output", type=Path, default=Path("movie_analysis_reports/movie_analysis_v3.json"))
    parser.add_argument("--model")
    parser.add_argument("--start", type=float, default=0)
    parser.add_argument("--duration", type=float)
    parser.add_argument("--chunk-duration", type=float, default=60,
                        help="Analyze short independent chunks in seconds (default: 60). Use 0 for one request.")
    parser.add_argument("--characters", type=Path, default=Path("Husbands_characters_reconciled.json"))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--keep-upload", action="store_true")
    parser.add_argument("--poll-interval", type=float, default=5)
    parser.add_argument("--file-timeout", type=float, default=900)
    parser.add_argument("--analysis-timeout", type=float, default=1800)
    args = parser.parse_args()

    video = args.video.resolve()
    output = args.output.resolve()
    character_path = args.characters.resolve()
    if args.start < 0 or (args.duration is not None and args.duration <= 0):
        raise SystemExit("--start must be >= 0 and --duration must be > 0.")
    if args.chunk_duration < 0 or args.poll_interval <= 0 or args.file_timeout <= 0 or args.analysis_timeout <= 0:
        raise SystemExit("Chunk duration must be >= 0 and polling/timeouts must be > 0.")
    if not video.is_file():
        raise SystemExit(f"Video not found: {video}")
    if output.exists() and not args.overwrite:
        raise SystemExit("Report exists; pass --overwrite to replace it.")
    if genai is None:
        raise SystemExit("Install google-genai and python-dotenv.")
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is missing.")

    model = args.model or os.getenv("GEMINI_VIDEO_MODEL") or os.getenv("GEMINI_MODEL") or "gemini-3.5-flash-lite"
    catalog = load_character_catalog(character_path)
    ffmpeg, ffprobe = get_media_tools()
    full_duration = probe_duration(ffprobe, video)
    requested_end = min(full_duration, args.start + args.duration) if args.duration else full_duration
    total_duration = requested_end - args.start
    if total_duration <= 0:
        raise SystemExit("Requested segment is outside the video duration.")
    chunk_length = args.chunk_duration or total_duration
    chunks = []
    cursor = args.start
    while cursor < requested_end - 0.001:
        length = min(chunk_length, requested_end - cursor)
        chunks.append((cursor, length))
        cursor += length

    print("\nGEMINI AGENTIC VIDEO ANALYSIS — V3", flush=True)
    print(f"Video: {video.name} | Model: {model}", flush=True)
    print(f"Requested range: {args.start:.2f}s–{requested_end:.2f}s ({total_duration:.1f}s)", flush=True)
    print(f"Chunk size: {chunk_length:.1f}s | Total chunks: {len(chunks)}", flush=True)
    print(f"Character catalog: {len(catalog)} known characters", flush=True)
    print("Input source: video audio + video frames only; external SRT is not used.", flush=True)

    client = genai.Client(api_key=api_key)
    report = {
        "analysis_scope": {
            "start_time": args.start,
            "end_time": requested_end,
            "segment_count": len(chunks),
            "notes": "Chunked audiovisual analysis. Times in final report are absolute seconds from the source video."
        },
        "scenes": [],
        "speakers": [],
        "utterances": [],
        "speaker_continuity": [],
        "audio_events": [],
        "localization_notes": [],
        "unresolved_questions": [],
        "quality_checks": {"chunk_results": [], "warnings": []},
    }
    known_character_ids = {item.get("id") for item in catalog if item.get("id")}
    speaker_by_character = {}
    speaker_counter = 0
    scene_counter = 0
    utterance_counter = 0
    event_counter = 0
    interaction_ids = []
    temp_paths = []

    try:
        for index, (chunk_start, chunk_length_actual) in enumerate(chunks, start=1):
            handle = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            chunk_path = Path(handle.name)
            handle.close()
            temp_paths.append(chunk_path)

            print(f"\n[{index}/{len(chunks)}] Cutting source segment {chunk_start:.2f}s–{chunk_start + chunk_length_actual:.2f}s", flush=True)
            command = [
                ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                "-ss", f"{chunk_start:.3f}", "-i", str(video),
                "-t", f"{chunk_length_actual:.3f}", "-c", "copy", str(chunk_path)
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)

            prompt = PROMPT_TEMPLATE.format(
                character_catalog=json.dumps(catalog, ensure_ascii=False, indent=2)
            )
            data, interaction_id = run_agentic_for_chunk(
                client, chunk_path, model, prompt, args, index, len(chunks)
            )
            if interaction_id:
                interaction_ids.append(interaction_id)

            for scene in data["scenes"]:
                scene_counter += 1
                scene["segment_scene_id"] = scene.get("scene_id")
                scene["scene_id"] = f"SCN_{scene_counter:04d}"
                scene["start_time"] = offset_time(scene.get("start_time"), chunk_start)
                scene["end_time"] = offset_time(scene.get("end_time"), chunk_start)
                report["scenes"].append(scene)

            local_speaker_map = {}
            for speaker in data["speakers"]:
                local_id = speaker.get("speaker_id") or f"SPK_LOCAL_{index}_{len(local_speaker_map)+1}"
                character_id = speaker.get("character_id")
                if character_id not in known_character_ids:
                    speaker["character_id"] = None
                    speaker["character_name"] = None
                    speaker["identity_confidence"] = "low"
                    character_id = None
                if character_id:
                    if character_id not in speaker_by_character:
                        speaker_counter += 1
                        global_id = f"SPK_{speaker_counter:03d}"
                        speaker_by_character[character_id] = global_id
                        speaker_copy = dict(speaker)
                        speaker_copy["speaker_id"] = global_id
                        speaker_copy["segment_speaker_ids"] = [local_id]
                        report["speakers"].append(speaker_copy)
                    else:
                        global_id = speaker_by_character[character_id]
                        existing = next(x for x in report["speakers"] if x["speaker_id"] == global_id)
                        if local_id not in existing["segment_speaker_ids"]:
                            existing["segment_speaker_ids"].append(local_id)
                    local_speaker_map[local_id] = global_id
                else:
                    speaker_counter += 1
                    global_id = f"SPK_{speaker_counter:03d}"
                    speaker_copy = dict(speaker)
                    speaker_copy["speaker_id"] = global_id
                    speaker_copy["segment_speaker_ids"] = [local_id]
                    report["speakers"].append(speaker_copy)
                    local_speaker_map[local_id] = global_id

            for utterance in data["utterances"]:
                utterance_counter += 1
                local_id = utterance.get("speaker_id")
                if utterance.get("character_id") not in known_character_ids:
                    utterance["character_id"] = None
                    utterance["character_name"] = None
                utterance["segment_speaker_id"] = local_id
                utterance["speaker_id"] = local_speaker_map.get(local_id, None)
                utterance["utterance_id"] = f"UTT_{utterance_counter:05d}"
                utterance["start_time"] = offset_time(utterance.get("start_time"), chunk_start)
                utterance["end_time"] = offset_time(utterance.get("end_time"), chunk_start)
                if isinstance(utterance.get("visual_context"), dict):
                    local_scene_id = utterance["visual_context"].get("scene_id")
                    mapped = next((s["scene_id"] for s in report["scenes"]
                                   if s.get("segment_scene_id") == local_scene_id
                                   and s.get("start_time", 0) >= chunk_start), None)
                    utterance["visual_context"]["scene_id"] = mapped
                report["utterances"].append(utterance)

            for continuity in data["speaker_continuity"]:
                local_id = continuity.get("speaker_id")
                continuity["segment_speaker_id"] = local_id
                continuity["speaker_id"] = local_speaker_map.get(local_id)
                report["speaker_continuity"].append(continuity)

            for event in data["audio_events"]:
                event_counter += 1
                event["event_id"] = f"AUD_{event_counter:05d}"
                event["start_time"] = offset_time(event.get("start_time"), chunk_start)
                event["end_time"] = offset_time(event.get("end_time"), chunk_start)
                report["audio_events"].append(event)

            notes = data.get("localization_notes", [])
            if isinstance(notes, list):
                report["localization_notes"].extend(notes)
            elif notes:
                report["localization_notes"].append(str(notes))
            unresolved = data.get("unresolved_questions", [])
            if isinstance(unresolved, list):
                report["unresolved_questions"].extend(unresolved)
            elif unresolved:
                report["unresolved_questions"].append(str(unresolved))

            chunk_stats = {
                "chunk_index": index,
                "start_time": chunk_start,
                "end_time": chunk_start + chunk_length_actual,
                "scene_count": len(data["scenes"]),
                "speaker_count": len(data["speakers"]),
                "utterance_count": len(data["utterances"]),
                "audio_event_count": len(data["audio_events"]),
            }
            report["quality_checks"]["chunk_results"].append(chunk_stats)
            if not data["utterances"]:
                warning = (
                    f"Chunk {index} ({chunk_start:.1f}-{chunk_start + chunk_length_actual:.1f}s) "
                    "returned zero utterances; verify whether it is truly silent."
                )
                report["quality_checks"]["warnings"].append(warning)
                print(f"  WARNING: {warning}", flush=True)

            print(
                f"  Segment result: {len(data['scenes'])} scenes, "
                f"{len(data['speakers'])} voices, {len(data['utterances'])} utterances, "
                f"{len(data['audio_events'])} audio events",
                flush=True
            )
            chunk_path.unlink(missing_ok=True)

        # Sort chronologically after merging all independent segment reports.
        for key in ("scenes", "utterances", "audio_events"):
            report[key].sort(key=lambda item: item.get("start_time", 0)
                             if isinstance(item.get("start_time"), (int, float)) else 0)

        # Add quality warnings rather than pretending a sparse transcript is complete.
        empty_chunks = len([x for x in report["utterances"] if x.get("verbatim_transcript")])
        if empty_chunks == 0:
            report["quality_checks"]["warnings"].append(
                "No transcribed utterances were returned; audio transcription requires manual verification."
            )
            report["unresolved_questions"].append(
                "No transcribed utterances were returned; audio transcription requires manual verification."
            )
        report["_metadata"] = {
            "source_file": video.name,
            "source_start_seconds": args.start,
            "duration_seconds": total_duration,
            "model": model,
            "processing": "agentic_chunked",
            "chunk_duration_seconds": chunk_length,
            "segment_count": len(chunks),
            "interaction_ids": interaction_ids,
            "character_catalog_file": character_path.name if catalog else None,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "note": "Standalone report only. Existing SRT, character data, speaker assignments, and review exports are not modified."
        }

        print("\nТайланг шалгаж хадгалж байна...", flush=True)
        output.parent.mkdir(parents=True, exist_ok=True)
        temp_output = output.with_name(output.name + ".tmp")
        temp_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temp_output, output)

        print("\nV3 ANALYSIS COMPLETE", flush=True)
        print(f"  Scenes: {len(report['scenes'])}", flush=True)
        print(f"  Speakers: {len(report['speakers'])}", flush=True)
        print(f"  Utterances: {len(report['utterances'])}", flush=True)
        print(f"  Audio events: {len(report['audio_events'])}", flush=True)
        print(f"  Unresolved questions: {len(report['unresolved_questions'])}", flush=True)
        print(f"  Saved: {output}", flush=True)
        if len(report["utterances"]) < len(chunks):
            print("  WARNING: Fewer utterances than chunks; inspect completeness before trusting this report.", flush=True)

    finally:
        for path in temp_paths:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
