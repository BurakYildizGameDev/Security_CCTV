"""
=============================================================================
Security CCTV Asset Production Suite - Asset 42
Asset Name: SEC_Access_Exit_Button (Kapi Cikis Butonu)
Texture Generation Script v1 (2048 x 2048)

ATLAS YERLESIMI (piksel):
    BANT-1 COVER  (32, 32)     - (1760, 1760)  1728 x 1728 -> 86 x 86 mm (20.09 px/mm)
    BANT-2 BUTTON (1790, 32)   - (2016, 258)    226 x  226 -> Ø44 aydinlatmali yuz
    BANT-3 RENK   (1790, 300)  - (2016, 1100)   duz renk alanlari

ON YUZ KURALI: +Y normaline bakan yuzler flip_u=True ile haritalanir; dunya +X
dokunun SOLUNA duser. cover_px() ayni eslemeyi kullanir.
=============================================================================
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")

FONT_MONO = r"C:\Windows\Fonts\consolab.ttf"
FONT_SANS = r"C:\Windows\Fonts\arialbd.ttf"

ATLAS_W, ATLAS_H = 2048, 2048

# ---------------------------------------------------------------- UV bantlari
REGION_COVER = (32, 32, 1760, 1760)          # 1728 x 1728 px -> 86.0 x 86.0 mm
REGION_BUTTON = (1790, 32, 2016, 258)        # 226 x 226 px -> dugme ust yuzu
REGION_DETAIL = (1790, 300, 2016, 1100)      # duz renk alanlari

# ---------------------------------------------------------------- Geometri esleme (m)
COVER_W, COVER_H = 0.0860, 0.0860            # Backplate on yuzu (86 x 86 mm)

BTN_R = 0.0220                               # Ø44 genis basmali dugme
COLLAR_R_IN, COLLAR_R_OUT = 0.0224, 0.0246   # ince cerceve (collar) halkasi
SCREW_X, SCREW_R = 0.0320, 0.0040            # iki vida basi

# Duz renk UV noktalari (piksel) - asagida swatch merkezlerinden hesaplanir
PIX_FLAT_BODY = (1890, 385)
PIX_FLAT_SIDE = (1890, 580)
PIX_FLAT_DARK = (1890, 775)
PIX_FLAT_METAL = (1890, 970)

# Renk Paleti (aile dili)
BODY_LIGHT = (243, 246, 250, 255)
BODY_MID = (228, 234, 242, 255)
BRUSH_LINE = (235, 240, 246, 255)
FRAME_LINE = (166, 177, 191, 255)
PLATE_DARK = (18, 22, 28, 255)
PLATE_DARK_2 = (30, 36, 44, 255)
AMBER = (226, 168, 32, 255)
INK_DARK = (18, 22, 28, 255)
INK_TEXT = (46, 54, 66, 255)
INK_SOFT = (98, 110, 124, 255)
WHITE = (255, 255, 255, 255)
COOL_LIGHT = (176, 196, 216, 255)
COOL_SOFT = (146, 168, 192, 255)
ALERT_RED = (196, 40, 32, 255)
GRAPHITE = (44, 50, 58, 255)
EXIT_GREEN = (48, 190, 110, 255)

_FONT_CACHE = {}
_TEXT_BOXES = []
_GRAPHIC_BOXES = []


def load_font(path, size):
    key = (path, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    try:
        f = ImageFont.truetype(path, size)
    except Exception:
        f = ImageFont.load_default()
    _FONT_CACHE[key] = f
    return f


def text_w(draw, text, font):
    try:
        return draw.textlength(text, font=font)
    except Exception:
        return draw.textlength(text)


def fit_font(draw, text, path, max_width, start_size, min_size=18):
    """Metin kutusuna tasmayacak en buyuk puntoyu secer (tasmasiz tipografi)."""
    size = start_size
    while size > min_size:
        f = load_font(path, size)
        if text_w(draw, text, f) <= max_width:
            return f
        size -= 2
    return load_font(path, min_size)


def _track_text(draw, x, y, text, font):
    """Tipografi QA: her metnin piksel kutusunu kaydeder."""
    if not text.strip():
        return
    try:
        l, t, r, b = draw.textbbox((0, 0), text, font=font)
    except Exception:
        return
    _TEXT_BOXES.append((x + l, y + t, x + r, y + b, text))


def draw_left(draw, x, y, text, font, fill):
    draw.text((x, y), text, font=font, fill=fill)
    _track_text(draw, x, y, text, font)


def draw_center(draw, cx, y, text, font, fill):
    x = cx - text_w(draw, text, font) / 2.0
    draw.text((x, y), text, font=font, fill=fill)
    _track_text(draw, x, y, text, font)


def track_rect(box, name):
    """Dekoratif bloklari cerceve QA'si icin kaydeder."""
    x0, y0, x1, y1 = box
    _GRAPHIC_BOXES.append((min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), name))


