# Vivienne Production Pilot 01 — Offline QA

## Purpose

Analyze the six MP3 files already generated in `vivienne_production_pilot_01/`. This is an offline diagnostic step. It does not generate audio, call ElevenLabs, call Gemini, or upload audio anywhere.

## Requirements

- Python 3.10 or newer (the project environment is already newer).
- `ffmpeg.exe` and `ffprobe.exe` available on PATH.
- The six existing MP3 files and `vivienne_production_pilot_01_manifest.json` in the pilot folder.

No additional Python package is required.

## Run on Windows PowerShell

From the local `SRT-Translator` repository root:

```powershell
git pull
.\.venv\Scripts\python.exe analyze_vivienne_production_pilot_01.py
```

If the virtual environment path is different, use the Python executable from the project's active environment. Do not run the earlier TTS generator.

## Outputs

The script writes two reports beside the six MP3s:

- `vivienne_production_pilot_01_qa_report.json`
- `vivienne_production_pilot_01_qa_report.md`

The JSON report includes:
- Actual decoded duration, codec, sample rate, channels, file size, and bitrate.
- Duration difference against the manifest's subtitle time window.
- Estimated speech-active regions and internal low-energy gaps.
- Peak and RMS loudness percentiles, plus near-full-scale sample count.
- Rough subtitle-word-per-minute proxies.

## Important interpretation limits

Speech activity is estimated from 20 ms RMS frames using an energy threshold. It is not speech recognition. Background noise, breaths, music, and quiet consonants can affect the estimates. Word-rate figures use subtitle word counts and must not be treated as exact spoken pacing or syllable timing.

The report cannot judge Mongolian pronunciation, stress, emotion, character identity, or acting quality. Those still require listening and comparison with the original film.

## Gemini / cloud assessment

This script deliberately makes no cloud request. Audio has not been authorized for upload to Gemini or another external service. If cloud listening assessment is later desired, decide on that separately before sending any of the six MP3s.

## Safety

- No ElevenLabs API key is read.
- No ElevenLabs or Gemini API calls are made.
- No audio files are modified.
- No TTS credits are consumed.
