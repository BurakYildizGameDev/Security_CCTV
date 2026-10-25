"""
=============================================================================
Security CCTV Asset Production Suite - Asset 37
Asset Name: SEC_Sensor_Ultrasonic (Ultrasonik Hareket Sensoru)
Texture Generation Script v1 (High Resolution 2048 x 2048)

Output:
    - exports/T_Security_Atlas.png (2048 x 2048)

ATLAS YERLESIMI (piksel):
    BANT-1 COVER      (32, 32)    - (1982, 1397)  1950 x 1365 -> 50 x 35 mm (39.0 px/mm)
    BANT-2 TRANSDUCER (32, 1430)  - (332, 1730)    300 x  300 -> transducer membrane
    BANT-3 LED        (360, 1430) - (560, 1630)    200 x  200 -> LED lens
    BANT-4 RENK       (600, 1430) - (2016, 2016)  duz renk alanlari (govde/pah/metal)

ON YUZ KURALI: +Y normaline bakan yuzler flip_u=True ile haritalanir. Bu
dosyadaki cover_px() fonksiyonu ayni eslemeyi kullanarak gomme transducer
cukurlarini ve LED yuvasini dogru piksel konumuna cizer.
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

# ---------------------------------------------------------------- UV bantlari (2048x2048)
REGION_COVER = (32, 32, 1982, 1397)         # 1950 x 1365 px -> 50.0 x 35.0 mm
REGION_TRANSDUCER = (32, 1430, 332, 1730)   # 300 x 300 px  -> transducer membrane
REGION_LED = (360, 1430, 560, 1630)         # 200 x 200 px  -> LED lens
REGION_DETAIL = (600, 1430, 2016, 2016)     # detay / duz renk bandi

# ---------------------------------------------------------------- Geometri esleme (m)
COVER_W, COVER_H = 0.0500, 0.0350           # Housing on yuzu
TRANSDUCER_X, TRANSDUCER_Z = 0.0128, 0.0075
LED_X, LED_Z = 0.0, 0.0075
TRANSDUCER_R = 0.0076                       # 3D puck yaricapi (cizilen halka ile ayni)

# Duz renk UV noktalari (piksel)
PIX_FLAT_BODY = (770, 1600)
PIX_FLAT_SIDE = (1120, 1600)
PIX_FLAT_DARK = (1470, 1600)
PIX_FLAT_METAL = (1820, 1600)

# Renk Paleti (varlik 36 ailesiyle ayni)
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
ALERT_RED = (176, 36, 30, 255)
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


def draw_left(draw, x, y, text, font, fill):
    draw.text((x, y), text, font=font, fill=fill)
    _track_text(draw, x, y, text, font)


def draw_center(draw, cx, y, text, font, fill):
    x = cx - text_w(draw, text, font) / 2.0
    draw.text((x, y), text, font=font, fill=fill)
    _track_text(draw, x, y, text, font)


def _track_text(draw, x, y, text, font):
    """Tipografi QA: her metnin piksel kutusunu kaydeder."""
    if not text.strip():
        return
    try:
        l, t, r, b = draw.textbbox((0, 0), text, font=font)
    except Exception:
        return
    _TEXT_BOXES.append((x + l, y + t, x + r, y + b, text))


def track_rect(box, name):
    """Dekoratif bloklari (plaka, bant, kutu) cerceve QA'si icin kaydeder."""
    x0, y0, x1, y1 = box
    _GRAPHIC_BOXES.append((min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), name))


# --- Murekkep tabanli yerlestirme -------------------------------------------
# draw.text() koordinati fontun em kutusunun tepesidir; ayni puntoda bile
# murekkebin ustunde 3-25 px bosluk kalir. Bu yardimcilar metni GERCEK murekkep
# kutusuna gore hizalar, boylece puntoyu degistirmek dikey ritmi bozmaz.

def ink_size(draw, text, font):
    """Metnin gercek murekkep genisligi ve yuksekligi."""
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


def verify_layout():
    """Metin kutularinin bant icinde kaldigini ve ust uste binmedigini dogrular."""
    regions = [REGION_COVER, REGION_TRANSDUCER, REGION_LED, REGION_DETAIL]
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

    # Dekoratif bloklar sus cercevesinin (x0+36 / y1-36) icine sigmali; tasan
    # bloklar cerceve cizgisini keser ve render'da kirik gorunur.
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


