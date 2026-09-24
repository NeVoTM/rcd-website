#!/usr/bin/env python3
"""Generate WebVTT subtitle files for RCD clips from transcript JSON."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = ROOT / "data" / "transcripts"
OUT = ROOT / "public" / "clips"

CLIP_SPECS = [
    {
        "id": "zerizus-miracle",
        "transcriptId": "accident-miracle",
        "startSec": 219,
        "durationSec": 45,
        "translations": {
            "es": [
                (0.0, 10.0, "Las lecciones del episodio — la grandeza del celo, el zerizut, en todos los asuntos de bondad."),
                (10.0, 20.0, "No solo en asuntos sagrados: hay que hacerlo con gran celo, gran entusiasmo, y no procrastinar."),
                (20.0, 30.0, "No dijo cómo llegó a determinar que esa era la lección, pero recuerdo haberle escrito."),
                (30.0, 40.0, "El conductor iba tan rápido — y en ese momento comprendí la lección del zerizut."),
                (40.0, 45.0, "Celo en la santidad — alacrity sagrada en todos los asuntos de bondad."),
            ],
            "fr": [
                (0.0, 10.0, "Les leçons de l'épisode — la grandeur de l'empressement, le zerizut, dans toutes les choses de bonté."),
                (10.0, 20.0, "Pas seulement dans les affaires sacrées : il faut le faire avec un grand zèle, un grand enthousiasme, sans procrastiner."),
                (20.0, 30.0, "Il n'a pas dit comment il a déterminé que c'était la leçon, mais je me souviens lui avoir écrit."),
                (30.0, 40.0, "Le conducteur roulait si vite — et à ce moment j'ai compris la leçon du zerizut."),
                (40.0, 45.0, "Empressement dans la sainteté — alacrité sacrée dans toutes les choses de bonté."),
            ],
        },
    },
    {
        "id": "yud-tes-kislev",
        "transcriptId": "litvak-becomes-a-chasid",
        "startSec": 90,
        "durationSec": 45,
        "translations": {
            "es": [
                (0.0, 8.0, "Es un libro legítimo — no es magia ni algo sin fundamento."),
                (8.0, 16.0, "Ha sido aceptado, y el Rebe lo mencionó muchas veces, especialmente en los fabrengens de Yud Tes Kislev."),
                (16.0, 28.0, "Escribe allí que hoy es un día de buenas noticias — basura significa noticias."),
                (28.0, 38.0, "Yud Tes Kislev es un día de buenas noticias, escrito mucho antes de que el Alter Rebe fuera liberado."),
                (38.0, 45.0, "Hay mucho de qué hablar — es un pequeño fabrengen y tenemos poco tiempo."),
            ],
            "fr": [
                (0.0, 8.0, "C'est un livre légitime — pas de la magie ni du vent."),
                (8.0, 16.0, "Il a été accepté, et le Rebbe l'a mentionné souvent, surtout lors des fabrengens de Yud Tes Kislev."),
                (16.0, 28.0, "Il y est écrit qu'aujourd'hui est un jour de bonnes nouvelles — basura signifie nouvelles."),
                (28.0, 38.0, "Yud Tes Kislev est un jour de bonnes nouvelles, écrit bien avant la libération de l'Alter Rebbe."),
                (38.0, 45.0, "Il y a tant à dire — c'est un petit fabrengen et nous avons peu de temps."),
            ],
        },
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


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for spec in CLIP_SPECS:
        en_segments = segments_from_transcript(
            spec["transcriptId"], spec["startSec"], spec["durationSec"]
        )
        write_vtt(OUT / f"{spec['id']}.en.vtt", en_segments, "en")
        for lang in ("es", "fr"):
            write_vtt(OUT / f"{spec['id']}.{lang}.vtt", spec["translations"][lang], lang)
        print(f"{spec['id']}: {len(en_segments)} EN cues, ES/FR translated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
