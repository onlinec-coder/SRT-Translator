import srt

with open("input.srt", encoding="utf-8-sig") as f:
    subtitles = list(srt.parse(f))

ids = [
    180, 275, 278, 279, 488, 493,
    518, 547, 559, 572, 544, 565,
    583, 603, 610, 620, 627, 651,
    762, 763, 773, 800, 811, 816,
    828, 852
]

for index in ids:
    subtitle = next(
        (s for s in subtitles if s.index == index),
        None
    )

    if subtitle:
        text = subtitle.content.replace("\n", " ")
        print(f"[{index}] {text}")
    else:
        print(f"[{index}] ОЛДСОНГҮЙ")