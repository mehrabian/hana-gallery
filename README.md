# Hana's Gallery 🖍️

A single-file static gallery site for Hana's artwork — images, videos, and the stories behind them. Styled like a real museum that takes a small artist completely seriously.

## Structure

```
00-hana-gallery/
├── index.html      ← the whole site (layout + artwork list)
├── art/            ← put photos/scans of her art here
│   └── originals/  ← (optional) full-resolution masters, not published
└── README.md
```

## Monthly routine — adding new art

1. Photograph or scan the piece. Export a web copy ≤ 500 KB (e.g. `art/2026-08-rainbow.jpg`).
   Keep the full-resolution original in `art/originals/` (kept in git, not linked from the site) — that's your archive.
2. Open `index.html`, find the `ARTWORKS` list near the top of the `<script>` section.
3. Copy an existing block, paste it at the **top** of the list, fill in:
   - `title` — what Hana calls it
   - `medium` — museum style, e.g. `"Crayon on printer paper"`
   - `date` — e.g. `"August 2026 · age 5"`
   - `category` — `Drawings`, `Paintings`, `Crafts`, `Videos`… new categories create new filter pills automatically
   - `note` — the story (optional, shown in the detail view)
4. Commit and push:

```bash
git add -A
git commit -m "Add: Rainbow Over Everything (Aug 2026)"
git push
```

The site updates itself within a minute. **Bonus:** the git history becomes a dated, annotated timeline of her entire artistic career.

## Videos

Two supported types in `ARTWORKS`:

| type | src | when to use |
|---|---|---|
| `video-youtube` | the YouTube video ID | **default choice** — upload as *Unlisted* or *Public*; free streaming, works on all devices |
| `video-file` | `art/clip.mp4` | only for very short clips (< ~20 MB); GitHub blocks files > 100 MB and streams poorly |

Long-term rule: **YouTube serves, you archive.** Keep the original video files in your own backup (external drive + cloud), because YouTube compresses and an account is not an archive.

## Deploying — see DEPLOY.md

Full step-by-step for hanasgallery.com (Cloudflare DNS + GitHub Pages) is in **[DEPLOY.md](DEPLOY.md)**.

## Quick reference: GitHub Pages setup

```bash
# from inside this folder
git init                      # (already done if you got this as a repo)
git add -A && git commit -m "Hana's gallery — opening day"

# create the repo on GitHub (using GitHub CLI):
gh repo create hana-gallery --public --source=. --push
# or create it on github.com and:
# git remote add origin git@github.com:YOURUSER/hana-gallery.git
# git push -u origin main
```

Then on GitHub: **Settings → Pages → Source: Deploy from branch → `main` / root**.
Site appears at `https://YOURUSER.github.io/hana-gallery/` in ~1 minute.

Optional: buy a domain (e.g. `hanasgallery.com`, ~$12/yr) and point it at Pages — domains outlive platforms.

## 10-year durability checklist

- [x] Plain HTML/CSS/JS, zero build step, zero dependencies to rot
- [x] Content is a human-readable list inside one file
- [x] Git history = complete dated archive, clonable anywhere
- [ ] Keep `art/originals/` populated with full-res masters
- [ ] Back up video originals outside YouTube (drive + cloud)
- [ ] Once a year: `git clone` the repo onto a backup drive
