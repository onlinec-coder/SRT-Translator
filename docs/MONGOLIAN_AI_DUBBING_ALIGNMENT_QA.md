# Mongolian AI Dubbing — Practical Alignment QA Standard

**Status:** Active working standard  
**Priority:** Human-listener intelligibility and natural performance over mathematically perfect word timestamps.

## 1. Goal

Produce Mongolian AI dubbing that a normal viewer can understand comfortably and that sounds natural for the character and scene. Word-level alignment is a support tool, not the final quality target.

## 2. Acceptance criteria

A cue or connected speech segment is acceptable when:

- The spoken words preserve the intended meaning and are in the correct order.
- No important word is omitted or replaced.
- The voice is understandable at normal playback speed.
- Delivery, emotion, and character identity fit the scene.
- Timing is close enough that the dub feels synchronized with the scene.
- Small word-boundary deviations do not noticeably harm comprehension or perceived synchronization.

## 3. What to fix

Correct an issue when it materially affects one or more of these:

- A word is missing, duplicated, or spoken in the wrong order.
- A boundary cuts off a clearly audible word or creates an unnatural gap.
- The line noticeably starts too early or too late.
- A pause, pace, or phrase duration makes the delivery hard to understand.
- Emotion, emphasis, or character voice is clearly wrong.

Do not spend time correcting tiny timestamp differences that a viewer cannot hear or notice.

## 4. Word-level timestamps

- Use forced alignment as an initial estimate.
- Treat alignment scores as diagnostic signals, not calibrated probabilities.
- Fast, reduced, whispered, or connected speech may have compressed word durations.
- Do not delete a word merely because its aligned interval is short or its score is low.
- Preserve the intended transcript when the word is audibly present.
- Review by listening when an uncertainty could materially affect dubbing.
- Do not force word timestamps to fit an SRT cue window if the audio clip's true offset or duration has not been verified.
- Keep audio-relative timestamps distinct from original-film timestamps until the clip origin is known.

## 5. Review priority

Review in this order:

1. Correct words and meaning.
2. Intelligibility at normal listening volume and speed.
3. Natural phrasing, pacing, and pauses.
4. Character identity and emotional delivery.
5. Overall synchronization with the scene.
6. Fine word-level boundary polish only when it makes an audible difference.

## 6. Decision labels

- **PASS:** Clear and usable for the dubbing workflow.
- **PASS WITH WARNINGS:** Usable; a minor uncertainty remains but does not block progress.
- **REVIEW:** A specific issue may noticeably affect intelligibility or synchronization.
- **FAIL:** A material error makes the cue unsuitable for use.

## 7. Pilot decision — Cue 427

**Status: PASS for pilot use.**

- Text: `Тэр чамайг огт мэддэггүй юм байна.`
- The user listened to the MP3 and confirmed that `юм` is spoken quickly and faintly.
- Keep `юм` in the transcript; do not remove or merge it just because its current aligned interval is short.
- Retain the existing alignment as a practical estimate:
  - `ter`: 0.121–0.283 s
  - `chamaig`: 0.324–0.667 s
  - `ogt`: 0.708–0.950 s
  - `meddeggui`: 1.031–1.496 s
  - `yum`: 1.496–1.577 s
  - `baina`: 1.577–1.779 s
- These are relative to the MP3 start. Do not convert them to the film timeline until the clip offset is confirmed.
- No further timestamp refinement is required unless later listening reveals a noticeable synchronization or intelligibility problem.

## 8. Scope and safety

This standard does not authorize processing additional audio assets, changing audio, calling TTS, or uploading audio to new services. Those actions remain subject to the project's existing approvals.
