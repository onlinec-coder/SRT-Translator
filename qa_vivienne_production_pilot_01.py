#!/usr/bin/env python3
"""QA the six existing Vivienne pilot MP3s. Never generates TTS.

Default: local-only measurements.
Optional: --gemini uploads the existing MP3s for audio review.
"""
from __future__ import annotations
import argparse, json, math, os, re, shutil, subprocess, sys
from array import array
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIO_DIR = ROOT / "acoustic_comparison_6_results_v2" / "vivienne_production_pilot_01"
OUT_DIR = AUDIO_DIR / "qa"
SR = 16000
WINDOW = 320  # 20 ms at 16 kHz
CLIPS = [
 {"file":"pilot_01_cue427_hurt_disappointed.mp3","cue_ids":[427],"time":"00:13:19.166–00:13:20.583","target_ms":1417,"text":"Тэр чамайг огт мэддэггүй юм байна.","direction":"Гомдол, итгэл алдрал, үл ялиг зэвүүцэл. Нам, шивнэх шахуу боловч үг тод."},
 {"file":"pilot_02_cues430-434_hurt_realization.mp3","cue_ids":[430,431,432,433,434],"time":"00:13:24.600–00:13:30.000","target_ms":5400,"text":"Тэр ерөөсөө мэддэггүй байсан юм. Тэгэхээр энэ олон жилийн турш, баяр ёслол бүрээр, сүргийн найр бүрээр тэр надтай уулзахаар ирдэггүй байжээ.","direction":"Cue 427-той ижил гомдол, итгэл алдрал. Нэг холбоотой бодол; cue бүрийн заагт хиймэл завсарлагагүй."},
 {"file":"pilot_03_cues776-778_assertive_explanation.mp3","cue_ids":[776,777,778],"time":"00:24:36.791–00:24:42.125","target_ms":5334,"text":"Хоёр хоногийн өмнө энэ гэрт ирсэн эмэгтэй би биш. Тэр үед би Колдвеллийн харшид оройн хоол идэж байсан. Ахлах ахлагч Лорант эхнэрийнхээ хамт байсан юм.","direction":"Тайван, өөртөө итгэлтэй, баримтад тулгуурласан тайлбар. Уур, ёжлол, хэт жүжиглэлтгүй."},
 {"file":"pilot_04_cue758_firm_correction.mp3","cue_ids":[758],"time":"00:23:55.800–00:23:56.958","target_ms":1158,"text":"Та хүнээ андуурчээ.","direction":"Тайван боловч шийдэмгий залруулга, үл ялиг дургүйцэл. Ууртай эсвэл ёжтой биш."},
 {"file":"pilot_05_cue963_disgusted_refusal.mp3","cue_ids":[963],"time":"00:30:08.800–00:30:09.791","target_ms":991,"text":"Ингэж болохгүй.","direction":"Зэвүүцэл, бага зэрэг барьсан уур, шийдэмгий татгалзалт. Орилохгүй, ширүүн түрэмгий биш."},
 {"file":"pilot_06_cues1203-1205_natural_resolution.mp3","cue_ids":[1203,1204,1205],"time":"00:37:24.541–00:37:27.583","target_ms":3042,"text":"Тохирлоо. Гэхдээ энэ удаа бид хоёулаа аз жаргалтай болно.","direction":"Энгийн, үнэн сэтгэлийн, тайван Vivienne. Хэт баярласан, жүжиглэсэн өнгөгүй."},
]

