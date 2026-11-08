# Vivienne — Mongolian Dubbing Voice Direction (V1.1 / Provisional)

Date: 2026-11-08  
Project: Husbands  
Status: **Provisional V1.2 — user has listened to all four generated auditions and rated each “боломжийн” (acceptable); detailed parameter calibration and final approval remain pending**

## 1. Purpose

Define a consistent Mongolian performance direction for Vivienne across direct dialogue, inner monologue, and narration. The goal is a believable, emotionally nuanced Mongolian voice with a stable identity. Do not imitate or clone the original actor; use the source performance only as a reference for dramatic intent, pacing, and emotional contrast.

## 2. Important correction: speaker identity audit

The six acoustic test groups were cross-checked against the current `speaker_assignments.json`. Some cue windows previously included other characters and must not be used as Vivienne voice evidence.

| Test group | Cues | Speaker audit | Use for Vivienne profile |
|---|---|---|---|
| Normal | 66–67 | C001 Vivienne (narration) | **Include** |
| Normal | 68–70 | C004 Mother | **Exclude** |
| Emotional | 698–702 | C001 Vivienne (narration / inner monologue / dialogue) | **Include** |
| Quiet | 9–10, 13, 17–19 | C001 Vivienne | **Include** |
| Quiet | 11–12, 14–16 | C002 Lucian | **Exclude** |

This means the earlier normal-group conclusion based on cues 66–70 and quiet-group conclusion based on cues 9–19 were mixed-speaker observations. They are not valid as a single-character Vivienne profile. The cue 68 “sadness” example belongs to Mother, not Vivienne; quiet cues 11–12 and 15–16 belong to Lucian.

## 3. Corrected acoustic evidence (Vivienne-only cues)

Using only cues confirmed as C001 in the current speaker assignment file:

- **Normal:** cues 66–67; mean Speech-minus-Original RMS = **−3.62 dB** (2 cues). Both are narration, so this is evidence about Vivienne's narrated voice, not direct dialogue.
- **Emotional:** cues 698–702; mean = **−3.31 dB** (5 cues). Cue 701 is the emphatic/angry line.
- **Quiet:** cues 9, 10, 13, 17–19; mean = **−3.56 dB** (6 cues). Cues 9–10 and 17–19 are inner monologue; cue 13 is narration.

These are small test subsets. The Speech versions have lower measured RMS in all three subsets. This does not, by itself, prove loss of breathiness or emotion. Original contains background audio and Speech has a different signal composition; measurements can reflect separation, denoising, gating, gain, or residual ambience.

### Qualitative interpretation, with speaker filtering applied

- Quiet cues 9–10 and 17–19 are Vivienne's restrained inner monologue. Gemini describes these as soft, breathy, low-intensity and slow.
- Quiet cue 13 is Vivienne narration and is described as neutral/clear; retain it as a contrast rather than labeling every quiet-group cue as sad.
- Emotional cue 701 is Vivienne's forceful angry line. Gemini describes the Original as more forceful than Speech, but this remains a perceptual machine assessment pending human listening.
- Normal cues 66–67 are Vivienne narration and are described as neutral/conversational. Do not use Mother cues 68–70 to characterize Vivienne.

The approximate F0 tracker is unreliable for several cues and must not be used to prescribe an exact pitch range.

## 4. Core voice identity

**Target:** a natural, mature-sounding Mongolian female voice with clear articulation, stable timbre, and controlled emotional range.

Performance qualities:
- Clear and intelligible, but not overly polished or announcer-like.
- Conversational phrasing; avoid a uniformly theatrical delivery.
- Preserve natural consonants and vowel length in Mongolian.
- Keep phrase endings alive and connected to the thought; do not cut them off mechanically.
- Use breathiness only where the scene supports it. Do not make the entire performance whispery.
- Keep the character recognizable across narration, inner monologue, and spoken dialogue.

Do not lock an exact pitch number based on the current autocorrelation measurements.

## 5. Performance modes

### A. Neutral narration / everyday delivery
- Calm, direct, and conversational.
- Moderate pace with natural variation between clauses.
- Clear articulation without exaggerated emphasis.
- Keep the emotional baseline restrained; do not add sadness or warmth unless the context supports it.

