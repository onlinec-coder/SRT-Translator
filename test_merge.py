import json

from translator import merge_characters


with open(
    "Husbands_characters.json",
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)


characters = data["characters"]

merged = merge_characters(characters)


output = {
    "characters": merged
}


with open(
    "Husbands_characters_merged.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        output,
        file,
        ensure_ascii=False,
        indent=4
    )


print("Эх бүртгэл:", len(characters))
print("Нэгтгэсэн бүртгэл:", len(merged))
print("Шинэ файл: Husbands_characters_merged.json")