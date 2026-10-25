"""
=============================================================================
Security CCTV Asset Production Suite - Asset 39
Asset Name: SEC_Beam_Detector_Dual (Cift Isinli Bariyer Dedektoru)
Texture Generation Script v1 (2048 x 2048)

Output:
    - exports/T_Security_Atlas.png (2048 x 2048)

ATLAS YERLESIMI (piksel):
    BANT-1 COVER  (32, 32)    - (882, 2016)   850 x 1984 -> 36 x 84 mm (23.61 px/mm)
    BANT-2 LENS   (900, 32)   - (1400, 532)   500 x  500 -> optik pencere cami
    BANT-3 LED    (1420, 32)  - (1720, 332)   300 x  300 -> durum gostergesi
    BANT-4 RENK   (900, 560)  - (2016, 2016)  duz renk alanlari

ON YUZ KURALI: +Y normaline bakan yuzler flip_u=True ile haritalanir; dunya +X
dokunun SOLUNA duser. cover_px() ayni eslemeyi kullanir.

Dikey yuz bolgeleri (Z -> atlas y):
    +42..+31 mm  y 32..292    ust marka plakasi
    +17..-17 mm  y 622..1425  orta teknik panel (LED yuvasi burada)
    -31..-42 mm  y 1756..2016 alt uyari bandi
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
REGION_COVER = (32, 32, 882, 2016)          # 850 x 1984 px -> 36.0 x 84.0 mm
REGION_LENS = (900, 32, 1400, 532)          # 500 x 500 px  -> optik cam
REGION_LED = (1420, 32, 1720, 332)          # 300 x 300 px  -> durum lensi
REGION_DETAIL = (900, 560, 2016, 2016)      # duz renk alanlari

# ---------------------------------------------------------------- Geometri esleme (m)
COVER_W, COVER_H = 0.0360, 0.0840           # Detector_Housing on yuzu
WINDOW_X, WINDOW_Z = 0.0, 0.0240            # ust pencere merkezi (alt = -Z)
WINDOW_R = 0.0070                           # 3D pencere yaricapi (Ø14 mm)
GLASS_R = 0.0062                            # cam diski yaricapi (Ø12.4 mm)
LED_X, LED_Z = -0.0115, 0.0100              # izleyicinin saginda
LED_R = 0.0025                              # Ø5 mm

# Alt teknik panel ve ust marka plakasi (atlas piksel, bant yerel degil)
PANEL_TOP, PANEL_BOT = 670, 1380
PLATE_TOP, PLATE_BOT = 74, 250

# Duz renk UV noktalari (piksel)
PIX_FLAT_BODY = (980, 620)
PIX_FLAT_SIDE = (1200, 620)
PIX_FLAT_DARK = (1420, 620)
PIX_FLAT_WARN = (1640, 620)

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


def cover_px(x_m, z_m):
    """On yuzdeki (X, Z) metre konumunu atlas pikseline cevirir.

    flip_u=True eslemesiyle ayni: +Y normalli on yuzde dunya +X, dokunun
    soluna (kucuk u) karsilik gelir; bu yuzden x1'den geri sayilir.
    """
    x0, y0, x1, y1 = REGION_COVER
    nx = (x_m + COVER_W / 2.0) / COVER_W
    nz = (z_m + COVER_H / 2.0) / COVER_H
    return (x1 - nx * (x1 - x0), y1 - nz * (y1 - y0))


PX_PER_MM = (REGION_COVER[2] - REGION_COVER[0]) / (COVER_W * 1000.0)


def verify_layout():
    """Metin kutularinin bant icinde kaldigini ve ust uste binmedigini dogrular."""
    regions = [REGION_COVER, REGION_LENS, REGION_LED, REGION_DETAIL]
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

    # Dekoratif bloklar sus cercevesinin (x0+36 / y1-36) icine sigmali.
    fx0 = REGION_COVER[0] + 36
    fy0 = REGION_COVER[1] + 36
    fx1 = REGION_COVER[2] - 36
    fy1 = REGION_COVER[3] - 36
    for (gx0, gy0, gx1, gy1, name) in _GRAPHIC_BOXES:
        if gx0 < fx0 or gy0 < fy0 or gx1 > fx1 or gy1 > fy1:
            problems.append(f"'{name}' sus cercevesini kesiyor: {(gx0, gy0, gx1, gy1)}")

    if problems:
        for p in problems:
            print("[LAYOUT-FAIL] " + p)
        raise AssertionError(f"Tipografi yerlesimi hatali: {len(problems)} sorun")
    print(f"[LAYOUT-OK] {len(_TEXT_BOXES)} metin blogu bant sinirlari icinde, cakisma yok")


def verify_optics():
    """Iki pencere yuvasinin simetrisini ve LED'in cukurlarla cakismadigini dogrular.

    Pencere yuzdalari optik eksende (X=0) ve Z=+/-WINDOW_Z'de olmali; pivotun
    tam ortada kalabilmesi bu simetriye baglidir.
    """
    up = cover_px(WINDOW_X, WINDOW_Z)
    lo = cover_px(WINDOW_X, -WINDOW_Z)
    led = cover_px(LED_X, LED_Z)
    r_win = WINDOW_R * 1000.0 * PX_PER_MM
    r_led = LED_R * 1000.0 * PX_PER_MM
    problems = []
    center_y = (REGION_COVER[1] + REGION_COVER[3]) / 2.0
    if abs(up[0] - lo[0]) > 0.5:
        problems.append(f"pencereler ayni dikey eksende degil: x {up[0]:.1f} vs {lo[0]:.1f}")
    if not (up[1] < center_y - 200 and lo[1] > center_y + 200):
        problems.append(f"pencereler on yuz merkezine gore simetrik degil "
                        f"(y {up[1]:.0f} / {lo[1]:.0f}, merkez {center_y:.0f})")
    if abs((up[1] - center_y) + (lo[1] - center_y)) > 1.0:
        problems.append(f"pencere cifti merkezde aynalik degil "
                        f"({up[1] - center_y:+.1f} / {lo[1] - center_y:+.1f} px)")
    for label, c in (("ust", up), ("alt", lo)):
        d = math.hypot(led[0] - c[0], led[1] - c[1])
        if d < (r_win + r_led + 24):
            problems.append(f"LED ile {label} pencere cakismasi (d={d:.0f}px)")
    if not (PANEL_TOP < led[1] < PANEL_BOT):
        problems.append("LED yuvasi teknik panelin disinda")
    if problems:
        for p in problems:
            print("[OPTICS-FAIL] " + p)
        raise AssertionError(f"Optik yerlesim hatali: {len(problems)} sorun")
    print(f"[OPTICS-OK] pencereler simetrik (x={up[0]:.0f}), LED paneli icinde "
          f"({led[0]:.0f},{led[1]:.0f}), cakisma yok")


def report_ink_heights():
    """En kucuk murekkep yuksekligini raporlar (render'da okunabilirlik tabani)."""
    if not _TEXT_BOXES:
        return
    heights = sorted((ty1 - ty0, txt) for (tx0, ty0, tx1, ty1, txt) in _TEXT_BOXES)
    print(f"[INK] En kucuk murekkep: {heights[0][0]:.0f} px "
          f"({heights[0][0] / PX_PER_MM:.2f} mm) -> '{heights[0][1]}'")
    print(f"[INK] En buyuk murekkep: {heights[-1][0]:.0f} px "
          f"({heights[-1][0] / PX_PER_MM:.2f} mm) -> '{heights[-1][1]}'")
    # QA flat render olcegi: 900 px / 0.105 m ortho
    render_cover_px = (900.0 / 0.105) * COVER_W
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
    draw.rectangle([x0 + 12, y0 + 12, x1 - 12, y1 - 12], outline=FRAME_LINE, width=5)
    draw.rectangle([x0 + 24, y0 + 24, x1 - 24, y1 - 24], outline=(210, 219, 230, 255), width=3)

    r_win = WINDOW_R * 1000.0 * PX_PER_MM
    r_led = LED_R * 1000.0 * PX_PER_MM

    # --- Optik pencere yuvalari (ust / alt) --------------------------------
    # Cam diski 0.6 mm gomme oldugu icin yuva halkasi onu siki sarar; boylece
    # egik bakista cam yuvasindan kaymis gorunmez (varlik 38 parlak dersi).
    for sz in (WINDOW_Z, -WINDOW_Z):
        cx, cy = cover_px(WINDOW_X, sz)
        draw.ellipse([cx - r_win - 20, cy - r_win - 20,
                      cx + r_win + 20, cy + r_win + 20], fill=GRAPHITE)
        draw.ellipse([cx - r_win - 21, cy - r_win - 21,
                      cx + r_win + 21, cy + r_win + 21],
                     outline=(206, 216, 228, 255), width=3)
        draw.ellipse([cx - r_win + 2, cy - r_win + 2,
                      cx + r_win - 2, cy + r_win - 2], fill=(10, 13, 18, 255))

    # --- Ust marka plakasi -------------------------------------------------
    PT = (x0 + 44, PLATE_TOP, x1 - 44, PLATE_BOT)
    track_rect(PT, "Marka plakasi")
    draw.rectangle([PT[0], PT[1], PT[2], PT[3]], fill=PLATE_DARK,
                   outline=(78, 90, 104, 255), width=4)
    draw.rectangle([PT[0], PT[1], PT[0] + 16, PT[3]], fill=AMBER)

    LX = PT[0] + 44
    RX = PT[2] - 26
    f_title = fit_font(draw, "SEC-BD 220", FONT_SANS, 520, 76, 40)
    f_sub = fit_font(draw, "DUAL BEAM DETECTOR  TX / RX", FONT_MONO, RX - LX, 36, 22)
    th = ink_size(draw, "SEC-BD 220", f_title)[1]
    sh = ink_size(draw, "DUAL BEAM DETECTOR  TX / RX", f_sub)[1]
    gap = 22
    y = PT[1] + (PT[3] - PT[1] - (th + sh + gap)) / 2.0
    bb = draw_left_ink(draw, LX, y, "SEC-BD 220", f_title, WHITE)
    f_tag = load_font(FONT_MONO, 26)
    draw_right_ink(draw, RX, y + 6, "IP66", f_tag, AMBER)
    draw_left_ink(draw, LX, bb[3] + gap, "DUAL BEAM DETECTOR  TX / RX", f_sub, COOL_LIGHT)

    # --- Orta teknik panel -------------------------------------------------
    PN = (x0 + 44, PANEL_TOP, x1 - 44, PANEL_BOT)
    track_rect(PN, "Teknik panel")
    draw.rectangle([PN[0], PN[1], PN[2], PN[3]], fill=PLATE_DARK,
                   outline=(78, 90, 104, 255), width=4)
    draw.rectangle([PN[0] + 10, PN[1] + 10, PN[2] - 10, PN[3] - 10],
                   outline=(58, 68, 80, 255), width=3)

    TX = PN[0] + 36
    TR = PN[2] - 30
    COL_W = 470
    y = PN[1] + 26

    f_h = fit_font(draw, "INFRARED BEAM PAIR", FONT_SANS, COL_W, 52, 30)
    bb = draw_left_ink(draw, TX, y, "INFRARED BEAM PAIR", f_h, WHITE)
    y = bb[3] + 10
    draw.rectangle([TX, y, TX + COL_W, y + 3], fill=AMBER)
    y += 16

    f_row = load_font(FONT_MONO, 30)
    for txt in ("RANGE 0 - 60 m", "BEAM SPACING 48 mm", "WAVELENGTH 880 nm"):
        bb = draw_left_ink(draw, TX, y, txt, f_row, COOL_LIGHT)
        y = bb[3] + 12
    bb = draw_left_ink(draw, TX, y, "12-30 VDC   RELAY 100 mA", f_row, COOL_LIGHT)
    y = bb[3] + 18

    # Hizalama semasi: iki isin + dikey optik eksen (panel boslugunu doldurur)
    GX0, GY0 = TX, y + 6
    GX1, GY1 = TX + COL_W, y + 292
    track_rect((GX0, GY0, GX1, GY1), "Hizalama semasi")
    draw.rectangle([GX0, GY0, GX1, GY1], fill=(24, 30, 38, 255),
                   outline=(70, 80, 92, 255), width=3)
    mid = (GX0 + GX1) / 2.0
    # Kesik cizgi periyodu 34 px (1.44 mm): render olceginde 14 px'e duser, ince
    # desenler (13 px periyot) yeniden orneklemede aliasing yapip Korelasyonu bozar.
    for k in range(8):
        yy = GY0 + 16 + k * 34
        draw.line([(mid, yy), (mid, yy + 18)], fill=(110, 122, 136, 255), width=3)
    for beam_y in (GY0 + 40, GY1 - 40):
        draw.line([(GX0 + 26, beam_y), (mid - 14, beam_y)], fill=AMBER, width=7)
        draw.line([(mid + 14, beam_y), (GX1 - 26, beam_y)], fill=AMBER, width=7)
    draw.polygon([(GX1 - 40, GY0 + 28), (GX1 - 18, GY0 + 40), (GX1 - 40, GY0 + 52)],
                 fill=(226, 168, 32, 255))
    f_g = load_font(FONT_MONO, 26)
    draw_left_ink(draw, GX0 + 30, GY0 + 8, "TX", f_g, COOL_SOFT)
    draw_left_ink(draw, GX0 + 30, GY1 - 32, "RX", f_g, COOL_SOFT)

    # --- Durum gostergesi yuvasi (panel icinde, sag ust) -------------------
    lcx, lcy = cover_px(LED_X, LED_Z)
    draw.ellipse([lcx - r_led - 22, lcy - r_led - 22,
                  lcx + r_led + 22, lcy + r_led + 22],
                 fill=(16, 20, 26, 255), outline=(88, 96, 108, 255), width=4)
    draw.ellipse([lcx - r_led - 8, lcy - r_led - 8,
                  lcx + r_led + 8, lcy + r_led + 8],
                 fill=(26, 46, 32, 255), outline=(150, 160, 172, 255), width=3)
    f_st = load_font(FONT_MONO, 24)
    draw_center_ink(draw, lcx, lcy + r_led + 36, "STATUS", f_st, COOL_SOFT)

    # --- Seri no + barkod (panel sag alt) ----------------------------------
    f_sn = load_font(FONT_MONO, 26)
    sn_y = PN[3] - 60
    draw_barcode(draw, TR - 300, sn_y - 84, 300, 56,
                 dark=(238, 242, 247, 255), light=PLATE_DARK)
    draw_right_ink(draw, TR, sn_y, "SN 39-BD-000714", f_sn, COOL_SOFT)

    # --- Alt uyari bandi ---------------------------------------------------
    WB = (x0 + 44, 1800, x1 - 44, y1 - 48)
    track_rect(WB, "Uyari bandi")
    draw.rectangle([WB[0], WB[1], WB[2], WB[3]], fill=(252, 246, 232, 255),
                   outline=(196, 152, 44, 255), width=4)
    draw.rectangle([WB[0], WB[1], WB[0] + 14, WB[3]], fill=AMBER)
    draw.polygon([(WB[0] + 34, WB[1] + 20), (WB[0] + 62, WB[1] + 68),
                  (WB[0] + 6, WB[1] + 68)], fill=AMBER, outline=(150, 108, 12, 255))
    f_w = load_font(FONT_SANS, 34)
    draw_center(draw, WB[0] + 34, WB[1] + 28, "!", f_w, PLATE_DARK)
    draw_left_ink(draw, WB[0] + 86, WB[1] + 20, "DO NOT OBSTRUCT", f_w, ALERT_RED)
    draw_left_ink(draw, WB[0] + 86, WB[1] + 62, "OPTICAL PATH", f_w, ALERT_RED)
    f_c = load_font(FONT_MONO, 23)
    draw_right_ink(draw, WB[2] - 20, WB[3] - 32, "CE  EN 50131-2-4  RoHS", f_c, INK_TEXT)


# ---------------------------------------------------------------- BANT-2: Optik cam
def draw_lens_band(draw):
    """Optik pencere cami: koyu IR filtre + Fresnel halkalari + merkez parlamasi."""
    x0, y0, x1, y1 = REGION_LENS
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = (x1 - x0) / 2.0
    draw.rectangle([x0, y0, x1, y1], fill=(10, 16, 22, 255))
    for rr, col, wd in ((0.99, (120, 150, 178, 255), 8),
                        (0.90, (58, 82, 104, 255), 6),
                        (0.74, (40, 60, 80, 255), 5),
                        (0.56, (52, 76, 98, 255), 4),
                        (0.36, (34, 52, 70, 255), 3)):
        draw.ellipse([cx - r * rr, cy - r * rr, cx + r * rr, cy + r * rr],
                     outline=col, width=wd)
    # Merkez IR goz (koyu) ve cam parlamasi
    draw.ellipse([cx - r * 0.17, cy - r * 0.17, cx + r * 0.17, cy + r * 0.17],
                 fill=(8, 10, 14, 255), outline=(96, 122, 148, 255), width=4)
    draw.line([(cx - r * 0.52, cy - r * 0.52), (cx - r * 0.14, cy - r * 0.86)],
              fill=(150, 178, 204, 255), width=9)
    draw.line([(cx + r * 0.30, cy + r * 0.36), (cx + r * 0.62, cy + r * 0.06)],
              fill=(84, 110, 136, 255), width=6)


# ---------------------------------------------------------------- BANT-3: Durum lensi
def draw_led_band(draw):
    x0, y0, x1, y1 = REGION_LED
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = (x1 - x0) / 2.0
    draw.rectangle([x0, y0, x1, y1], fill=(12, 44, 26, 255))
    draw.ellipse([cx - r * 0.98, cy - r * 0.98, cx + r * 0.98, cy + r * 0.98],
                 fill=(34, 146, 80, 255), outline=(96, 220, 140, 255), width=8)
    draw.ellipse([cx - r * 0.58, cy - r * 0.58, cx + r * 0.58, cy + r * 0.58],
                 fill=(118, 238, 158, 255), outline=(150, 246, 180, 255), width=6)
    draw.ellipse([cx - r * 0.30, cy - r * 0.30, cx + r * 0.30, cy + r * 0.30],
                 fill=(140, 240, 170, 255))


# ---------------------------------------------------------------- BANT-4: Renk alanlari
def draw_detail(draw):
    x0, y0, x1, y1 = REGION_DETAIL
    draw.rectangle([x0, y0, x1, y1], fill=BODY_LIGHT)
    sw, gap = 268, 12
    labels = (("BODY RAL 7035", BODY_LIGHT, INK_TEXT),
              ("SIDE TONE", BODY_MID, INK_TEXT),
              ("DARK SLATE", PLATE_DARK_2, WHITE),
              ("AMBER TRIM", AMBER, INK_TEXT))
    for i, (lbl, col, ink) in enumerate(labels):
        sx = x0 + 8 + i * (sw + gap)
        draw.rectangle([sx, y0 + 16, sx + sw, y0 + 236], fill=col,
                       outline=(132, 144, 158, 255), width=4)
        f = load_font(FONT_MONO, 26)
        draw_center_ink(draw, sx + sw / 2.0, y0 + 250, lbl, f, ink)


def generate_textures():
    img = Image.new("RGB", (ATLAS_W, ATLAS_H), (128, 132, 140))
    draw = ImageDraw.Draw(img)

    draw_cover(draw)
    draw_lens_band(draw)
    draw_led_band(draw)
    draw_detail(draw)

    verify_layout()
    verify_optics()
    report_ink_heights()

    img.save(ATLAS_PATH, "PNG")
    print(f"[OK] Atlas kaydedildi: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")
    print(f"[OK] Cover: {COVER_W * 1000:.0f} x {COVER_H * 1000:.0f} mm -> "
          f"{REGION_COVER[2] - REGION_COVER[0]} x {REGION_COVER[3] - REGION_COVER[1]} px "
          f"({PX_PER_MM:.2f} px/mm)")
    print(f"[OK] Metin bloklari: {len(_TEXT_BOXES)}  |  dekoratif blok: {len(_GRAPHIC_BOXES)}")


if __name__ == "__main__":
    generate_textures()




