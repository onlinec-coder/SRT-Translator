# Vivienne — Production TTS Preparation Guide V1

Date: 2026-11-08  
Status: **PRE-PRODUCTION PREPARATION COMPLETE — no TTS audio generated and no paid request authorized**

## 1. Purpose

This guide defines how to use the 29 chronological Vivienne cue batches and their per-cue TTS preparation files. It is an execution specification, not permission to generate audio.

## 2. Locked production inputs

- Repository: onlinec-coder/SRT-Translator only.
- Speaker identity: C001 Vivienne for narration, inner monologue, and direct dialogue.
- Voice ID: 6Km4T9TrZXIhfMaxglHw.
- Model: eleven_v3.
- Numerical voice settings: retain the current saved values; do not silently override or optimize.
- Source subtitles and timestamps: Husbands_mn_v3.srt.
- Speaker roles: speaker_assignments.json.
- Confirmed performance direction: VIVIENNE_MN_DUBBING_DIRECTION_V1.md and VIVIENNE_EMOTION_DELIVERY_MAP_V1.md.
- Per-cue source of truth: VIVIENNE_PRODUCTION_CUE_LEDGER_V1.json.
- Batch order: VIVIENNE_PRODUCTION_BATCH_PLAN_V1.json.

## 3. Batch inventory

| Batch | Cue ID span | Vivienne cues | Confirmed delivery | Needs scene review |
|---|---:|---:|---:|---:|
| VIV_01 | 1–53 | 32 | 3 | 29 |
| VIV_02 | 54–104 | 32 | 0 | 32 |
| VIV_03 | 105–158 | 34 | 0 | 34 |
| VIV_04 | 159–207 | 33 | 0 | 33 |
| VIV_05 | 208–244 | 33 | 0 | 33 |
| VIV_06 | 245–285 | 32 | 0 | 32 |
| VIV_07 | 289–334 | 32 | 0 | 32 |
| VIV_08 | 335–372 | 33 | 0 | 33 |
| VIV_09 | 373–413 | 32 | 0 | 32 |
| VIV_10 | 415–455 | 32 | 6 | 26 |
| VIV_11 | 456–496 | 32 | 0 | 32 |
| VIV_12 | 497–529 | 32 | 0 | 32 |
| VIV_13 | 530–569 | 33 | 0 | 33 |
| VIV_14 | 570–617 | 32 | 0 | 32 |
| VIV_15 | 618–656 | 33 | 0 | 33 |
| VIV_16 | 657–695 | 33 | 11 | 22 |
| VIV_17 | 696–735 | 32 | 4 | 28 |
| VIV_18 | 736–774 | 32 | 2 | 30 |
| VIV_19 | 775–814 | 32 | 16 | 16 |
| VIV_20 | 815–864 | 32 | 5 | 27 |
| VIV_21 | 865–897 | 33 | 0 | 33 |
| VIV_22 | 898–948 | 33 | 5 | 28 |
| VIV_23 | 949–983 | 33 | 1 | 32 |
| VIV_24 | 984–1022 | 32 | 0 | 32 |
| VIV_25 | 1024–1072 | 32 | 0 | 32 |
| VIV_26 | 1073–1105 | 33 | 0 | 33 |
| VIV_27 | 1106–1159 | 32 | 2 | 30 |
| VIV_28 | 1160–1206 | 32 | 3 | 29 |
| VIV_29 | 1207–1213 | 7 | 0 | 7 |

Total: 915 Vivienne cues in 29 batches.

## 4. Per-cue generation contract

1. Generate one separate audio asset per subtitle cue. Do not concatenate an entire batch into one TTS request.
2. Use each preparation file's `tts_text` as the request text and preserve its cue ID and original SRT start/end timestamps.
3. Keep the original `source_text` unchanged. Flatten SRT line breaks only in `tts_text`; do not paraphrase, translate, or silently normalize wording.
4. Use only the explicitly approved [angry] tag for the user-validated strong-anger cues 710 and 736. Other emotional classes are acting directions, not automatic Eleven v3 tags.
5. For `needs_scene_review` cues, use restrained natural Vivienne baseline. Do not infer acting emotion from subtitle text alone.
6. Use neighboring Vivienne cue IDs and direction as continuity context. Do not send neighboring cue text as part of the current cue's spoken text.
7. Do not insert [pause] or other tags unless the source acting and a separately approved direction require them.
8. Never change speaker assignments or subtitle timing as part of TTS preparation.

## 5. Batch-level QA gate

For each batch, before any paid generation:
- Confirm the batch's cue count and cue IDs match the batch plan.
- Confirm every cue is C001 and the timestamp/text matches the source SRT.
- Confirm the voice ID and model are unchanged.
- Inspect transitions between neutral, hurt, irony, displeasure, firmness, and anger; do not carry an emotion tag into neighboring cues automatically.
- Flag any cue whose source performance needs human review instead of guessing.
- Ensure the output naming scheme is deterministic, e.g. `VIV_01_CUE_0001.mp3`, and that retries do not overwrite a previously accepted asset without an explicit version suffix.

## 6. Timing and assembly rules

- Preserve source SRT timestamps as the authoritative placement for each generated cue.
- Measure actual generated audio duration before assembly.
- Flag any audio longer than its available subtitle window; do not speed-stretch or truncate automatically.
- Preserve natural phrase endings. Where a sentence spans multiple subtitle cues, inspect adjacent audio as a continuous thought while retaining separate timed assets.
- Maintain a QA report per batch with generated, passed, needs-fix, and not-generated counts.
- Final assembly must include checks for missing/duplicate cue IDs, overlap, gaps, clipping, abrupt loudness changes, and dialogue synchronization.

## 7. No-credit boundary

No ElevenLabs TTS request has been made during this preparation stage. No paid generation is authorized by this guide. Before the first batch is generated, obtain the user's explicit approval for the named batch and its expected request count / credit use.

## 8. Prepared batch files

- Batch 01: VIVIENNE_BATCH_01_TTS_PREP_V1.json
- Batches 02–29: VIV_02_TTS_PREP_V1.json through VIV_29_TTS_PREP_V1.json

Each file contains per-cue source text, TTS text, timestamp, delivery class, review status, direction, and continuity references.
