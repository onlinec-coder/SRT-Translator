# Vivienne — Mongolian Dubbing Voice Direction (V1 / Provisional)

Date: 2026-11-08
Project: Husbands
Status: **Provisional direction — pending manual A/B listening and generated-voice audition**

## 1. Purpose

Define a consistent Mongolian performance direction for Vivienne across direct dialogue, inner monologue, and narration. The goal is a believable, emotionally nuanced Mongolian voice with a stable identity. Do not imitate or clone the original actor; use the source performance only as a reference for dramatic intent, pacing, and emotional contrast.

## 2. Evidence currently available

### Supported by the six acoustic comparisons

- Normal cues 66–70: the voice is broadly stable, clear, and conversational. The Speech stem is quieter than Original by an average of about 5.25 dB RMS across this small sample.
- Emotional cues 698–702: Speech is quieter by about 3.31 dB RMS on average. Cue 701 is the emphatic/angry example; the Speech stem has lower RMS and peak than Original.
- Quiet cues 9–19: Speech is quieter by about 4.56 dB RMS on average. The quietest frame levels are often substantially lower in Speech.
- The approximate F0 tracker is unreliable for several cues and must not be used to prescribe an exact pitch range.

### Qualitative Gemini analysis

- Sad/quiet delivery is described as softer, lower-intensity, more restrained, sometimes breathy, and slower.
- Cue 701 Original is described as more forceful and angry than its Speech counterpart.
- Several short cues are emotionally ambiguous; do not force an emotion label where the performance is neutral or unclear.

### Important limitation

These are short samples. The Original contains background audio, and the Speech stem has a different signal composition. The measured differences cannot isolate whether changes came from source separation, denoising, gating, gain, or other processing. Treat this direction as a testable starting point, not a final full-film voice specification.

## 3. Core voice identity

**Target:** a natural, mature-sounding Mongolian female voice with clear articulation, stable timbre, and controlled emotional range.

Performance qualities:
- Clear and intelligible, but not overly polished or announcer-like.
- Conversational phrasing; avoid a uniformly theatrical delivery.
- Preserve natural consonants and vowel length in Mongolian.
- Keep phrase endings alive and connected to the thought; do not cut them off mechanically.
- Use breathiness only where the scene supports it. Do not make the entire performance whispery.
- Keep the character recognizable across narration, inner monologue, and spoken dialogue.

Do not lock an exact pitch number based on the current autocorrelation measurements.

## 4. Performance modes

### A. Neutral / everyday dialogue

- Calm, direct, and conversational.
- Moderate pace with natural variation between clauses.
- Clear articulation without exaggerated emphasis.
- Keep the emotional baseline restrained; do not add sadness or warmth unless the context supports it.

### B. Sad / quiet / vulnerable

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

## 5. Existing ElevenLabs direction conventions

The current project convention recorded for Vivienne is:
- Narration: `[reflective]`
- Natural pause: `[pause]`
- Direct dialogue: no tag by default

Keep this as the baseline. Add emotion tags only when a specific line needs them and after auditioning the generated result. Do not stack several emotion tags automatically. The tag should support the acting direction, not replace it.

## 6. Six priority A/B listening checks

Compare Original and Speech at matched playback loudness where possible. Do not normalize each cue independently before first noting its natural level difference.

| Cue | Test | Listen for | Decision to record |
|---|---|---|---|
| Normal 68 | Soft/low-energy line | Does Speech lose breath, softness, or phrase tail? Is the apparent pitch change audible or only a tracking error? | Preserve / partially preserve / not audible |
| Emotional 701 | Angry/emphatic line | Does Speech reduce force, edge, emphasis, or emotional urgency? | Preserve / partially preserve / not audible |
| Quiet 9 | Quiet emotional line | Are breath and soft onset preserved? | Preserve / partially preserve / not audible |
| Quiet 11 | Neutral/clear contrast line | Is the voice body or consonant clarity reduced? | Preserve / partially preserve / not audible |
| Quiet 12 | Very soft / low-level segment | Is speech still intelligible? Is the low level intentional or extraction loss? | Preserve / partially preserve / not audible |
| Quiet 16 | Restrained emotional line | Is the low register / subdued quality preserved? | Preserve / partially preserve / not audible |

For each cue, record:
1. Original emotion and intensity (low / medium / high).
2. Speech emotion and intensity (low / medium / high).
3. Breathiness (less / same / more).
4. Articulation clarity (worse / same / better).
5. Phrase onset and ending (cut / preserved / exaggerated).
6. Whether the Speech stem is suitable as a dubbing performance reference.

## 7. First ElevenLabs audition set

Use the same voice and broadly consistent generation settings for all variants. Change only the acting direction so the comparison is meaningful.

1. **Neutral baseline:** conversational, clear, restrained, natural Mongolian phrasing.
2. **Quiet/sad:** intimate, slower, softer vocal force, subtle breathiness, preserve phrase tails; no whispering.
3. **Angry:** firm projection, sharper emphasis, controlled tension, dynamic phrasing; no automatic shouting.
4. **Reflective narration:** intimate, measured, thoughtful; retain the existing `[reflective]` convention.

Evaluate each render for:
- Stable character identity.
- Natural Mongolian pronunciation and stress.
- Emotional contrast between the four modes.
- No artificial whispering, excessive rasp, or overacting.
- Phrase timing and intelligibility.

## 8. Provisional decisions

- Use Original as the primary emotional-performance reference.
- Use Speech as a secondary clarity reference, not the sole source for emotional acting.
- Keep one Vivienne voice identity across dialogue, narration, and inner monologue.
- Do not apply one uniform emotion or loudness adjustment to every cue.
- Do not finalize pitch, speed, stability, similarity, or style values from this sample alone; audition controlled variants first.

## 9. Next gate

Before marking this direction final:
1. Complete the six matched A/B listening checks.
2. Generate the four audition modes with the same voice and settings.
3. Compare the renders against the Original performance and Mongolian subtitle intent.
4. Adjust only the acting direction or one generation setting at a time.
5. Record accepted settings and examples in a versioned voice profile.

**V1 status: provisional.** This document does not claim that the six audio cues have been manually auditioned in this session.
