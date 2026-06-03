# Data Reconciliation — digital menu vs package price list

*2026-06-03. Two-pass automated match. 185/185 matched prices agree except one. Confirm the items below and I lock `data.json` v2.*

## Summary

- Digital priced entries **224** · package rows **237**
- Exact matches **185** — prices agree **184**, conflict **1**
- Same dish, wrong category label in package list: **22**
- Junk placeholder rows: **3** · minor name diffs: **11** · Live Counters: **4** · Shakes (structural): **12**
- On digital only (never in a package): **7**

## 1 · Price conflict — your call

| Dish | Digital | Package |
|---|---|---|
| Grilled Sandwich – Veg | ₹100 | ₹90 |

## 2 · Wrong category label (recommend: align to the digital name)

| Package label | Correct name | # items |
|---|---|---|
| Chinese Starter | Tandoor Starter | 12 |
| Kulcha | Paratha | 7 |
| Kaju | Kofta | 3 |

## 3 · Junk rows (recommend: delete)

| Row | Price |
|---|---|
| Tandoor Starter | ₹8 |
| Kofta | ₹25 |
| Paratha | ₹1 |

## 4 · Minor name differences — same dish, same price (recommend: standardize, no decision needed)

| Package name | Digital name | Price |
|---|---|---|
| Chinese Starter – Soya Hariyali Chaap Tikka | ? | ₹270 |
| Coffee – Black Coffee | Coffee – Black | ₹25 |
| Coffee – Instant Coffee | Coffee – Instant | ₹30 |
| Hot Milk – Horlicks Milk | Hot Milk – Horlicks | ₹50 |
| Hot Milk – Turmeric Milk | Hot Milk – Turmeric | ₹40 |
| Nuggets – Cheese Nuggets | Nuggets – Cheese | ₹180 |
| Soft Drink – Soft Drink | Soft Drink – Regular | ₹25 |
| Tea – Black Tea | Tea – Black | ₹20 |
| Tea – Lemon Tea | Tea – Regular | ₹25 |
| Tea – Masala Tea | Tea – Masala | ₹30 |
| Tea – Regular Tea | Tea – Regular | ₹25 |

## 5 · Shakes — structural difference (your call)

Package list prices each flavour individually; digital groups them (Fruit Shake, Flavoured Shake, Dry Fruit Shake, Cookie Shake…). Per-flavour package rows:

- Shakes – Apple — ₹120
- Shakes – Badam — ₹150
- Shakes – Chocolate — ₹120
- Shakes – Cold Coffee with Ice Cream — ₹140
- Shakes – Kaju — ₹150
- Shakes – Kit Kat — ₹140
- Shakes – Mango — ₹120
- Shakes – Oreo — ₹140
- Shakes – Pineapple — ₹120
- Shakes – Rose — ₹100
- Shakes – Strawberry — ₹120
- Shakes – Vanilla — ₹100

## 6 · Live Counters — package-only, no standalone price (recommend: keep, hidden from digital menu)

- Live Counter – Momos
- Live Counter – Chaat
- Live Counter – Gupchup
- Live Counter – Bhel

## 7 · On digital only, not in any package (7) — informational

- Tandoor Starter – Soya Hariyali Chaap (₹270)
- Pizza – Garlic Bread (₹100)
- Shakes – Dry Fruit Shake (₹150)
- Shakes – Cookie Shake (₹140)
- Shakes – Coffee Float (₹140)
- Shakes – Flavoured Shake (₹100)
- Shakes – Fruit Shake (₹120)

## 8 · Category mapping (digital ↔ package)

| Digital group | Digital cat | Pkg section | Pkg cat | # |
|---|---|---|---|---|
| Mains | Beverages | Mains | Beverages | 1 |
| Mains | Breads | Mains | Main (Breads) | 10 |
| Mains | Combos | Mains | Combos | 2 |
| Mains | Curries | Mains | Daal | 5 |
| Mains | Curries | Mains | Main (Curries) | 41 |
| Mains | Dessert | Mains | Dessert | 3 |
| Mains | Rice | Mains | Main (Rice) | 16 |
| Mains | Starters | Mains | Main (Starter) | 36 |
| Snacks | Cold Beverages | Snacks | Cold Beverages | 12 |
| Snacks | Hot Beverages | Snacks | Hot Beverages | 3 |
| Snacks | Snacks | Snacks | Snacks | 56 |