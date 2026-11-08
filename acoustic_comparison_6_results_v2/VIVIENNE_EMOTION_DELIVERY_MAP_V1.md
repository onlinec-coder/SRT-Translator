# Vivienne — Emotion Delivery Map V1

Date: 2026-11-08
Repository scope: `onlinec-coder/SRT-Translator` only
Status: **Planning inventory only — no TTS generated and no ElevenLabs credits used**

## 1. Locked voice-production constraints

- Character identity: C001 Vivienne across narration, inner monologue, and direct dialogue.
- Voice ID: `6Km4T9TrZXIhfMaxglHw`.
- Model: `eleven_v3`.
- Keep saved numerical voice defaults unchanged.
- A — Neutral, B — Reflective, C — Quiet remain accepted working directions.
- D3 — `[angry]` is validated against the original film for two separate lines: cue 736 and cue 710. The user confirmed all three criteria for both: clear anger/confrontation, feminine controlled Vivienne identity, and match to the original acting.
- D2 remains a softer comparison reference.
- Do not generate more audition audio unless a specific unresolved production question requires it and the user approves the paid request first.

## 2. Purpose

This map groups existing C001 lines by likely acting function so production can select the right delivery without applying the same emotional tag to every line. The group labels below are **editorial hypotheses based on the verified Mongolian subtitle text and scene sequence**, not claims that every line has been acoustically or visually validated. Original-film performance remains the final reference.

## 3. Candidate emotion groups

| Group | Candidate cues / film time | Verified Mongolian text (selected) | Suggested delivery principle |
|---|---|---|---|
| A. Neutral / matter-of-fact | 47 (00:01:32.791); 198 (00:06:41.400); 534 (00:16:18.400) | “Үгүй.” / “Мэдэж байна.” / “Дотогш орж болох уу?” | Conversational, direct, no added emotional coloring unless the scene clearly calls for it. |
| B. Reflective / hurt realization | 427, 430–434 (00:13:19–00:13:30) | “Тэр чамайг огт мэддэггүй юм байна.” … “тэр надтай уулзахаар ирдэггүй байжээ.” | Let the realization land; restrained hurt and disbelief, not melodrama. Phrase-by-phrase continuity matters. |
| C. Quiet vulnerability / trauma | 17–19 (00:00:36–00:00:41); 1153/1155 (00:35:50–00:35:54) | “Би орилмоор байлаа. Түүнийг тасчин хаямаар байлаа. Гэвч миний бие аль хэдийн амьгүй болж байв.” / “Би арван долоотой байсан.” | Intimate and emotionally exposed, but intelligible; no automatic whispering. The repeated age line needs scene-context review before choosing one cue. |
| D. Controlled hurt / bitter irony | 679–680, 684–686, 690 (00:21:35–00:22:05) | “Чи сэтгэл хүйтэн эмэгтэйтэй болсон. Чиний хүссэн зүйл чинь энэ биз дээ?” / “Гэрээн дээр чинь миний нэр байгаагүй.” / “надгүйгээр асуудалгүй өнгөрсөн бололтой.” | Cool, pointed, wounded irony. Do not use full D3 anger unless the original acting clearly rises to anger. |
| E. Controlled anger / confrontation | 701, 705–710 (00:22:22–00:22:37); 734–736 (00:23:13–00:23:19) | “Новшийн амьтан!” / “Чи намайг хүсэл зоригийн минь эсрэг энд авчирсан.” / “Одоо бүр надаас тайлбар нэхэж байна уу?” / “Чиний надад өгөхөөр шийдсэн юуг ч хамаагүй хүлээн авах ёстой байсан уу?” | D3 is the validated starting direction for the clearly angry peaks. Adapt intensity per line; do not flatten the whole sequence into one continuous shout. Cues 710 and 736 have direct user approval against the original video. |
| F. Firm boundary / calm defiance | 712–713, 722–724 (00:22:40–00:23:01); 758 (00:23:55); 765–789 (00:24:12–00:25:02) | “Би явлаа.” / “Шийдэх ямар ч асуудал байхгүй.” / “Чи өөрийнхөө сонголтыг хийсэн. Би ч бас өөрийнхийгөө хийсэн.” / “Та хүнээ андуурчээ.” | Firm, self-possessed, decisive. Strength comes from clear intention and emphasis, not necessarily anger. |
| G. Evidence-led, assertive explanation | 775–789, 812–819 (00:24:35–00:26:06) | “Хоёр хоногийн өмнө энэ гэрт ирсэн эмэгтэй би биш.” / “Түүний нэрийг Моргана гэдэг.” / “Надтай уулзах гэж биш. Түүнтэй уулзах гэж.” | Controlled confidence; articulate facts cleanly. Emphasize contrast only where the meaning requires it. |
| H. Sarcasm / dry resignation | 913–915 (00:28:47–00:28:51) | “Тэгвэл хүссэндээ хүрч дээ. Намайг гэрт минь явуул.” | Dry, tired, possibly bitter; verify the film's exact emotional temperature before adding sarcasm. |
| I. Disgusted, decisive refusal | 925–926, 963 (00:29:07–00:30:10) | “Чи намайг дүр эсгээд чиний хань болохыг хүсэж байна уу?” / “Ингэж болохгүй.” | Disgust with slight, controlled anger; firm and decisive, without shouting or aggression. |
| J. Hopeful resolution / cautious warmth | 1203–1205 (00:37:24–00:37:28) | “Тохирлоо. Гэхдээ энэ удаа бид хоёулаа аз жаргалтай болно.” | Gentle resolve and cautious optimism; avoid turning it into an overly bright or theatrical happy voice. |

