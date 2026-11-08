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

The local generator uses Eleven v3 audio tags to make the acting comparison reproducible:
- Variant A: no tag (neutral baseline).
- Variant B: retain the project's existing `[reflective]` tag.
- Variant C: `[sad]` for a restrained vulnerable reading; do not use a whisper tag.
- Variant D: `[angry]` for firm anger; do not add a shout tag.

Use only the exact Mongolian subtitle wording shown above. Do not paste the prose acting directions into the spoken text field. Do not add `[pause]` unless the source performance contains a meaningful natural pause and the text is deliberately segmented there.

The emotional tags are a first-pass test, not a final decision. If a tag overacts or changes the character identity, record that and remove or replace it in the next audition round.

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

## 9. Local generation script

The repository includes two local diagnostic/generation scripts:
- `list_elevenlabs_voices.py`: lists the voices accessible to the API key in the local `.env`, including exact voice IDs.
- `generate_vivienne_auditions.py`: generates the four audition clips.

The generator:
- Uses only Python standard-library modules.
- Reads `ELEVENLABS_API_KEY` from the process environment or the project's local `.env`.
- Reads optional `ELEVENLABS_VOICE_ID` from the environment or `.env`; if absent, it tries the historical ID `t9cfscnpanqv8SAN8rHS`.
- Checks that the selected voice is accessible before sending any text-to-speech requests. If the ID is inaccessible, it stops before generating audio.
- Uses `eleven_v3` and `mp3_44100_128`.
- Omits per-request voice settings so all four requests use the same saved voice defaults.
- Saves MP3s and an `audition_manifest.json` under `acoustic_comparison_6_results_v2/vivienne_elevenlabs_auditions/`.
- Does not overwrite existing clips; it can resume by reusing files already generated.
- Stops after an API error to avoid repeated unexpected credit use.

The script makes four paid/credit-consuming API requests if none of the output clips already exists. If the historical voice ID returns 404, first run `list_elevenlabs_voices.py`, identify the intended Vivienne voice in the returned list, and set `ELEVENLABS_VOICE_ID` in the local `.env`. Never guess or silently substitute a different voice. It never prints or modifies the API key. Do not commit `.env`.

## 10. Next step after generation

Listen to all four clips and complete the manual evaluation. Add the four output files and the completed evaluation notes to the authorized `SRT-Translator` repository if desired. Then compare the human listening results with the corrected speaker-filtered acoustic findings before making V2 decisions.
