#!/usr/bin/env python3
import json
from pathlib import Path

text = Path(__file__).parent.joinpath("_shop_full.html").read_text(encoding="utf-8", errors="ignore")
pos = text.find('"totalCount":106')
print("pos", pos)
print(text[pos-500:pos+800])

# bracket parse from nearest "list":[
list_pos = text.rfind('"list":[', 0, pos)
print("\nlist pos", list_pos)
print(text[list_pos:list_pos+300])

# Try parse the productsWithMetaData object
start = text.rfind('"productsWithMetaData":', 0, pos)
val_start = start + len('"productsWithMetaData":')
depth = 0
in_str = False
esc = False
for i in range(val_start, len(text)):
    c = text[i]
    if in_str:
        if esc: esc = False
        elif c == '\\': esc = True
        elif c == '"': in_str = False
        continue
    if c == '"':
        in_str = True
        continue
    if c == '{':
        depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0:
            meta = json.loads(text[val_start:i+1])
            print("\nkeys", meta.keys())
            print("totalCount", meta.get("totalCount"))
            lst = meta.get("list") or []
            print("list len", len(lst))
            if lst:
                item = lst[0]
                print("first item keys", item.keys())
                p = item.get("product") or item
                print("product keys sample", list(p.keys())[:25])
            break
