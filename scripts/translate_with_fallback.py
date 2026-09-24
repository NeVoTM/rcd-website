#!/usr/bin/env python3
"""Translate text with googletrans → Google → MyMemory → Linguee fallbacks."""
import re
import time

from deep_translator import GoogleTranslator, LingueeTranslator, MyMemoryTranslator

LINGUEE = {"es": "spanish", "fr": "french"}
MYMEMORY = {"es": "es-ES", "fr": "fr-FR"}

try:
    import translators as ts
except ImportError:
    ts = None

GoogletransTranslator = None
try:
    from googletrans import Translator as GoogletransTranslator
except Exception:
    GoogletransTranslator = None



def _linguee_chunks(text: str, target: str) -> str:
    ling = LingueeTranslator(source="english", target=LINGUEE[target])
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = []
    for part in parts:
        if not part.strip():
            continue
        words = part.split()
        chunk = ""
        for word in words:
            candidate = f"{chunk} {word}".strip()
            if len(candidate) > 40:
                if chunk:
                    out.append(ling.translate(chunk))
                chunk = word
            else:
                chunk = candidate
        if chunk:
            out.append(ling.translate(chunk))
        time.sleep(0.2)
    return " ".join(out)


def _try_translate(label: str, fn, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            return fn()
        except Exception as exc:
            wait = 2 ** attempt
            print(f"  {label} retry {attempt + 1}: {exc}")
            time.sleep(wait)
    raise RuntimeError(f"{label} failed after {retries} retries")


def translate_text(text: str, target: str, retries: int = 3) -> str:
    if not text.strip():
        return text

    backends = []
    if ts is not None:

        def _bing():
            return ts.translate_text(
                text, translator="bing", from_language="en", to_language=target
            )

        backends.append(("bing", _bing))
    if GoogletransTranslator is not None:

        def _googletrans():
            result = GoogletransTranslator().translate(text, src="en", dest=target)
            if result is None or not getattr(result, "text", None):
                raise RuntimeError("googletrans returned empty")
            return result.text

        backends.append(("googletrans", _googletrans))
    backends.extend(
        [
            ("google", lambda: GoogleTranslator(source="en", target=target).translate(text)),
            (
                "mymemory",
                lambda: MyMemoryTranslator(
                    source="en-US", target=MYMEMORY[target]
                ).translate(text),
            ),
            ("linguee", lambda: _linguee_chunks(text, target)),
        ]
    )

    last_exc = None
    for label, fn in backends:
        try:
            return _try_translate(label, fn, retries=retries)
        except Exception as exc:
            last_exc = exc
            print(f"  {label} exhausted, trying next backend…")
    raise RuntimeError(f"translation failed for {target}: {last_exc}")
