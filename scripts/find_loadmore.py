#!/usr/bin/env python3
import json
import re
from pathlib import Path

text = Path(__file__).parent.joinpath("_shop_full.html").read_text(encoding="utf-8", errors="ignore")

# Find loadMore contexts
for m in re.finditer(r'.{0,80}loadMore.{0,120}', text):
    s = m.group(0).replace("\n", " ")
    if "product" in s.lower() or "offset" in s.lower() or "cursor" in s.lower():
        print(s[:200])
        print("---")

# Find category filter URLs
for m in re.finditer(r'href="(/shop/[^"]+)"', text):
    print("shop link", m.group(1))

for m in re.finditer(r'"urlPart"\s*:\s*"([^"]+)"', text):
    pass

# collections in page
for m in re.finditer(r'"name"\s*:\s*"(Lubavitch[^"]+|Chasidic[^"]+|Mysticism[^"]+|Biography[^"]+|Great Leaders[^"]+|The Rebbe[^"]+|Chabad Portraits[^"]+)"', text):
    print("cat name", m.group(1))

# look for offset/limit in scripts near products
idx = text.find("loadMore")
chunks = []
pos = 0
while True:
    i = text.find("loadMore", pos)
    if i < 0:
        break
    chunks.append(text[i-200:i+400])
    pos = i + 8

Path(__file__).parent.joinpath("_loadmore_samples.txt").write_text("\n\n===\n\n".join(chunks[:5]), encoding="utf-8")
print("saved", len(chunks), "loadMore samples")

# search for product slugs beyond the 18
all_slugs = set(re.findall(r'product-page/([a-z0-9-]+)', text))
print("slugs in html", len(all_slugs))

# Check if there's a separate data file or graphql
for term in ["graphql", "ProductsQuery", "getProducts", "listProducts", "storeProducts"]:
    print(term, text.count(term))