## 4. Recommended validation order — no new TTS yet

1. **D — Controlled hurt / bitter irony:** review cues 679–690 against the original film. This is distinct from the already validated angry confrontation.
2. **F — Firm boundary / calm defiance:** review cues 722–724 and 758 against the original film. Determine whether the delivery is cool/decisive rather than angry.
3. **B/C — Hurt realization and vulnerability:** review cues 427–434 and 17–19. Keep narration/inner-monologue voice identity identical to direct dialogue.
4. **G — Evidence-led explanation:** review cues 775–789 and 812–819. This is a long multi-cue sequence; prioritize continuity and clear Mongolian articulation.
5. **I/J — Emotional limit and resolution:** review cues 925–926, 963, and 1203–1205.

For each group, first listen to the original film and existing generated clips if available. Record the user's judgment. Do not spend credits just to create a sample when the original performance already provides enough direction.

## 5. Production rules

- Emotional category is not a command to add a literal ElevenLabs tag. Select tags only after listening to the original performance.
- Use `[angry]` D3 only where anger is clearly present and strong enough; do not apply it to bitterness, sadness, irony, firmness, or hurt by default.
- Keep one Vivienne voice identity across all delivery roles.
- Preserve cue boundaries and subtitle wording. Do not merge cues into new text without checking the timing and source.
- If a line's emotion is ambiguous, mark it **needs original-video review** rather than guessing.
- Any future paid TTS request must have a specific question, selected cue(s), expected comparison, and the user's approval before generation.

## 6. Evidence and scope

The candidate cue IDs, text, timestamps, speaker IDs, and speaker roles in this inventory were checked against `Husbands_mn_v3.srt` and `speaker_assignments.json` in this repository. Only C001 Vivienne character lines are used for the dialogue inventory; inner-monologue cues are included where explicitly identified. No other repository was consulted.

## 7. User-confirmed clarification — group D (2026-11-08)

The user explicitly confirms that the scene at cues 679–690 (approximately 00:21:35–00:22:05) is **hurt, cold irony / bitter sarcasm, not anger**. Keep this distinction firm: do not use the D3 `[angry]` direction for this passage. The delivery should feel wounded, cool, and pointed, with restrained ironic emphasis. This is a user-confirmed acting interpretation and takes precedence over any broad text-based inference.



## 8. User-confirmed clarification — group F, cues 722–724 (2026-11-08)

The user compared cues 722–724 (00:22:57.200–00:23:00.791) against the original film and confirmed all three delivery criteria:

1. Calm but decisive — **yes**.
2. A slight trace of hurt / emotional injury remains audible — **yes**.
3. Does not lean into anger or become excessively cold — **yes**.

Treat this passage as **calm, self-possessed boundary-setting with restrained hurt**. Do not use the D3 `[angry]` direction. The strength comes from the certainty of her decision, not raised intensity. This is a user-confirmed interpretation, not merely a text-based hypothesis.


## 9. User-confirmed clarification — group F, cue 758 (2026-11-08)

The user compared cue 758 (00:23:55.800–00:23:56.958), “Та хүнээ андуурчээ.”, against the original film and confirmed:

1. Calm and self-confident — **yes**.
2. A firm position is clearly conveyed — **yes**.
3. Not angry or sarcastic — **yes**, with a slight trace of displeasure.

Treat this line as **calm, confident correction with firm resolve and slight displeasure**. Do not use D3 `[angry]`; do not add sarcasm. This is a user-confirmed acting interpretation.


## 10. User-confirmed clarification — group B, cues 427 and 430–434 (2026-11-08)

The user compared this passage (approximately 00:13:19–00:13:30) against the original film and identified the emotional delivery as a combination of **hurt, loss of trust, and slight disgust at discovering the truth**. The speaking tone is **slightly lowered, close to a whisper**.

