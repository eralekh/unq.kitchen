# Folder restructure — proposal (needs your approval)

*2026-06-03. Nothing is moved or deleted until you approve. Principle: published URLs stay the same, generated files are separated from the source of truth, and the old editor is **archived, not deleted**.*

## Proposed layout (URL-stable)

```
unq-kitchen-site/
  data/
    data.json              ← SINGLE SOURCE OF TRUTH (v2)        [already created]
  tools/
    build.py               ← generator engine (all outputs)     [already created]
  assets/                  ← shared fonts + crest                [unchanged]
  menu/
    index.html             ← PRINT menu (will become generated)
    assets/ mains/ snacks/ xlsx/ …  ← food images + source sheets [unchanged]
  digital-menu/index.html  ← generated
  package/index.html       ← PRINT package (will become generated)
  digital-package/index.html ← NEW output                       [already created]
  editor/                  ← the one 3-mode editor + helper app  [Phase 3+]
  docs/                    ← all plans, schema, reports, help
  archive/
    menu-editor/           ← retired old editor (kept intact)
```

## Action list

| Current file/folder | Action | Why |
|---|---|---|
| `data/data.json`, `tools/build.py`, `digital-package/` | **keep** (new) | the new pipeline |
| `assets/` | keep | shared fonts + crest |
| `menu/index.html`, `package/index.html`, `digital-menu/index.html` | keep — become **generated** | published URLs unchanged |
| `menu/assets`, `mains`, `snacks`, `bookends`, `xlsx` | keep | food images + source spreadsheets |
| `menu-editor/index.html` | **move → `archive/`** | replaced by `editor/` (Phase 3) |
| `menu-editor/data.json` | **move → `archive/`** | superseded by `data/data.json` (kept as backup) |
| `menu-editor/rebuild.py` | **delete** | superseded by `tools/build.py` |
| `menu-editor/template.html` | **move → `tools/`** | becomes the print-package template |
| `menu-editor/help.html` | **move → `docs/`** | documentation |
| `2026-06-0*.md` (plans, schema, reports) | **move → `docs/`** | tidy the root |
| `digital-menu/index.generated.html` | preview only | replaces `digital-menu/index.html` once you OK how it looks |

## What I'll run on approval

1. Create `docs/` and `archive/`.
2. Move `menu-editor/` into `archive/` (intact), then lift `help.html` → `docs/`, `template.html` → `tools/`.
3. Move the dated `.md` docs into `docs/`.
4. Delete only `menu-editor/rebuild.py` (fully superseded). Everything else is moved, not deleted.

The only outright **delete** is `rebuild.py`. If you'd rather archive that too, say so and I'll keep it.
