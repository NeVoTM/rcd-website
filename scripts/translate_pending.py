#!/usr/bin/env python3
"""Translate only pending ES/FR transcripts with retry/backoff."""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IDS = ["nigun-therapy", "litvak-becomes-a-chasid"]
MAX_ATTEMPTS = 3
BACKOFF_SEC = [60, 180, 300]


def main():
    for tid in IDS:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            print(f"\n=== {tid} (attempt {attempt}/{MAX_ATTEMPTS}) ===")
            cmd = [
                sys.executable,
                str(ROOT / "scripts" / "translate_resumable.py"),
                "--id",
                tid,
            ]
            if tid == "litvak-becomes-a-chasid":
                cmd.append("--force")
            rc = subprocess.call(cmd, cwd=str(ROOT))
            if rc == 0:
                break
            if attempt < MAX_ATTEMPTS:
                wait = BACKOFF_SEC[attempt - 1]
                print(f"WARN: {tid} failed (rc={rc}), waiting {wait}s…")
                time.sleep(wait)
            else:
                print(f"ERROR: {tid} failed after {MAX_ATTEMPTS} attempts")
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
