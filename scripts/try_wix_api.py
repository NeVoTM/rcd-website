#!/usr/bin/env python3
import json
import time
import urllib.request

META_SITE = "c8e668fd-88ae-43e4-8355-5e1a430934b0"
BASE = "https://www.rabbidalfin.com"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Referer": f"{BASE}/shop",
    "x-wix-meta-site-id": META_SITE,
    "x-wix-client-artifact-id": "wixstores-storefront-buyer",
    "Origin": BASE,
}

endpoints = [
    "/_api/wixstores-web/v1/products/query",
    "/_api/wixstores-web/v2/products/query",
    "/_api/wixstores-web/v3/products/query",
    "/_api/ecom/v1/products/query",
    "/_api/ecommerce-store/v1/products/query",
]

bodies = [
    {"query": {}, "paging": {"limit": 100, "offset": 0}},
    {"query": {"paging": {"limit": 100, "offset": 0}}},
    {"limit": 100, "offset": 0},
    {"includeHiddenProducts": False, "limit": 100, "offset": 0, "sort": {"fieldName": "name", "order": "ASC"}},
]

for ep in endpoints:
    for body in bodies:
        try:
            data = json.dumps(body).encode()
            req = urllib.request.Request(BASE + ep, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
            prods = result.get("products") or result.get("payload", {}).get("products") or result.get("items") or []
            total = result.get("totalCount") or result.get("payload", {}).get("totalCount")
            print(f"OK {ep} body={list(body.keys())}: {len(prods)} total={total}")
            if prods:
                print("  first:", prods[0].get("name"))
        except Exception as e:
            print(f"FAIL {ep} {list(body.keys())}: {e}")
        time.sleep(1)
