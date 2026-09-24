#!/usr/bin/env python3
"""Fetch all 106 products via Wix storefront pagination."""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://www.rabbidalfin.com"
SHOP = f"{BASE}/shop"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def fetch(url, data=None, headers=None):
    h = {"User-Agent": UA, "Referer": SHOP}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_catalog(html):
    idx = html.find('"catalog":{"isCatalogV3"')
    if idx < 0:
        return None, None
    cat_key = html.find('"catalog":', idx - 50)
    val_start = cat_key + len('"catalog":')
    depth = 0
    in_str = False
    esc = False
    for i in range(val_start, len(html)):
        c = html[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return json.loads(html[val_start : i + 1]), html
    return None, html


def extract_products(catalog):
    cat = catalog.get("category") or {}
    meta = cat.get("productsWithMetaData") or {}
    items = meta.get("list") or []
    total = meta.get("totalCount", 0)
    products = []
    for item in items:
        products.append(item.get("product") or item)
    return products, total


def extract_filters(html):
    cats = {}
    for key, val in re.findall(
        r'\{"id":null,"key":"([a-f0-9-]+)","value":"((?:\\.|[^"\\])*)"', html
    ):
        if key.startswith("00000000") or key in ("10.00",):
            continue
        if "." in key and key.replace(".", "").isdigit():
            continue
        cats[key] = json.loads('"' + val + '"')
    return cats


def try_page_urls():
    """Try Wix gallery page query params."""
    products_by_id = {}
    for page in range(1, 8):
        for qs in [
            f"?page={page}",
            f"?pageNumber={page}",
            f"?offset={(page-1)*18}",
            f"?page={page}&category=00000000-000000-000000-000000000001",
        ]:
            url = SHOP + qs
            try:
                html = fetch(url)
                catalog, _ = parse_catalog(html)
                if not catalog:
                    continue
                prods, total = extract_products(catalog)
                print(f"{url}: {len(prods)} items, total={total}")
                for p in prods:
                    products_by_id[p["id"]] = p
            except Exception as e:
                print(f"fail {url}: {e}")
            time.sleep(1.5)
    return products_by_id


def try_category_pages(categories):
    products_by_id = {}
    for cid, cname in categories.items():
        if cname in ("All Products",):
            continue
        for qs in [f"?category={cid}", f"?filters=categoryId.eq.{cid}"]:
            url = SHOP + qs
            try:
                html = fetch(url)
                catalog, _ = parse_catalog(html)
                if not catalog:
                    continue
                prods, total = extract_products(catalog)
                print(f"{cname} ({qs}): {len(prods)}/{total}")
                for p in prods:
                    p["_category"] = cname
                    products_by_id[p["id"]] = p
            except Exception as e:
                print(f"fail {cname}: {e}")
            time.sleep(2)
    return products_by_id


def try_api():
    endpoints = [
        "/_api/wixstores-web/v1/products/query",
        "/_api/wixstores-web/v2/products/query",
        "/_api/ecom/v1/products/query",
    ]
    for ep in endpoints:
        for offset in [0, 18, 36, 54, 72, 90]:
            body = json.dumps(
                {
                    "query": {},
                    "paging": {"limit": 18, "offset": offset},
                    "sort": {"sortField": "name", "sortOrder": "ASC"},
                }
            ).encode()
            try:
                html = fetch(
                    BASE + ep,
                    data=body,
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                )
                data = json.loads(html)
                prods = data.get("products") or data.get("payload", {}).get("products") or []
                print(f"{ep} offset={offset}: {len(prods)}")
                if prods:
                    return data
            except Exception as e:
                print(f"api {ep} {offset}: {e}")
            time.sleep(2)
    return None


def main():
    print("Fetching main shop...")
    html = fetch(SHOP)
    categories = extract_filters(html)
    print("Categories:", categories)

    all_products = {}
    catalog, _ = parse_catalog(html)
    if catalog:
        prods, total = extract_products(catalog)
        print(f"Initial: {len(prods)}/{total}")
        for p in prods:
            all_products[p["id"]] = p

    print("\nTrying category pages...")
    cat_prods = try_category_pages(categories)
    all_products.update(cat_prods)
    print(f"After categories: {len(all_products)}")

    if len(all_products) < 50:
        print("\nTrying page URLs...")
        page_prods = try_page_urls()
        all_products.update(page_prods)
        print(f"After pages: {len(all_products)}")

    if len(all_products) < 50:
        print("\nTrying API...")
        try_api()

    out = Path(__file__).parent / "_all_products_raw.json"
    out.write_text(
        json.dumps(list(all_products.values()), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nSaved {len(all_products)} products to {out}")


if __name__ == "__main__":
    main()
