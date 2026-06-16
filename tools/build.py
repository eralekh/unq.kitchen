#!/usr/bin/env python3
"""UNQ Kitchen — unified builder.
Reads data/data.json (single source of truth) and regenerates the output pages.
Currently generates the two digital outputs; print menu + package generators land next.
    python3 tools/build.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data', 'data.json')

def load():
    with open(DATA, encoding='utf-8') as f:
        return json.load(f)

def price_str(p):
    return '' if p is None else f'₹{p}'

def with_tags(name, tags):
    s = name or ''
    if tags and 'spicy' in tags: s += '\U0001F336️'
    if tags and 'sweet' in tags: s += '\U0001F36C'
    return s

def safe(payload):
    return json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')

# ---- package display names: derive from catalog instead of hand-typed strings ----
def _build_catalog_index(d):
    """itemId -> {'item': item, 'variants': {variantId: variant}}"""
    idx = {}
    for it in d['menu']['items']:
        idx[it['id']] = {'item': it, 'variants': {v['id']: v for v in it.get('variants', [])}}
    return idx

def _ref_names(ref, catalog):
    entry = catalog.get(ref.get('itemId'))
    if not entry:
        return None
    item_name = entry['item'].get('name')
    variant = entry['variants'].get(ref.get('variantId'))
    variant_name = variant.get('name') if variant else None
    return item_name, variant_name

def group_section_items(items, catalog):
    """Turn a section's `items` list into render units, deriving names from
    the catalog instead of relying on hand-typed `displayName`.

    Consecutive items that are single-ref variants of the SAME catalog item
    (e.g. Tea – Masala, Tea – Black, Tea – Lemon) are collapsed into one
    'group' unit: a label (the item name, e.g. "Tea") plus one option per
    variant (e.g. "Masala", "Black", "Lemon") — each option becomes its own
    selectable checkbox/chip, but the item name is shown only once.

    Returns a list of:
      {'kind':'single', 'name':..., 'note':..., 'badge':...}
      {'kind':'group', 'label':..., 'options':[{'name':...,'note':...,'badge':...}, ...]}

    Multi-ref combo items (e.g. "Tea / Coffee") keep their curated
    `displayName` as-is, since that phrasing is hand-picked, not derivable."""
    out = []
    i, n = 0, len(items)
    while i < n:
        it = items[i]
        refs = it.get('refs') or []
        names = _ref_names(refs[0], catalog) if len(refs) == 1 else None
        if names and names[1]:
            item_name, variant_name = names
            group = [{'name': variant_name, 'note': it.get('note'), 'badge': it.get('badge')}]
            j = i + 1
            while j < n:
                refs2 = items[j].get('refs') or []
                names2 = _ref_names(refs2[0], catalog) if len(refs2) == 1 else None
                if names2 and names2[1] and refs2[0].get('itemId') == refs[0].get('itemId'):
                    group.append({'name': names2[1], 'note': items[j].get('note'), 'badge': items[j].get('badge')})
                    j += 1
                    continue
                break
            out.append({'kind': 'group', 'label': item_name, 'options': group})
            i = j
            continue
        if names:
            out.append({'kind': 'single', 'name': names[0], 'note': it.get('note'), 'badge': it.get('badge')})
        else:
            out.append({'kind': 'single', 'name': it.get('displayName') or '', 'note': it.get('note'), 'badge': it.get('badge')})
        i += 1
    return out

# ---- v2 -> digital-menu SECTIONS shape ----
def v2_to_sections(d, img_prefix='../', settings=None):
    s = settings or {}
    show_img = s.get('showImages', True)
    show_ing = s.get('showIngredients', True)
    hidden = set(s.get('hidden') or [])
    cats_by_id = {c['id']: c for c in d['menu']['categories']}
    order = [cid for cid in (s.get('categoryOrder') or []) if cid in cats_by_id]
    for c in d['menu']['categories']:
        if c['id'] not in order:
            order.append(c['id'])
    groups = {g['id']: g['name'] for g in d['menu']['groups']}
    by_cat = {}
    for it in d['menu']['items']:
        by_cat.setdefault(it['categoryId'], []).append(it)
    sections = []
    for cid in order:
        c = cats_by_id.get(cid)
        if not c or cid == 'live-counters' or cid in hidden:
            continue
        items = []
        for it in by_cat.get(cid, []):
            if it.get('showOnDigital') is False:
                continue
            obj = {'name': with_tags(it['name'], it.get('tags')),
                   'desc': it.get('desc', ''),
                   'img': (img_prefix + it['img']) if (show_img and it.get('img')) else '',
                   'price': price_str(it.get('price')),
                   'variants': []}
            for v in it.get('variants', []):
                obj['variants'].append({'name': with_tags(v['name'], v.get('tags')),
                                        'ing': (v.get('ing', '') if show_ing else ''),
                                        'price': price_str(v.get('price'))})
            items.append(obj)
        if items:
            sections.append({'group': groups.get(c['groupId'], ''),
                             'category': c['name'], 'sub': c.get('sub', ''),
                             'items': items})
    return sections

def gen_digital_menu(d):
    s = (d.get('presentation') or {}).get('digitalMenu') or {}
    src = open(os.path.join(ROOT, 'digital-menu', 'index.html'), encoding='utf-8').read()
    secs = v2_to_sections(d, '../', s)
    payload = safe(secs)
    out, replaced = [], False
    for line in src.splitlines():
        if 'const SECTIONS' in line and not replaced:
            indent = line[:len(line) - len(line.lstrip())]
            out.append(f'{indent}const SECTIONS = {payload};')
            replaced = True
        else:
            out.append(line)
    res = '\n'.join(out)
    res = re.sub(r'<style id="l3">.*?</style>\n?', '', res, flags=re.S)
    if s.get('search', True) is False:
        res = res.replace('</head>', '<style id="l3">.searchbar{display:none}</style>\n</head>', 1)
    path = os.path.join(ROOT, 'digital-menu', 'index.html')
    open(path, 'w', encoding='utf-8').write(res)
    return path, len(secs), sum(len(x['items']) for x in secs)

# ---- new digital package page ----
PKG_TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0" />
<title>UNQ Kitchen — Event Packages</title>
<meta name="theme-color" content="#7A8434" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
<style>
@font-face{font-family:'BlippoMN';src:url('../assets/BlippoMN.ttf') format('truetype');font-display:swap;}
:root{--olive:#7A8434;--olive-dark:#5C6330;--ink:#14160C;--gold:#c9a96a;--paper:#fff;--paper-2:#faf9f3;--line:rgba(122,132,52,.18);--muted:rgba(20,22,12,.6);--veg:#2E7D32;}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
body{font-family:'Inter',sans-serif;background:var(--paper);color:var(--ink);line-height:1.5;padding-bottom:64px;}
header.top{background:var(--paper-2);border-bottom:1px solid var(--line);text-align:center;padding:18px 16px 14px;}
.crest{width:124px;height:50px;margin:0 auto;background-color:var(--olive-dark);-webkit-mask:url('../assets/crest.png') center/contain no-repeat;mask:url('../assets/crest.png') center/contain no-repeat;}
.kitchen{font-family:'BlippoMN','Cormorant Garamond',serif;font-size:1rem;letter-spacing:.3em;text-transform:uppercase;color:var(--olive);padding-left:.3em;margin-top:2px;}
.tagline{font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-top:8px;}
nav.pnav{position:sticky;top:0;z-index:20;background:var(--paper);border-bottom:1px solid var(--line);display:flex;gap:8px;overflow-x:auto;padding:10px 14px;scrollbar-width:none;}
nav.pnav::-webkit-scrollbar{display:none;}
nav.pnav button{flex:0 0 auto;border:1px solid var(--line);background:var(--paper-2);color:var(--olive-dark);border-radius:999px;padding:7px 14px;font-size:.78rem;font-weight:600;white-space:nowrap;cursor:pointer;font-family:inherit;}
nav.pnav button.active{background:var(--olive);color:#fff;border-color:var(--olive);}
main{max-width:760px;margin:0 auto;padding:0 14px;}
.pkg{scroll-margin-top:70px;padding:26px 0 8px;border-bottom:1px solid var(--line);}
.pkg-head{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;}
.pkg-name{font-family:'Cormorant Garamond',serif;font-size:1.7rem;font-weight:600;color:var(--olive-dark);}
.pkg-price{flex:0 0 auto;text-align:right;}
.pkg-price b{font-size:1.4rem;color:var(--ink);}
.pkg-price span{display:block;font-size:.66rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);}
.pkg-desc{font-size:.9rem;color:var(--muted);margin-top:6px;}
.ideal{display:inline-block;margin-top:10px;font-size:.74rem;background:rgba(122,132,52,.08);border:1px solid var(--line);border-radius:8px;padding:6px 10px;color:var(--olive-dark);}
.ideal b{color:var(--ink);}
.sec{margin-top:18px;}
.sec-h{display:flex;align-items:center;gap:6px;flex-wrap:wrap;}
.sec-name{font-family:'Cormorant Garamond',serif;font-size:1.35rem;font-weight:700;color:var(--ink);margin-right:4px;}
.sec-chip{font-size:.74rem;font-weight:600;letter-spacing:.02em;color:#5C6330;background:rgba(122,132,52,.08);border:1px solid rgba(122,132,52,.25);border-radius:20px;padding:3px 11px;}
.sec-inst{font-size:.74rem;font-weight:600;letter-spacing:.02em;color:#5C6330;background:rgba(122,132,52,.08);border:1px solid rgba(122,132,52,.25);border-radius:20px;padding:3px 11px;}
.items{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;}
.chip{font-size:.84rem;background:var(--paper-2);border:1px solid var(--line);border-radius:8px;padding:7px 11px;}
.chip .badge{display:inline-block;margin-left:6px;font-size:.62rem;letter-spacing:.06em;text-transform:uppercase;color:var(--gold);}
.chip .note{display:block;font-size:.7rem;color:var(--muted);}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:8px 18px;margin-top:14px;background:var(--paper-2);border:1px solid var(--line);border-radius:10px;padding:12px 14px;}
.grid .k{font-size:.66rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);}
.grid .v{font-size:.9rem;font-weight:600;color:var(--ink);}
.note-gold{margin-top:12px;font-size:.8rem;color:var(--olive-dark);background:rgba(201,169,106,.12);border-left:3px solid var(--gold);border-radius:4px;padding:8px 12px;}
.block-h{font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin:18px 0 6px;}
.terms{list-style:none;display:flex;flex-direction:column;gap:5px;}
.terms li{position:relative;padding-left:16px;font-size:.8rem;color:var(--muted);}
.terms li:before{content:'\2022';position:absolute;left:2px;color:var(--olive);}
.cancel{width:100%;border-collapse:collapse;margin-top:4px;font-size:.8rem;}
.cancel td{padding:6px 8px;border-bottom:1px solid var(--line);}
.cancel td:last-child{text-align:right;font-weight:600;color:var(--olive-dark);}
footer.foot{background:var(--ink);color:#f5f0e6;text-align:center;padding:30px 16px;margin-top:8px;}
footer.foot .fk{font-family:'BlippoMN','Cormorant Garamond',serif;letter-spacing:.28em;text-transform:uppercase;color:var(--gold);padding-left:.28em;}
footer.foot p{font-size:.8rem;opacity:.85;margin-top:8px;}
footer.foot a{color:var(--gold);text-decoration:none;}
.backhome{display:inline-block;margin-top:14px;font-size:.78rem;color:var(--gold);text-decoration:none;border:1px solid rgba(201,169,106,.5);border-radius:8px;padding:7px 16px;}
</style>
</head>
<body>
<header class="top">
  <div class="crest" role="img" aria-label="UNQ"></div>
  <div class="kitchen">Kitchen</div>
  <div class="tagline">Event Packages &middot; Fully Managed &middot; Bilaspur</div>
</header>
<nav class="pnav" id="pnav" aria-label="Packages"></nav>
<main id="packages"></main>
<footer class="foot">
  <div class="fk">UNQ Kitchen</div>
  <p>Open Every Day &middot; 8:00 AM – 10:30 PM</p>
  <p>Khamtarai, Baima Nagoi Road, Sarkanda, Bilaspur, CG</p>
  <p><a href="tel:+917030070800">+91 70300 70800</a></p>
  <a class="backhome" href="../">&larr; Back to home</a>
</footer>
<script>
const DATA = __DATA_JSON__;
const esc = s => (s==null?'':String(s)).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const SET = __SET__;
let pkgs = DATA.packages || [];
if(SET.packageOrder && SET.packageOrder.length){const ord=SET.packageOrder;pkgs=ord.map(id=>pkgs.find(p=>p.id===id)).filter(Boolean).concat(pkgs.filter(p=>!ord.includes(p.id)));}
const nav = document.getElementById('pnav');
const root = document.getElementById('packages');
pkgs.forEach((p,i)=>{
  const b=document.createElement('button'); b.textContent=p.name;
  b.onclick=()=>document.getElementById('pkg-'+i).scrollIntoView({behavior:'smooth',block:'start'});
  nav.appendChild(b);
});
pkgs.forEach((p,i)=>root.appendChild(renderPkg(p,i)));
function renderPkg(p,i){
  const s=document.createElement('section'); s.className='pkg'; s.id='pkg-'+i;
  let h='<div class="pkg-head"><div><div class="pkg-name">'+esc(p.name)+'</div>'+
        (p.description?'<div class="pkg-desc">'+esc(p.description)+'</div>':'')+'</div>'+
        '<div class="pkg-price"><b>₹'+esc(p.price)+'</b><span>per person</span></div></div>';
  if(p.idealValue) h+='<div class="ideal"><b>'+esc(p.idealLabel||'Ideal For')+':</b> '+esc(p.idealValue)+'</div>';
  (p.sections||[]).forEach(sec=>{
    h+='<div class="sec"><div class="sec-h"><span class="sec-name">'+esc(sec.name)+'</span>'+
       (sec.instruction?'<span class="sec-inst">'+esc(sec.instruction)+'</span>':'')+
       (sec.chip?'<span class="sec-chip">'+esc(sec.chip)+'</span>':'')+'</div>'+
       '<div class="items">';
    (sec.renderItems||[]).forEach(it=>{
      if(it.kind==='group'){
        const opts=it.options.map(o=>esc(o.name)+
          (o.badge?'<span class="badge">'+esc(o.badge)+'</span>':'')+
          (o.note?'<span class="note">'+esc(o.note)+'</span>':'')).join(' / ');
        h+='<div class="chip"><b>'+esc(it.label)+'</b> – '+opts+'</div>';
        return;
      }
      h+='<div class="chip">'+esc(it.name||'')+
         (it.badge?'<span class="badge">'+esc(it.badge)+'</span>':'')+
         (it.note?'<span class="note">'+esc(it.note)+'</span>':'')+'</div>';
    });
    h+='</div></div>';
  });
  if(SET.showBooking!==false && p.booking){
    h+='<div class="grid">';
    Object.keys(p.booking).forEach(k=>{h+='<div><div class="k">'+esc(k)+'</div><div class="v">'+esc(p.booking[k])+'</div></div>';});
    h+='</div>';
  }
  if(p.waterNote) h+='<div class="note-gold">'+esc(p.waterNote)+'</div>';
  if(SET.showTerms!==false && p.terms && p.terms.length){
    h+='<div class="block-h">Terms</div><ul class="terms">';
    p.terms.forEach(t=>h+='<li>'+t+'</li>');
    h+='</ul>';
  }
  if(SET.showCancellation!==false && p.cancellation && p.cancellation.length){
    h+='<div class="block-h">Cancellation</div><table class="cancel">';
    p.cancellation.forEach(r=>h+='<tr><td>'+esc(r.when)+'</td><td>'+esc(r.result)+'</td></tr>');
    h+='</table>';
  }
  s.innerHTML=h; return s;
}
const blocks=[...document.querySelectorAll('.pkg')], btns=[...nav.querySelectorAll('button')];
const obs=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){btns.forEach(b=>b.classList.remove('active'));const a=btns[blocks.indexOf(e.target)];if(a){a.classList.add('active');a.scrollIntoView({inline:'center',block:'nearest',behavior:'smooth'});}}}),{rootMargin:'-60px 0px -75% 0px'});
blocks.forEach(b=>obs.observe(b));
</script>
</body>
</html>'''

def gen_digital_package(d):
    sett = (d.get('presentation') or {}).get('digitalPackage') or {}
    catalog = _build_catalog_index(d)
    packages = json.loads(json.dumps(d['packages']))  # cheap deep copy
    for p in packages:
        for s in p.get('sections', []):
            s['renderItems'] = group_section_items(s.get('items', []), catalog)
    html = PKG_TEMPLATE.replace('__DATA_JSON__', safe({'packages': packages})).replace('__SET__', safe(sett))
    os.makedirs(os.path.join(ROOT, 'digital-package'), exist_ok=True)
    path = os.path.join(ROOT, 'digital-package', 'index.html')
    open(path, 'w', encoding='utf-8').write(html)
    return path, len(d['packages'])

# ---- print package (A4) ----
def t(s):
    return '' if s is None else str(s)

REFUND_CLASS = {'full refund': 'refund-full', '50% refund': 'refund-half', 'no refund': 'refund-none'}
def refund_cls(r):
    return REFUND_CLASS.get((r or '').strip().lower(), 'refund-full')

def _pkg_page(p, n, total, catalog):
    ideals = ''.join(f'<span class="ideal-tag">{t(x).strip()}</span>'
                     for x in t(p.get('idealValue')).split('·') if x.strip())
    secs = []
    for s in p.get('sections', []):
        ct = s.get('choiceType') or ''
        cls = 'section' + (f' choice-{ct}' if ct else '')
        banner_text = t(s.get('instruction'))
        if s.get('chip'):
            banner_text = (banner_text + '  ·  ' if banner_text else '') + t(s.get('chip'))
        banner_chips = ''
        if s.get('instruction'):
            banner_chips += f'<span class="inst-chip-b">{t(s.get("instruction"))}</span>'
        if s.get('chip'):
            banner_chips += f'<span class="qty-badge-b">{t(s.get("chip"))}</span>'
        def exc(it):
            tag = it.get('note') or it.get('badge')
            return f'<span class="item-exc-tag">{t(tag)}</span>' if tag else ''
        def chipbadge(it):
            tag = it.get('note') or it.get('badge')
            return f'<span class="chip-badge">{t(tag)}</span>' if tag else ''
        rendered = group_section_items(s.get('items', []), catalog)
        item_lines, chip_lines = [], []
        for r in rendered:
            if r['kind'] == 'group':
                opts = ''.join(f'<span class="item-group-opt">{t(o["name"])}{exc(o)}</span>' for o in r['options'])
                item_lines.append(f'        <div class="item-name item-group"><span class="item-group-label">{t(r["label"])}</span>{opts}</div>')
                copts = ''.join(f'<span class="chip-group-opt"><span class="chip-check"></span>{t(o["name"])}{chipbadge(o)}</span>' for o in r['options'])
                chip_lines.append(f'        <span class="chip-group"><span class="chip-group-label">{t(r["label"])}</span>{copts}</span>')
            else:
                item_lines.append('        <div class="item-name">' + t(r['name']) + exc(r) + '</div>')
                if ct in ('individual', 'party'):
                    chip_lines.append('        <span class="chip-choice"><span class="chip-check"></span>' +
                                       t(r['name']) + chipbadge(r) + '</span>')
                else:
                    chip_lines.append('        <span class="chip-fixed">' + t(r['name']) + chipbadge(r) + '</span>')
        items = '\n'.join(item_lines)
        chips = '\n'.join(chip_lines)
        secs.append(
f'''    <div class="{cls}">
      <div class="sec-head-b"><span class="sec-name-b">{t(s.get("name"))}</span><span class="sec-banner-b">{banner_chips}</span></div>
      <div class="col-cat"><div class="sec-name">{t(s.get("name"))}</div></div>
      <div class="col-items">
        <div class="sec-banner">{banner_text}</div>
{items}
      </div>
      <div class="sec-chips">
{chips}
      </div>
    </div>''')
    sections = '\n'.join(secs)
    booking = '\n'.join(f'      <div class="book-item"><div class="book-label">{t(k)}</div><div class="book-value">{t(v)}</div></div>'
                        for k, v in (p.get('booking') or {}).items())
    terms = '\n'.join(f'      <li>{t(x)}</li>' for x in (p.get('terms') or []))
    cancels = '\n'.join(f'      <div class="cancel-box"><div class="cancel-when">{t(c.get("when"))}</div><div class="cancel-result {refund_cls(c.get("result"))}">{t(c.get("result"))}</div></div>'
                        for c in (p.get('cancellation') or []))
    return f'''<div class="page">
  <div class="frame"><span class="fc tl"></span><span class="fc tr"></span><span class="fc bl"></span><span class="fc br"></span></div>
  <div class="content">
    <div class="pkg-hero">
      <div class="pkg-number"><span class="unq-logo">UNQ</span>'s Package {t(p.get("number"))}</div>
      <div class="pkg-title-row">
        <span class="pkg-name">{t(p.get("name"))}</span>
        <span class="pkg-at">@</span>
        <span class="pkg-price">&#x20B9;{t(p.get("price"))}<span class="per-person">/ Person</span></span>
      </div>
      <div class="pkg-desc">{t(p.get("description"))}</div>
    </div>
    <div class="ideal-row">{ideals}</div>
    <div class="pkg-table">
      <div class="table-header">
        <div class="col-cat th">Category</div>
        <div class="col-items th">Items</div>
      </div>
{sections}
    </div>
    <div class="water-note">&#9670; &nbsp;<strong>Note:</strong> {t(p.get("waterNote"))}</div>
    <div class="booking-strip">
{booking}
    </div>
  </div>
  <div class="booking-note">
    <div class="note-title">Terms &amp; Conditions</div>
    <ul class="note-list">
{terms}
    </ul>
    <div class="cancel-boxes">
{cancels}
    </div>
  </div>
  <div class="page-footer">
    <div class="footer-rule"></div>
    <div class="footer-text">UNQ Kitchen &nbsp;&middot;&nbsp; Nagoi Road, Khamtarai, Bilaspur C.G.</div>
    <div class="footer-rule"></div>
  </div>
  <div class="page-num">{n} of {total}</div>
</div>'''

def _venue_page(v, total):
    secs = []
    for s in v.get('sections', []):
        items = '\n'.join('          <div class="item-name">' + t(it.get('name')) +
                          (f'<span class="item-exc-tag">{t(it.get("note"))}</span>' if it.get('note') else '') +
                          '</div>' for it in s.get('items', []))
        secs.append(
f'''    <div class="section">
      <div class="col-cat"><div class="sec-name">{t(s.get("name"))}</div></div>
      <div class="col-inst"><div class="sec-inst">{t(s.get("instruction"))}</div></div>
      <div class="col-items">
{items}
      </div>
      <div class="col-chip"><span class="chip">{t(s.get("chip"))}</span></div>
    </div>''')
    sections = '\n'.join(secs)
    return f'''<div class="page">
  <div class="frame"><span class="fc tl"></span><span class="fc tr"></span><span class="fc bl"></span><span class="fc br"></span></div>
  <div class="watermark"><div class="wm-text">UNQ</div></div>
  <div class="content">
    <div class="pkg-hero">
      <div class="pkg-number"><span class="unq-logo">UNQ</span>'s Venue &amp; Services</div>
      <div class="pkg-title-row"><span class="pkg-name">Book Your Space</span></div>
      <div class="pkg-desc">{t(v.get("subtitle"))}</div>
    </div>
    <div class="pkg-table">
      <div class="table-header">
        <div class="col-cat th">Venue</div>
        <div class="col-items th">Available For</div>
      </div>
{sections}
    </div>
  </div>
  <div class="page-footer">
    <div class="footer-rule"></div>
    <div class="footer-text">UNQ Kitchen &nbsp;&middot;&nbsp; Nagoi Road, Khamtarai, Bilaspur C.G.</div>
    <div class="footer-rule"></div>
  </div>
  <div class="page-num">{total} of {total}</div>
</div>'''

def gen_print_package(d, preview=True):
    tmpl = open(os.path.join(ROOT, 'tools', 'template-print-package.html'), encoding='utf-8').read()
    total = len(d['packages']) + 1
    catalog = _build_catalog_index(d)
    pages = '\n'.join(_pkg_page(p, p.get('number'), total, catalog) for p in d['packages'])
    venue = _venue_page(d.get('venuePage', {}), total)
    html = tmpl.replace('{{PAGES}}', pages).replace('{{VENUE_PAGE}}', venue)
    name = 'index.generated.html' if preview else 'index.html'
    path = os.path.join(ROOT, 'package', name)
    open(path, 'w', encoding='utf-8').write(html)
    return path, total

# ---- print menu (A4) : sync catalog prices into the frozen hand-paginated layout ----
import html as _html
_EMOJI = re.compile(r'[\U0001F000-\U0001FAFF☀-➿←-⇿️]')
def _n(x):
    return re.sub(r'\s+', ' ', _EMOJI.sub('', _html.unescape(x or '')).replace('–', '-').replace('—', '-')).strip().lower()
def _txt(t):
    return _html.unescape(re.sub(r'<[^>]+>', '', t)).strip()
def _catprice(d):
    idx = {}
    for it in d['menu']['items']:
        if it.get('variants'):
            for v in it['variants']:
                idx[(_n(it['name']), _n(v['name']))] = v['price']
        else:
            idx[(_n(it['name']), _n(it['name']))] = it.get('price')
    return idx

def _patch_card_prices(card, idx, counter):
    nm = re.search(r'item-name">(.*?)</h3>', card, re.S) or re.search(r'item-name">([^<]+)', card)
    iname = _n(_txt(nm.group(1))) if nm else ''
    def repl(mrow):
        row = mrow.group(0)
        vn = re.search(r'v-name">(.*?)</span>', row, re.S)
        if not vn:
            return row
        key = (iname, _n(_txt(vn.group(1))))
        if key not in idx or idx[key] is None:
            return row
        newp = idx[key]
        def setp(z):
            cur = z.group(2)
            digits = re.findall(r'\d+', re.sub(r'&#\d+;|&#x[0-9a-fA-F]+;', '', cur))
            curval = int(''.join(digits)) if digits else None
            if curval == newp:          # already correct -> leave byte-for-byte untouched
                return z.group(0)
            prefix = '&#8377;' if '&#8377;' in cur else ('&#x20B9;' if '20B9' in cur.upper() else '₹')
            counter[0] += 1
            return z.group(1) + prefix + str(newp) + z.group(3)
        return re.sub(r'(v-price">)(.*?)(</span>)', setp, row, count=1, flags=re.S)
    return re.sub(r'<div class="variant-row">.*?</div>', repl, card, flags=re.S)

def _esc_html(s):
    return ('' if s is None else str(s)).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def _badges(tags):
    b = ''
    if tags and 'spicy' in tags: b += '<span class="chilli-badge" aria-label="spicy">🌶️</span>'
    if tags and 'sweet' in tags: b += '<span class="sweet-badge" aria-label="mildly sweet">🍬</span>'
    return b

def _print_card(it):
    if not it:
        return ''
    shape = it.get('printShape', 'shape-bowl')
    src = re.sub(r'^menu/', '', it.get('img', '') or '')
    rows = ''
    if it.get('variants'):
        for v in it['variants']:
            rows += ('<div class="variant-row"><span class="v-name">' + _esc_html(v['name']) + _badges(v.get('tags')) +
                     '</span><span class="v-ing">' + _esc_html(v.get('ing', '')) +
                     '</span><span class="v-price">₹' + str(v.get('price', '')) + '</span></div>')
    elif it.get('price') is not None:
        rows += ('<div class="variant-row"><span class="v-name">' + _esc_html(it['name']) +
                 '</span><span class="v-ing"></span><span class="v-price">₹' + str(it['price']) + '</span></div>')
    return ('<div class="menu-item"><div class="item-image"><img class="food-img ' + shape + '" src="' + src +
            '" alt="' + _esc_html(it['name']) + '" loading="lazy" referrerpolicy="no-referrer"></div>'
            '<div class="item-content"><div class="item-name-row"><h3 class="item-name">' + _esc_html(it['name']) +
            '</h3><div class="item-name-rule"></div></div><div class="item-description">' + _esc_html(it.get('desc', '')) +
            '</div><div class="variant-table">' + rows + '</div></div></div>')

def gen_print_menu(d):
    lf = os.path.join(ROOT, 'tools', 'print-layout.json')
    if not os.path.exists(lf):
        return None, 0, 0
    L = json.load(open(lf, encoding='utf-8'))
    idx = _catprice(d)
    items_by_id = {it['id']: it for it in d['menu']['items']}
    synced = [0]
    out = L['head']
    joiners = L.get('joiners', [])
    for k, p in enumerate(L['pages']):
        if p['kind'] == 'raw':
            out += p['html']
        else:
            parts = []
            for b in p['blocks']:
                if b['t'] != 'item':
                    parts.append(b['html'])
                elif b.get('gen'):
                    parts.append(_print_card(items_by_id.get(b.get('id'))))
                else:
                    parts.append(_patch_card_prices(b['html'], idx, synced))
            out += p['open'] + ''.join(parts) + p['close']
        if k < len(joiners):
            out += joiners[k]
    out += L['tail']
    path = os.path.join(ROOT, 'menu', 'index.html')
    open(path, 'w', encoding='utf-8').write(out)
    return path, len(L['pages']), synced[0]

if __name__ == '__main__':
    d = load()
    mp, nsec, nit = gen_digital_menu(d)
    pp, npk = gen_digital_package(d)
    rp, tot = gen_print_package(d, preview=False)
    mm2, npg, nsy = gen_print_menu(d)
    print(f'digital menu  -> {os.path.relpath(mp, ROOT)}  ({nsec} sections, {nit} items)')
    print(f'digital pkg   -> {os.path.relpath(pp, ROOT)}  ({npk} packages)')
    print(f'print pkg     -> {os.path.relpath(rp, ROOT)}  ({tot} pages)')
    if mm2:
        print(f'print menu    -> {os.path.relpath(mm2, ROOT)}  ({npg} pages, {nsy} prices synced)')