def verify_columns():
    """Plaka icindeki iki kolonun birbirine tasmadigini dogrular.

    Sol kolon 96..1150, sag kolon 1190..1884 px araliginda calisir; 40 px'lik
    orta oluk iki kolonun optik olarak ayrismasini saglar. Metin bu oluga
    girerse plaka dagilmis gorunur, bu yuzden sert kontrol edilir.
    """
    x0, y0, x1, y1 = REGION_COVER
    plate_top = y0 + 758
    plate_x0, plate_x1 = x0 + 64, x1 - 64
    left_max, right_min = 1150.0, 1190.0
    problems = []
    for (tx0, ty0, tx1, ty1, txt) in _TEXT_BOXES:
        cy = (ty0 + ty1) / 2.0
        if not (y0 <= cy <= y1):
            continue
        if cy < plate_top:
            continue
        if tx0 < plate_x0 + 20 or tx1 > plate_x1 - 20:
            problems.append(f"'{txt}' plaka kenar boslugunu asiyor: {(tx0, tx1)}")
        if tx1 > left_max + 1 and tx0 < right_min - 1:
            problems.append(f"'{txt}' kolon oluguna giriyor: {(tx0, tx1)}")
    if problems:
        for p in problems:
            print("[COLUMN-FAIL] " + p)
        raise AssertionError(f"Kolon yerlesimi hatali: {len(problems)} sorun")
    print("[COLUMN-OK] Sol/sag kolon ayrimi korunuyor, oluk temiz")


def report_ink_heights():
    """En kucuk murekkep yuksekligini raporlar (render'da okunabilirlik tabani)."""
    if not _TEXT_BOXES:
        return
    heights = sorted((ty1 - ty0, txt) for (tx0, ty0, tx1, ty1, txt) in _TEXT_BOXES)
    px_per_mm = (REGION_COVER[2] - REGION_COVER[0]) / (COVER_W * 1000.0)
    print(f"[INK] En kucuk murekkep: {heights[0][0]:.0f} px "
          f"({heights[0][0] / px_per_mm:.2f} mm) -> '{heights[0][1]}'")
    print(f"[INK] En buyuk murekkep: {heights[-1][0]:.0f} px "
          f"({heights[-1][0] / px_per_mm:.2f} mm) -> '{heights[-1][1]}'")
    # QA flat render olcegi: 900 px / 0.105 m ortho -> 50 mm kapak = 428.6 px
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


def draw_placard(draw, box, fill=PLATE_DARK, accent=AMBER):
    x0, y0, x1, y1 = box
    track_rect(box, "Marka plakasi")
    draw.rectangle([x0, y0, x1, y1], fill=fill, outline=(78, 90, 104, 255), width=5)
    draw.rectangle([x0, y0, x0 + 22, y1], fill=accent)
    draw.rectangle([x0 + 12, y0 + 12, x1 - 12, y1 - 12], outline=(58, 68, 80, 255), width=3)


def draw_cert_box(draw, box, label, sub=None):
    """Sertifika kutusu: etiket + alt yazi dikeyde ortalanmis blok olarak durur."""
    x0, y0, x1, y1 = box
    track_rect(box, "Sertifika kutusu " + label)
    draw.rectangle([x0, y0, x1, y1], fill=(238, 242, 247, 255),
                   outline=(132, 144, 158, 255), width=4)
    f = fit_font(draw, label, FONT_SANS, (x1 - x0) - 26, 40, 20)
    f2 = fit_font(draw, sub, FONT_MONO, (x1 - x0) - 14, 24, 16) if sub else None
    lh = ink_size(draw, label, f)[1]
    sh = ink_size(draw, sub, f2)[1] if sub else 0
    gap = 16 if sub else 0
    top = y0 + (y1 - y0 - (lh + sh + gap)) / 2.0
    draw_center_ink(draw, (x0 + x1) / 2.0, top, label, f, INK_DARK)
    if sub:
        draw_center_ink(draw, (x0 + x1) / 2.0, top + lh + gap, sub, f2, INK_SOFT)


def draw_warning(draw, x, y, size):
    draw.polygon([(x + size / 2, y), (x + size, y + size), (x, y + size)],
                 fill=AMBER, outline=(150, 108, 12, 255))
    f = fit_font(draw, "!", FONT_SANS, size * 0.5, int(size * 0.62))
    draw_center(draw, x + size / 2, y + size * 0.30, "!", f, PLATE_DARK)


