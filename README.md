# UNQ Kitchen — Menu Website

Live menus for UNQ Kitchen, hosted on GitHub Pages at **https://unq.kitchen**.

```
.
├── index.html            Restaurant homepage  → https://unq.kitchen/
├── assets/               Shared brand assets (UNQ crest, BlippoMN font)
│   ├── crest.png
│   └── BlippoMN.ttf
├── menu/                 Static menu (mirrors the offline printed menu)
│   ├── index.html        Menu picker  → https://unq.kitchen/menu/
│   ├── mains/            Main menu    → https://unq.kitchen/menu/mains/
│   │   ├── index.html
│   │   ├── assets/       Food photos
│   │   └── UNQ-Kitchen-Mains-List.xlsx   (source price/item list)
│   └── snacks/           Snacks & beverages → https://unq.kitchen/menu/snacks/
│       ├── index.html
│       ├── assets/food-photos/
│       ├── assets/beverages/
│       └── UNQ-Kitchen-Snacks-List.xlsx
├── digital-menu/         Digital menu (QR target) → https://unq.kitchen/digital-menu/
│   └── index.html        Mobile-first; reads items from the static menus.
│                         order-slot hooks are in place for future ordering.
└── CNAME                 Custom domain (unq.kitchen)
```

## Pages & URLs

- **Homepage** `https://unq.kitchen/` — branding, hours, address, contact, and buttons to the menus.
- **Static menu** `https://unq.kitchen/menu/` — same as the offline printed menu (mains + snacks).
- **Digital menu** `https://unq.kitchen/digital-menu/` — the QR-code target. This URL is permanent and safe to print; future ordering features will be added here without changing the link.

## Editing the digital menu

The digital menu's item data is embedded in `digital-menu/index.html` (in the `SECTIONS` variable inside the `<script>`). It was generated from the static menu HTML. When you update prices/items in the static menu, re-generate or hand-edit the `SECTIONS` data so the two stay in sync.

## The everyday workflow (replaces manual version folders)

You no longer copy the folder for each new version. Git keeps the full history for you.

1. Edit `mains/index.html` or `snacks/index.html` (and swap assets if needed).
2. Open the folder in VS Code → Source Control panel → write a short message → **Commit**.
3. Click **Sync / Push**. The live site updates in ~1 minute.

### Marking a version (optional but recommended)

When you finish a meaningful update, tag it so you can always come back to it:

```
git tag v0.9 -m "Mains: added new thali, updated prices"
git push --tags
```

To see an old version later: `git checkout v0.8` (then `git checkout main` to return).
Your old `V0.x` / `V 1.x` folders are kept outside this repo as a one-time backup; once you trust git, you can archive or delete them.

## First-time setup on GitHub

**Start git fresh (run once, in the VS Code terminal inside this folder):**

```
rm -rf .git          # removes a leftover partial .git from setup
git init -b main
git add -A
git commit -m "Initial site: mains v0.8 + snacks v1.5"
git tag v0.8
git tag v1.5-snacks
```

Then:

1. Create a new repository on GitHub (e.g. `unq-kitchen-menu`), empty.
2. In VS Code, publish this folder to that repo (or `git remote add origin <url>` then `git push -u origin main --tags`).
3. On GitHub: **Settings → Pages** → Source = `Deploy from a branch`, Branch = `main`, folder = `/ (root)` → Save.
4. **Settings → Pages → Custom domain** → enter `unq.kitchen` → Save (the `CNAME` file is already in this repo).

### DNS for unq.kitchen (set at your domain registrar)

For the apex domain `unq.kitchen`, add four **A records** pointing to GitHub Pages:

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

(Optional) a `www` **CNAME** record pointing to `<your-github-username>.github.io`.
After DNS propagates, tick **Enforce HTTPS** in Settings → Pages.

## Notes

- The large menu **PDFs are intentionally not in git** (GitHub rejects files over 100 MB, and they regenerate from the HTML). Keep them locally if you need them.
- Food photos were compressed (2026-05-30) from ~137 MB total to ~6.5 MB (resized to max 1000 px, optimized PNG) for fast loading — especially on phones scanning the digital-menu QR. Filenames are unchanged. Originals remain recoverable from git history if ever needed.
