#!/usr/bin/env python3
"""Generate Spanish and French transcript JSON files from English sources."""
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = ROOT / "data" / "transcripts"

try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None


def translate_text(text: str, target: str) -> str:
    if not text.strip():
        return text
    if GoogleTranslator is None:
        raise RuntimeError("Install deep-translator: pip install deep-translator")
    translator = GoogleTranslator(source="en", target=target)
    # Google Translate has length limits; chunk long lines.
    if len(text) <= 4500:
        return translator.translate(text)
    parts = []
    chunk = ""
    for word in text.split():
        candidate = f"{chunk} {word}".strip()
        if len(candidate) > 4000:
            parts.append(translator.translate(chunk))
            time.sleep(0.15)
            chunk = word
        else:
            chunk = candidate
    if chunk:
        parts.append(translator.translate(chunk))
    return " ".join(parts)


def translate_transcript(path: Path, lang: str, lang_code: str):
    data = json.loads(path.read_text(encoding="utf-8"))
    out_path = path.with_suffix(f".{lang_code}.json")
    if out_path.exists():
        print(f"skip existing {out_path.name}")
        return
    title = translate_text(data["title"], lang)
    time.sleep(0.15)
    lines = []
    for i, line in enumerate(data.get("lines", []), 1):
        translated = translate_text(line["text"], lang)
        lines.append({"time": line["time"], "text": translated})
        if i % 10 == 0:
            print(f"  {path.stem}.{lang_code}: {i}/{len(data['lines'])}")
        time.sleep(0.6)
    out = {
        "id": data["id"],
        "title": title,
        "youtubeId": data["youtubeId"],
        "youtubeUrl": data["youtubeUrl"],
        "language": lang_code,
        "lines": lines,
    }
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path.name} ({len(lines)} lines)")


def main():
    if GoogleTranslator is None:
        raise SystemExit("pip install deep-translator")
    for path in sorted(TRANSCRIPTS.glob("*.json")):
        if path.name.count(".") > 1:
            continue
        print(path.name)
        translate_transcript(path, "es", "es")
        translate_transcript(path, "fr", "fr")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
