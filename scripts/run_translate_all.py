#!/usr/bin/env python3
"""Run transcript translations with cooldown for Google rate limits."""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IDS = ["rebbe-in-mikva", "nigun-therapy", "litvak-becomes-a-chasid", "accident-miracle"]
COOLDOWN_SEC = 600


def main():
    print(f"Waiting {COOLDOWN_SEC}s for translation API cooldown…")
    time.sleep(COOLDOWN_SEC)
    for tid in IDS:
        print(f"\n=== {tid} ===")
        rc = subprocess.call(
            [sys.executable, str(ROOT / "scripts" / "translate_transcripts.py"), "--id", tid, "--force"],
            cwd=str(ROOT),
        )
        if rc != 0:
            print(f"WARN: {tid} failed (rc={rc}), waiting before next…")
            time.sleep(300)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
