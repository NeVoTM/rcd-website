#!/usr/bin/env python3
"""Rebuild accident-miracle ES/FR from EN using MyMemory (Google rate-limit fallback)."""
import json
import time
from pathlib import Path

from deep_translator import MyMemoryTranslator

ROOT = Path(__file__).resolve().parent.parent / "data" / "transcripts"
SRC = ROOT / "accident-miracle.json"

TARGETS = {
    "es": "es-ES",
    "fr": "fr-FR",
}


def translate_text(text: str, lang_code: str, retries: int = 5) -> str:
    if not text.strip():
        return text
    target = TARGETS[lang_code]
    translator = MyMemoryTranslator(source="en-US", target=target)
    for attempt in range(retries):
        try:
            return translator.translate(text)
        except Exception as exc:
            wait = 3 * (attempt + 1)
            print(f"  wait {wait}s ({lang_code}): {exc}")
            time.sleep(wait)
    raise RuntimeError(f"failed to translate after {retries} attempts")


def build(lang_code: str):
    data = json.loads(SRC.read_text(encoding="utf-8"))
    print(f"Translating title -> {lang_code}")
    title = translate_text(data["title"], lang_code)
    time.sleep(1)
    lines = []
    total = len(data["lines"])
    for i, line in enumerate(data["lines"], 1):
        translated = translate_text(line["text"], lang_code)
        lines.append({"time": line["time"], "text": translated})
        if i % 5 == 0:
            print(f"  {lang_code}: {i}/{total}")
        time.sleep(0.8)
    out = {
        "id": data["id"],
        "title": title,
        "youtubeId": data["youtubeId"],
        "youtubeUrl": data["youtubeUrl"],
        "language": lang_code,
        "lines": lines,
    }
    out_path = ROOT / f"accident-miracle.{lang_code}.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path.name} ({len(lines)} lines)")


def main():
    build("es")
    build("fr")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
