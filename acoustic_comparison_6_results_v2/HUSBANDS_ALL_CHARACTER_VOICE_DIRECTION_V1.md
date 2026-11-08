# Husbands — All-Character Voice Reference V1

Date: 2026-11-08  
Repository scope: `onlinec-coder/SRT-Translator` only  
Status: **PROVISIONAL CAST / VOICE-DIRECTION REFERENCE — not final emotion map**

## Source and alignment

- Source audio SHA-256: `6e1c1cfaad4867dcae717f38e0e636e0ec481c9e9c43d9454c59703b932b03a7`
- Actual WAV duration: **00:37:40.997** (mono, 16 kHz, 16-bit PCM)
- English source subtitles: `Husbands_ocr_en.srt`
- Mongolian subtitles: `Husbands_mn_v3.srt`
- Speaker mapping: `speaker_assignments.json`
- Character registry: `Husbands_characters_reconciled.json`
- Cue coverage: **1,213 / 1,213** cue assignments; 11 characters have dialogue assignments. The registry also contains Narrator, but Narrator has zero independent assignments because narration is mapped to Vivienne/C001.

Machine-readable acoustic measurements: [HUSBANDS_SOURCE_AUDIO_ACOUSTIC_REFERENCE_V1.json](HUSBANDS_SOURCE_AUDIO_ACOUSTIC_REFERENCE_V1.json)  
Compressed cue-level source timing and voice features for all 1,213 cues: [HUSBANDS_SOURCE_AUDIO_CUE_FEATURES_V1.json](HUSBANDS_SOURCE_AUDIO_CUE_FEATURES_V1.json)

## How to read the measurements

- F0 is a rough median pitch estimate in Hz from cue-aligned frames. It is not a voice ID and may contain octave errors.
- RMS is a rough median level in dBFS; it is affected by the mix, music, and effects.
- Spectral centroid is a rough brightness indicator, not a direct timbre label.
- English words per subtitle-slot minute is word count divided by subtitle slot time. It is **not** the exact active-speech rate.
- WebRTC VAD mode 2 and mode 3 disagree substantially on many cues. Music/effects and quiet speech make automatic active-duration estimates uncertain. Do not use VAD duration as a direct TTS speed multiplier.
- Short-sample characters must not be assigned a final voice solely from these numbers.

## Character reference

| Character | ID | Assigned cues | Median F0 (rough) | Median RMS | Spectral centroid | Sample coverage |
|---|---:|---:|---:|---:|---:|---|
| Vivienne | C001 | 915 | 162 Hz | -17.1 dBFS | 744 Hz | Sufficient |
| Aria | C003 | 82 | 199 Hz | -20.7 dBFS | 919 Hz | Sufficient |
| Alpha Valeris | C012 | 13 | 184.5 Hz | -21.8 dBFS | 946 Hz | Limited |
| Luna Valerius | C013 | 14 | 162 Hz | -19.4 dBFS | 895.5 Hz | Limited |
| Chief Elder Laurent | C014 | 17 | 105.5 Hz | -16.9 dBFS | 818 Hz | Limited |
| Lucian | C002 | 110 | 140.5 Hz | -19.9 dBFS | 913 Hz | Sufficient |
| Mother | C004 | 28 | 162 Hz | -20.4 dBFS | 776 Hz | Limited |
| Morgana | C008 | 20 | 185 Hz | -19.9 dBFS | 966.5 Hz | Limited |
| Lance Laurent | C009 | 7 | 102 Hz | -18.7 dBFS | 760 Hz | Very limited |
| Luke Laurent | C010 | 5 | 102 Hz | -15.6 dBFS | 660 Hz | Very limited |
| The royal seer | C019 | 2 | 152 Hz | -20.2 dBFS | 1,498 Hz | Very limited |
| Narrator | C005 | 0 | — | — | — | No independent speaker assignment |

## Preliminary voice-direction notes

These are working descriptions from short source-audio auditions plus the measurements above. They are not final casting approvals.

