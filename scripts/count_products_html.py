#!/usr/bin/env python3
import json
import re
from pathlib import Path

text = Path(__file__).parent.joinpath("_shop_full.html").read_text(encoding="utf-8", errors="ignore")

# Find all unique urlPart slugs
slugs = set(re.findall(r'"urlPart"\s*:\s*"([a-z0-9-]+)"', text))
print("urlPart slugs:", len(slugs))

# Find all product names with id
pattern = r'"id"\s*:\s*"([a-f0-9-]+)"[^}]{0,2000}?"name"\s*:\s*"((?:\\.|[^"\\])*)"'
matches = re.findall(pattern, text)
print("id+name blocks:", len(matches))

# simpler: all names near prices
blocks = re.findall(
    r'"name"\s*:\s*"((?:\\.|[^"\\])*)"[^}]{0,800}?"price"\s*:\s*(\d+(?:\.\d+)?)',
    text,
)
print("name+price blocks:", len(blocks))
uniq = {}
for name, price in blocks:
    name = json.loads('"' + name + '"')
    uniq[name] = float(price)
print("unique products:", len(uniq))
for n, p in sorted(uniq.items(), key=lambda x: x[0].lower()):
    print(f"  ${p:.0f}  {n}")

# search product names in visible HTML text (Quick View sections)
# Wix renders alt text or aria labels