def ink_size(draw, text, font):
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    return (r - l, b - t)


def draw_left_ink(draw, x, ink_top, text, font, fill):
    """Sol kenari x'e, murekkep tepesi ink_top'a gelecek sekilde yazar."""
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    draw_left(draw, x - l, ink_top - t, text, font, fill)
    return (x, ink_top, x + (r - l), ink_top + (b - t))


def draw_center_ink(draw, cx, ink_top, text, font, fill):
    """Murekkep kutusunu yatayda cx'e gore ortalar."""
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    draw_left(draw, cx - (l + r) / 2.0, ink_top - t, text, font, fill)
    return (cx - (r - l) / 2.0, ink_top, cx + (r - l) / 2.0, ink_top + (b - t))


def draw_right_ink(draw, rx, ink_top, text, font, fill):
    """Sag kenari rx'e, murekkep tepesi ink_top'a gelecek sekilde yazar."""
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    tw = text_w(draw, text, font)
    draw_left(draw, rx - tw, ink_top - t, text, font, fill)
    return (rx - (r - l), ink_top, rx, ink_top + (b - t))


PX_PER_MM = (REGION_COVER[2] - REGION_COVER[0]) / (COVER_W * 1000.0)


def cover_px(x_m, z_m):
    """On yuzdeki (X, Z) konumunu atlas pikseline cevirir (flip_u=True eslemesi)."""
    x0, y0, x1, y1 = REGION_COVER
    nx = (x_m + COVER_W / 2.0) / COVER_W
    nz = (z_m + COVER_H / 2.0) / COVER_H
    return (x1 - nx * (x1 - x0), y1 - nz * (y1 - y0))


def verify_layout():
    """Metin kutularinin bant icinde kaldigini ve ust uste binmedigini dogrular."""
    regions = [REGION_COVER, REGION_BUTTON, REGION_DETAIL]
    problems = []
    for (tx0, ty0, tx1, ty1, txt) in _TEXT_BOXES:
        cx, cy = (tx0 + tx1) / 2.0, (ty0 + ty1) / 2.0
        rx0 = ry0 = rx1 = ry1 = None
        for (ax0, ay0, ax1, ay1) in regions:
            if ax0 <= cx <= ax1 and ay0 <= cy <= ay1:
                rx0, ry0, rx1, ry1 = ax0, ay0, ax1, ay1
                break
        if rx0 is None:
            problems.append(f"'{txt}' hicbir banda ait degil: {(tx0, ty0, tx1, ty1)}")
            continue
        if tx0 < rx0 + 6 or ty0 < ry0 + 4 or tx1 > rx1 - 6 or ty1 > ry1 - 4:
            problems.append(f"'{txt}' bant disina tasiyor: {(tx0, ty0, tx1, ty1)}")

    boxes = sorted(_TEXT_BOXES)
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            ax0, ay0, ax1, ay1, at = boxes[i]
            bx0, by0, bx1, by1, bt = boxes[j]
            ox = min(ax1, bx1) - max(ax0, bx0)
            oy = min(ay1, by1) - max(ay0, by0)
            if ox > 4 and oy > 4:
                problems.append(f"'{at}' ile '{bt}' ust uste biniyor ({ox:.0f} x {oy:.0f} px)")

    fx0 = REGION_COVER[0] + 40
    fy0 = REGION_COVER[1] + 40
    fx1 = REGION_COVER[2] - 40
    fy1 = REGION_COVER[3] - 40
    for (gx0, gy0, gx1, gy1, name) in _GRAPHIC_BOXES:
        if gx0 < fx0 or gy0 < fy0 or gx1 > fx1 or gy1 > fy1:
            problems.append(f"'{name}' sus cercevesini kesiyor: {(gx0, gy0, gx1, gy1)}")

    if problems:
        for p in problems:
            print("[LAYOUT-FAIL] " + p)
        raise AssertionError(f"Tipografi yerlesimi hatali: {len(problems)} sorun")
    print(f"[LAYOUT-OK] {len(_TEXT_BOXES)} metin blogu bant sinirlari icinde, cakisma yok")


