# Vivienne — ElevenLabs Controlled Audition Plan V1

Date: 2026-11-08  
Status: **Prepared — generation and human evaluation pending**

## 1. Objective

Create four short Mongolian audition renders to test whether one voice can carry Vivienne's neutral narration, reflective narration, vulnerable inner monologue, and angry direct dialogue without losing a consistent character identity.

This is a performance-direction test, not a final voice-setting optimization. The four clips use different verified film lines because each line has a different narrative function. Since the text differs, compare the results as a direction/acting check, not as a perfectly controlled acoustic experiment.

## 2. Fixed generation conditions

Keep these unchanged for all four auditions:
- Voice ID: `t9cfscnpanqv8SAN8rHS`
- Model: `eleven_v3`
- Same output format and generation configuration.
- Do not change stability, similarity, style, speed, or any other numerical setting between variants.
- Do not apply per-clip loudness normalization before the first listening pass.
- Record the exact generation settings used with the output filenames.

Only the text and the intended acting direction vary. If the current project configuration has changed since this plan was written, record the actual current values rather than silently overriding them.

## 3. Four audition variants

### A. Neutral narration — cue 67

**Verified subtitle text:**

`Тэр хүчээр инээмсэглэв.`

**Direction:** Calm, conversational, observational narration. Moderate pace. Clear consonants, natural vowel length, no added sadness or dramatic emphasis. The phrase should sound like a thought being narrated, not a documentary announcer.

**Purpose:** Establish a clean baseline for Vivienne's narration.

### B. Reflective narration — cue 13

**Verified subtitle text:**

`[reflective] Түүний хоолой огт чичирсэнгүй.`

**Direction:** Intimate and thoughtful, measured but not slow for its own sake. Let the meaning settle naturally. Keep the voice recognizably the same as Variant A; change the delivery, not the identity.

**Purpose:** Test the existing `[reflective]` convention on a verified Vivienne narration cue.

### C. Quiet / vulnerable inner monologue — cues 9–10

**Verified subtitle text:**

`Би юм хэлэхийг оролдсон ч амнаас минь ганц ч үг гарсангүй.`

**Direction:** Restrained, intimate, emotionally contained. Slightly softer vocal force and a naturally measured pace. Allow subtle breath where it occurs naturally; preserve the phrase ending. Do not whisper, over-breathe, tremble artificially, or flatten the line into a monotone.

**Purpose:** Test whether the voice can communicate vulnerability without becoming indistinct.

### D. Angry direct dialogue — cue 701

**Verified subtitle text:**

`Новшийн амьтан!`

**Direction:** Firm, immediate, forceful emphasis. Sharper consonants and controlled vocal tension. The anger should be clear, but do not turn it into uncontrolled shouting. Keep the Mongolian words fully intelligible.

**Purpose:** Test whether the same voice can deliver a strong emotional peak without sounding like a different character.

## 4. Text and tag handling

- Use only the exact Mongolian subtitle text shown above.
- Keep `[reflective]` only on Variant B as the existing project convention.
- Do not add `[pause]` unless a real pause is required by the source performance and the text is split at that pause.
- Do not invent new emotion tags during this first comparison.
- Keep acting directions in the production notes; do not paste the prose direction into the spoken text field.

## 5. Output naming

Save the four generated files with clear names, for example:

- `vivienne_audition_A_neutral_narration.wav`
- `vivienne_audition_B_reflective_narration.wav`
- `vivienne_audition_C_quiet_inner_monologue.wav`
- `vivienne_audition_D_angry_dialogue.wav`

If the generation service returns a different audio format, preserve its actual extension and note the format. Do not overwrite the six original acoustic comparison WAV files.

## 6. Human evaluation checklist

Listen to all four clips in one session. Evaluate:

| Criterion | What to check |
|---|---|
| Character identity | Does each clip still sound like the same Vivienne? |
| Mongolian naturalness | Are pronunciation, stress, vowel length, and consonants natural? |
| Neutral narration | Is it conversational rather than announcer-like? |
| Reflective narration | Is the thought intimate and measured without overacting? |
| Vulnerability | Is emotion present without whispering or artificial trembling? |
| Anger | Is it forceful and intelligible without unnecessary shouting? |
| Phrase endings | Are word endings and sentence tails preserved naturally? |
| Artifacts | Any clipping, robotic rhythm, strange pauses, or inserted breaths? |

Record each item as **pass / partial / fail**, with a short note and timestamp if needed.

## 7. Decision rules

- If all four sound like the same character and each mode is believable, keep the voice identity and refine only performance direction.
- If neutral and reflective narration sound like different people, reduce the difference in acting direction before changing voice settings.
- If the quiet line is unintelligible, first adjust articulation and vocal support; do not immediately increase loudness or add whisper tags.
- If anger sounds shouted or distorted, reduce the acting intensity before changing numerical voice settings.
- Do not select final settings based on one short line. Use a larger sample after the first audition succeeds.

## 8. Current project decisions

- Vivienne remains one voice identity (C001) across narration, inner monologue, and direct dialogue.
- Narration and inner monologue are delivery roles, not separate speaker identities.
- Existing tag baseline: narration `[reflective]`; natural pause `[pause]`; direct dialogue untagged by default.
- No numerical ElevenLabs settings are finalized by this document.

## 9. Next step after generation

Add the four output files and the completed evaluation notes to the authorized `SRT-Translator` repository. Then compare the human listening results with the corrected speaker-filtered acoustic findings before making V2 decisions.