def cover_px(x_m, z_m):
    """Cover on yuzundeki (X, Z) metre konumunu atlas pikseline cevirir.

    flip_u=True eslemesiyle ayni: +Y normalli on yuzde dunya +X, dokunun
    soluna (kucuk u) karsilik gelir; bu yuzden x1'den geri sayilir.
    """
    x0, y0, x1, y1 = REGION_COVER
    nx = (x_m + COVER_W / 2.0) / COVER_W
    nz = (z_m + COVER_H / 2.0) / COVER_H
    return (x1 - nx * (x1 - x0), y1 - nz * (y1 - y0))


# ---------------------------------------------------------------- BANT-1: Kapak
def draw_cover(draw):
    x0, y0, x1, y1 = REGION_COVER
    draw.rectangle([x0, y0, x1, y1], fill=BODY_LIGHT)

    # Fircalanmis dovme aluminyum mikro dokusu
    for yy in range(y0 + 4, y1, 9):
        draw.line([(x0, yy), (x1, yy)], fill=BRUSH_LINE)
    draw.rectangle([x0 + 16, y0 + 16, x1 - 16, y1 - 16], outline=FRAME_LINE, width=6)
    draw.rectangle([x0 + 30, y0 + 30, x1 - 30, y1 - 30], outline=(210, 219, 230, 255), width=3)

    # --- Gomme transducer cukurlari ---------------------------------------
    # 3D puck yaricapi TRANSDUCER_R = 7.6 mm -> 296 px. Cizilen koyu halka
    # puck'in hemen disinda kalir, boylece render'da gomme (recess) golgesi okunur.
    px_per_mm = (x1 - x0) / (COVER_W * 1000.0)
    r_puck = TRANSDUCER_R * 1000.0 * px_per_mm
    for sx in (TRANSDUCER_X, -TRANSDUCER_X):
        cx, cy = cover_px(sx, TRANSDUCER_Z)
        for rr, col, wd in ((r_puck + 40, GRAPHITE, 40),
                            (r_puck + 52, (206, 216, 228, 255), 4),
                            (r_puck + 3, (12, 15, 20, 255), 6)):
            draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=col, width=wd)

    # TX / RX ayrimi plaka uzerindeki "DUAL 40 kHz TRANSDUCER (TX / RX)"
    # satirinda verilir; iki cukur arasindaki 36 px'lik bosluga etiket
    # sigmadigi icin (halka cizgisine biner) burada ayri etiket cizilmez.

    # --- LED yuvasi --------------------------------------------------------
    ldx, ldy = cover_px(LED_X, LED_Z)
    led_r = 0.0026 * 1000.0 * px_per_mm          # 3D lens yaricapi
    draw.ellipse([ldx - led_r - 26, ldy - led_r - 26, ldx + led_r + 26, ldy + led_r + 26],
                 fill=(16, 20, 26, 255), outline=(88, 96, 108, 255), width=4)
    draw.ellipse([ldx - led_r - 8, ldy - led_r - 8, ldx + led_r + 8, ldy + led_r + 8],
                 fill=(28, 42, 34, 255), outline=(150, 160, 172, 255), width=3)
    f_stat = load_font(FONT_MONO, 26)
    draw_center_ink(draw, ldx, ldy + led_r + 62, "STATUS", f_stat, INK_SOFT)

    # --- Alt etiket plakasi ------------------------------------------------
    PL = (x0 + 64, y0 + 758, x1 - 64, y1 - 44)
    draw_placard(draw, PL)
    px0, py0, px1, py1 = PL

    LX = px0 + 58                 # sol kolon metin sol kenari
    L_RIGHT = 1150                # sol kolon sag siniri (piksel)
    R_X0 = 1190                   # sag kolon sol kenari
    R_X1 = px1 - 34

    # ---- Sol kolon: kimlik + teknik satirlar + barkod
    y = py0 + 34
    f_title = fit_font(draw, "SEC-US 300", FONT_SANS, L_RIGHT - LX, 108, 54)
    bb = draw_left_ink(draw, LX, y, "SEC-US 300", f_title, WHITE)
    y = bb[3] + 20

    f_sub = fit_font(draw, "ULTRASONIC MOTION SENSOR", FONT_MONO, L_RIGHT - LX, 46, 24)
    bb = draw_left_ink(draw, LX, y, "ULTRASONIC MOTION SENSOR", f_sub, COOL_LIGHT)
    y = bb[3] + 16

    f_acc = fit_font(draw, "DUAL 40 kHz TRANSDUCER  (TX / RX)", FONT_MONO, L_RIGHT - LX, 38, 22)
    bb = draw_left_ink(draw, LX, y, "DUAL 40 kHz TRANSDUCER  (TX / RX)", f_acc, AMBER)
    y = bb[3] + 22

    draw.rectangle([LX, y, L_RIGHT, y + 3], fill=(96, 108, 122, 255))
    y += 20

    f_spec = load_font(FONT_MONO, 34)
    bb = draw_left_ink(draw, LX, y, "RANGE 0.2 - 8 m    BEAM 15 deg", f_spec, COOL_LIGHT)
    y = bb[3] + 40
    bb = draw_left_ink(draw, LX, y, "SUPPLY 12-24 VDC   RELAY 50 mA", f_spec, COOL_LIGHT)
    y = bb[3] + 32

    SN_TOP = py1 - 28
    f_sn = load_font(FONT_MONO, 28)
    sn_h = ink_size(draw, "SN 37-US-004128", f_sn)[1]
    bc_h = max(56, (SN_TOP - sn_h - 22) - y)
    draw_barcode(draw, LX, y, L_RIGHT - LX, bc_h, dark=(240, 244, 249, 255), light=PLATE_DARK)
    draw_left_ink(draw, LX, SN_TOP, "SN 37-US-004128", f_sn, INK_SOFT)

    # ---- Sag kolon: sertifikalar + uyari kutusu + uretim satirlari
    box_w, box_gap, box_h = 210, 12, 108
    certs = (("CE", "EN 61326"), ("RoHS", "2011/65/EU"), ("IP65", "IEC 60529"))
    for i, (lbl, sub) in enumerate(certs):
        cx0 = R_X0 + i * (box_w + box_gap)
        draw_cert_box(draw, (cx0, py0 + 34, cx0 + box_w, py0 + 34 + box_h), lbl, sub)

    WB = (R_X0, py0 + 162, R_X1, py0 + 425)
    track_rect(WB, "Uyari kutusu")
    draw.rectangle([WB[0], WB[1], WB[2], WB[3]], fill=(252, 246, 232, 255),
                   outline=(196, 152, 44, 255), width=4)
    draw.rectangle([WB[0], WB[1], WB[0] + 14, WB[3]], fill=AMBER)
    draw_warning(draw, WB[0] + 30, WB[1] + 22, 54)

    f_warn = load_font(FONT_MONO, 34)
    draw_left_ink(draw, WB[0] + 104, WB[1] + 24, "DO NOT PAINT", f_warn, ALERT_RED)
    draw_left_ink(draw, WB[0] + 104, WB[1] + 70, "TRANSDUCER FACE", f_warn, ALERT_RED)
    f_wsoft = load_font(FONT_MONO, 26)
    draw_left_ink(draw, WB[0] + 30, WB[1] + 134, "KEEP FACE CLEAR OF DIRT,", f_wsoft, INK_TEXT)
    draw_left_ink(draw, WB[0] + 30, WB[1] + 172, "PAINT AND OBSTACLES.", f_wsoft, INK_TEXT)
    draw.rectangle([WB[0] + 30, WB[1] + 218, WB[2] - 26, WB[1] + 221], fill=(200, 186, 152, 255))
    draw_left_ink(draw, WB[0] + 30, WB[1] + 234, "MOUNT 1.8 - 2.4 m AFF", f_wsoft, INK_SOFT)

    f_foot = load_font(FONT_MONO, 26)
    draw_left_ink(draw, R_X0, py1 - 92, "MADE IN EU   -   REV 3.1", f_foot, COOL_SOFT)
    f_brand = load_font(FONT_MONO, 30)
    draw_left_ink(draw, R_X0, py1 - 48, "SEC-TECH INDUSTRIAL", f_brand, AMBER)


