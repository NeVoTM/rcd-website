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
| Transcripts | Drive `RCD/05-Transcripts/<title>/transcript.txt` (from `scripts/vtt_to_transcript.py`) |
| Code | GitHub NeVoTM/rcd-website |

## Deploy

Push to `main` on GitHub — Render should auto-deploy from `NeVoTM/rcd-website`.

### Verify auto-deploy is wired

In [Render → rcd-website → Settings](https://dashboard.render.com):

1. **Build & Deploy → Auto-Deploy:** must be **On** for branch `main`.
2. **Repository:** must show `NeVoTM/rcd-website` (reconnect GitHub if blank or wrong repo).
3. After each push, check **Events** for a new deploy; failed builds leave the previous version live.

`render.yaml` in this repo documents the static site (`runtime: static`, publish path `.`). If the service was created manually in the dashboard, Blueprint fields alone do not re-link GitHub — use Settings above or **Sync Blueprint** if you manage the service from `render.yaml`.

### Manual deploy (when auto-deploy misses a push)

Render Dashboard → **rcd-website** → **Manual Deploy** → **Deploy latest commit**.

No API key needed. Optional: Settings → **Deploy Hook** URL for CI; store the hook URL as a secret, not in git.

### Quick live check

- `https://rcd-website.onrender.com/data/clips.json` — clips should include `"subtitles"` objects after caption deploys.
- `https://rcd-website.onrender.com/public/clips/zerizus-miracle.en.vtt` — should return **200**, not 404.
