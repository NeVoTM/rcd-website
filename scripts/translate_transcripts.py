#!/usr/bin/env python3
"""Generate Spanish and French transcript JSON files from English sources."""
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = ROOT / "data" / "transcripts"

try:
    from translate_with_fallback import translate_text as _translate_text
except ImportError:
    _translate_text = None


def translate_text(text: str, target: str) -> str:
    if not text.strip():
        return text
    if _translate_text is None:
        raise RuntimeError("Install deep-translator: pip install deep-translator")

    def _once(chunk: str) -> str:
        for attempt in range(6):
            try:
                return _translate_text(chunk, target)
            except RuntimeError:
                if attempt == 5:
                    raise
                wait = 60 * (attempt + 1)
                print(f"  rate-limit pause {wait}s ({target})…")
                time.sleep(wait)

    if len(text) <= 4500:
        return _once(text)
    parts = []
    chunk = ""
    for word in text.split():
        candidate = f"{chunk} {word}".strip()
        if len(candidate) > 4000:
            parts.append(_once(chunk))
            time.sleep(0.15)
            chunk = word
        else:
            chunk = candidate
    if chunk:
        parts.append(_once(chunk))
    return " ".join(parts)


def _write_partial(out_path: Path, data: dict, title: str, lang_code: str, lines: list):
    out = {
        "id": data["id"],
        "title": title,
        "youtubeId": data["youtubeId"],
        "youtubeUrl": data["youtubeUrl"],
        "language": lang_code,
        "lines": lines,
    }
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


def translate_transcript(path: Path, lang: str, lang_code: str, force: bool = False, resume: bool = False):
    data = json.loads(path.read_text(encoding="utf-8"))
    out_path = path.with_suffix(f".{lang_code}.json")
    total = len(data.get("lines", []))
    start_at = 0
    title = data["title"]
    lines = []

    if out_path.exists():
        existing = json.loads(out_path.read_text(encoding="utf-8"))
        have = len(existing.get("lines", []))
        if have >= total and not force:
            print(f"skip complete {out_path.name}")
            return
        if resume and 0 < have < total:
            title = existing.get("title", title)
            lines = existing["lines"]
            start_at = have
            print(f"resume {out_path.name} from line {start_at + 1}/{total}")
        elif force:
            print(f"rebuild {out_path.name}")
        else:
            print(f"skip partial {out_path.name} ({have}/{total}); use --resume")
            return

    if start_at == 0:
        title = translate_text(data["title"], lang)
        time.sleep(0.15)

    for i, line in enumerate(data.get("lines", [])[start_at:], start_at + 1):
        translated = translate_text(line["text"], lang)
        lines.append({"time": line["time"], "text": translated})
        if i % 10 == 0:
            print(f"  {path.stem}.{lang_code}: {i}/{total}")
            _write_partial(out_path, data, title, lang_code, lines)
        time.sleep(2.0)
    _write_partial(out_path, data, title, lang_code, lines)
    print(f"wrote {out_path.name} ({len(lines)} lines)")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Translate transcript JSON to ES/FR")
    parser.add_argument("--id", help="Only translate this transcript id (e.g. accident-miracle)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing translations")
    parser.add_argument("--resume", action="store_true", help="Continue partial ES/FR files")
    args = parser.parse_args()

    if _translate_text is None:
        raise SystemExit("pip install deep-translator")
    for path in sorted(TRANSCRIPTS.glob("*.json")):
        if path.name.count(".") > 1:
            continue
        if args.id and path.stem != args.id:
            continue
        print(path.name)
        translate_transcript(path, "es", "es", force=args.force, resume=args.resume)
        translate_transcript(path, "fr", "fr", force=args.force, resume=args.resume)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
