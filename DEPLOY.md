# Deploying hanasgallery.com — step by step

Domain: **hanasgallery.com** (registered at Cloudflare)
Host: **GitHub Pages**

## 0. Verify your email (do this first!)

Click the link in the ICANN verification email Cloudflare sent you.
**Deadline: 14 days after purchase**, or the domain gets suspended. Check spam if missing.

## 1. Push this folder to GitHub

```bash
# from inside this folder (git is already initialized with a first commit)
gh repo create hana-gallery --public --source=. --push

# or without GitHub CLI: create an empty repo on github.com, then
# git remote add origin git@github.com:YOURUSER/hana-gallery.git
# git push -u origin main
```

Then on GitHub: **Settings → Pages → Source: Deploy from a branch → `main` / `(root)` → Save**.
Check the temporary address works: `https://YOURUSER.github.io/hana-gallery/`

## 2. Add DNS records in Cloudflare

Cloudflare dashboard → **hanasgallery.com → Manage → DNS → Records → Add record**.
Create these five:

| Type  | Name  | Content               | Proxy status            |
|-------|-------|-----------------------|-------------------------|
| A     | `@`   | `185.199.108.153`     | **DNS only** (grey ☁️) |
| A     | `@`   | `185.199.109.153`     | **DNS only**            |
| A     | `@`   | `185.199.110.153`     | **DNS only**            |
| A     | `@`   | `185.199.111.153`     | **DNS only**            |
| CNAME | `www` | `YOURUSER.github.io`  | **DNS only**            |

⚠️ **Cloudflare gotcha:** click each record's orange cloud so it turns **grey ("DNS only")**.
The orange proxy blocks GitHub from issuing your HTTPS certificate. You can turn the
proxy back on after HTTPS works (optional — grey is fine forever).

## 3. Tell GitHub about the domain

Repo → **Settings → Pages → Custom domain** → enter `hanasgallery.com` → Save.

- Wait for the DNS check to turn green (minutes to ~1 hour)
- Then tick **Enforce HTTPS** (the checkbox becomes clickable once the certificate is issued)

GitHub will add a `CNAME` file to the repo — commit it if prompted; it must stay.

## 4. Done — and two settings for the next 10 years

- ✅ `https://hanasgallery.com` is live; the github.io address now redirects to it
- 🔁 Cloudflare → Manage domain → **turn on auto-renewal** (a lost card payment is how domains die)
- 🔐 Enable **2FA** on both the Cloudflare and GitHub accounts — the accounts *are* the ownership
- 💾 Once a year: `git clone` this repo onto a backup drive

## Troubleshooting

- **DNS check stays red:** confirm all five records exist and clouds are grey; give it up to an hour
- **"Domain already taken" on GitHub:** someone verified it on another account — see GitHub's docs on verified domains, or contact support
- **HTTPS checkbox greyed out:** certificate still issuing — wait, re-save the custom domain if > 24 h
