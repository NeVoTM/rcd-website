#!/usr/bin/env python3
import json
import re
from pathlib import Path

text = Path(__file__).parent.joinpath("_shop_full.html").read_text(encoding="utf-8", errors="ignore")

# Extract warmup
m = re.search(r'<script type="application/json" id="wix-warmup-data">(.*?)</script>', text, re.DOTALL)
warmup = json.loads(m.group(1)) if m else {}

def find_keys(obj, key, results=None):
    if results is None:
        results = []
    if isinstance(obj, dict):
        if key in obj:
            results.append(obj[key])
        for v in obj.values():
            find_keys(v, key, results)
    elif isinstance(obj, list):
        for i in obj:
            find_keys(i, key, results)
    return results

products = find_keys(warmup, "products")
print("products arrays:", len(products))
for i, arr in enumerate(products):
    if isinstance(arr, list):
        print(f"  array {i}: len={len(arr)}")

# all objects with name+price
found = []

def walk(obj):
    if isinstance(obj, dict):
        if obj.get("name") and (obj.get("priceData") or obj.get("formattedPrice")):
            found.append(obj["name"])
        for v in obj.values():
            walk(v)
    elif isinstance(obj, list):
        for i in obj:
            walk(i)

walk(warmup)
print("named products in warmup:", len(found), len(set(found)))
for n in sorted(set(found)):
    print(" ", n)

# category tabs in html
for pat in [r'Lubavitch with others', r'Chasidic Thought', r'Mysticism', r'Biography', r'Great Leaders']:
    print(pat, text.count(pat))

# product-page links
links = re.findall(r'https://www\.rabbidalfin\.com/product-page/[a-z0-9-]+', text)
print("product-page links:", len(set(links)))
for l in sorted(set(links))[:10]:
    print(" ", l)
print("...", len(set(links)), "total unique")

# search for catalog in inline scripts
for m in re.finditer(r'"catalog"\s*:\s*\{', text):
    start = m.start()
    print("catalog at", start, text[start:start+200])
