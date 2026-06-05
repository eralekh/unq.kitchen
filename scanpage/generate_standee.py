#!/usr/bin/env python3
"""
UNQ Kitchen — A6 Standee  105 × 148 mm  (+3 mm bleed on all sides)
Print-ready: crop marks, CMYK-safe colours.
Font rule: BlippoMN for UNQ brand name only; all other text = Helvetica.
"""

import io, os, math
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image

# ── Paths ──────────────────────────────────────────────────────────────────
BASE         = os.path.dirname(os.path.abspath(__file__))
ASSETS       = os.path.join(BASE, '..', 'assets')
OUTPUT       = os.path.join(BASE, 'unq-kitchen-standee.pdf')
BLIPPO       = os.path.join(ASSETS, 'BlippoMN.ttf')
QR_IMG       = os.path.join(ASSETS, 'qr-scancode.png')
INSTA_IMG    = os.path.join(ASSETS, 'instagram-logo.png')
APP_IMG      = os.path.join(ASSETS, 'AppLogo.png')
PLAY_BTN_IMG = os.path.join(ASSETS, 'play-button-black.png')

# ── Colours ────────────────────────────────────────────────────────────────
INK        = HexColor('#1a1c12')
OLIVE      = HexColor('#7A8434')
OLIVE_MID  = HexColor('#5c6b28')
GOLD_LIGHT = HexColor('#e8a820')
CREAM      = HexColor('#f5f0e8')
CREAM_DARK = HexColor('#e9e3d6')
RULE_CLR   = HexColor('#ccc7b8')
MUTED      = HexColor('#9a9a8e')
FOOTER_CLR = HexColor('#b0ab9e')
WHITE      = HexColor('#ffffff')

# ── Canvas — A6 + 3 mm bleed ───────────────────────────────────────────────
W      = 105 * mm          # trim width
H      = 148 * mm          # trim height
BLEED  =   3 * mm
CW     = W + 2 * BLEED    # canvas 111 mm
CH     = H + 2 * BLEED    # canvas 154 mm
ML     =   5 * mm          # left / right margin inside bleed
CX     = BLEED + ML        # 8 mm — left content edge
CRX    = CW - BLEED - ML  # 103 mm — right content edge
CWIDTH = CRX - CX          # 95 mm usable width

pdfmetrics.registerFont(TTFont('Blippo', BLIPPO))


# ── Image helpers ──────────────────────────────────────────────────────────

def _to_reader(img: Image.Image) -> ImageReader:
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return ImageReader(buf)


def load_cropped(path: str):
    img = Image.open(path).convert('RGBA')
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    return _to_reader(img), img.width, img.height


def load_rgba(path: str) -> ImageReader:
    return _to_reader(Image.open(path).convert('RGBA'))


# ── Drawing primitives ─────────────────────────────────────────────────────

def rrect(c, x, y, w, h, r, fill=None, stroke=None, sw=1.0):
    c.saveState()
    if fill:   c.setFillColor(fill)
    if stroke: c.setStrokeColor(stroke); c.setLineWidth(sw)
    p = c.beginPath()
    p.moveTo(x + r, y);              p.lineTo(x + w - r, y)
    p.arcTo(x+w-2*r, y,         x+w, y+2*r,   startAng=-90, extent=90)
    p.lineTo(x + w, y + h - r)
    p.arcTo(x+w-2*r, y+h-2*r,   x+w, y+h,     startAng=0,   extent=90)
    p.lineTo(x + r, y + h)
    p.arcTo(x,       y+h-2*r, x+2*r, y+h,     startAng=90,  extent=90)
    p.lineTo(x, y + r)
    p.arcTo(x,       y,       x+2*r, y+2*r,   startAng=180, extent=90)
    p.close()
    c.drawPath(p, fill=1 if fill else 0, stroke=1 if stroke else 0)
    c.restoreState()


