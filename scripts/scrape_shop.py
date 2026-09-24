#!/usr/bin/env python3
"""Scrape products from rabbidalfin.com Wix shop."""
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SHOP_URL = "https://www.rabbidalfin.com/shop"
OUT_JSON = Path(__file__).resolve().parent.parent / "data" / "books.json"
IMAGES_DIR = Path(__file__).resolve().parent.parent / "public" / "images" / "books"


def slugify(title: str) -> str:
    s = title.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "product"


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (RCD migration bot)"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def extract_warmup_data(html: str) -> dict | None:
    m = re.search(
        r'<script type="application/json" id="wix-warmup-data">(.*?)</script>',
        html,
        re.DOTALL,
    )
    if not m:
        return None
    return json.loads(m.group(1))


def walk_products(obj, found=None):
    if found is None:
        found = []
    if isinstance(obj, dict):
        if "name" in obj and ("price" in obj or "formattedPrice" in obj or "priceData" in obj):
            if obj.get("productType") or obj.get("slug") or obj.get("priceData"):
                found.append(obj)
        for v in obj.values():
            walk_products(v, found)
    elif isinstance(obj, list):
        for item in obj:
            walk_products(item, found)
    return found


def extract_from_html_patterns(html: str) -> list[dict]:
    """Fallback: parse product cards from rendered HTML patterns."""
    products = []
    # Wix often embeds product list in JSON-LD or inline state
    for m in re.finditer(r'"name"\s*:\s*"((?:\\.|[^"\\])*)"\s*,\s*"price"', html):
        name = json.loads('"' + m.group(1) + '"')
        products.append({"name": name})
    return products


def parse_product(raw: dict, categories_map: dict) -> dict | None:
    name = raw.get("name") or raw.get("title")
    if not name:
        return None

    price_data = raw.get("priceData") or raw.get("price") or {}
    if isinstance(price_data, (int, float)):
        price = float(price_data)
    elif isinstance(price_data, dict):
        price = price_data.get("price") or price_data.get("discountedPrice") or 0
        if isinstance(price, dict):
            price = price.get("price", 0)
    else:
        price = 0
    price = float(price) if price else 0

    slug = raw.get("slug") or slugify(name)
    product_id = raw.get("id") or raw.get("productId") or slug

    # Images
    media = raw.get("media") or raw.get("mediaItems") or []
    image_url = None
    if isinstance(media, dict):
        items = media.get("items") or media.get("mediaItems") or []
        if items:
            image_url = items[0].get("url") or items[0].get("image", {}).get("url")
    elif isinstance(media, list) and media:
        first = media[0]
        if isinstance(first, dict):
            image_url = first.get("url") or first.get("image", {}).get("url") or first.get("src")

    if not image_url:
        img = raw.get("image") or raw.get("mainMedia")
        if isinstance(img, dict):
            image_url = img.get("url") or img.get("src")
        elif isinstance(img, str):
            image_url = img

    # Category
    category = None
    coll = raw.get("collectionId") or raw.get("categoryId")
    if coll and categories_map:
        category = categories_map.get(coll)
    if not category:
        category = raw.get("category") or raw.get("collectionName") or "General"

    # Tags / badges
    tags = []
    ribbon = raw.get("ribbon") or raw.get("badge") or raw.get("ribbons")
    if isinstance(ribbon, str) and ribbon.strip():
        tags.append(ribbon.strip())
    elif isinstance(ribbon, dict):
        t = ribbon.get("text") or ribbon.get("title")
        if t:
            tags.append(t)
    elif isinstance(ribbon, list):
        for r in ribbon:
            if isinstance(r, dict):
                t = r.get("text") or r.get("title")
                if t:
                    tags.append(t)
            elif isinstance(r, str):
                tags.append(r)

    for key in ("customTextFields", "infoSections", "description"):
        val = raw.get(key)
        if isinstance(val, str) and any(
            x in val.lower() for x in ("new", "limited", "dvd", "cd")
        ):
            pass

    # Format detection
    fmt = "book"
    name_lower = name.lower()
    desc = (raw.get("description") or "") + " " + name
    desc_lower = desc.lower()
    if "dvd" in name_lower or "dvd" in desc_lower:
        fmt = "dvd"
    elif " cd" in name_lower or "cd " in name_lower:
        fmt = "cd"

    # Purchase URL
    url_slug = raw.get("urlPart") or raw.get("slug") or slug
    purchase_url = f"https://www.rabbidalfin.com/product-page/{url_slug}"

    description = raw.get("description") or ""
    if isinstance(description, dict):
        description = description.get("text") or ""

    return {
        "id": slugify(name) if not slug else slugify(slug) if isinstance(slug, str) and " " in slug else str(slug).lower().replace(" ", "-"),
        "title": name.strip(),
        "price": round(price, 2),
        "currency": "USD",
        "category": category,
        "tags": list(dict.fromkeys(tags)),
        "image": None,
        "imageUrl": image_url,
        "description": re.sub(r"<[^>]+>", " ", description).strip() if description else "",
        "format": fmt,
        "purchaseUrl": purchase_url,
        "sourceId": str(product_id),
    }


