# Husbands — Objective Acoustic A/B Findings (Speaker-Filtered Revision)

Date: 2026-11-08
Source repository: `onlinec-coder/SRT-Translator`

## Executive conclusion

The acoustic test groups were cross-checked against the current `speaker_assignments.json`. Several groups contain more than one speaker. Earlier whole-group means describe the WAV cue sets, but must not be treated as Vivienne-only measurements.

For Vivienne-specific interpretation, use only these C001 cue subsets:

| Test group | C001 Vivienne cues | Mean Speech-minus-Original RMS |
|---|---|---:|
| Normal | 66, 67 | **−3.62 dB** (2 cues) |
| Emotional | 698–702 | **−3.31 dB** (5 cues) |
| Quiet | 9, 10, 13, 17–19 | **−3.56 dB** (6 cues) |

Speech RMS is lower than Original across all three Vivienne-only subsets. These are small samples, and RMS includes all audio in each cue window. The measurements do not isolate whether the difference came from source separation, denoising, gating, gain, or residual background audio.

## 1. Speaker identity audit

| Group | Cue IDs | Speaker in speaker_assignments.json | Vivienne profile |
|---|---|---|---|
| Normal | 66–67 | C001 Vivienne | Include |
| Normal | 68–70 | C004 Mother | Exclude |
| Emotional | 698–702 | C001 Vivienne | Include |
| Quiet | 9–10 | C001 Vivienne | Include |
| Quiet | 11–12 | C002 Lucian | Exclude |
| Quiet | 13 | C001 Vivienne | Include |
| Quiet | 14–16 | C002 Lucian | Exclude |
| Quiet | 17–19 | C001 Vivienne | Include |

Corrections:
- Normal cue 68 (“Үнэхээр уучлаарай.”) and cues 69–70 belong to Mother, not Vivienne.
- Quiet cues 11–12 and 14–16 belong to Lucian.
- Quiet cues 9–10 and 17–19 are Vivienne's inner monologue; cue 13 is Vivienne narration.
- Emotional cues 698–702 are all Vivienne, across narration, inner monologue, and direct dialogue.

The former normal mean of −5.25 dB across cues 66–70 and quiet mean of −4.56 dB across cues 9–19 are mixed-speaker statistics. Do not use them as Vivienne-only values.

## 2. Vivienne-only measurements

### Normal narration — cues 66–67
- Mean RMS difference: **−3.62 dB**.
- Cue 66: −3.50 dB; cue 67: −3.74 dB.
- Both are Vivienne narration, not direct dialogue.

Use these as neutral narration references, not evidence about direct conversational dialogue.

### Emotional performance — cues 698–702
- Mean RMS difference: **−3.31 dB**.
- Cue 701 (direct angry/emphatic dialogue): RMS −3.94 dB; peak −3.35 dB.
- Cue 701 approximate median F0: 163.8 Hz Original vs 176.5 Hz Speech; Speech p90 is 320.3 Hz vs 208.4 Hz Original.

Cue 701 is the strongest emotional test. Gemini described Original as more forceful than Speech, but human A/B listening is required. The F0 estimate is approximate and does not establish a true pitch shift or emotional reduction.

### Quiet / restrained performance — cues 9, 10, 13, 17–19
- Mean RMS difference: **−3.56 dB**.
- Cues 9–10 and 17–19 are Vivienne inner monologue.
- Cue 13 is Vivienne narration and provides a neutral/clear contrast.

Gemini describes Vivienne's inner-monologue cues as restrained, soft, breathy and slow. Speech is quieter in the measured windows. This supports listening for soft onsets, breath, low-level detail, and phrase tails; it does not prove those features were removed.

## 3. Qualitative findings (speaker-filtered)

- Vivienne's quiet inner monologue (9–10, 17–19) is described as soft, breathy, low-intensity and slow.
- Vivienne narration cue 13 is described as neutral and clear, a useful contrast.
- Cue 701 is Vivienne's emphatic angry line; Original is described as more forceful than Speech.
- Normal cues 66–67 are Vivienne narration and are described as clear and conversational.
- Do not use the soft/sad analysis for normal cue 68 as Vivienne evidence; it belongs to Mother.

Automated emotion labels remain provisional. Short cue windows can be ambiguous; judge acting intent in scene context.

## 4. What the measurements do and do not establish

Established:
1. Speech RMS is lower than Original in all three speaker-filtered Vivienne subsets.
2. Mean differences are approximately −3.3 to −3.6 dB in these selected subsets.
3. Cue 701 has lower RMS and peak in Speech than Original.
4. Some quiet-frame values are substantially lower in Speech.

Not established:
1. Whether lower levels are caused by source separation, gain staging, denoising, gating, or a combination.
2. Whether breathiness, emotion, or phrase tails are perceptually lost in every cue.
3. Whether measured F0 changes are genuine vocal pitch changes. The estimator is approximate and reaches a 400 Hz ceiling in some cues.
4. Whether these findings generalize to all Vivienne lines in the film.

## 5. Production recommendations

1. **Use Original as the emotional ground truth.** Do not define Vivienne's acting from Speech alone.
2. **Use Speech as a secondary clarity reference.** It can help inspect words and articulation, but do not copy its lower level or quiet tails as the acting target.
3. **Use speaker-filtered evidence only.** Exclude Mother cues 68–70 and Lucian cues 11–12 and 14–16 from Vivienne's voice profile.
4. **Preserve emotional contrast.** Neutral narration, vulnerable inner monologue, and angry dialogue should not be flattened into one delivery.
5. **Do not normalize every cue independently before emotional review.** First record natural dynamics, then optionally compare loudness-matched versions for timbre and intelligibility.
6. **Do not set exact pitch or speed from this sample.** Finalize only after manual listening and controlled generated-voice auditions.

## 6. Corrected priority listening set

- Normal: cues 66 and 67 (Vivienne narration).
- Emotional: cue 701 (Vivienne direct dialogue).
- Quiet: cues 9, 10, 13, 17, 18 and 19 (Vivienne inner monologue / narration).

Two passes:
1. Natural playback level to understand actual dynamic contrast.
2. Loudness-matched playback to compare timbre, breath, articulation, and phrase endings without loudness bias.

## 7. Measurement limitations

- Mono PCM 16-bit, source sample rate 16 kHz; analysis resampled to 8 kHz.
- RMS/peak include all audio inside the cue window, including residual background sound.
- F0 uses windowed autocorrelation and is approximate. Values at 400 Hz are ceiling hits, not reliable exact pitch values.
- ZCR is sensitive to music, noise, and source-separation artifacts; do not use it as a voice-quality score.
- This is a small selected sample, not a full-film statistical validation.
