# UNQ Kitchen — Data Consolidation & 3-Level Editor Plan

*Draft for review — 2026-06-02. Nothing built yet.*

## 1. The problem in one line

You have **four outputs** but **three disconnected copies of the data**, so one price change can mean editing the same thing in three places by hand.

### Current state

| Output | File | Where its data lives | Editable today? |
|---|---|---|---|
| Print menu (A4) | `menu/index.html` | **Hardcoded static HTML** (0 scripts, ~171 item blocks, paginated by hand) | ❌ no tool |
| Digital menu | `digital-menu/index.html` | **Embedded `SECTIONS` JS array** (rich: groups → categories → items → variants, with desc, image, ingredients, price, spicy/sweet tags) | ❌ no tool |
| Print packages (A4) | `package/index.html` | Generated from `menu-editor/data.json` | ✅ menu-editor |
| Digital packages | — | **does not exist** | — |

### The three data stores today

1. `menu-editor/data.json` → `masterMenu` (237 flat priced rows named `"Parent – Variant"`, e.g. `Pizza – Margherita ₹200`) + `packages` + `venuePage`.
2. `digital-menu/index.html` → `SECTIONS` (the richest source — full descriptions, images, ingredients, variant prices, tags).
3. `menu/index.html` → the same dishes again, baked into static markup.

### The one relationship that makes consolidation possible

`masterMenu` is just a **flattened, variant-level view** of the rich menu:

```
digital "Pizza" › variant "Margherita" ₹200   ≡   masterMenu "Pizza – Margherita" ₹200
```

So a **single rich item model can mechanically derive** the flat `masterMenu` that packages need. That's the whole basis of the plan.

### Two mismatches the migration must resolve

- **Taxonomy differs.** Print/digital use `Starters, Curries, Breads, Rice…`; `masterMenu` uses `Main (Starter), Main (Curries)…`, splits `Daal` out, and has a `Live Counters` section the digital menu doesn't show. These need an explicit mapping.
- **Prices may already disagree** between `SECTIONS` and `masterMenu`. Consolidating forces a single correct number — I'll produce a diff so you choose.

---

## 2. Target architecture

### One source of truth: `data.json` v2

One rich item model + per-output presentation settings. Shape (sketch):

```
{
  "menu": {
    "groups":     ["Mains", "Snacks", "Live Counters"],
    "categories": [ { id, name, group, sub } ],
    "items": [
      { id, categoryId, name, desc, img, tags:["spicy","sweet"],
        price: "",                                  // for variant-less items
        variants: [ { id, name, ing, price } ] }    // price lives on the variant
    ]
  },
  "packages":   [ ... ],     // reference menu items/variants by ID (not by name)
  "venuePage":  { ... },
  "presentation": {
    "printMenu":      { sectionOrder, cover, lastPage, footnotes, colors, fonts, pagination },
    "printPackage":   { templateCss, terms styling, cover, lastPage, page-numbering },
    "digitalMenu":    { filters, search on/off, category-nav order, show/hide fields, badges },
    "digitalPackage": { ... }
  }
}
```

Key choice: **`masterMenu` becomes derived**, not stored. The builder flattens `items × variants` into `"Name – Variant" @ price` at build time. Packages link by stable **ID**, so renaming a dish never breaks a package.

### This maps exactly onto your three editor levels

| Level | Edits | Writes to |
|---|---|---|
| **L1 — Data (catalog)** | The food catalog **only**: items, variants, prices, category. Nothing about menus or packages | `menu.items` (content only) |
| **L2 — Print authoring** | Builds the print menu **and the party packages** from the catalog: which items go in each, sections, package price, terms, cancellation, venue, footnotes, notes, cover/last page, colors, fonts, images, A4 layout | `packages[]`, `presentation.printMenu`, `presentation.printPackage`, `venuePage` |
| **L3 — Digital authoring** | Digital menu **and digital package**: filters, search, filter position, show/hide fields, badges, and other digital-only features | `presentation.digitalMenu`, `presentation.digitalPackage` |

Same data, three lenses. A price typed once in L1 flows to all four outputs.

### Render pipeline (local helper app — your choice)

```
                         ┌──────────────┐
        L1 / L2 / L3  →  │  data.json   │  ←  single source of truth
        editors          └──────┬───────┘
                                │  local helper app: saves data + rebuilds all 4
              ┌─────────────────┼───────────────────┬───────────────────┐
              ▼                 ▼                   ▼                   ▼
       menu/index.html   package/index.html  digital-menu/...   digital-package/...
        (print A4)         (print A4)          (mobile/web)      (mobile/web, NEW)
```

You launch a small local helper app, which opens in your browser. Editing in any mode writes straight to `data.json` and regenerates all four output pages on save — no export/replace/rebuild step. The generated pages stay plain HTML that work on GitHub Pages once pushed.

---

## 3. One-time migration

1. Parse `digital-menu` `SECTIONS` → canonical `menu.items` (richest source).
2. Map taxonomy (`Main (Curries)` → `Curries`, split-out `Daal`, `Live Counters`, etc.) and **reconcile prices** vs `masterMenu` → produce a **diff report** for you to approve.
3. Re-point every package item from name-reference to item/variant **ID**.
4. **Verify:** derived `masterMenu` == current `masterMenu`, so existing packages render identically.
5. Pull print-menu-only details (cover page, last page, footnotes, exact section order/pagination, any dishes not in the digital set) into `presentation.printMenu` and fill gaps in `menu.items`.

---

## 4. Phasing (each phase independently shippable)

- **Phase 0** — Approve this architecture + the decisions below.
- **Phase 1** — Build `data.json` v2 + migration + reconciliation/diff report. I pause for your decisions on any conflicts before locking the data. Prove all four outputs can be generated (digital package is the only new one). *No UI changes yet — today's editor keeps working.*
- **Phase 2** — Unified builder replacing `rebuild.py`, generating all 4 files.
- **Phase 3** — **L1 editor**: extend the current editor to edit menu items/variants/prices; auto-derive `masterMenu`.
- **Phase 4** — **L2 editor**: print presentation for menu + package (your existing Design/Terms/Venue tabs generalize into this).
- **Phase 5** — **L3 editor**: digital presentation + the new digital-package output.

Your current package workflow stays fully functional until each piece is replaced.

---

## 5. Decisions — locked

1. **One rich item model.** The flat price list (`masterMenu`) is *derived* from it — a price is edited once and flows everywhere.
2. **Core data must match exactly.** Where the digital menu and the package price list currently disagree, I produce a reconciliation report and **ask which value to keep** — nothing is auto-picked.
3. **One shared description** per dish, used by both print and digital.
4. **One editor, three modes** (L1 catalog / L2 print authoring / L3 digital authoring) over the shared `data.json`.
5. **Local helper app** to save — writes `data.json` directly and rebuilds all four pages on save; no manual export/replace.
6. **Clean restructure allowed.** I'll reorganize folders into a clean layout and remove dead files, showing you the exact rename/delete list before doing it.

**Start point: Phase 1** — consolidate + reconcile the data before any UI work.
