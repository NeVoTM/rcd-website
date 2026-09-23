# RCD.com — Live URLs

- **Render (live now):** https://rcd-website.onrender.com
- **GitHub:** https://github.com/NeVoTM/rcd-website
- **Google Drive:** RCD/ folder (dalfinny5 via rclone)

## Custom domain RCD.com

Render → rcd-website → Settings → Custom Domains → Add `rcd.com` and `www.rcd.com`

DNS:
- CNAME `www` → `rcd-website.onrender.com`
- ANAME/ALIAS `@` → Render (or redirect root to www)

## Storage

| Layer | Location |
|-------|----------|
| Originals | Google Drive `RCD/01-Originals/` |
| Edited clips | Drive `RCD/04-Edited-Backup/` + `public/clips/` + Render |
| Code | GitHub NeVoTM/rcd-website |