### B. Sad / quiet / vulnerable inner monologue
- Reduce vocal force rather than simply lowering the volume in post.
- Use a contained, intimate delivery with a slightly slower pace.
- Allow gentle breathiness and softer phrase onsets where natural.
- Preserve small hesitations and phrase tails when they carry vulnerability.
- Avoid constant whispering, excessive vocal fry, or an artificially trembling voice.
- Do not flatten every line into the same sad tone; distinguish resignation, hurt, grief, and quiet reflection when the scene supports those differences.

### C. Anger / confrontation (cue 701 reference)
- Increase intention and emphasis, not just loudness.
- Use firmer projection, sharper consonant focus, and more decisive phrasing.
- Allow controlled vocal tension and dynamic pitch movement.
- Keep the anger credible and contained; avoid shouting unless the source performance clearly calls for it.
- Maintain intelligibility in Mongolian even during forceful delivery.

### D. Narration / inner monologue
- Use the same Vivienne voice identity as direct dialogue.
- Narration and inner monologue are delivery roles, not separate speaker identities.
- Reflective narration can remain intimate and measured.
- Do not create a separate “Narrator” voice for this film.

## 6. Existing ElevenLabs direction conventions

The current project convention recorded for Vivienne is:
- Narration: `[reflective]`
- Natural pause: `[pause]`
- Direct dialogue: no tag by default

Keep this as the baseline. Add emotion tags only when a specific line needs them and after auditioning the generated result. Do not stack several emotion tags automatically. The tag should support the acting direction, not replace it.

## 7. Corrected priority A/B listening set

Compare the matching Original and Speech files. Use two passes:

1. **Natural-level pass:** listen without independently normalizing cues. Record the natural level and emotional contrast.
2. **Loudness-matched pass:** match playback loudness only for judging timbre, breath, articulation, and phrase tails. Do not mistake loudness matching for evidence that the source dynamics are equivalent.

| Priority | Cue | Time in film | Subtitle | Role | Listen for |
|---|---:|---|---|---|---|
| A | 66 | 00:02:04.958–00:02:06.500 | Ээж Лусиан руу эргэж харав. | Narration | Neutral baseline, clarity, phrase ending |
| A | 67 | 00:02:06.500–00:02:08.166 | Тэр хүчээр инээмсэглэв. | Narration | Measured narration, natural cadence |
| A | 701 | 00:22:22.200–00:22:23.500 | Новшийн амьтан! | Direct dialogue | Anger, emphasis, force, intelligibility |
| A | 9 | 00:00:22.000–00:00:23.125 | Би юм хэлэхийг оролдсон ч | Inner monologue | Soft onset, breathiness, vulnerability |
| A | 10 | 00:00:23.583–00:00:24.600 | амнаас минь ганц ч үг гарсангүй. | Inner monologue | Phrase continuation, breath, ending |
| B | 13 | 00:00:29.541–00:00:30.800 | Түүний хоолой огт чичирсэнгүй. | Narration | Neutral contrast against sad lines |
| B | 17 | 00:00:36.000–00:00:37.374 | Би орилмоор байлаа. | Inner monologue | Restrained anger / suppressed force |
| B | 18 | 00:00:37.500–00:00:39.166 | Түүнийг тасчин хаямаар байлаа. | Inner monologue | Intensity continuity and articulation |
| B | 19 | 00:00:39.200–00:00:41.000 | Гэвч миний бие аль хэдийн амьгүй болж байв. | Inner monologue | Emotional falloff and phrase tail |

For each cue, record:
- Original vs Speech: emotion and intensity (low / medium / high).
- Breathiness: less / same / more.
- Articulation clarity: worse / same / better.
- Phrase onset and ending: cut / preserved / exaggerated.
- Does Speech remain a useful clarity reference?
- Which version better preserves Vivienne's acting intent?

Do not score cues 68–70 or quiet cues 11–12 and 14–16 as Vivienne. They belong to Mother or Lucian in the current speaker assignment file.

## 8. First ElevenLabs audition set