- **Vivienne (C001):** Keep one continuous voice identity for direct dialogue, inner monologue, and narration. The sampled narration is restrained, close, and natural rather than theatrical. Use a flexible phrase-level pace; vary speed, pauses, emphasis, and breath according to meaning. Do not lock her to a single speaking speed.
- **Aria (C003):** Her measured median pitch and spectral brightness are higher than Vivienne's. Preserve a clearly distinct, brighter and more forward identity; do not simply copy Vivienne's voice.
- **Alpha Valeris (C012):** Male character per the reconciled character understanding. Only 13 cues; the measured pitch distribution is wide and not enough to lock a final register or voice identity. Keep the first voice audition provisional.
- **Luna Valerius (C013):** Female character. The short sample suggests a controlled, clear delivery with a brighter upper spectrum than Vivienne. Verify more clean dialogue before final casting.
- **Chief Elder Laurent (C014):** The sample has the lowest stable median F0 among the better-sampled characters. Use a lower, resonant, measured, authoritative direction; avoid making the voice artificially gravelly.
- **Lucian (C002):** Male low-to-mid register with a broad cue-level pitch range. Preserve controlled, steady delivery and allow meaningful shifts between calm, defensive, and emotionally charged lines.
- **Mother (C004):** Female mid-register sample, comparatively less bright than Aria or Morgana. Keep the delivery natural and grounded; confirm warmth and breath texture against more scenes.
- **Morgana (C008):** Female upper-mid sample with a brighter spectral profile. Keep articulation clear and a distinct sharper/brighter identity; do not overstate pitch because the sample is limited.
- **Lance Laurent (C009):** Male character, but only seven cues. The lower-register estimate is too sample-sensitive for a final voice decision. Do not assume Lance and Luke should share a voice.
- **Luke Laurent (C010):** Male character, only five cues. Treat the measured profile as a provisional reference; audition against Lance to preserve brother-to-brother distinction.
- **The royal seer (C019):** Only two cues. The sample is too short for reliable voice casting; preserve the source's distinct character impression and defer final pitch/timbre decisions.
- **Narrator (C005):** No independent narrator voice. Narration belongs to Vivienne/C001 under the current project decision.

## Emotion and acting policy

1. Acoustic measurements (pitch, intensity, brightness, VAD timing) are stored separately from interpreted emotion.
2. Do not label anger, sadness, disgust, sarcasm, confidence, or fear from pitch/loudness alone.
3. Vivienne's user-confirmed emotion decisions remain in `VIVIENNE_EMOTION_DELIVERY_MAP_V1.md`. Her narration normally stays natural and restrained; D3 [angry] is reserved for the specific user-approved genuinely angry cues.
4. Other characters still need a cue-by-cue emotion and acting map based on the source performance, dialogue meaning, scene context, and human listening.
5. For every emotion annotation, retain the cue ID, label, intensity, vocal evidence, confidence, and whether it is source-confirmed or provisional.

## Production use

- Use the cue's actual available time window and Mongolian syllable load to decide pace. Never apply one global speed to all cues.
- Preserve phrase continuity across subtitle boundaries.
- Use the measurements as reference ranges, not strict targets.
- Resolve VAD disagreement and apparent overlaps by listening to the original scene, especially when one speaker's line may spill into the next speaker.
- Before assigning ElevenLabs voice IDs to small-sample characters, build clean reference excerpts and compare the characters directly.
- No new paid TTS generation is authorized by this analysis.

## Remaining work

- Human review of timing and phrase contour for all priority cues.
- Cue-level emotion, emphasis, breath, pause, and vocal-texture annotation for every speaking character.
- Clean non-overlapping voice samples for each character, particularly Lance, Luke, Alpha, Luna, and the royal seer.
- Per-cue Mongolian delivery-rate targets using natural localization, not literal English duration matching.

## Full-film source-audio extraction — 2026-11-08

The original WAV was processed across its full **00:37:40.997** duration. The WAV itself is intentionally not stored; its SHA-256 is retained in the acoustic reference.

Persisted companion datasets (all cue IDs join by `cue_id`; speaker labels join by `speaker_id`):

1. `HUSBANDS_SOURCE_AUDIO_CUE_FEATURES_V1.json` — all 1,213 cue windows; conservative 30 ms VAD onset/end/active-duration estimates, rough median F0 and median RMS.
2. `HUSBANDS_FULL_FILM_AUDIO_DYNAMICS_V1.json` — complete 2,260-frame, one-second RMS/peak timeline for the whole soundtrack, compressed in three parts.
3. `HUSBANDS_FULL_FILM_CUE_PACING_INDEX_V1.json` — all 1,213 cue start/end/duration values, speaker assignment, English word count, subtitle-gap-to-next-cue timing and display-WPM proxy.
4. `HUSBANDS_SOURCE_AUDIO_ACOUSTIC_REFERENCE_V1.json` — source fingerprint, cast-level reference, join keys, outputs and limitations.

### Important interpretation rules

- Cue display-WPM is only a subtitle pacing proxy. It is not measured spoken WPM and must not be used alone to set TTS speed.
- Inter-cue subtitle gaps are not guaranteed speech pauses. Phrase continuity can cross cue boundaries; silence can also occur inside a cue.
- VAD onset/end and active duration are conservative estimates, not word or phoneme alignment.
- Full-mix RMS/peak/spectral measurements include music and effects and are not isolated character voice measurements.
- Emotion, breath, emphasis, detailed intonation contours and nuanced acting direction are not fully human-verified for every cue and every character. Preserve explicit human-confirmed emotion decisions separately; do not invent labels from signal features.
- Word-level forced alignment, phoneme durations and fully verified character-isolated prosody profiles remain future work.
