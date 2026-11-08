#!/usr/bin/env python3
"""Offline QA for the six existing Vivienne pilot MP3s. No network or TTS calls."""
from __future__ import annotations
import json, math, re, shutil, statistics, subprocess, sys
from array import array
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PILOT = ROOT / "acoustic_comparison_6_results_v2" / "vivienne_production_pilot_01"
MANIFEST = PILOT / "vivienne_production_pilot_01_manifest.json"
OUT_JSON = PILOT / "vivienne_production_pilot_01_qa_report.json"
OUT_MD = PILOT / "vivienne_production_pilot_01_qa_report.md"
RATE, FRAME_MS = 16000, 20

def run(args):
    try:
        p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except FileNotFoundError as e:
        raise RuntimeError(f"Required executable not found: {args[0]}. Install ffmpeg and ffprobe and add them to PATH.") from e
    if p.returncode:
        raise RuntimeError(p.stderr.decode("utf-8", "replace")[-1600:])
    return p.stdout

def dbfs(x):
    return round(20 * math.log10(x), 2) if x > 0 else None

def analyze(path, clip):
    probe = json.loads(run(["ffprobe","-v","error","-show_entries","format=duration,size,bit_rate:stream=codec_name,sample_rate,channels","-of","json",str(path)]))
    fmt, stream = probe.get("format",{}), (probe.get("streams") or [{}])[0]
    raw = run(["ffmpeg","-v","error","-i",str(path),"-f","s16le","-acodec","pcm_s16le","-ac","1","-ar",str(RATE),"pipe:1"])
    samples = array("h"); samples.frombytes(raw)
    if not samples: raise RuntimeError("No decoded audio samples")
    frame_n = RATE * FRAME_MS // 1000
    levels = []
    for i in range(0,len(samples),frame_n):
        chunk=samples[i:i+frame_n]
        rms=math.sqrt(sum(int(x)*int(x) for x in chunk)/len(chunk))/32768
        levels.append(dbfs(rms) if rms else -120.0)
    peak=max(abs(int(x)) for x in samples)/32768
    threshold=max(-48.0,(dbfs(peak) or -48.0)-34.0)
    mask=[v>=threshold for v in levels]
    spans=[]; start=None
    for i,on in enumerate(mask):
        if on and start is None: start=i
        elif not on and start is not None: spans.append((start,i)); start=None
    if start is not None: spans.append((start,len(mask)))
    merged=[]
    for a,b in spans:
        if merged and a-merged[-1][1] <= 6: merged[-1]=(merged[-1][0],b)
        else: merged.append((a,b))
    spans=[(a,b) for a,b in merged if b-a>=4]
    duration=len(samples)/RATE
    active=sum(b-a for a,b in spans)*FRAME_MS/1000
    regions=[{"start_seconds":round(a*FRAME_MS/1000,3),"end_seconds":round(b*FRAME_MS/1000,3),"duration_seconds":round((b-a)*FRAME_MS/1000,3)} for a,b in spans]
    pauses=[{"start_seconds":round(b*FRAME_MS/1000,3),"end_seconds":round(c*FRAME_MS/1000,3),"duration_seconds":round((c-b)*FRAME_MS/1000,3)} for (_,b),(c,_) in zip(spans,spans[1:]) if c-b>=7]
    text=clip.get("subtitle_text_without_delivery_tags") or clip.get("text_sent_to_tts","")
    words=re.findall(r"[^\W_]+(?:[’'-][^\W_]+)*",text,flags=re.UNICODE)
    sorted_levels=sorted(levels); p10=sorted_levels[int((len(sorted_levels)-1)*.1)]; p95=sorted_levels[int((len(sorted_levels)-1)*.95)]
    target=clip.get("target_subtitle_window_ms")
    return {
      "file":path.name,"duration_seconds":round(float(fmt.get("duration",duration)),3),
      "file_size_bytes":int(fmt.get("size",path.stat().st_size)),
      "bit_rate_kbps":round(int(fmt["bit_rate"])/1000,1) if fmt.get("bit_rate") else None,
      "codec":stream.get("codec_name"),"source_sample_rate_hz":int(stream["sample_rate"]) if stream.get("sample_rate") else None,
      "source_channels":stream.get("channels"),"target_subtitle_window_ms":target,
      "duration_vs_target_ms":round(duration*1000-target) if target else None,"subtitle_word_count":len(words),
      "estimated_speech_activity":{"method":"20ms RMS energy threshold; 120ms gap merge; diagnostic only, not ASR","threshold_dbfs":round(threshold,2),
        "active_speech_seconds_estimate":round(active,3),"active_speech_ratio":round(active/duration,3) if duration else None,
        "speech_regions":regions,"internal_pauses_over_140ms":pauses,"internal_pause_count":len(pauses)},
      "level_dynamics":{"peak_dbfs":dbfs(peak),"rms_p10_dbfs":round(p10,2),"rms_median_dbfs":round(statistics.median(levels),2),
        "rms_p95_dbfs":round(p95,2),"near_full_scale_sample_count":sum(abs(int(x))>=32700 for x in samples)},
      "pacing_proxies":{"words_per_minute_full_clip":round(len(words)/duration*60,1) if duration else None,
        "words_per_minute_estimated_active_speech":round(len(words)/active*60,1) if active else None,
        "warning":"Rough subtitle-word and energy proxies; not true spoken-word timing or acting assessment."}
    }

