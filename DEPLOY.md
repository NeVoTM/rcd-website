# RCD.com — Live URLs

- **Render (live now):** https://rcd-website.onrender.com
- **GitHub:** https://github.com/NeVoTM/rcd-website
- **Google Drive:** [17274/RCD](https://drive.google.com/drive/folders/1Q0rMoUb7ho-rt-m1uwCDSin3FHDJkeir) on elichalfinny@gmail.com

## Custom domain RCD.com

In Render → **rcd-website** → Settings → Custom Domains → Add `rcd.com` and `www.rcd.com`

Point DNS at your registrar:

| Host | Type | Value |
|------|------|-------|
| `www` | CNAME | `rcd-website.onrender.com` |
| `@` | ANAME/ALIAS or redirect | Render root target, or redirect apex → `www.rcd.com` |

Render will issue SSL automatically once DNS propagates.

## Storage

| Layer | Location |
|-------|----------|
| Originals | Google Drive `RCD/01-Originals/` |
| Portraits | `RCD/02-Photos/portraits/` + site `public/images/portraits/` |
| Edited clips | Drive `RCD/04-Edited-Backup/` + `public/clips/` + Render |
| Code | GitHub NeVoTM/rcd-website |

## Deploy

Push to `main` on GitHub — Render auto-deploys from `NeVoTM/rcd-website`.
