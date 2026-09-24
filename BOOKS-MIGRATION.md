# Books Migration

- **Source:** https://www.rabbidalfin.com/shop
- **Scraped:** 2026-09-23
- **Products migrated:** 106
- **Categories:** 12 (heuristic assignment from titles; shop filters used as taxonomy)
- **Images:** Downloaded to `public/images/books/` where available (Wix CDN fallback otherwise)
- **Purchase flow:** External — "Buy on RabbiDalfin.com" links to original Wix product pages

## Pages

| Page | Purpose |
|------|---------|
| `/books.html` | Filterable catalog grid |
| `/product.html?id={slug}` | Individual book detail |
| `/book.html` | Unchanged — invite Rabbi Dalfin (booking) |

## Regenerate

```bash
python scripts/build_books.py
```

Raw browser scrape: `scripts/_browser_products.json` (106 items via Load More automation).

## Notes

- 5 products show $0 on shop (e.g. Chabad's Secret, Soul Journeys) — displayed as "See shop"
- 2 products had missing cover images in shop DOM at scrape time (Davening: Shabbos, Davening: Weekday)
- Render deploy may require manual trigger after push to `main`