def verify_sockets():
    """Cerceve (collar), dugme ve iki vidanin cakismadigini / yuz icinde kaldigini dogrular."""
    problems = []
    mm = PX_PER_MM
    cx0, cy0, cx1, cy1 = REGION_COVER

    bcx, bcy = cover_px(0.0, 0.0)
    r_out = COLLAR_R_OUT * 1000.0 * mm
    r_btn = BTN_R * 1000.0 * mm
    if (bcx - r_out < cx0 + 30 or bcy - r_out < cy0 + 30 or
            bcx + r_out > cx1 - 30 or bcy + r_out > cy1 - 30):
        problems.append("cerceve on yuz cercevesini asiyor")
    if COLLAR_R_IN <= BTN_R:
        problems.append(f"cerceve ic yaricapi dugmeyi kesiyor "
                        f"({COLLAR_R_IN*1000:.1f} <= {BTN_R*1000:.1f} mm)")

    for name, sx in (("Sol vida", -SCREW_X), ("Sag vida", +SCREW_X)):
        px, py = cover_px(sx, 0.0)
        r_sc = SCREW_R * 1000.0 * mm
        gap = math.hypot(px - bcx, py - bcy) - (r_out + r_sc)
        if gap < 12:
            problems.append(f"{name} cerceveye cok yakin (bosluk {gap:.0f} px)")
        if px - r_sc < cx0 + 24 or px + r_sc > cx1 - 24:
            problems.append(f"{name} yuz cercevesini asiyor")

    if problems:
        for p in problems:
            print("[SOCKET-FAIL] " + p)
        raise AssertionError(f"Yuva yerlesimi hatali: {len(problems)} sorun")
    print(f"[SOCKET-OK] cerceve Ø{COLLAR_R_OUT*2000:.1f} mm dugmeyi "
          f"(Ø{BTN_R*2000:.1f} mm) serbest birakiyor, iki vida cakismasiz")


def report_ink_heights():
    """En kucuk murekkep yuksekligini raporlar (render'da okunabilirlik tabani)."""
    if not _TEXT_BOXES:
        return
    heights = sorted((ty1 - ty0, txt) for (tx0, ty0, tx1, ty1, txt) in _TEXT_BOXES)
    print(f"[INK] En kucuk murekkep: {heights[0][0]:.0f} px "
          f"({heights[0][0] / PX_PER_MM:.2f} mm) -> '{heights[0][1]}'")
    print(f"[INK] En buyuk murekkep: {heights[-1][0]:.0f} px "
          f"({heights[-1][0] / PX_PER_MM:.2f} mm) -> '{heights[-1][1]}'")
    render_cover_px = (900.0 / 0.115) * COVER_W
    scale = render_cover_px / float(REGION_COVER[2] - REGION_COVER[0])
    print(f"[INK] Render'da kapak genisligi {render_cover_px:.1f} px "
          f"(olcek {scale:.4f}) -> en kucuk murekkep ~{heights[0][0] * scale:.1f} px, "
          f"en buyuk ~{heights[-1][0] * scale:.1f} px")


def draw_barcode(draw, x0, y0, width, height, dark=INK_DARK, light=WHITE):
    x = x0
    idx = 0
    while x < x0 + width:
        thick = 3 + (idx * 7) % 5
        col = dark if (idx % 3 == 0 or idx % 7 == 0) else light
        draw.line([(x, y0), (x, y0 + height)], fill=col, width=thick)
        x += 9
        idx += 1


