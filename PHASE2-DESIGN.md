# Phase 2 Design Upgrade

## Inspiration Sources

Design patterns studied (layout, typography, spacing — **not content or branding**):

| Site | Patterns Adopted |
|------|------------------|
| [TheYeshiva.net](https://www.theyeshiva.net/) | Sticky header with gold accent border; featured content sections; card grid with duration/metadata hierarchy; multi-column footer with Explore/Connect columns |
| [InsideChassidus.org](https://www.insidechassidus.org/) | Clean scholarly palette; serif/sans-serif pairing; generous whitespace; section labels above headings |
| MeaningfulLife.com | *(403 on fetch)* — general Torah-education site conventions applied from category |

## Changes Made

### Typography
- **Cormorant Garamond** (headings) + **Source Sans 3** (body/nav) via Google Fonts
- Clear hierarchy: eyebrow labels → h1 → lead → body
- Section headings with gold gradient underline

### Color Palette
- Warm scholarly tones: navy deep `#141f33`, gold `#b8922a`, parchment background `#f7f4ed`
- Consistent CSS custom properties for shadows, borders, and radii

### Header & Navigation
- Sticky header with gold bottom border
- Mobile hamburger toggle with slide-down nav
- Active page highlighted with gold pill background

### Homepage Hero
- Full-width gradient hero banner with portrait
- Eyebrow label, prominent headline, dual CTAs
- Featured clip section in elevated card container

### Watch / Clip Pages
- Page banner on watch listing
- Clip cards with play-button overlay and hover lift
- Centered clip page header above vertical video player

### Footer
- Three-column layout: brand blurb, Explore links, Connect links
- Copyright bar with phone link

### Responsive
- Mobile nav collapse at 768px
- Single-column clip grid on small screens
- Full-width CTAs on narrow viewports

## Files Modified

- `styles.css` — complete Phase 2 design system
- `app.js` — mobile nav, play overlay on cards, featured section wrapper
- All HTML pages — updated header/footer structure, font preconnect
- `index.html`, `watch.html` — enhanced hero/banner layouts

## Preserved

- All existing RCD content, clips, transcripts, multilingual pages
- Self-hosted MP4 players (no YouTube embeds reintroduced)
- Existing data files and deployment config unchanged
