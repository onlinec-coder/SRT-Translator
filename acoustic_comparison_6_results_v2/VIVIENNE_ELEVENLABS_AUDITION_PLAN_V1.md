# Vivienne — ElevenLabs Controlled Audition Plan V1

Date: 2026-11-08  
Status: **Generated and initially evaluated — A, B, C, and D2 accepted as working delivery modes; numerical voice-setting calibration remains pending**

## 1. Objective

Create four short Mongolian audition renders to test whether one voice can carry Vivienne's neutral narration, reflective narration, vulnerable inner monologue, and angry direct dialogue without losing a consistent character identity.

This is a performance-direction test, not a final voice-setting optimization. The four clips use different verified film lines because each line has a different narrative function. Since the text differs, compare the results as a direction/acting check, not as a perfectly controlled acoustic experiment.

## 2. Fixed generation conditions

Keep these unchanged for all four auditions:
- Voice ID: `6Km4T9TrZXIhfMaxglHw` (verified working Vivienne candidate used for the generated auditions)
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
- Original Variant D: `[angry]` for firm anger; retained only as a comparison reference. The accepted D2 follow-up uses `[frustrated]` for softer, controlled frustration; do not add a shout tag.

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
- Reads optional `ELEVENLABS_VOICE_ID` from the environment or `.env`; if absent, it uses the newly supplied candidate ID `6Km4T9TrZXIhfMaxglHw`. This candidate must pass the live voice-access check before generation.
- Checks that the selected voice is accessible before sending any text-to-speech requests. If the ID is inaccessible, it stops before generating audio.
- Uses `eleven_v3` and `mp3_44100_128`.
- Omits per-request voice settings so all four requests use the same saved voice defaults.
- Saves MP3s and an `audition_manifest.json` under `acoustic_comparison_6_results_v2/vivienne_elevenlabs_auditions/`.
- Does not overwrite existing clips; it can resume by reusing files already generated.
- Stops after an API error to avoid repeated unexpected credit use.

The script makes four paid/credit-consuming API requests if none of the output clips already exists. The current candidate ID is `6Km4T9TrZXIhfMaxglHw`; the preflight check will confirm whether this API key can access it. If `.env` already contains `ELEVENLABS_VOICE_ID`, that value overrides the default candidate. Never guess or silently substitute a different voice. It never prints or modifies the API key. Do not commit `.env`.

## 10. Next step after generation

Listen to all four clips and complete the manual evaluation. Add the four output files and the completed evaluation notes to the authorized `SRT-Translator` repository if desired. Then compare the human listening results with the corrected speaker-filtered acoustic findings before making V2 decisions.


## 10. Actual generation and user evaluation (2026-11-08)

The four auditions were generated locally with:
- Voice ID: `6Km4T9TrZXIhfMaxglHw`
- Model: `eleven_v3`
- Output: `mp3_44100_128`
- Saved voice defaults; no numerical voice settings were overridden.

The user listened to A, B, C, and original D. All four were judged **“боломжийн”** (acceptable). A separate softer angry-dialogue D2 was then generated using the same voice ID/model and the tag `[frustrated]`, with text `Новшийн амьтан!`. The user listened to D2 and confirmed **“болж байна”**.

### Accepted working performance directions

| Mode | Working direction | Status |
|---|---|---|
| A — Neutral narration | Calm, conversational, clear | Accepted |
| B — Reflective narration | Intimate, measured, thoughtful | Accepted |
| C — Quiet inner monologue | Restrained, softer force, subtle breathiness; not whispering | Accepted |
| D2 — Angry dialogue | Feminine, softer attack, controlled frustration, firm intention, no shouting | Accepted |
| Original D — Angry | Stronger `[angry]` version | Comparison reference only; D2 is preferred working direction |

### Unified voice consistency rule

Keep the same recognizable Vivienne voice identity across all modes. Emotional contrast should come from phrasing, emphasis, pacing, and vocal force—not from making her sound like a different person. Even when angry, preserve a feminine, controlled, intelligible delivery. Do not make neutral or reflective lines artificially soft, and do not make quiet lines uniformly whispered.

### Next stage

Use these accepted delivery modes as the baseline for a broader, representative line sample. Calibrate numerical ElevenLabs settings only after confirming the same voice identity and natural Mongolian pronunciation across longer lines. Change one numerical setting at a time; record the exact value and compare against the current accepted baseline. No numerical setting is approved or locked by the present auditions.


## 11. Longer-line consistency round — prepared (2026-11-08)

The next audition uses four longer, verified Mongolian subtitle cues assigned to C001 Vivienne in the repository's current `speaker_assignments.json`. The intent is to test phrase flow and naturalness beyond the short initial audition lines. The same voice ID, model, output format, and saved voice defaults are retained.

| Mode | Cue | Verified role | Exact audition text | Direction |
|---|---:|---|---|---|
| A — Neutral | 153 | Narration | Тэр гараа өвдгөн дээрээ зөрүүлэн тавьж, огт хөдөлгөөнгүй суусаар байв. | Calm, conversational, clear |
| B — Reflective | 502 | Narration | Бид үгээ гүйцээж амжаагүй байхад ээж гэрээнүүдийг гаргаж ирсэн байлаа. | Thoughtful, measured, not artificially slow |
| C — Quiet | 293 | Inner monologue | Эсвэл би тодорхой зааж хэлж чадахаар ямар нэгэн зүйл хийгээгүй. | Contained vulnerability, softer force, not whispered |
| D2 — Soft angry | 736 | Direct dialogue | Чиний надад өгөхөөр шийдсэн юуг ч хамаагүй хүлээн авах ёстой байсан уу? | Feminine controlled frustration, softer attack, firm intention, no shouting |

