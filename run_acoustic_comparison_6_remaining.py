# -*- coding: utf-8 -*-
"""
Run the four remaining revised acoustic analyses for Husbands.

The emotional Original/Speech pilot results already exist in
acoustic_comparison_6_results_v2 and are preserved.
This runner analyzes only the normal and quiet Original/Speech pairs.
"""

import json
import time

import test_acoustic_comparison_6 as acoustic


TARGET_NAMES = (
    "normal_original",
    "normal_speech",
    "quiet_original",
    "quiet_speech",
)


def result_is_complete(path, item):
    if not path.exists():
        return False

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False

    expected = {f"Cue {cue_id}" for cue_id in item["cues"]}
    return isinstance(data, dict) and expected.issubset(data.keys()) and isinstance(
        data.get("comparison"), dict
    )


def main():
    items = {
        item["name"]: item
        for item in acoustic.AUDIO_FILES
        if item["name"] in TARGET_NAMES
    }

    print("HUSBANDS — REMAINING REVISED ACOUSTIC ANALYSES")
    print("Model: gemini-3.5-flash-lite")
    print(f"Output: {acoustic.OUTPUT_DIR}")
    print(f"Target files: {len(TARGET_NAMES)}")

    results = []

    for index, name in enumerate(TARGET_NAMES, start=1):
        item = items[name]
        output_path = acoustic.OUTPUT_DIR / f"{name}.json"

        print(f"\nFile {index}/{len(TARGET_NAMES)}: {name}")

        if result_is_complete(output_path, item):
            print(f"[SKIP] Complete result already exists: {output_path}")
            results.append((name, True, "already complete"))
            continue

        if output_path.exists():
            print("[WARNING] Existing result is incomplete or invalid; regenerating.")
            output_path.unlink()

        success = acoustic.process_audio(item)
        complete = result_is_complete(output_path, item) if success else False

        if success and not complete:
            print("[ERROR] Gemini хүсэлт амжилттай болсон ч JSON-д шаардлагатай бүх cue эсвэл comparison алга байна.")
            success = False

        results.append((name, success, "processed and validated" if success else "failed or incomplete"))

        if index < len(TARGET_NAMES):
            time.sleep(3)

    print("\n" + "=" * 60)
    print("SUMMARY")

    for name, success, note in results:
        status = "SUCCESS" if success else "FAILED"
        print(f"{status}: {name} ({note})")

    successful = sum(1 for _, success, _ in results if success)
    print(f"\nSuccessful: {successful}/{len(results)}")
    print(f"Results folder: {acoustic.OUTPUT_DIR}")


if __name__ == "__main__":
    main()
