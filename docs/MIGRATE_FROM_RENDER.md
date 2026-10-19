# Migrate rcd-website from Render to Cloudflare Pages

This site is static HTML at the repo root. Render used a `/clip` → `/clip.html` rewrite; that rule lives in [`_redirects`](../_redirects) at the publish root.

## Cloudflare Pages (free)

1. Log in at [dash.cloudflare.com](https://dash.cloudflare.com/) → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
2. Choose GitHub → authorize → select **`NeVoTM/rcd-website`**.
3. **Build settings**
   - Production branch: `main`
   - Framework preset: **None**
   - Build command: *(leave empty)*
   - Build output directory: **`/`** (repo root)
4. **Save and Deploy**. Note the `*.pages.dev` URL and test `/clip?id=…`.
5. **Custom domain** (if you use one): Pages project → **Custom domains** → add hostname → follow DNS instructions (CNAME to your `*.pages.dev` host, or move DNS to Cloudflare for apex).

## After Pages is live

1. Update any bookmarks/links that pointed at `*.onrender.com`.
2. In [Render Dashboard](https://dashboard.render.com/): open **rcd-website** → **Settings** → suspend or **Delete** the static service so you are not billed.

## Local check

`_redirects` is only applied on Cloudflare Pages (not when opening `index.html` from disk). Use `/clip.html?id=…` locally, or serve the folder with a static server that honors `_redirects`.