def draw_star(c, cx, cy, r, color):
    c.saveState()
    c.setFillColor(color)
    pts = [
        (cx + (r if i % 2 == 0 else r * 0.40) * math.cos(math.pi/2 + i*math.pi/5),
         cy + (r if i % 2 == 0 else r * 0.40) * math.sin(math.pi/2 + i*math.pi/5))
        for i in range(10)
    ]
    p = c.beginPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def hrule(c, y_pdf, pad=5*mm):
    """Horizontal rule — pad scaled for A6 narrower page."""
    c.saveState()
    c.setStrokeColor(RULE_CLR)
    c.setLineWidth(0.4)
    c.line(BLEED + pad, y_pdf, CW - BLEED - pad, y_pdf)
    c.restoreState()


def draw_crop_marks(c):
    c.saveState()
    c.setStrokeColor(HexColor('#000000'))
    c.setLineWidth(0.35)
    gap, arm = BLEED + 1.5*mm, 5*mm
    for hx, hy, dx, dy in [
        (BLEED,     BLEED + H, -1, +1),
        (BLEED + W, BLEED + H, +1, +1),
        (BLEED,     BLEED,     -1, -1),
        (BLEED + W, BLEED,     +1, -1),
    ]:
        c.line(hx + dx*gap, hy, hx + dx*(gap+arm), hy)
        c.line(hx, hy + dy*gap, hx, hy + dy*(gap+arm))
    c.restoreState()


# ── Footer zone (reserved first — panel must end above this) ───────────────
FOOTER_H       = 12 * mm
BOTTOM_PAD     =  3 * mm
FOOTER_RULE_GAP = 1.5 * mm
PANEL_FLOOR_GAP = 2 * mm

# ── QR scan frame — scaled for A6 ─────────────────────────────────────────
QR_SIZE   = 48 * mm
FRAME_PAD =  2.5 * mm
FRAME_W   = QR_SIZE + 2 * FRAME_PAD   # 53 mm
FRAME_X   = (CW - FRAME_W) / 2
ARM       =  7 * mm
BWIDTH    =  2.0


def draw_brackets(c, fx, fy, fw, fh):
    c.saveState()
    c.setStrokeColor(INK)
    c.setLineWidth(BWIDTH)
    c.setLineCap(1)
    for x0, y0, x1, y1 in [
        (fx,     fy+fh, fx+ARM,   fy+fh),
        (fx,     fy+fh, fx,       fy+fh-ARM),
        (fx+fw,  fy+fh, fx+fw-ARM,fy+fh),
        (fx+fw,  fy+fh, fx+fw,    fy+fh-ARM),
        (fx,     fy,    fx+ARM,   fy),
        (fx,     fy,    fx,       fy+ARM),
        (fx+fw,  fy,    fx+fw-ARM,fy),
        (fx+fw,  fy,    fx+fw,    fy+ARM),
    ]:
        c.line(x0, y0, x1, y1)
    c.restoreState()


# ── Main build ─────────────────────────────────────────────────────────────

def footer_zone():
    """Fixed footer band anchored inside trim — panel must stay above this."""
    bot  = BLEED + BOTTOM_PAD
    top  = bot + FOOTER_H
    rule = top + FOOTER_RULE_GAP
    floor = rule + PANEL_FLOOR_GAP
    return bot, top, rule, floor


