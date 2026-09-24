#!/usr/bin/env python3
import json
import re
import urllib.request
from pathlib import Path

HTML = Path(__file__).parent / "_shop_full.html"
if not HTML.exists():
    req = urllib.request.Request(
        "https://www.rabbidalfin.com/shop",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        HTML.write_bytes(resp.read())
    print("saved full html", HTML.stat().st_size)

text = HTML.read_text(encoding="utf-8", errors="ignore")
print("html size", len(text))

for term in ["totalCount", "loadMore", "offset", "cursor", "hasNext", "collectionId", "wixstores"]:
    print(term, text.count(term))

# collections/categories
cats = re.findall(r'"collection(?:Name)?"\s*:\s*"([^"]{3,80})"', text)
print("collection names sample", sorted(set(cats))[:20])

# try API endpoints
apis = [
    ("POST", "https://www.rabbidalfin.com/_api/wixstores-web/v1/products/query", {"query": {}, "paging": {"limit": 100, "offset": 0}}),
    ("POST", "https://www.rabbidalfin.com/_api/wixstores-web/v2/products/query", {"query": {}, "paging": {"limit": 100, "offset": 0}}),
    ("POST", "https://www.rabbidalfin.com/_api/wix-ecommerce-store-web/v1/products/query", {"query": {}, "paging": {"limit": 100, "offset": 0}}),
]
for method, url, body in apis:
    try:
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.rabbidalfin.com/shop",
            },
            method=method,
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
        prods = result.get("products") or result.get("payload", {}).get("products") or result.get("items") or []
        total = result.get("totalCount") or result.get("payload", {}).get("totalCount")
        print(f"OK {url}: {len(prods)} products, total={total}")
        if prods:
            print("  first:", prods[0].get("name"))
    except Exception as e:
        print(f"FAIL {url}: {e}")

# sitemap
for sm in [
    "https://www.rabbidalfin.com/store-products-sitemap.xml",
    "https://www.rabbidalfin.com/sitemap.xml",
]:
    try:
        req = urllib.request.Request(sm, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode()
        locs = re.findall(r"<loc>([^<]+product[^<]*)</loc>", body)
        print(sm, "product locs", len(locs))
        for l in locs[:5]:
            print(" ", l)
    except Exception as e:
        print(sm, "fail", e)
