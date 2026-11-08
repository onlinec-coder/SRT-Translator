# Vivienne production pilot 01 — offline audio QA

Generated: 2026-11-08T12:13:50.818272+00:00

**Scope:** six existing MP3s only. No TTS generation, audio upload, or network/API calls.
**Limit:** these measurements cannot assess Mongolian pronunciation, emotion, acting quality, or voice identity. Human listening is still required.

| File | Duration | Target | Difference | Active speech est. | Peak | Whole-clip WPM* | Pauses |
|---|---:|---:|---:|---:|---:|---:|---:|
| pilot_01_cue427_hurt_disappointed.mp3 | 1.840s | 1417 ms | +423 ms | 1.48s | -2.45 dBFS | 195.7 | 0 |
| pilot_02_cues430-434_hurt_realization.mp3 | 10.320s | 5400 ms | +4920 ms | 6.90s | -0.94 dBFS | 122.1 | 6 |
| pilot_03_cues776-778_assertive_explanation.mp3 | 10.240s | 5334 ms | +4906 ms | 7.54s | -0.8 dBFS | 146.5 | 3 |
| pilot_04_cue758_firm_correction.mp3 | 1.360s | 1158 ms | +202 ms | 1.30s | -2.71 dBFS | 132.4 | 0 |
| pilot_05_cue963_disgusted_refusal.mp3 | 2.560s | 991 ms | +1569 ms | 1.12s | -2.85 dBFS | 46.9 | 0 |
| pilot_06_cues1203-1205_natural_resolution.mp3 | 3.600s | 3042 ms | +558 ms | 2.86s | -1.82 dBFS | 150.0 | 1 |

*WPM divides subtitle word count by full clip duration; it is not a true spoken-word rate.

## Per-clip activity and pauses

### pilot_01_cue427_hurt_disappointed.mp3

- Speech regions (estimated): [{"start_seconds": 0.14, "end_seconds": 1.62, "duration_seconds": 1.48}]
- Internal pauses: []
- RMS p10 / median / p95: -58.0 / -30.22 / -14.35 dBFS

### pilot_02_cues430-434_hurt_realization.mp3

- Speech regions (estimated): [{"start_seconds": 0.12, "end_seconds": 0.78, "duration_seconds": 0.66}, {"start_seconds": 1.02, "end_seconds": 1.68, "duration_seconds": 0.66}, {"start_seconds": 3.48, "end_seconds": 5.16, "duration_seconds": 1.68}, {"start_seconds": 5.52, "end_seconds": 6.5, "duration_seconds": 0.98}, {"start_seconds": 6.76, "end_seconds": 7.84, "duration_seconds": 1.08}, {"start_seconds": 8.28, "end_seconds": 9.3, "duration_seconds": 1.02}, {"start_seconds": 9.5, "end_seconds": 10.32, "duration_seconds": 0.82}]
- Internal pauses: [{"start_seconds": 0.78, "end_seconds": 1.02, "duration_seconds": 0.24}, {"start_seconds": 1.68, "end_seconds": 3.48, "duration_seconds": 1.8}, {"start_seconds": 5.16, "end_seconds": 5.52, "duration_seconds": 0.36}, {"start_seconds": 6.5, "end_seconds": 6.76, "duration_seconds": 0.26}, {"start_seconds": 7.84, "end_seconds": 8.28, "duration_seconds": 0.44}, {"start_seconds": 9.3, "end_seconds": 9.5, "duration_seconds": 0.2}]
- RMS p10 / median / p95: -80.09 / -28.44 / -8.27 dBFS

### pilot_03_cues776-778_assertive_explanation.mp3

- Speech regions (estimated): [{"start_seconds": 0.04, "end_seconds": 2.38, "duration_seconds": 2.34}, {"start_seconds": 3.14, "end_seconds": 6.02, "duration_seconds": 2.88}, {"start_seconds": 6.84, "end_seconds": 8.12, "duration_seconds": 1.28}, {"start_seconds": 8.48, "end_seconds": 9.52, "duration_seconds": 1.04}]
- Internal pauses: [{"start_seconds": 2.38, "end_seconds": 3.14, "duration_seconds": 0.76}, {"start_seconds": 6.02, "end_seconds": 6.84, "duration_seconds": 0.82}, {"start_seconds": 8.12, "end_seconds": 8.48, "duration_seconds": 0.36}]
- RMS p10 / median / p95: -84.57 / -26.06 / -6.26 dBFS

### pilot_04_cue758_firm_correction.mp3

- Speech regions (estimated): [{"start_seconds": 0.04, "end_seconds": 1.34, "duration_seconds": 1.3}]
- Internal pauses: []
- RMS p10 / median / p95: -48.25 / -21.2 / -9.64 dBFS

### pilot_05_cue963_disgusted_refusal.mp3

- Speech regions (estimated): [{"start_seconds": 0.16, "end_seconds": 1.28, "duration_seconds": 1.12}]
- Internal pauses: []
- RMS p10 / median / p95: -86.27 / -68.86 / -9.76 dBFS

### pilot_06_cues1203-1205_natural_resolution.mp3

- Speech regions (estimated): [{"start_seconds": 0.04, "end_seconds": 0.56, "duration_seconds": 0.52}, {"start_seconds": 1.24, "end_seconds": 3.58, "duration_seconds": 2.34}]
- Internal pauses: [{"start_seconds": 0.56, "end_seconds": 1.24, "duration_seconds": 0.68}]
- RMS p10 / median / p95: -87.07 / -27.36 / -8.25 dBFS

## Interpretation limits

- RMS activity can be affected by breaths, background noise, music, and quiet consonants.
- Pauses are low-energy gaps, not semantic or dramatic pause labels.
- No ASR, pitch, phoneme alignment, pronunciation, emotion, or speaker-identity judgment is performed.
- No audio is sent to Gemini or any external service. Any cloud audio upload requires a separate explicit decision.