# ---------------------------------------------------------------- BANT-2: Transducer
def draw_transducer_band(draw):
    x0, y0, x1, y1 = REGION_TRANSDUCER
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = (x1 - x0) / 2.0
    draw.rectangle([x0, y0, x1, y1], fill=(10, 12, 16, 255))
    # Piezo membrane: es merkezli halkalar + ince isin deseni
    for i, rr in enumerate((0.96, 0.82, 0.66, 0.50, 0.34)):
        col = (58, 64, 74, 255) if i % 2 == 0 else (34, 38, 46, 255)
        draw.ellipse([cx - r * rr, cy - r * rr, cx + r * rr, cy + r * rr],
                     outline=col, width=7)
    for ang_step in range(0, 360, 45):
        a = math.radians(ang_step)
        draw.line([(cx + math.cos(a) * r * 0.24, cy + math.sin(a) * r * 0.24),
                   (cx + math.cos(a) * r * 0.92, cy + math.sin(a) * r * 0.92)],
                  fill=(26, 30, 37, 255), width=3)
    draw.ellipse([cx - r * 0.20, cy - r * 0.20, cx + r * 0.20, cy + r * 0.20],
                 fill=(22, 26, 32, 255), outline=(70, 78, 90, 255), width=5)
    draw.ellipse([cx - r * 0.99, cy - r * 0.99, cx + r * 0.99, cy + r * 0.99],
                 outline=(112, 122, 136, 255), width=8)