# ---------------------------------------------------------------- BANT-1: On yuz
def draw_cover(draw):
    x0, y0, x1, y1 = REGION_COVER
    draw.rectangle([x0, y0, x1, y1], fill=BODY_LIGHT)

    # Fircalanmis govde mikro dokusu + cift sus cercevesi
    for yy in range(y0 + 4, y1, 9):
        draw.line([(x0, yy), (x1, yy)], fill=BRUSH_LINE)
    draw.rectangle([x0 + 16, y0 + 16, x1 - 16, y1 - 16], outline=FRAME_LINE, width=6)
    draw.rectangle([x0 + 40, y0 + 40, x1 - 40, y1 - 40],
                   outline=(210, 219, 230, 255), width=3)

    r_out = COLLAR_R_OUT * 1000.0 * PX_PER_MM
    r_sc = SCREW_R * 1000.0 * PX_PER_MM
    ccx, ccy = cover_px(0.0, 0.0)

    # --- Cerceve arkasi koyu cep ------------------------------------------
    # 3D cerceve (Frame_Ring) dugmeyi cevreler; cep cerceveden genis tutulur ki
    # egik bakista cerceve kaydiginda arkasinda hep koyu zemin kalsin.
    draw.ellipse([ccx - r_out + 6, ccy - r_out + 6,
                  ccx + r_out - 6, ccy + r_out - 6], fill=(14, 17, 22, 255))
    draw.ellipse([ccx - r_out + 10, ccy - r_out + 10,
                  ccx + r_out - 10, ccy + r_out - 10], fill=(8, 10, 14, 255))

    # --- Vida yuvalari -----------------------------------------------------
    for sx in (-SCREW_X, SCREW_X):
        px, py = cover_px(sx, 0.0)
        draw.ellipse([px - r_sc - 14, py - r_sc - 14,
                      px + r_sc + 14, py + r_sc + 14], fill=(20, 24, 30, 255))
        draw.ellipse([px - r_sc - 12, py - r_sc - 12,
                      px + r_sc + 12, py + r_sc + 12],
                     outline=(120, 132, 148, 255), width=3)

    # --- Ust marka plakasi -------------------------------------------------
    PT = (x0 + 64, 84, x1 - 64, 320)
    track_rect(PT, "Marka plakasi")
    draw.rectangle([PT[0], PT[1], PT[2], PT[3]], fill=PLATE_DARK,
                   outline=(78, 90, 104, 255), width=4)
    draw.rectangle([PT[0], PT[1], PT[0] + 18, PT[3]], fill=AMBER)

    LX = PT[0] + 52
    RX = PT[2] - 28
    f_t = fit_font(draw, "SEC-EB 1", FONT_SANS, 760, 96, 48)
    f_s = fit_font(draw, "EXIT BUTTON", FONT_MONO, RX - LX, 46, 24)
    f_tag = load_font(FONT_MONO, 30)
    th = ink_size(draw, "SEC-EB 1", f_t)[1]
    sh = ink_size(draw, "EXIT BUTTON", f_s)[1]
    gap = 26
    ty = PT[1] + (PT[3] - PT[1] - (th + sh + gap)) / 2.0
    bb = draw_left_ink(draw, LX, ty, "SEC-EB 1", f_t, WHITE)
    draw_right_ink(draw, RX, ty + 8, "IP54", f_tag, AMBER)
    draw_left_ink(draw, LX, bb[3] + gap, "EXIT BUTTON", f_s, COOL_LIGHT)

    # --- Alt yonlendirme ---------------------------------------------------
    f_p = fit_font(draw, "PUSH TO EXIT", FONT_SANS, 900, 84, 44)
    f_h = load_font(FONT_MONO, 34)
    bb = draw_center_ink(draw, ccx, 1440, "PUSH TO EXIT", f_p, INK_DARK)
    draw_center_ink(draw, ccx, bb[3] + 22, "MOMENTARY  -  NO / COM", f_h, INK_SOFT)

    # --- Alt kimlik satiri -------------------------------------------------
    f_sn = load_font(FONT_MONO, 30)
    draw_left_ink(draw, x0 + 64, 1616, "SN 42-EB-000451", f_sn, INK_SOFT)
    draw_right_ink(draw, x1 - 64, 1616, "CE  EN 61000-6-1", f_sn, INK_SOFT)
    draw_barcode(draw, x0 + 64, 1650, 300, 34,
                 dark=(150, 162, 178, 255), light=BODY_LIGHT)


