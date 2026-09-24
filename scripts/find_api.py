#!/usr/bin/env python3
import json
import re
from pathlib import Path

text = Path(__file__).parent.joinpath("_shop_full.html").read_text(encoding="utf-8", errors="ignore")

for pat in [r'"metaSiteId"\s*:\s*"([^"]+)"', r'"siteId"\s*:\s*"([^"]+)"', r'"instanceId"\s*:\s*"([^"]+)"', r'"appDefId"\s*:\s*"([^"]+)"']:
    vals = list(dict.fromkeys(re.findall(pat, text)))
    print(pat, vals[:5])

# find store app id
if "215238eb-22a5-4c36-9e7b-e7c08025e04e" in text:
    print("Wix Stores app found")

# Extract authorization or xsrf
for pat in [r'"authorization"\s*:\s*"([^"]+)"', r'commonConfig[^}]{0,500}', r'"instance"\s*:\s*"([^"]+)"']:
    m = re.search(pat, text)
    if m:
        print("match", pat, str(m.group(0))[:200])

# Look for products v3 endpoint in bundles - fetch one JS file
js_url = "https://static.parastorage.com/services/wixstores-client-gallery/1.6042.0/client-viewer/6175.chunk.min.js"
print("fetching js...")
import urllib.request
req = urllib.request.Request(js_url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    js = resp.read().decode("utf-8", errors="ignore")
print("js len", len(js))
for term in ["products/query", "getFilteredProducts", "loadMore", "offset", "wixstores-web", "ecom/v1", "productsV3"]:
    if term in js:
        idx = js.find(term)
        print(term, "->", js[max(0,idx-80):idx+120])
