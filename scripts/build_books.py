#!/usr/bin/env python3
"""Build data/books.json and download cover images from browser scrape."""
from __future__ import annotations

import json
import re
import time
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BROWSER_JSON = Path(__file__).resolve().parent / "_browser_products.json"
CATALOG_JSON = Path(__file__).resolve().parent / "_catalog_raw.json"
OUT_JSON = ROOT / "data" / "books.json"
IMAGES_DIR = ROOT / "public" / "images" / "books"
UA = "Mozilla/5.0 (RCD books migration)"


def slug_from_url(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def detect_format(title: str) -> str:
    t = title.lower()
    if "dvd" in t:
        return "dvd"
    if " cd" in t or t.endswith(" cd") or "cd -" in t:
        return "cd"
    if "via online" in t or "download" in t:
        return "digital"
    return "book"


def detect_category(title: str, fmt: str) -> str:
    t = title.lower()
    if fmt in ("dvd", "cd", "digital"):
        return "DVD's / CD's"
    if "portrait" in t or "habad portrait" in t:
        return "Chabad Portraits"
    if "rebbe's advice" in t or "rebbe's advice" in t or t.startswith("rebbe's advice"):
        return "The Rebbe's Advice"
    if "davening" in t or "rosh hashana" in t or "prayer" in t or "inspired:" in t:
        return "Prayer and Holidays"
    if any(x in t for x in ("mystic", "maamar", "demystifying", "soul journey", "invisible hand", "mental health")):
        return "Mysticism"
    if any(x in t for x in ("lifestory", "holocaust", "surviving", "the real zalman", "the real shlomo", "biography")):
        return "Biography"
    if any(x in t for x in ("rashab", "leadership", "model for leadership", "seven chabad", "great leaders")):
        return "Great Leaders"
    if any(
        x in t
        for x in (
            "chasid",
            "farbreng",
            "tanya",
            "to be chassidic",
            "to be lubavitch",
            "ginzei",
            "nigunim",
            "lubavitch speak",
        )
    ):
        return "Chasidic Thought"
    if any(
        x in t
        for x in (
            "chabad and",
            " and chabad",
            " and lubavitch",
            " and rebbe",
            "breslov",
            "satmar",
            "lakewood",
            "mir",
            "ponovitz",
            "telz",
            "sephardim",
            "yeshiva university",
            "young israel",
            "aguda",
            "orthodoxy",
            "boro park",
            "world leaders",
            "presidents",
        )
    ):
        return "Lubavitch with others"
    if "who's who" in t or "rebbe and" in t or "rebbe's" in t or "conversations with the rebbe" in t:
        return "Chabad/Lubavitch Culture"
    return "Books"


def ribbon_tags(ribbon: str) -> list[str]:
    if not ribbon or not ribbon.strip():
        return []
    return [ribbon.strip()]


def normalize_badge(badge: str) -> list[str]:
    if not badge:
        return []
    return [badge.strip()]


def wix_media_id(url: str) -> str | None:
    if not url:
        return None
    m = re.search(r"/media/([^/?]+)", url)
    return m.group(1) if m else None


def high_res_url(url: str) -> str:
    media = wix_media_id(url)
    if not media:
        return url
    ext = "jpeg" if media.endswith(".jpeg") else "jpg"
    return f"https://static.wixstatic.com/media/{media}/v1/fit/w_420,h_640,q_85/file.{ext}"


def download(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 1000:
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = resp.read()
        if len(data) < 500:
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return True
    except Exception as exc:
        print(f"  skip image {dest.name}: {exc}")
        return False


def load_ribbons() -> dict[str, str]:
    ribbons: dict[str, str] = {}
    if not CATALOG_JSON.exists():
        return ribbons
    catalog = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
    for raw in catalog.get("products") or []:
        slug = raw.get("urlPart") or ""
        ribbon = raw.get("ribbon") or ""
        if slug and ribbon:
            ribbons[slug] = ribbon
    return ribbons


def main() -> int:
    raw_items = json.loads(BROWSER_JSON.read_text(encoding="utf-8"))
    ribbons = load_ribbons()
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    products = []
    for item in raw_items:
        slug = slug_from_url(item["purchaseUrl"])
        fmt = detect_format(item["title"])
        category = detect_category(item["title"], fmt)
        tags = normalize_badge(item.get("badge") or "")
        if slug in ribbons:
            tags = list(dict.fromkeys(tags + ribbon_tags(ribbons[slug])))
        for kw, tag in [
            ("limited", "Limited Print"),
            ("new", "New Arrival"),
        ]:
            if any(kw in t.lower() for t in tags):
                break
        else:
            pass

        img_url = high_res_url(item.get("image") or "")
        ext = ".jpeg" if img_url.endswith(".jpeg") else ".jpg"
        local_name = f"{slug}{ext}"
        local_path = IMAGES_DIR / local_name
        image_web = None
        if img_url and wix_media_id(item.get("image") or ""):
            if download(img_url, local_path):
                image_web = f"/public/images/books/{local_name}"
            else:
                image_web = img_url
            time.sleep(0.15)
        elif img_url:
            image_web = img_url

        products.append(
            {
                "id": slug,
                "title": item["title"].strip(),
                "price": float(item.get("price") or 0),
                "currency": "USD",
                "category": category,
                "tags": tags,
                "image": image_web,
                "description": "",
                "format": fmt,
                "purchaseUrl": item["purchaseUrl"],
            }
        )

    categories = sorted(set(p["category"] for p in products))
    output = {
        "source": "https://www.rabbidalfin.com/shop",
        "scrapedAt": date.today().isoformat(),
        "productCount": len(products),
        "categories": categories,
        "products": sorted(products, key=lambda p: p["title"].lower()),
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(products)} products -> {OUT_JSON}")
    downloaded = sum(1 for p in products if (p.get("image") or "").startswith("/public/"))
    print(f"Local images: {downloaded}/{len(products)}")
    return len(products)


if __name__ == "__main__":
    raise SystemExit(0 if main() == 106 else 1)