def make_md(report):
    lines=["# Vivienne production pilot 01 — offline audio QA","",f"Generated: {report['generated_at']}","",
      "**Scope:** six existing MP3s only. No TTS generation, audio upload, or network/API calls.",
      "**Limit:** these measurements cannot assess Mongolian pronunciation, emotion, acting quality, or voice identity. Human listening is still required.","",
      "| File | Duration | Target | Difference | Active speech est. | Peak | Whole-clip WPM* | Pauses |",
      "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for x in report["clips"]:
        a=x["estimated_speech_activity"]; p=x["pacing_proxies"]
        target=f"{x['target_subtitle_window_ms']} ms" if x["target_subtitle_window_ms"] else "—"
        diff=f"{x['duration_vs_target_ms']:+} ms" if x["duration_vs_target_ms"] is not None else "—"
        lines.append(f"| {x['file']} | {x['duration_seconds']:.3f}s | {target} | {diff} | {a['active_speech_seconds_estimate']:.2f}s | {x['level_dynamics']['peak_dbfs']} dBFS | {p['words_per_minute_full_clip']} | {a['internal_pause_count']} |")
    lines += ["","*WPM divides subtitle word count by full clip duration; it is not a true spoken-word rate.","","## Per-clip activity and pauses",""]
    for x in report["clips"]:
        lines += [f"### {x['file']}","",f"- Speech regions (estimated): {json.dumps(x['estimated_speech_activity']['speech_regions'],ensure_ascii=False)}",
          f"- Internal pauses: {json.dumps(x['estimated_speech_activity']['internal_pauses_over_140ms'],ensure_ascii=False)}",
          f"- RMS p10 / median / p95: {x['level_dynamics']['rms_p10_dbfs']} / {x['level_dynamics']['rms_median_dbfs']} / {x['level_dynamics']['rms_p95_dbfs']} dBFS",""]
    lines += ["## Interpretation limits","","- RMS activity can be affected by breaths, background noise, music, and quiet consonants.",
      "- Pauses are low-energy gaps, not semantic or dramatic pause labels.","- No ASR, pitch, phoneme alignment, pronunciation, emotion, or speaker-identity judgment is performed.",
      "- No audio is sent to Gemini or any external service. Any cloud audio upload requires a separate explicit decision.",""]
    return "\n".join(lines)

def main():
    if not MANIFEST.is_file(): print(f"Missing manifest: {MANIFEST}"); return 2
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"): print("ffmpeg and ffprobe must be on PATH."); return 2
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); results=[]; errors=[]
    for clip in manifest.get("clips",[]):
        name=clip.get("file",""); path=(PILOT/name).resolve()
        if path.parent!=PILOT.resolve() or not path.is_file(): errors.append({"file":name,"error":"Missing file or invalid path"}); continue
        try: print("Analyzing",name); results.append(analyze(path,clip))
        except Exception as e: errors.append({"file":name,"error":str(e)})
    report={"project":manifest.get("project"),"pilot":manifest.get("pilot"),"voice_name":manifest.get("voice_name"),
      "model_id":manifest.get("model_id"),"generated_at":datetime.now(timezone.utc).isoformat(),
      "analysis_sample_rate_hz":RATE,"analysis_frame_ms":FRAME_MS,"clips_analyzed":len(results),
      "errors":errors,"clips":results,"network_calls_made":0,"tts_requests_made":0}
    OUT_JSON.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    OUT_MD.write_text(make_md(report),encoding="utf-8")
    print(f"Analyzed {len(results)}/{len(manifest.get('clips',[]))} clips")
    print("JSON:",OUT_JSON); print("Markdown:",OUT_MD); print("Network/API calls: 0; TTS requests: 0")
    return 1 if errors else 0

if __name__=="__main__": raise SystemExit(main())
