#!/usr/bin/env python3
"""Generate WebVTT subtitle files for RCD clips from transcript JSON."""
import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = ROOT / "data" / "transcripts"
OUT = ROOT / "public" / "clips"

try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None

CLIP_SPECS = [
    {
        "id": "zerizus-miracle",
        "transcriptId": "accident-miracle",
        "startSec": 202,
        "durationSec": 44,
    },
    {
        "id": "yud-tes-kislev",
        "transcriptId": "litvak-becomes-a-chasid",
        "startSec": 90,
        "durationSec": 45,
    },
]


def parse_time(ts: str) -> float:
    parts = ts.split(":")
    h, m, s = int(parts[0]), int(parts[1]), float(parts[2])
    return h * 3600 + m * 60 + s


def format_vtt_time(sec: float) -> str:
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".rstrip("0").rstrip(".")


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    return text


def segments_from_transcript(transcript_id: str, start_sec: float, duration_sec: float):
    data = json.loads((TRANSCRIPTS / f"{transcript_id}.json").read_text(encoding="utf-8"))
    end_sec = start_sec + duration_sec
    lines = data.get("lines", [])
    parsed = [(parse_time(l["time"]), clean_text(l["text"])) for l in lines]
    in_range = [(t, txt) for t, txt in parsed if start_sec <= t < end_sec]
    if not in_range:
        return []
    segments = []
    for i, (t, txt) in enumerate(in_range):
        rel_start = t - start_sec
        if i + 1 < len(in_range):
            rel_end = in_range[i + 1][0] - start_sec
        else:
            rel_end = min(duration_sec, rel_start + 4.0)
        rel_end = max(rel_end, rel_start + 0.5)
        segments.append((rel_start, rel_end, txt))
    return segments


def write_vtt(path: Path, segments, lang_label: str):
    lines = ["WEBVTT", f"NOTE Language: {lang_label}", ""]
    for i, (start, end, text) in enumerate(segments, 1):
        lines.append(str(i))
        lines.append(f"{format_vtt_time(start)} --> {format_vtt_time(end)}")
        lines.append(text)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def translate_segments(segments, target: str):
    if GoogleTranslator is None:
        raise RuntimeError("Install deep-translator: pip install deep-translator")
    translator = GoogleTranslator(source="en", target=target)
    texts = [text for _, _, text in segments]
    for attempt in range(6):
        try:
            translated_texts = translator.translate_batch(texts)
            break
        except Exception as exc:
            if attempt == 5:
                raise
            wait = 3 * (2 ** attempt)
            print(f"  retry batch {target} in {wait}s: {exc}")
            time.sleep(wait)
    return [(start, end, txt) for (start, end, _), txt in zip(segments, translated_texts)]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for spec in CLIP_SPECS:
        en_segments = segments_from_transcript(
            spec["transcriptId"], spec["startSec"], spec["durationSec"]
        )
        write_vtt(OUT / f"{spec['id']}.en.vtt", en_segments, "en")
        for lang in ("es", "fr"):
            lang_segments = translate_segments(en_segments, lang)
            write_vtt(OUT / f"{spec['id']}.{lang}.vtt", lang_segments, lang)
        print(f"{spec['id']}: {len(en_segments)} EN cues, ES/FR translated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
