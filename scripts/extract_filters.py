#!/usr/bin/env python3
import json
import re
from pathlib import Path

text = Path(__file__).parent.joinpath("_shop_full.html").read_text(encoding="utf-8", errors="ignore")

# Parse warmup for filters
m = re.search(r'<script type="application/json" id="wix-warmup-data">(.*?)</script>', text, re.DOTALL)
warmup = json.loads(m.group(1))

filters = []

def walk(obj, path=""):
    if isinstance(obj, dict):
        if obj.get("label") and obj.get("link") and "collection" in str(obj).lower():
            filters.append(obj)
        if "filters" in obj and isinstance(obj["filters"], list):
            for f in obj["filters"]:
                if isinstance(f, dict):
                    filters.append(f)
        for k, v in obj.items():
            walk(v, path + "/" + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, path + f"[{i}]")

walk(warmup)

print("filter-like objects:", len(filters))
seen = set()
for f in filters:
    label = f.get("label") or f.get("name") or f.get("title")
    if label and label not in seen:
        seen.add(label)
        print(" ", label, f.get("id"), f.get("collectionId"), f.get("link"))

# Find all filter list items in HTML
for m in re.finditer(r'data-hook="filter-item[^"]*"[^>]*>([^<]{2,60})', text):
    print("html filter", m.group(1).strip()[:50])

# Extract all product objects with name and price from entire HTML (not just warmup)
pattern = r'\{"id":"[a-f0-9-]+","name":"((?:\\.|[^"\\])*)","price":(\d+(?:\.\d+)?)'
matches = re.findall(pattern, text)
print("regex products name+price:", len(matches))
uniq = {}
for name, price in matches:
    name = json.loads('"' + name + '"')
    uniq[name] = float(price)
print("unique:", len(uniq))
for n, p in sorted(uniq.items(), key=lambda x: x[0].lower())[:30]:
    print(f"  {p:.0f} - {n}")
print("...")
for n, p in sorted(uniq.items(), key=lambda x: x[0].lower())[-10:]:
    print(f"  {p:.0f} - {n}")

# totalCount near catalog
for m in re.finditer(r'"totalCount"\s*:\s*(\d+)', text):
    print("totalCount", m.group(1), "at", m.start())

# look for productsWithMetaData total
for m in re.finditer(r'"productsWithMetaData"\s*:\s*\{[^}]*"totalCount"\s*:\s*(\d+)', text):
    print("productsWithMetaData totalCount", m.group(1))
