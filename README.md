# Hana's Gallery

A static gallery site for Hana's artwork — images, videos, and the stories behind them. Styled like a real museum that takes a small artist completely seriously.

**Live:** https://mehrabian.github.io/hana-gallery/

## Structure

```
00-hana-gallery/
├── index.html      ← layout + gallery UI
├── art.json        ← artwork list (what the wall shows)
├── art/            ← web-sized photos
│   └── originals/  ← full-resolution masters
├── .github/
│   ├── ISSUE_TEMPLATE/new-acquisition.yml
│   ├── scripts/process_acquisition.py
│   └── workflows/new-acquisition.yml
└── README.md
```

## Phone ritual — new acquisition (recommended)

1. On your phone, open the repo → **Issues** → **New issue** → **New acquisition**
   Direct link: https://github.com/mehrabian/hana-gallery/issues/new?template=new-acquisition.yml
2. Attach **one photo** of the piece.
3. Fill Title, Medium, Date, Category (Note optional).
4. Submit. In ~2 minutes the Action commits the image + `art.json` entry, closes the issue, and GitHub Pages redeploys.
5. Check https://mehrabian.github.io/hana-gallery/

If something is wrong, the Action comments the error on the issue. Open a **new** issue to retry (edits do not re-run the Action).

## Desktop ritual — edit art.json

1. Put a web copy ≤ 500 KB in `art/` (e.g. `art/2026-08-rainbow.jpg`). Keep the full-res original in `art/originals/`.
2. Open `art.json`, paste a new object at the **top** of the array:

```json
{
  "type": "image",
  "src": "art/2026-08-rainbow.jpg",
  "title": "Rainbow Over Everything",
  "medium": "Crayon on printer paper",
  "date": "August 2026",
  "category": "Drawings",
  "note": "Optional story for the detail view"
}
```

3. Commit and push:

```bash
cd /mnt/c/mnt/00-hana-gallery
git add -A
git commit -m "Add: Rainbow Over Everything (Aug 2026)"
git push
```

## Videos

| type | src | when to use |
|---|---|---|
| `video-youtube` | YouTube video ID | default — Unlisted or Public |
| `video-file` | `art/clip.mp4` | only short clips (< ~20 MB) |

Long-term rule: **YouTube serves, you archive.** Keep original video files on a drive + cloud backup.

## Deploying

Full step-by-step for hanasgallery.com (Cloudflare DNS + GitHub Pages) is in **[DEPLOY.md](DEPLOY.md)**.

## 10-year durability checklist

- [x] Plain HTML/CSS/JS, zero build step, zero dependencies to rot
- [x] Content is a human-readable `art.json`
- [x] Git history = complete dated archive, clonable anywhere
- [x] Phone upload via GitHub Issues + Actions (no extra host)
- [ ] Keep `art/originals/` populated with full-res masters
- [ ] Back up video originals outside YouTube (drive + cloud)
- [ ] Once a year: `git clone` the repo onto a backup drive