Cue IDs, speaker roles, and text were checked against `Husbands_mn_v3.srt` and `speaker_assignments.json` in this repository. Do not change the wording for this audition.

### Local generation

New script: `generate_vivienne_long_line_auditions.py`

Run after pulling the repository:

```powershell
git pull
.\.venv\Scripts\python.exe generate_vivienne_long_line_auditions.py
```

The script can make up to four TTS requests, one per missing clip. It reuses any output clip that already exists, checks voice access before generation, and never prints or modifies the API key or `.env`.

Output folder: `acoustic_comparison_6_results_v2\vivienne_elevenlabs_auditions\`

Expected files:
- `vivienne_long_A_neutral_narration_cue153.mp3`
- `vivienne_long_B_reflective_narration_cue502.mp3`
- `vivienne_long_C_quiet_inner_monologue_cue293.mp3`
- `vivienne_long_D2_soft_angry_dialogue_cue736.mp3`
- `vivienne_long_line_auditions_manifest.json`

### Human listening checklist

Listen to each complete sentence, not only its opening:
1. Are Mongolian consonants, vowel lengths, and word stress natural?
2. Does the voice maintain one recognizable Vivienne identity across all four modes?
3. Are pauses and phrase endings natural, without abrupt cuts or excessive slowing?
4. Does B sound reflective without becoming sleepy or overacted?
5. Does C communicate vulnerability while remaining intelligible and not whispery?
6. Does D2 remain feminine and controlled while still conveying frustration?

Do not adjust stability, similarity, style, speed, pitch, or other numerical settings during this round. First establish whether the accepted performance directions remain natural over longer text. Record the user's listening notes before numerical calibration.


## 12. Longer-line listening results and D3 refinement (2026-11-08)

The user listened to all four longer-line clips and reported:
- Mongolian pronunciation and naturalness: yes.
- Long-sentence breathing and rhythm: yes.
- One consistent Vivienne identity across all four modes: yes.
- Sentence endings are not cut off: yes.
- D2 anger intensity: slightly too weak; the listener cannot clearly tell that the line is angry.

### Decision

The longer-line round passes for A, B, C, pronunciation, pacing, identity consistency, and phrase endings. Preserve the current accepted A/B/C directions and the same Vivienne voice ID/model. D2 remains a useful softer comparison, but is not yet strong enough as the final angry-dialogue direction.

Next generate one D3 comparison for cue 736 using the `[angry]` delivery tag, while keeping the same saved voice defaults and exact subtitle wording. Target a clearly perceptible increase in anger relative to D2, without shouting, harshness, or losing the feminine controlled Vivienne identity. This is a performance-direction test only; do not change numerical voice settings.

Generation script: `generate_vivienne_D3_controlled_angry.py`
Output: `acoustic_comparison_6_results_v2/vivienne_elevenlabs_auditions/vivienne_D3_controlled_angry_cue736.mp3`
One TTS request; may consume account credits. Existing output is reused. Keep D2 unchanged for A/B comparison.


## 13. D3 compared against the original video (2026-11-08)

The user compared the D3 controlled-angry audition for cue 736 against the corresponding performance in the original film, listening around 23:10–23:25 (cue 736: 00:23:17.600–00:23:19.166). The user's verdict was: "болсон байна" (acceptable / works).

### Decision

D3 is accepted as the current angry-delivery direction for Vivienne, based on the user's direct comparison with the original video. It is preferred over D2 for this cue because D3 was judged to work in the real-film comparison after D2 had been reported as too weak. Keep D2 as a softer comparison/reference, not the primary angry baseline.

This is a provisional performance-direction approval for Vivienne's controlled-angry mode, not approval to alter numerical voice settings or to apply the angry tag indiscriminately to every emotional line. Keep the same voice ID and eleven_v3 model. Preserve A/B/C directions. For future angry cues, adapt intensity to scene context and validate representative lines before applying the direction broadly.


## 14. Second-scene D3 validation — confrontation (2026-11-08)

After the user's approval of D3 against the original film for cue 736, the next validation is a distinct confrontation line, not another take of the same sentence. The verified cue is:

| Cue | Time in film | Role | Exact Mongolian line | Intended test |
|---:|---|---|---|---|
| 710 | 00:22:34.800–00:22:36.791 | C001 Vivienne, direct dialogue | Одоо бүр надаас тайлбар нэхэж байна уу? | Angry rhetorical confrontation; controlled feminine force, clear emphasis, no shouting |

This cue is part of the same confrontation sequence as cues 701 and 705–709. Cue 710 is selected first because it is a complete, self-contained rhetorical question and allows a focused comparison without joining multiple subtitle cues into one TTS request.

Generation script: `generate_vivienne_D3_confrontation_cue710.py`
Output: `acoustic_comparison_6_results_v2/vivienne_elevenlabs_auditions/vivienne_D3_confrontation_cue710.mp3`
One TTS request; it may consume account credits. The script reuses an existing output, checks voice access first, and reads the API key from the local environment or `.env` without printing or changing it.

Keep Voice ID `6Km4T9TrZXIhfMaxglHw`, model `eleven_v3`, and saved voice defaults unchanged. Use the same approved D3 `[angry]` tag. This is a second-scene validation only; do not apply the result to all angry lines until the user compares it against the original film.