# ---------------------------------------------------------------- BANT-2: Dugme
def draw_button_band(draw):
    """Aydinlatmali basma yuzu (M_Emission): yesil alan + EXIT yazisi."""
    x0, y0, x1, y1 = REGION_BUTTON
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = (x1 - x0) / 2.0
    draw.rectangle([x0, y0, x1, y1], fill=(12, 52, 30, 255))
    draw.ellipse([cx - r * 0.99, cy - r * 0.99, cx + r * 0.99, cy + r * 0.99],
                 fill=(34, 150, 86, 255), outline=(120, 240, 160, 255), width=8)
    draw.ellipse([cx - r * 0.84, cy - r * 0.84, cx + r * 0.84, cy + r * 0.84],
                 fill=(44, 178, 100, 255), outline=(96, 220, 140, 255), width=4)

    # EXIT yazisi (radyal UV duzlemsel oldugu icin metin bozulmaz)
    f = fit_font(draw, "EXIT", FONT_SANS, r * 1.20, int(r * 0.40), 20)
    hh = ink_size(draw, "EXIT", f)[1]
    draw_center_ink(draw, cx, cy - hh / 2.0 - r * 0.06, "EXIT", f, (245, 255, 248, 255))

    # Alt cikis oku (chevron + govde)
    ay = cy + r * 0.40
    draw.line([(cx - r * 0.34, ay), (cx + r * 0.06, ay)],
              fill=(228, 255, 238, 255), width=7)
    draw.line([(cx - r * 0.16, ay - r * 0.11), (cx + r * 0.06, ay)],
              fill=(228, 255, 238, 255), width=7)
    draw.line([(cx + r * 0.06, ay), (cx - r * 0.16, ay + r * 0.11)],
              fill=(228, 255, 238, 255), width=7)


# ---------------------------------------------------------------- BANT-3: Renk
def draw_detail(draw):
    x0, y0, x1, y1 = REGION_DETAIL
    draw.rectangle([x0, y0, x1, y1], fill=BODY_LIGHT)
    labels = (("BODY", BODY_LIGHT, INK_TEXT),
              ("SIDE", BODY_MID, INK_TEXT),
              ("DARK", PLATE_DARK_2, WHITE),
              ("METAL", (176, 186, 198, 255), INK_TEXT))
    for i, (lbl, col, ink) in enumerate(labels):
        sy = y0 + 10 + i * 195
        draw.rectangle([x0 + 12, sy, x0 + 192, sy + 150], fill=col,
                       outline=(132, 144, 158, 255), width=4)
        f = load_font(FONT_MONO, 26)
        draw_center_ink(draw, x0 + 102, sy + 158, lbl, f, ink)


def generate_textures():
    img = Image.new("RGB", (ATLAS_W, ATLAS_H), (128, 132, 140))
    draw = ImageDraw.Draw(img)

    draw_cover(draw)
    draw_button_band(draw)
    draw_detail(draw)

    verify_layout()
    verify_sockets()
    report_ink_heights()

    img.save(ATLAS_PATH, "PNG")
    print(f"[OK] Atlas kaydedildi: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")
    print(f"[OK] Cover: {COVER_W * 1000:.0f} x {COVER_H * 1000:.0f} mm -> "
          f"{REGION_COVER[2] - REGION_COVER[0]} x {REGION_COVER[3] - REGION_COVER[1]} px "
          f"({PX_PER_MM:.2f} px/mm)")
    print(f"[OK] Metin bloklari: {len(_TEXT_BOXES)}  |  dekoratif blok: {len(_GRAPHIC_BOXES)}")


if __name__ == "__main__":
    generate_textures()



