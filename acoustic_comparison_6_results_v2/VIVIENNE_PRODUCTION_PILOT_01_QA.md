# Vivienne Production Pilot 01 — QA procedure

## Purpose
Evaluate the six existing MP3 files. This procedure does not create or alter speech.

## Cost and privacy controls
- The script never calls ElevenLabs and cannot generate TTS.
- Default execution is local-only and does not contact Gemini.
- Gemini review requires the explicit --gemini option.
- Gemini API usage may consume quota or incur charges. Check billing and quota first.
- Temporary Gemini Files uploads are deleted after each review when supported.
- Never commit .env, API keys, or private audio to a public repository.

## Local-only run
From the repository root in PowerShell:

```powershell
.venv\Scripts\python.exe qa_vivienne_production_pilot_01.py
```

FFmpeg must be available on PATH. If necessary, set its full path for this PowerShell session:

```powershell
$env:FFMPEG_EXE = "C:\path\to\ffmpeg.exe"
```

Outputs:
- acoustic_comparison_6_results_v2/vivienne_production_pilot_01/qa/vivienne_production_pilot_01_qa.json
- acoustic_comparison_6_results_v2/vivienne_production_pilot_01/qa/vivienne_production_pilot_01_qa.md

## Optional Gemini review
Only after deciding to use Gemini, confirm GEMINI_API_KEY or GOOGLE_API_KEY is set in the local .env file. Then run:

```powershell
.venv\Scripts\python.exe qa_vivienne_production_pilot_01.py --gemini
```

Default model: gemini-2.5-flash. You may choose a supported audio-capable Gemini model with --model. The script uploads existing MP3s for audio understanding; it does not synthesize or modify audio.

## Interpretation
Local measurements include duration, approximate leading/trailing silence, mean and peak level, active-window ratio, clipping count, and a rough vowel-nuclei-per-active-second indicator. These are screening metrics only.

Gemini is asked to assess Mongolian pronunciation, intelligibility, naturalness, pacing, emotional direction, and suspected audible defects. Treat its output as a second opinion. Human listening against the original film remains the acceptance gate before full-film production.
