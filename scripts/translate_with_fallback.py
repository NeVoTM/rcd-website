#!/usr/bin/env python3
"""Translate text using Google with Linguee fallback."""
import time

from deep_translator import GoogleTranslator, LingueeTranslator

LINGUEE = {"es": "spanish", "fr": "french"}


def translate_text(text: str, target: str, retries: int = 3) -> str:
    if not text.strip():
        return text
    for attempt in range(retries):
        try:
            return GoogleTranslator(source="en", target=target).translate(text)
        except Exception as exc:
            wait = 2 * (attempt + 1)
            print(f"  google {target} retry {attempt + 1}: {exc}")
            time.sleep(wait)
    ling = LingueeTranslator(source="english", target=LINGUEE[target])
    for attempt in range(retries):
        try:
            return ling.translate(text)
        except Exception as exc:
            wait = 2 * (attempt + 1)
            print(f"  linguee {target} retry {attempt + 1}: {exc}")
            time.sleep(wait)
    raise RuntimeError(f"translation failed for {target}")