def build():
    app_r      = load_rgba(APP_IMG)
    insta_r    = load_rgba(INSTA_IMG)
    qr_r       = load_rgba(QR_IMG)
    play_btn_r = load_rgba(PLAY_BTN_IMG)
    PLAY_ASPECT = 722 / 217   # play-button-black.png pixel ratio
    footer_bot, footer_top, footer_rule_y, panel_floor = footer_zone()

    c = rl_canvas.Canvas(OUTPUT, pagesize=(CW, CH))

    # Background
    c.setFillColor(CREAM)
    c.rect(0, 0, CW, CH, fill=1, stroke=0)
    draw_crop_marks(c)

    cur = CH - BLEED   # 151 mm from canvas bottom

    # ════════════════════════════════════════════════════════════════════
    # 1. HEADLINE — "SCAN TO ORDER"   (no subtitle below)
    # ════════════════════════════════════════════════════════════════════
    cur -= 7 * mm   # top margin — keep headline clear of trim edge
    c.setFont('Helvetica-Bold', 20)
    c.setFillColor(INK)
    c.drawCentredString(CW / 2, cur, 'SCAN TO ORDER')
    cur -= 4.5 * mm

    # ════════════════════════════════════════════════════════════════════
    # 2. QR CODE — absolute hero
    # ════════════════════════════════════════════════════════════════════
    cur -= 2 * mm   # gap before frame
    frame_top = cur
    frame_bot = frame_top - FRAME_W

    draw_brackets(c, FRAME_X, frame_bot, FRAME_W, FRAME_W)
    c.drawImage(qr_r,
                FRAME_X + FRAME_PAD, frame_bot + FRAME_PAD,
                width=QR_SIZE, height=QR_SIZE,
                preserveAspectRatio=True, mask='auto')
    cur = frame_bot

    # ════════════════════════════════════════════════════════════════════
    # 3. GOOGLE RATING CTA
    # ════════════════════════════════════════════════════════════════════
    cur -= 2.5 * mm
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(OLIVE)
    c.drawCentredString(CW / 2, cur, 'Loved the experience?')
    cur -= 3 * mm

    c.setFont('Helvetica', 8)
    c.setFillColor(INK)
    c.drawCentredString(CW / 2, cur, 'Please rate us on Google')
    cur -= 2.5 * mm

    n, sr, sg = 5, 2.2 * mm, 1.0 * mm
    star_cx0 = CW / 2 - (n * 2 * sr + (n - 1) * sg) / 2 + sr
    for i in range(n):
        draw_star(c, star_cx0 + i * (2*sr + sg), cur - sr, sr, GOLD_LIGHT)
    cur -= 2 * sr + 2 * mm

    hrule(c, cur)

    # ════════════════════════════════════════════════════════════════════
    # 4–6. ACTIONS PANEL — must end at or above panel_floor
    # ════════════════════════════════════════════════════════════════════
    ROW_GAP = 1 * mm
    cur -= 1 * mm

    # ── Row 1: Download ────────────────────────────────────────────────
    ASIZE    = 8 * mm
    BTN_H_DL =  9 * mm
    BTN_W_DL = BTN_H_DL * PLAY_ASPECT
    ROW_H_DL = 10 * mm

    row_bot = cur - ROW_H_DL
    row_mid = row_bot + ROW_H_DL / 2

    c.drawImage(app_r, CX, row_mid - ASIZE / 2,
                width=ASIZE, height=ASIZE,
                preserveAspectRatio=True, mask='auto')

    txt_x = CX + ASIZE + 2.5 * mm
    c.setFont('Helvetica', 7)
    c.setFillColor(MUTED)
    c.drawString(txt_x, row_mid + 2.2 * mm, 'Download our App')
    c.setFont('Helvetica-Bold', 11)
    c.setFillColor(OLIVE)
    c.drawString(txt_x, row_mid - 3.2 * mm, 'Order Online')

    c.drawImage(play_btn_r,
                CRX - BTN_W_DL, row_mid - BTN_H_DL / 2,
                width=BTN_W_DL, height=BTN_H_DL,
                preserveAspectRatio=True, mask='auto')

    cur = row_bot - ROW_GAP

    # ── Row 2: Instagram ─────────────────────────────────────────────
    IGSIZE = 7.5 * mm
    ig_bot = cur - IGSIZE
    ig_ctr = ig_bot + IGSIZE / 2

    c.drawImage(insta_r, CX, ig_bot,
                width=IGSIZE, height=IGSIZE,
                preserveAspectRatio=True, mask='auto')

    c.setFont('Helvetica-Bold', 8.5)
    c.setFillColor(INK)
    c.drawString(CX + IGSIZE + 2.5 * mm, ig_ctr - 1.1 * mm,
                 'Follow us on Instagram')

    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(OLIVE)
    handle_w = c.stringWidth('@unqkitchen', 'Helvetica-Bold', 10)
    c.drawString(CRX - handle_w, ig_ctr - 1.35 * mm, '@unqkitchen')

    cur = ig_bot - ROW_GAP

    # ── Row 3: Explore grid (height capped to panel_floor) ─────────────
    # Label removed per request; keep a small top pad before cards.
    GRID_TOP_PAD = 2.0 * mm
    grid_top = cur - GRID_TOP_PAD

    CARD_W   = (CWIDTH - 4 * mm) / 2
    CARD_GAP =  4 * mm
    GRID_GAP =  1.5 * mm
    CARD_H   = (grid_top - panel_floor - GRID_GAP) / 2
    if CARD_H < 7 * mm:
        raise RuntimeError(
            f'Layout overflow: grid cards would be {CARD_H/mm:.1f} mm '
            f'(need >= 7 mm). panel_floor={panel_floor/mm:.1f} mm'
        )

    items = [
        'BOOK EVENTS',
        'EXPLORE MENU',
        'GIVE FEEDBACK',
        'DISCOVER MORE',
    ]

    for idx, hero_txt in enumerate(items):
        row = idx // 2
        col = idx % 2
        cx  = CX + col * (CARD_W + CARD_GAP)
        cy  = grid_top - row * (CARD_H + GRID_GAP) - CARD_H

        rrect(c, cx, cy, CARD_W, CARD_H, r=2.5 * mm,
              fill=WHITE, stroke=OLIVE_MID, sw=0.8)

        c.setFont('Helvetica-Bold', 9)
        c.setFillColor(INK)
        c.drawCentredString(cx + CARD_W / 2, cy + CARD_H / 2 - 1.4 * mm, hero_txt)

    grid_bot = grid_top - 2 * CARD_H - GRID_GAP
    if grid_bot < panel_floor - 0.5 * mm:
        raise RuntimeError(
            f'Layout overlap: grid bottom {grid_bot/mm:.1f} mm '
            f'below panel floor {panel_floor/mm:.1f} mm'
        )

    # ════════════════════════════════════════════════════════════════════
    # 7. FOOTER — UNQ (Blippo) | divider | website + phone (2 rows)
    # ════════════════════════════════════════════════════════════════════
    footer_ctr = footer_bot + FOOTER_H / 2
    hrule(c, footer_rule_y)

    # "unq" wordmark — BlippoMN, drawn not pasted
    UNQ_SIZE = 24
    c.setFont('Blippo', UNQ_SIZE)
    c.setFillColor(INK)
    c.drawString(CX, footer_ctr - 2.2 * mm, 'UNQ')

    div_x = CW / 2
    c.saveState()
    c.setStrokeColor(RULE_CLR)
    c.setLineWidth(0.6)
    c.line(div_x, footer_bot + 2 * mm, div_x, footer_top - 2 * mm)
    c.restoreState()

    # Line 2 anchored from footer bottom — guarantees full visibility in print
    txt_x   = div_x + 3.5 * mm
    line2_y = footer_bot + 3 * mm
    line1_y = line2_y + 4.5 * mm

    c.setFont('Helvetica-Bold', 8)
    c.setFillColor(INK)
    c.drawString(txt_x, line1_y, 'Website : unq.kitchen')
    c.drawString(txt_x, line2_y, 'Ph: 70 300 70 800')

    c.save()
    print(f'Saved → {OUTPUT}')
    print(f'Canvas: {CW/mm:.1f} × {CH/mm:.1f} mm  '
          f'(trim {W/mm:.0f} × {H/mm:.0f} mm, bleed {BLEED/mm:.0f} mm)')
    print(f'Layout: grid_bot={grid_bot/mm:.1f} mm  panel_floor={panel_floor/mm:.1f} mm  '
          f'gap={(grid_bot - panel_floor)/mm:.1f} mm')


if __name__ == '__main__':
    build()