# ---------------------------------------------------------------- BANT-3: LED lens
def draw_led_band(draw):
    x0, y0, x1, y1 = REGION_LED
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = (x1 - x0) / 2.0
    draw.rectangle([x0, y0, x1, y1], fill=(14, 46, 30, 255))
    draw.ellipse([cx - r * 0.98, cy - r * 0.98, cx + r * 0.98, cy + r * 0.98],
                 fill=(36, 150, 84, 255), outline=(96, 220, 140, 255), width=8)
    draw.ellipse([cx - r * 0.58, cy - r * 0.58, cx + r * 0.58, cy + r * 0.58],
                 fill=(120, 240, 160, 255), outline=(150, 246, 180, 255), width=6)
    draw.ellipse([cx - r * 0.30, cy - r * 0.30, cx + r * 0.30, cy + r * 0.30],
                 fill=(232, 255, 240, 255))
    draw.line([(cx - r * 0.28, cy - r * 0.44), (cx + r * 0.02, cy - r * 0.72)],
              fill=(236, 255, 244, 255), width=7)


# ---------------------------------------------------------------- BANT-4: Renk alanlari
def draw_detail(draw):
    x0, y0, x1, y1 = REGION_DETAIL
    draw.rectangle([x0, y0, x1, y1], fill=BODY_LIGHT)
    sw = 340
    labels = (("BODY RAL 7035", BODY_LIGHT, INK_TEXT),
              ("SIDE TONE", BODY_MID, INK_TEXT),
              ("DARK SLATE", PLATE_DARK_2, INK_TEXT),
              ("METAL TRIM", (176, 186, 198, 255), INK_TEXT))
    for i, (lbl, col, ink) in enumerate(labels):
        sx = x0 + 8 + i * (sw + 10)
        draw.rectangle([sx, y0 + 20, sx + sw, y0 + 360], fill=col,
                       outline=(132, 144, 158, 255), width=4)
        f = load_font(FONT_MONO, 26)
        draw_center_ink(draw, sx + sw / 2.0, y0 + 376, lbl, f, ink)


def generate_textures():
    img = Image.new("RGB", (ATLAS_W, ATLAS_H), (128, 132, 140))
    draw = ImageDraw.Draw(img)

    draw_cover(draw)
    draw_transducer_band(draw)
    draw_led_band(draw)
    draw_detail(draw)

    verify_layout()
    verify_columns()
    report_ink_heights()

    img.save(ATLAS_PATH, "PNG")
    print(f"[OK] Atlas kaydedildi: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")
    print(f"[OK] Cover: {COVER_W * 1000:.0f} x {COVER_H * 1000:.0f} mm -> "
          f"{REGION_COVER[2] - REGION_COVER[0]} x {REGION_COVER[3] - REGION_COVER[1]} px "
          f"({(REGION_COVER[2] - REGION_COVER[0]) / (COVER_W * 1000.0):.2f} px/mm)")
    print(f"[OK] Metin bloklari: {len(_TEXT_BOXES)}  |  dekoratif blok: {len(_GRAPHIC_BOXES)}")


if __name__ == "__main__":
    generate_textures()