Preserve all of these elements together:
- The hurt and broken trust are the emotional core.
- The slight disgust comes from the truth becoming clear; do not turn it into overt anger or an aggressive outburst.
- Keep the voice somewhat low and softly delivered, almost whispering, while preserving clear Mongolian articulation.
- Maintain continuity across cues 427 and 430–434 so the realization unfolds as one connected emotional thought.

This is the user's confirmed interpretation of the original performance and supersedes the initial generic “restrained hurt and disbelief” hypothesis for this passage.


## 11. User-confirmed clarification — group C, cues 17–19 (2026-11-08)

For cues 17–19 (approximately 00:00:36–00:00:41), the user specifies **ordinary Vivienne narration delivery**, with no strong emotional leaning in either direction. Do not impose fear, shock, anger, trauma, or whispering merely because of the subtitle wording.

Use the established natural Vivienne narration voice: balanced, steady, and matter-of-fact. Preserve the meaning and clarity without adding an emotional performance that is not present in the original.


## 12. User-confirmed clarification — narration baseline and cues 1153/1155 (2026-11-08)

The user clarifies a general production principle: **Vivienne narration passages generally carry little to no added emotion**. Do not assume narration should be emotionally performed simply because the content describes a painful or dramatic event.

For cues 1153/1155 (approximately 00:35:50–00:35:54), “Би арван долоотой байсан.”, the user confirms that Vivienne herself speaks in her **ordinary, natural voice**.

Direction:
- Use the standard Vivienne narration voice, neutral and natural.
- Do not add a special emotion, dramatic emphasis, sadness, fear, or whispering unless the original performance clearly contains it.
- Keep the narration consistent with the neutral delivery established for cues 17–19.


## 13. User-confirmed clarification — group G, cues 775–789 (2026-11-08)

The user compared cues 775–789 (approximately 00:24:35–00:25:02) against the original film and confirmed all three criteria:

1. Vivienne is calm and self-confident — **yes**.
2. She explains the facts clearly and decisively — **yes**.
3. Anger, hurt, or sarcasm does not dominate; she retains an ordinary conversational tone — **yes**.

Treat this passage as **calm, self-confident, clear factual explanation in Vivienne's natural conversational voice**. The decisiveness should come from clear articulation and intention, not added anger, bitterness, sarcasm, or theatrical emphasis.


## 14. User-confirmed clarification — group G, cues 812–819 (2026-11-08)

The user compared cues 812–819 (approximately 00:25:45–00:26:06) against the original film and confirmed all three criteria:

1. Vivienne remains calm and self-confident — **yes**.
2. She clearly articulates and emphasizes the contrast in phrases such as “Надтай уулзах гэж биш. Түүнтэй уулзах гэж.” — **yes**.
3. The delivery remains naturally decisive and explanatory, not angry or hurt — **yes**.

Treat this passage as **calm, self-confident factual explanation with clear contrastive emphasis**. Emphasize the key contrast through articulation, not through anger, bitterness, or theatrical emotion.


## 15. User-confirmed clarification — group H, cues 913–915 (2026-11-08)

The user compared cues 913–915 (approximately 00:28:47–00:28:51) against the original film and clarified that Vivienne is **expressing displeasure, not anger**. In particular, “Тэгвэл хүссэндээ хүрч дээ” should be delivered with displeasure rather than cold irony, bitter sarcasm, or contempt.

Production direction:
- Convey restrained, audible displeasure.
- Do not turn the line into anger, aggression, cold sarcasm, or bitter resignation.
- Keep the delivery natural and controlled, consistent with the original performance.


## 16. User-confirmed clarification — group I, cues 925–926 (2026-11-08)

The user compared cues 925–926 (approximately 00:29:07–00:29:12) against the original film and clarified that Vivienne delivers the refusal with **disgust and a slight degree of anger**.

Production direction:
- The emotional color is disgust, with a restrained trace of anger.
- Do not recast this as quiet sadness, wounded vulnerability, or purely calm refusal.
- Keep the anger slight and controlled; do not escalate into shouting or an aggressive outburst unless the original performance clearly does so.


## 17. User-confirmed clarification — group I, cue 963 (2026-11-08)

The user compared cue 963 (approximately 00:30:08–00:30:10) against the original film and confirmed:

- Vivienne speaks with **disgust**.
- A **slight degree of anger** is audible.
- Her voice is **decisive and firm**; she states her position with resolve.

Production direction:
- Preserve the combination of disgust, slight controlled anger, and decisiveness.
- Do not soften the line into sadness or a merely vulnerable refusal.
- Do not exaggerate the anger into shouting or aggression.
- Keep the delivery natural and faithful to the original performance.
