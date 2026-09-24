#!/usr/bin/env python3
import json
import re
from pathlib import Path

text = Path(__file__).parent.joinpath("_shop_full.html").read_text(encoding="utf-8", errors="ignore")

idx = text.find('"catalog":{"isCatalogV3"')
print("catalog idx", idx)
if idx < 0:
    raise SystemExit("catalog not found")

# Bracket-match from catalog start
start = text.rfind("{", 0, idx)  # might need to go back further
# Actually start from "catalog":
cat_key = text.find('"catalog":', idx - 50)
chunk_start = cat_key
depth = 0
in_str = False
esc = False
obj_start = None
for i in range(cat_key, min(len(text), cat_key + 500000)):
    c = text[i]
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
        if depth == 0:
            obj_start = i
        depth += 1
    elif c == "}":
        depth -= 1
        if depth == 0 and obj_start is not None:
            obj_text = text[obj_start : i + 1]
            try:
                catalog_wrapper = json.loads("{" + text[cat_key:cat_key+12] + obj_text[1:])
            except Exception:
                # parse just the catalog value
                val = text[cat_key + len('"catalog":') : i + 1]
                catalog = json.loads(val)
                print("parsed catalog keys", catalog.keys())
                cat = catalog
                break
else:
    raise SystemExit("failed bracket match")

# Re-parse properly
val_start = cat_key + len('"catalog":')
depth = 0
in_str = False
esc = False
for i in range(val_start, len(text)):
    c = text[i]
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
            catalog = json.loads(text[val_start : i + 1])
            break

print("catalog keys:", list(catalog.keys()))
print("isCatalogV3:", catalog.get("isCatalogV3"))

# categories
categories = {}
if "categories" in catalog:
    for c in catalog["categories"]:
        categories[c["id"]] = c["name"]
        print("cat", c["name"], c["id"])

# products from category all products
cat_all = catalog.get("category") or {}
plist = cat_all.get("productsWithMetaData", {}).get("list") or []
print("products in main category list:", len(plist))

all_products = []
for item in plist:
    p = item.get("product") or item
    all_products.append(p)

# also check other category structures
def walk_cats(obj):
    if isinstance(obj, dict):
        if "productsWithMetaData" in obj:
            lst = obj["productsWithMetaData"].get("list") or []
            for item in lst:
                p = item.get("product") or item
                all_products.append(p)
        if "id" in obj and "name" in obj and "products" in str(obj.keys()):
            pass
        for v in obj.values():
            walk_cats(v)
    elif isinstance(obj, list):
        for x in obj:
            walk_cats(x)

walk_cats(catalog)

# dedupe by id
seen = {}
for p in all_products:
    pid = p.get("id") or p.get("name")
    seen[pid] = p

products = list(seen.values())
print("unique products total:", len(products))
for p in sorted(products, key=lambda x: x.get("name", ""))[:5]:
    print(" sample:", p.get("name"), p.get("price"), p.get("ribbon"))

# save raw for scraper
out = Path(__file__).parent / "_catalog_raw.json"
out.write_text(json.dumps({"categories": categories, "products": products}, indent=2), encoding="utf-8")
print("wrote", out)
