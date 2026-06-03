# data.json v2 — concrete schema (for approval)

*2026-06-03. This is the single source of truth all four outputs are built from. Real migrated examples below.*

## Top-level shape

```jsonc
{
  "version": 2,
  "meta": { "currency": "₹", "updated": "2026-06-03" },
  "menu":        { "groups": [...], "categories": [...], "items": [...] },
  "packages":    [...],
  "venuePage":   { ... },          // unchanged from today
  "presentation":{ "printMenu":{}, "printPackage":{}, "digitalMenu":{}, "digitalPackage":{} }
}
```

## menu — the food catalog (edited in L1)

```jsonc
"groups": [
  { "id": "mains",  "name": "Mains" },
  { "id": "snacks", "name": "Snacks" },
  { "id": "live",   "name": "Live Counters" }
],

"categories": [
  { "id": "starters", "groupId": "mains", "name": "Starters",
    "sub": "Soups, salads, shared bites & grills" }
  // …Curries, Breads, Rice, Combos, Dessert, Snacks, Hot/Cold Beverages, Live Counters
],

"items": [
  {
    "id": "soup",                          // stable slug — packages link to this
    "categoryId": "starters",
    "name": "Soup",
    "desc": "Warm, comforting and made fresh every time…",
    "img": "menu/assets/mains/manchow-soup.png",   // site-root relative; builder fixes prefix per page
    "tags": [],                            // "spicy" | "sweet"  (from the 🌶️ / 🍬 markers)
    "price": null,                         // null when the item has variants
    "variants": [
      { "id": "soup-manchow", "name": "Manchow",
        "ing": "Spicy Indo-Chinese broth with crispy noodle garnish",
        "price": 100, "tags": [] }
    ]
  },

  // Live Counter — package-only, no price, hidden from the digital menu
  { "id": "live-chaat", "categoryId": "live-counters", "name": "Chaat",
    "desc": "", "img": "", "tags": [], "price": null,
    "showOnDigital": false, "variants": [] }
]
```

## packages — built in L2, reference the catalog by ID

```jsonc
{
  "id": "pkg1", "number": 1, "name": "Quick Gather", "price": 199,
  "description": "…", "idealValue": "…", "waterNote": "…",
  "sections": [
    { "name": "Welcome", "instruction": "Each guest picks 1 on the day", "chip": "1 per person",
      "items": [
        { "ref": { "itemId": "tea", "variantId": "tea-masala" },
          "displayName": "Masala Tea",   // optional — overrides catalog name on the package page only
          "badge": "", "note": null }
      ]
    }
  ],
  "booking": { ... }, "terms": [ ... ], "cancellation": [ ... ]
}
```

`displayName` preserves today's behaviour where a package can show a custom label (e.g. "Veg Pakoda") while still linking to the catalog item for price.

## Derived, not stored: `masterMenu`

The builder flattens `items × variants` → `"Name – Variant" @ price` to reproduce today's flat list for pricing and back-compat. A dish renamed in L1 never breaks a package, because packages link by **ID**.

## presentation — stubbed now, filled in L2/L3

```jsonc
"printMenu":      { "sectionOrder": [...], "cover": {...}, "lastPage": {...}, "footnotes": [...], "theme": { "colors": {...}, "fonts": {...} } },
"printPackage":   { "css": "<full template CSS>", "cover": {...}, "lastPage": {...}, "pageNumbering": true },
"digitalMenu":    { "search": true, "filters": [...], "categoryNavOrder": [...], "fields": { "images": true, "ingredients": true }, "badges": {} },
"digitalPackage": { /* same idea — built new */ }
```

## Migration rules being applied

1. **Prices stored as numbers** (`100`), not `"₹100"` strings; `meta.currency` holds the symbol.
2. **Catalog built from the digital menu** (richest source: descriptions, images, ingredients, tags).
3. **Fixes from your decisions:** Grilled Sandwich (Veg) = ₹100; 22 mislabeled items filed under their correct category; 3 junk rows dropped; 11 minor names standardized; shakes stored **per-flavour with prices**; 4 Live Counters added as `showOnDigital:false`.
4. **Packages re-pointed** from name-references to `itemId`/`variantId`, with `displayName` kept where it differed.
5. **Verification:** I regenerate the package price list from v2 and diff it against today's — it must match except the intended fixes above.

## One content gap to flag

Per-flavour shakes (Mango, Badam, Oreo…) have prices but **no individual ingredient text** in either source today (the digital menu grouped them). I'll carry prices and leave `ing` blank for those — you can fill them later in L1, or I can draft them. Switching shakes to per-flavour also means the **digital menu will list flavours individually** instead of the grouped families it shows now.
