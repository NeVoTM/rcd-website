#!/usr/bin/env python3
"""Resumable ES/FR transcript translation with incremental saves."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = ROOT / "data" / "transcripts"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from translate_with_fallback import translate_text

LANGS = [("es", "es"), ("fr", "fr")]
SLEEP_SEC = 2.5


def translate_one(path: Path, lang: str, lang_code: str, force: bool = False):
    data = json.loads(path.read_text(encoding="utf-8"))
    out_path = path.with_suffix(f".{lang_code}.json")
    start_idx = 0
    title = None
    lines = []

    if out_path.exists() and not force:
        existing = json.loads(out_path.read_text(encoding="utf-8"))
        lines = existing.get("lines", [])
        title = existing.get("title")
        start_idx = len(lines)
        if start_idx >= len(data["lines"]):
            print(f"skip complete {out_path.name}")
            return

    if title is None:
        for attempt in range(6):
            try:
                title = translate_text(data["title"], lang)
                break
            except RuntimeError:
                time.sleep(60 * (attempt + 1))
        else:
            raise RuntimeError(f"title translation failed for {lang_code}")

    total = len(data["lines"])
    print(f"{path.stem}.{lang_code}: resume at {start_idx}/{total}")

    for i in range(start_idx, total):
        src = data["lines"][i]
        for attempt in range(8):
            try:
                translated = translate_text(src["text"], lang)
                break
            except RuntimeError:
                wait = 45 * (attempt + 1)
                print(f"  line {i + 1} pause {wait}s…")
                time.sleep(wait)
        else:
            raise RuntimeError(f"line {i + 1} failed for {lang_code}")

        lines.append({"time": src["time"], "text": translated})
        out = {
            "id": data["id"],
            "title": title,
            "youtubeId": data["youtubeId"],
            "youtubeUrl": data["youtubeUrl"],
            "language": lang_code,
            "lines": lines,
        }
        out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        if (i + 1) % 10 == 0 or i + 1 == total:
            print(f"  {path.stem}.{lang_code}: {i + 1}/{total}")
        time.sleep(SLEEP_SEC)

    print(f"wrote {out_path.name} ({len(lines)} lines)")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    path = TRANSCRIPTS / f"{args.id}.json"
    if not path.exists():
        raise SystemExit(f"missing {path}")
    for lang, code in LANGS:
        translate_one(path, lang, code, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