def load_env():
    p = ROOT / ".env"
    if not p.is_file(): return
    for line in p.read_text(encoding="utf-8-sig").splitlines():
        line=line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k,v=line.split("=",1); k=k.strip(); v=v.strip()
        if (v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"')): v=v[1:-1]
        if k and k not in os.environ: os.environ[k]=v

def find_ffmpeg():
    p=os.environ.get("FFMPEG_EXE")
    if p and Path(p).is_file(): return p
    return shutil.which("ffmpeg.exe") or shutil.which("ffmpeg")

def decode(ffmpeg,path):
    cmd=[ffmpeg,"-hide_banner","-loglevel","error","-i",str(path),"-vn","-ac","1","-ar",str(SR),"-f","s16le","pipe:1"]
    r=subprocess.run(cmd,capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr.decode("utf-8",errors="replace")[-1000:])
    samples=array("h"); samples.frombytes(r.stdout)
    if sys.byteorder!="little": samples.byteswap()
    if not samples: raise RuntimeError("Decoded audio is empty")
    return samples

def dbfs(x): return round(20*math.log10(max(x,1e-9)/32768),2)

def measure(samples,target_ms):
    duration=len(samples)/SR
    levels=[]; peak=0; clipped=0
    for i in range(0,len(samples),WINDOW):
        block=samples[i:i+WINDOW]
        if not block: continue
        peak=max(peak,max(abs(x) for x in block))
        levels.append(math.sqrt(sum(x*x for x in block)/len(block)))
    active=[i for i,x in enumerate(levels) if x >= 32768*(10**(-38/20))]
    if active:
        lead=active[0]*0.02
        trail=max(0,duration-(active[-1]+1)*0.02)
        active_sec=(active[-1]-active[0]+1)*0.02
    else: lead=duration; trail=duration; active_sec=0
    mean=math.sqrt(sum(x*x for x in levels)/max(1,len(levels)))
    clipped=sum(abs(x)>=32760 for x in samples)
    return {
      "duration_seconds":round(duration,3),"target_window_seconds":round(target_ms/1000,3),
      "duration_minus_target_seconds":round(duration-target_ms/1000,3),
      "mean_level_dbfs":dbfs(mean),"peak_level_dbfs":dbfs(peak),
      "leading_silence_approx_seconds":round(lead,3),"trailing_silence_approx_seconds":round(trail,3),
      "active_audio_approx_seconds":round(active_sec,3),
      "active_window_ratio":round(len(active)/max(1,len(levels)),3),
      "clipped_sample_count":clipped,"measurement_window_ms":20,"silence_threshold_dbfs":-38
    }

def nuclei(text):
    words=re.findall(r"[А-Яа-яӨөҮүЁёA-Za-z]+",text.lower())
    vowels=set("аэиоуөүяеёыю")
    return sum(max(1,sum(c in vowels for c in w)) for w in words)

def local_qa(ffmpeg):
    records=[]; errors=[]
    for c in CLIPS:
        p=AUDIO_DIR/c["file"]
        if not p.is_file():
            errors.append({"file":c["file"],"error":"Missing file"}); continue
        try:
            s=decode(ffmpeg,p); m=measure(s,c["target_ms"])
            active=max(.01,m["active_audio_approx_seconds"])
            m["approx_vowel_nuclei"]=nuclei(c["text"])
            m["approx_vowel_nuclei_per_active_second"]=round(m["approx_vowel_nuclei"]/active,2)
            records.append({"file":c["file"],"cue_ids":c["cue_ids"],"source_time":c["time"],
              "expected_text":c["text"],"delivery_direction":c["direction"],
              "file_bytes":p.stat().st_size,"metrics":m})
        except Exception as e: errors.append({"file":c["file"],"error":str(e)})
    return {"project":"Husbands","pilot":"Vivienne production pilot 01",
      "created_utc":datetime.now(timezone.utc).isoformat(),"mode":"local_only",
      "tts_generated":False,"gemini_audio_review_performed":False,
      "ffmpeg":ffmpeg,"clips":records,"errors":errors}

PROMPT = """Та бол монгол хэлний кино дубляжийн аудио чанарын хянагч. MP3-г бүхэлд нь сонсож, зөвхөн бодитоор сонсогдож буй зүйлд тулгуурлан үнэл. Өгөгдсөн текст, жүжиглэлтийн чиглэлийг лавлах материал гэж үз. Дуудлага, ойлгомж, байгалийн яриа, хэмнэл, cue хоорондын холбоос, завсарлага, сэтгэл хөдлөлийн нийцэл, гацалт/тасалдал/сунгалтыг шалга. Сонссон үг текстээс зөрвөл ойролцоо цагийг тэмдэглэ. Таамаг бүү хий; эргэлзвэл uncertain гэж бич. Зөвхөн JSON буцаа: { "overall_score":0, "pronunciation_score":0, "naturalness_score":0, "pacing_score":0, "emotion_match_score":0, "intelligibility":"good|mixed|poor|uncertain", "heard_text_match":"match|minor_difference|major_difference|uncertain", "observations":[""], "suspected_issues":[{"approx_time":"","issue":""}], "recommendation":"accept|revise|human_listening_required", "confidence":"low|medium|high" }"""

def gemini_qa(report,model):
    try:
        from google import genai
        from google.genai import types
    except ImportError as e:
        raise RuntimeError("google-genai суулгаагүй байна. .venv\\Scripts\\python.exe -m pip install google-genai") from e
    key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key: raise RuntimeError("GEMINI_API_KEY эсвэл GOOGLE_API_KEY алга. Аудио upload хийгдээгүй.")
    client=genai.Client(api_key=key); output=[]
    available={x["file"] for x in report["clips"]}
    for c in CLIPS:
        if c["file"] not in available: continue
        path=AUDIO_DIR/c["file"]; uploaded=None
        print("Gemini review:",c["file"])
        try:
            uploaded=client.files.upload(file=str(path))
            prompt=(PROMPT+"\nФайл: "+c["file"]+"\nCue: "+str(c["cue_ids"])+"\nТекст: "+c["text"]+"\nЧиглэл: "+c["direction"])
            response=client.models.generate_content(model=model,contents=[uploaded,prompt],
              config=types.GenerateContentConfig(response_mime_type="application/json",temperature=0.1))
            raw=(response.text or "").strip()
            try: parsed=json.loads(raw)
            except json.JSONDecodeError:
                match=re.search(r"\{.*\}",raw,re.S)
                if not match: raise RuntimeError("Gemini JSON буцаасангүй")
                parsed=json.loads(match.group(0))
            output.append({"file":c["file"],"model":model,"review":parsed})
        except Exception as e: output.append({"file":c["file"],"model":model,"error":str(e)})
        finally:
            if uploaded is not None:
                try: client.files.delete(name=uploaded.name)
                except Exception as e: print("WARNING: Gemini temporary file cleanup:",e)
    return output

def write_report(report,reviews=None,model=None):
    OUT_DIR.mkdir(parents=True,exist_ok=True)
    if reviews is not None:
        report["mode"]="local_plus_gemini"
        report["gemini_audio_review_performed"]=True
        report["gemini_model"]=model
        report["gemini_reviews"]=reviews
    jp=OUT_DIR/"vivienne_production_pilot_01_qa.json"
    mp=OUT_DIR/"vivienne_production_pilot_01_qa.md"
    jp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# Vivienne Production Pilot 01 — QA","",
      "- Mode: "+report["mode"],"- TTS generation: NOT PERFORMED",
      "- Clips measured: "+str(len(report["clips"]))+"/6","","## Local measurements","",
      "| Clip | Duration | Target | Δ | Mean dBFS | Peak dBFS | Leading silence | Active ratio |",
      "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for c in report["clips"]:
        m=c["metrics"]
        lines.append("| "+c["file"]+" | "+str(m["duration_seconds"])+"s | "+str(m["target_window_seconds"])+"s | "+str(m["duration_minus_target_seconds"])+"s | "+str(m["mean_level_dbfs"])+" | "+str(m["peak_level_dbfs"])+" | "+str(m["leading_silence_approx_seconds"])+"s | "+str(m["active_window_ratio"])+" |")
    lines += ["","> Эдгээр нь техникийн screening хэмжилт; жүжиглэлт, сэтгэл хөдлөлийг батлахгүй.","","## Gemini listening review",""]
    if reviews is None: lines.append("Gemini ажиллуулаагүй. Зөвшөөрсөн үед --gemini сонголтоор ажиллуулна.")
    else:
        for item in reviews:
            lines += ["### "+item["file"],""]
            if "error" in item: lines.append("Error: "+item["error"])
            else:
                r=item["review"]
                for k in ("overall_score","pronunciation_score","naturalness_score","pacing_score","emotion_match_score","recommendation","confidence"):
                    lines.append("- "+k+": "+str(r.get(k,"—")))
                for x in r.get("observations",[]): lines.append("- "+str(x))
                for x in r.get("suspected_issues",[]): lines.append("- Issue "+str(x.get("approx_time","?"))+": "+str(x.get("issue","")))
            lines.append("")
    if report["errors"]:
        lines += ["## Missing or failed files",""]+[ "- "+x["file"]+": "+x["error"] for x in report["errors"]]
    lines += ["","## Limitations","",
      "- Local measurements cannot judge natural acting or emotional credibility.",
      "- Gemini is a second opinion, not a substitute for human listening against the film scene.",
      "- Do not scale to full-film TTS until all six clips are human-reviewed and accepted.",""]
    mp.write_text("\n".join(lines),encoding="utf-8")
    print("JSON:",jp); print("Markdown:",mp)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gemini",action="store_true",help="Upload existing MP3s for Gemini listening review; no TTS calls.")
    ap.add_argument("--model",default=None,help="Gemini audio model; default GEMINI_AUDIO_MODEL or gemini-2.5-flash.")
    args=ap.parse_args(); load_env()
    ff=find_ffmpeg()
    if not ff:
        print("ERROR: ffmpeg.exe олдсонгүй. PATH эсвэл FFMPEG_EXE тохируул."); return 2
    missing=[c["file"] for c in CLIPS if not (AUDIO_DIR/c["file"]).is_file()]
    if missing:
        print("ERROR: Pilot MP3 дутуу байна:")
        for x in missing: print(" -",x)
        print("Хүлээж буй хавтас:",AUDIO_DIR); return 2
    report=local_qa(ff); reviews=None; model=None
    if args.gemini:
        model=args.model or os.environ.get("GEMINI_AUDIO_MODEL","gemini-2.5-flash")
        print("Gemini аудио review асаалттай. Зөвхөн одоо байгаа MP3 upload хийнэ; TTS үүсгэхгүй.")
        reviews=gemini_qa(report,model)
    write_report(report,reviews,model)
    print("Хэмжсэн клип:",len(report["clips"]),"/6")
    print("ElevenLabs хүсэлт илгээгээгүй. TTS үүсгээгүй.")
    if not args.gemini: print("Gemini рүү холбогдоогүй. Бэлэн үед --gemini нэмнэ.")
    return 0 if not report["errors"] else 1

if __name__=="__main__":
    raise SystemExit(main())