Use the same voice and broadly consistent generation settings for all variants. Change only the acting direction so the comparison is meaningful.

1. **Neutral narration:** conversational, clear, restrained, natural Mongolian phrasing.
2. **Quiet / vulnerable inner monologue:** intimate, slightly slower, softer vocal force, subtle breathiness, preserve phrase tails; no whispering.
3. **Angry direct dialogue:** firm projection, sharper emphasis, controlled tension, dynamic phrasing; no automatic shouting.
4. **Reflective narration:** intimate, measured, thoughtful; retain the existing `[reflective]` convention.

Evaluate each render for:
- Stable character identity across all four variants.
- Natural Mongolian pronunciation and stress.
- Emotional contrast without exaggerated acting.
- Preserved consonants, vowel length, and phrase endings.
- No clipping, robotic cadence, or unnatural breath insertion.

Do not finalize numerical ElevenLabs settings (stability, similarity, style, speed, pitch) from this small sample. Keep the voice ID/model and generation settings fixed during the first controlled comparison; record the exact settings used.

## 9. User evaluation of the first generated audition set (2026-11-08)

The user listened to all four ElevenLabs renders generated with model `eleven_v3` and voice **Vivienne (6Km4T9TrZXIhfMaxglHw)**. All four were rated **“боломжийн” (acceptable / reasonable)**:

| Variant | Intended performance | User evaluation |
|---|---|---|
| A — Neutral | Everyday narration | Боломжийн |
| B — Reflective | Thoughtful, restrained narration | Боломжийн |
| C — Quiet | Vulnerable inner monologue, not over-whispered | Боломжийн |
| D — Angry | Angry dialogue without excessive shouting or theatricality | Боломжийн |

### Interpretation and limits

- The candidate voice is acceptable as the **working Vivienne voice** for the next calibration stage.
- No variant was identified as a clear winner; the four variants represent different delivery modes, not four competing voice identities.
- “Боломжийн” is an initial acceptability judgment, not final sign-off for the full film.
- The user has not yet provided detailed comments on pronunciation, timbre, phrase endings, or whether one mode needs adjustment.
- Keep the same voice ID and model for the next comparison. Do not change multiple generation parameters at once.
- Do not infer that the four performances have identical timbre or that the voice is production-final based only on this brief evaluation.

## 10. Provisional production decisions

1. Keep Original as the emotional-performance reference.
2. Use Speech as a secondary clarity/intelligibility reference.
3. Use only C001 cues when drawing conclusions about Vivienne.
4. Preserve one Vivienne voice identity across narration, inner monologue, and dialogue.
5. Do not apply uniform emotion or loudness normalization.
6. Do not finalize pitch, speed, stability, similarity, or style settings until the manual A/B review and four audition variants are evaluated.

## 11. Next action

Treat the current voice ID as the working Vivienne candidate. Next, perform a controlled parameter-calibration round while keeping the voice ID and model fixed. Change one setting at a time, compare the resulting clips against this accepted baseline, and record the exact settings and user preference before locking a production preset. Do not select one of A–D as the sole winner: all four are accepted as usable delivery modes.


## 12. User evaluation of the softer angry-dialogue audition D2 (2026-11-08)

A separate softer angry-dialogue audition was generated using the same Vivienne voice ID **6Km4T9TrZXIhfMaxglHw** and model **eleven_v3**. The acting direction was controlled frustration: softer attack, less harshness, and no shouting. The user listened to the D2 render and confirmed **“болж байна” (works / acceptable)**.

- Keep D2 as the accepted working direction for Vivienne's angry dialogue.
- Preferred acting quality: feminine and softer in attack, but still clearly frustrated, firm, and intentional.
- Avoid harshness, shouting, or excessive aggression unless a particular scene explicitly requires it.
- Retain the original D version as a comparison reference; do not delete or overwrite it.
- This is approval of the D2 performance direction, not a final lock of all ElevenLabs numerical settings or the complete film's voice mix.

Update the anger performance baseline from the generic D direction in Section 5C to this more specific D2 direction for subsequent Vivienne angry-dialogue generation.
