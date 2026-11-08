import srt
from pathlib import Path

subtitle_text = Path("input.srt").read_text(
    encoding="utf-8-sig"
)

subtitles = list(srt.parse(subtitle_text))

for item in subtitles[:40]:
    text = item.content.replace("\n", " / ")
    print(f"{item.index}: {text}")