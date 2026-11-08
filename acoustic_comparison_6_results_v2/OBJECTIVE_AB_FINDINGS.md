# Husbands — Objective Acoustic A/B Findings

Date: 2026-11-08
Source repository: `onlinec-coder/SRT-Translator`
Inputs:
- `acoustic_comparison_6_results_v2/objective_measurements.json`
- `acoustic_comparison_6_results_v2/objective_measurements.csv`
- Six Gemini qualitative analyses in `acoustic_comparison_6_results_v2/`

## Executive conclusion

The Speech versions are consistently quieter than the Original versions in the measured cue windows. The average Speech-minus-Original RMS difference is approximately:
- Normal: **-5.25 dB** (5 cues)
- Emotional: **-3.31 dB** (5 cues)
- Quiet: **-4.56 dB** (10 cues)
- All measured cues: **-4.40 dB** (20 cues)

Peak level is also lower in Speech. The most important pattern is not simply lower overall level: the lower-tail frame RMS values (p10) are often much lower in Speech, consistent with reduced quiet details, breaths, tails, or low-level ambience. This supports the qualitative Gemini observation that quiet/sad delivery may sound less breathy and less emotionally nuanced after speech extraction/processing.

Do not interpret this as proof that the extraction algorithm itself caused every difference: the Original includes background audio and the Speech stem has a different signal composition. RMS, peak, ZCR and frame-level values are therefore affected by music/background separation as well as voice processing.

## By test group

### Normal delivery

- Mean RMS difference: **-5.25 dB**.
- Cues 66, 67 and 69 are each about -3.5 to -3.7 dB.
- Cue 70 is -6.13 dB.
- Cue 68 is the largest change: RMS -9.34 dB, peak -3.21 dB, approximate median F0 +98.5 Hz.
- Cue 68's F0 estimate is especially suspect because the autocorrelation estimate reaches the 400 Hz ceiling in both versions; do not use this cue to set pitch.

Interpretation: the ordinary voice remains broadly recognizable, but level and quiet details are reduced. Cue 68 needs listening-based review because the large F0 estimate shift may be a pitch-tracking error, a change in which voiced frames dominate, or a genuine change; this measurement cannot decide which.

### Emotional delivery

- Mean RMS difference: **-3.31 dB**.
- All five cues have a consistent RMS reduction of roughly -3.1 to -3.9 dB.
- Cue 701 (the angry/emphatic cue) has RMS -3.94 dB and peak -3.35 dB. Approximate median F0 rises from 163.8 to 176.5 Hz; Speech F0 p90 is 320.3 Hz versus 208.4 Hz in Original.
- Gemini's qualitative assessment rated cue 701's anger stronger in Original than Speech.

Interpretation: the loudness contrast is reduced in Speech, while the pitch tracker suggests some higher-pitch activity remains or becomes more prominent. This is not enough to conclude that anger has been removed. Preserve the Original as the primary emotional-performance reference; use Speech as a cleaned intelligibility reference.

### Quiet delivery

- Mean RMS difference: **-4.56 dB**.
- Cues 9, 10, 13, 15, 17, 18 and 19 are mostly around -3.1 to -4.8 dB.
- Cue 11 is -6.91 dB and cue 12 is -12.83 dB.
- Several cues show a very large reduction in the quietest 10% of frames. Examples: cue 9 p10 changes from -31.02 to -57.74 dBFS; cue 10 from -35.16 to -68.82 dBFS; cue 17 from -27.53 to -62.00 dBFS.
- The approximate F0 tracker is unreliable for cues where values hit 400 Hz or show unusually large jumps (notably cues 9, 11, 12 and 16).

Interpretation: this is the clearest evidence of low-level detail suppression. The quiet/sad Original contains soft, breathy and subdued delivery noted in the Gemini analysis; Speech has a much lower noise/quiet-frame floor and a more consistently voiced-looking frame ratio. This may make it cleaner, but it can also remove breath, soft onset/offset, and fragile emotional texture.

## What the measurements do and do not establish

Established by this A/B measurement:
1. Speech RMS and peak are lower across all three groups.
2. The largest level losses occur in selected quiet/soft cues, especially normal cue 68 and quiet cues 11–12.
3. The quietest frame levels are often substantially lower in Speech.
4. Median F0 is broadly similar in many cues, but several estimates are unreliable.

Not established:
1. Whether the lower level is caused by source separation, gain staging, denoising, gating, or a combination.
2. Whether a measured F0 change is a true vocal pitch change. The estimator is approximate and capped at 400 Hz.
3. Whether emotional performance is perceptually weaker in every cue. This requires direct listening and, ideally, waveform-aligned comparison.

## Production recommendations

1. **Keep Original as the emotional ground truth.** Do not use the Speech stem alone to define Vivienne's sadness, anger, breathiness, or emotional intensity.
2. **Use Speech as a speech-cleanliness / intelligibility reference.** It can help inspect words and voice detail, but do not copy its quieter tails or flattened delivery as the target performance.
3. **For ElevenLabs voice direction, preserve contrast rather than applying one uniform emotion.**
   - Neutral: stable, clear, conversational, moderate pace.
   - Sad/quiet: softer intensity, lower/contained delivery, slower pace, gentle breathiness, natural phrase tails; avoid making it uniformly whispery.
   - Anger (cue 701): stronger emphasis, firmer projection, more dynamic pitch movement and controlled strain; do not merely raise average loudness.
4. **Do not normalize every cue independently before emotional review.** That could erase the intended contrast between quiet and emphatic lines.
5. **Before final settings, listen to Original and Speech side by side for cues 68, 701, quiet 9, 11, 12 and 16.** These are the highest-priority review points.

## Measurement limitations

- Mono PCM 16-bit, source sample rate 16 kHz; analysis resampled to 8 kHz.
- RMS/peak include all audio inside the cue window, including any residual background sound.
- F0 uses windowed autocorrelation and is approximate. Values at 400 Hz are ceiling hits, not reliable exact pitch values.
- ZCR is sensitive to music, noise, and source-separation artifacts; do not use it as a voice-quality score.
- This is a 20-cue test sample, not a full-film statistical validation.

## Recommended next phase

Proceed to **speaker-to-character validation and emotion/dubbing direction**, using the Original audio as the emotional reference and the Speech stem as a secondary clarity reference. Prioritize manual A/B listening on the six cues listed above before locking the Vivienne voice direction.
