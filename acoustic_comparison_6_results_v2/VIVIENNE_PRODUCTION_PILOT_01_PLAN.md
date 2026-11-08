# Vivienne Production Pilot 01

Date: 2026-11-08  
Status: **PREPARED — awaiting local generation and human listening**  
Repository: `onlinec-coder/SRT-Translator`

## Purpose

Test the already accepted Vivienne voice in six short, representative production samples. This is not a new voice audition and does not authorize full-film production.

## Locked settings

- Character identity: C001 Vivienne, including narration and inner-monologue voice identity.
- Voice ID: `6Km4T9TrZXIhfMaxglHw`
- Model: `eleven_v3`
- Output: MP3 44.1 kHz / 128 kbps.
- Keep saved numerical voice defaults unchanged.
- Do not override speed, pitch, stability, similarity, or style.
- No other voice IDs or models.
- The generator checks voice access before TTS and stops after the first failed generation.
- Existing output files are reused to avoid duplicate credit charges.
- The user explicitly approved up to six new TTS requests for this pilot.

## Six selected samples

| # | Cue(s) | Source time | Acting target | Why selected |
|---:|---|---|---|---|
| 1 | 427 | 00:13:19.166–00:13:20.583 | Hurt, broken trust, slight disgust; lowered, near-whisper but intelligible | Tests intimate wounded dialogue |
| 2 | 430–434 | 00:13:24.600–00:13:30.000 | Same connected hurt/realization; preserve phrase flow | Tests emotional continuity across five adjacent cues |
| 3 | 776–778 | 00:24:36.791–00:24:42.125 | Calm, self-confident, evidence-led explanation | Tests longer assertive speech without anger |
| 4 | 758 | 00:23:55.800–00:23:56.958 | Calm correction, firm resolve, slight displeasure | Tests quiet authority without sarcasm |
| 5 | 963 | 00:30:08.800–00:30:09.791 | Disgust with slight controlled anger; decisive refusal | Tests nuanced negative emotion without shouting |
| 6 | 1203–1205 | 00:37:24.541–00:37:27.583 | Ordinary, natural Vivienne; no exaggerated happiness | Tests restrained ending delivery |

Cue IDs, speaker assignments, Mongolian wording, and source timing were checked against `Husbands_mn_v3.srt`, `speaker_assignments.json`, the cue pacing index, and the user-confirmed emotion delivery map in this repository.

## Continuity decisions

- Cues 430–434 are sent as one connected utterance because the subtitle sequence is a continuous realization. Do not split it into five TTS calls.
- Cues 776–778 are sent together as one continuous factual explanation.
- Cues 1203–1205 are sent together to preserve the final thought and natural phrase ending.
- Delivery tags are limited to the two near-whisper samples and the disgusted refusal. The remaining samples use the unchanged default voice behavior.
- No artificial speed adjustment is applied in this round. Actual generated durations will be measured and compared with the source subtitle windows after generation.

## Run

From the project root in PowerShell:

```powershell
git pull
.\.venv\Scripts\python.exe generate_vivienne_production_pilot_01.py
```

The local script reads `ELEVENLABS_API_KEY` from the existing environment or local `.env`. It never prints or modifies the key. Do not upload or commit `.env`.

Outputs are written locally to:

`acoustic_comparison_6_results_v2/vivienne_production_pilot_01/`

## Listening and acceptance checklist

Listen to each complete clip against the corresponding original-film passage.

1. Is the voice recognizably the same Vivienne as the accepted A/B/C/D3 references?
2. Are Mongolian consonants, vowel lengths, and word stress clear and natural?
3. Does the acting direction match the user-confirmed original-film interpretation?
4. Are phrase onset, ending, breath, and pauses natural?
5. Does the combined multi-cue sample flow as one thought without artificial subtitle-boundary pauses?
6. Is the generated duration practical for the source window? If not, record the actual duration first; do not immediately force speed.
7. Does the performance remain feminine and controlled without overacting?

## Acceptance boundary

This pilot tests six representative performances only. Passing it does not automatically approve all 915 Vivienne cues. Any timing or voice-setting changes must be based on measured output and a specific listening issue. Do not spend additional ElevenLabs credits beyond this approved six-request pilot without new explicit approval.

## Result status

- Generation: pending local run.
- Human listening: pending.
- Production approval: not yet granted.
