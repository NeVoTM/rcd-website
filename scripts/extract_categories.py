#!/usr/bin/env python3
import json
import re
from pathlib import Path

text = Path(__file__).parent.joinpath("_shop_full.html").read_text(encoding="utf-8", errors="ignore")

# Extract filters
m = re.search(r'"filters_default_TPASection_kesuye65_default":\[(.*?)\],"filters', text, re.DOTALL)
if not m:
    # try simpler
    idx = text.find('"filters_default_TPASection_kesuye65_default"')
    chunk = text[idx:idx+4000]
    print(chunk[:3500])
else:
    print("found filters block")

# Extract all category filter values
cat_pattern = r'\{"id":null,"key":"([a-f0-9-]+)","value":"((?:\\.|[^"\\])*)"'
cats = re.findall(cat_pattern, text)
categories = {}
for key, val in cats:
    val = json.loads('"' + val + '"')
    categories[key] = val
print(f"\nCategories ({len(categories)}):")
for k, v in categories.items():
    print(f"  {v}: {k}")

# Save categories
Path(__file__).parent.joinpath("_categories.json").write_text(json.dumps(categories, indent=2), encoding="utf-8")

# Search for getProducts / loadProducts endpoints
for pat in [r'getFilteredProducts', r'loadProducts', r'products/query', r'offset', r'pageSize', r'itemsPerPage']:
    matches = [(m.start(), text[m.start():m.start()+100]) for m in re.finditer(pat, text)]
    print(f"\n{pat}: {len(matches)}")
    for pos, snippet in matches[:3]:
        print(" ", snippet.replace("\n", " ")[:120])

# Look in viewer model for store config
vm = re.search(r'<script type="application/json" id="wix-viewer-model">(.*?)</script>', text, re.DOTALL)
if vm:
    model = json.loads(vm.group(1))
    # search for store related keys
    def find_store(obj, depth=0):
        if depth > 8:
            return
        if isinstance(obj, dict):
            for k, v in obj.items():
                if any(x in k.lower() for x in ['store', 'catalog', 'product', 'gallery']):
                    if isinstance(v, (str, int, bool)) and len(str(v)) < 200:
                        print(f"  {k}: {v}")
                find_store(v, depth+1)
        elif isinstance(obj, list) and len(obj) < 5:
            for i in obj:
                find_store(i, depth+1)
    print("\nViewer model store keys:")
    find_store(model)