def build_categories_map(warmup: dict) -> dict:
    mapping = {}
    def walk(o):
        if isinstance(o, dict):
            if "collectionId" in o and "name" in o and len(o.get("name", "")) > 2:
                mapping[o["collectionId"]] = o["name"]
            if "id" in o and "name" in o and o.get("type") == "collection":
                mapping[o["id"]] = o["name"]
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for i in o:
                walk(i)
    walk(warmup)
    return mapping


def dedupe_products(products: list[dict]) -> list[dict]:
    seen = {}
    for p in products:
        key = p["title"].lower().strip()
        if key not in seen or p.get("price", 0) > seen[key].get("price", 0):
            seen[key] = p
    return list(seen.values())


def download_image(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"  image fail {dest.name}: {e}", file=sys.stderr)
        return False


def try_wix_api(html: str) -> list[dict]:
    """Try Wix stores API if we can find store/instance IDs."""
    products = []
    # Extract metaSiteId
    m = re.search(r'"metaSiteId"\s*:\s*"([a-f0-9-]+)"', html)
    if not m:
        return products
    meta_site = m.group(1)
    print(f"metaSiteId: {meta_site}")

    # Try catalog query endpoint used by Wix
    api_urls = [
        f"https://www.rabbidalfin.com/_api/wixstores-web/v1/products/query",
        f"https://www.rabbidalfin.com/_api/wix-ecommerce-store-web/v1/products/query",
    ]
    body = json.dumps({"query": {}, "paging": {"limit": 100, "offset": 0}}).encode()
    for api in api_urls:
        try:
            req = urllib.request.Request(
                api,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0",
                    "Referer": SHOP_URL,
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            items = data.get("products") or data.get("payload", {}).get("products") or []
            if items:
                print(f"API {api}: {len(items)} products")
                return items
        except Exception as e:
            print(f"API fail {api}: {e}", file=sys.stderr)
    return products


def main():
    print("Fetching shop page...")
    html = fetch_html(SHOP_URL)
    Path(__file__).parent.joinpath("_shop.html").write_text(html[:500000], encoding="utf-8")

    warmup = extract_warmup_data(html)
    categories_map = build_categories_map(warmup) if warmup else {}
    print(f"Categories found: {len(categories_map)}")
    for cid, cname in list(categories_map.items())[:10]:
        print(f"  {cname}")

    raw_products = []
    if warmup:
        raw_products = walk_products(warmup)
        print(f"Warmup walk found: {len(raw_products)} raw product-like objects")

    if len(raw_products) < 10:
        api_products = try_wix_api(html)
        raw_products.extend(api_products)

    # Also try to find products in script tags
    if len(raw_products) < 10:
        for m in re.finditer(r'"products"\s*:\s*(\[[\s\S]*?\])\s*,\s*"(?:totalCount|pagination|filters)"', html):
            try:
                chunk = m.group(1)
                items = json.loads(chunk)
                raw_products.extend(items)
                print(f"Script products chunk: {len(items)}")
            except json.JSONDecodeError:
                pass

    parsed = []
    for raw in raw_products:
        p = parse_product(raw, categories_map)
        if p and p["title"] and p["price"] > 0:
            parsed.append(p)

    parsed = dedupe_products(parsed)
    print(f"Parsed unique products: {len(parsed)}")

    if len(parsed) < 15:
        print("WARNING: fewer products than expected; dumping sample raw keys")
        for raw in raw_products[:3]:
            print(list(raw.keys())[:20])

    # Download images
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    for p in parsed:
        url = p.pop("imageUrl", None)
        ext = ".jpg"
        if url:
            if ".png" in url.lower():
                ext = ".png"
            elif ".webp" in url.lower():
                ext = ".webp"
            img_path = IMAGES_DIR / f"{p['id']}{ext}"
            if download_image(url, img_path):
                p["image"] = f"/public/images/books/{p['id']}{ext}"
            else:
                p["image"] = url  # fallback to remote
        else:
            p["image"] = None

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "source": SHOP_URL,
        "scrapedAt": __import__("datetime").datetime.now().strftime("%Y-%m-%d"),
        "categories": sorted(set(p["category"] for p in parsed)),
        "products": sorted(parsed, key=lambda x: x["title"].lower()),
    }
    OUT_JSON.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(parsed)} products to {OUT_JSON}")
    return len(parsed)


if __name__ == "__main__":
    count = main()
    sys.exit(0 if count >= 15 else 1)
