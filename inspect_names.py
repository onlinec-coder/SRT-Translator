import srt

names = [
    "Vivienne", "Viviana", "Vivian",
    "Lucian", "Lucien",
    "Aria", "Arya",
    "Morgana",
    "Alpha Various", "Alpha Valerce",
    "Alpha Valeris", "Alpha Valerius",
    "Luna Various", "Luna Valerce", "Luna Valerius",
    "Chief Elder LaRonde", "Chief Elder Laurent",
    "Chief Elder Lawrence",
    "Lance Laurent", "Luke Laurent",
    "Lawrence Brothers"
]

with open("input.srt", encoding="utf-8-sig") as f:
    subtitles = list(srt.parse(f.read()))

for name in names:

    matches = [
        sub for sub in subtitles
        if name.casefold() in sub.content.casefold()
    ]

    print(f"\n===== {name} ({len(matches)}) =====")

    for sub in matches:
        content = sub.content.replace("\n", " ")
        print(f"[{sub.index}] {content}")