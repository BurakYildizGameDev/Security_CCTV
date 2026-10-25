"""
=============================================================================
Security CCTV Asset Production Suite - Asset 38
Asset Name: SEC_Sensor_Gas (Gaz Guvenlik Sensoru)
Texture Generation Script v1 (2048 x 2048)

Output:
    - exports/T_Security_Atlas.png (2048 x 2048)

ATLAS YERLESIMI (piksel):
    BANT-1 COVER (32, 32)    - (1832, 1688)  1800 x 1656 -> 50 x 46 mm (36.0 px/mm)
    BANT-2 VENT  (32, 1720)  - (332, 2020)    300 x  300 -> delikli koruyucu kapak
    BANT-3 LED   (350, 1720) - (550, 2020)    200 x  200 -> alarm lensi
    BANT-4 RENK  (580, 1720) - (2016, 2016)  duz renk alanlari

ON YUZ KURALI: +Y normaline bakan yuzler flip_u=True ile haritalanir. Bu
dosyadaki cover_px() fonksiyonu ayni eslemeyi kullanarak kubbe cukurunu ve
LED yuvasini dogru piksel konumuna cizer.
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
REGION_COVER = (32, 32, 1832, 1688)         # 1800 x 1656 px -> 50.0 x 46.0 mm
REGION_VENT = (32, 1720, 332, 2020)         # 300 x 300 px  -> delikli kapak
REGION_LED = (350, 1720, 550, 1920)         # 200 x 200 px  -> alarm lensi
REGION_DETAIL = (580, 1720, 2016, 2016)     # detay / duz renk bandi

# ---------------------------------------------------------------- Geometri esleme (m)
COVER_W, COVER_H = 0.0500, 0.0460           # Housing on yuzu (50 x 46 mm)
VENT_X, VENT_Z = 0.0, 0.0060
VENT_R = 0.0140                             # 3D kubbe taban yaricapi (28 mm cap)
LED_X, LED_Z = 0.0195, 0.0160
LED_R = 0.0030                              # 3D lens yaricapi (6 mm cap)

# Alt etiket plakasi (on yuz uzerinde, X/Z metre)
PLATE_X0, PLATE_X1 = -0.0225, 0.0225
PLATE_Z0, PLATE_Z1 = -0.0215, -0.0095

# Duz renk UV noktalari (piksel)
PIX_FLAT_BODY = (740, 1900)
PIX_FLAT_SIDE = (1090, 1900)
PIX_FLAT_DARK = (1450, 1900)
PIX_FLAT_METAL = (1800, 1900)
PIX_FLAT_WARN = (740, 1860)

# Renk Paleti (varlik 36/37 ailesiyle ayni)
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


def draw_left(draw, x, y, text, font, fill):
    draw.text((x, y), text, font=font, fill=fill)
    _track_text(draw, x, y, text, font)


def draw_center(draw, cx, y, text, font, fill):
    x = cx - text_w(draw, text, font) / 2.0
    draw.text((x, y), text, font=font, fill=fill)
    _track_text(draw, x, y, text, font)


def draw_right(draw, rx, y, text, font, fill):
    x = rx - text_w(draw, text, font)
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


def draw_right_ink(draw, rx, ink_top, text, font, fill):
    """Sag kenari rx'e, murekkep tepesi ink_top'a gelecek sekilde yazar."""
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    draw_right(draw, rx - r, ink_top - t, text, font, fill)
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


def plate_px_rect():
    """Etiket plakasinin atlas piksel dikdortgeni (sol, ust, sag, alt)."""
    ax, ay = cover_px(PLATE_X1, PLATE_Z1)      # sol-ust
    bx, by = cover_px(PLATE_X0, PLATE_Z0)      # sag-alt
    return (ax, ay, bx, by)


PLATE_PX = plate_px_rect()


def verify_layout():
    """Metin kutularinin bant icinde kaldigini ve ust uste binmedigini dogrular."""
    regions = [REGION_COVER, REGION_VENT, REGION_LED, REGION_DETAIL]
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


def verify_plate():
    """Plaka icindeki tum metinlerin plaka kenar bosluguna uydugunu dogrular.

    Plaka koyu zeminli oldugu icin metin disina tasan bir satir render'da
    govde uzerine biner ve okunmaz; bu kontrol tasmayi derleme aninda durdurur.
    """
    px0, py0, px1, py1 = PLATE_PX
    inset = 26
    problems = []
    inside = 0
    for (tx0, ty0, tx1, ty1, txt) in _TEXT_BOXES:
        cx, cy = (tx0 + tx1) / 2.0, (ty0 + ty1) / 2.0
        if not (px0 <= cx <= px1 and py0 <= cy <= py1):
            continue
        inside += 1
        if tx0 < px0 + inset or tx1 > px1 - inset or ty0 < py0 + 12 or ty1 > py1 - 12:
            problems.append(f"'{txt}' plaka bosluğunu asiyor: {(tx0, ty0, tx1, ty1)}")
    if inside == 0:
        problems.append("plakada hic metin yok")
    if problems:
        for p in problems:
            print("[PLATE-FAIL] " + p)
        raise AssertionError(f"Plaka yerlesimi hatali: {len(problems)} sorun")
    print(f"[PLATE-OK] {inside} satir plaka icinde, kenar boslugu korunuyor")


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
    # QA flat render olcegi: 900 px / 0.105 m ortho -> 46 mm yukseklik 394 px
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


def draw_warning(draw, x, y, size):
    draw.polygon([(x + size / 2, y), (x + size, y + size), (x, y + size)],
                 fill=AMBER, outline=(150, 108, 12, 255))
    f = fit_font(draw, "!", FONT_SANS, size * 0.5, int(size * 0.62))
    draw_center(draw, x + size / 2, y + size * 0.30, "!", f, PLATE_DARK)


# ---------------------------------------------------------------- BANT-1: On yuz
def draw_cover(draw):
    x0, y0, x1, y1 = REGION_COVER
    draw.rectangle([x0, y0, x1, y1], fill=BODY_LIGHT)

    # Fircalanmis govde mikro dokusu + cift sus cercevesi
    for yy in range(y0 + 4, y1, 9):
        draw.line([(x0, yy), (x1, yy)], fill=BRUSH_LINE)
    draw.rectangle([x0 + 16, y0 + 16, x1 - 16, y1 - 16], outline=FRAME_LINE, width=6)
    draw.rectangle([x0 + 30, y0 + 30, x1 - 30, y1 - 30], outline=(210, 219, 230, 255), width=3)

    px_per_mm = (x1 - x0) / (COVER_W * 1000.0)
    r_vent = VENT_R * 1000.0 * px_per_mm
    r_led = LED_R * 1000.0 * px_per_mm

    # --- Havalandirma kubbesi cukuru --------------------------------------
    # 3D kubbe yaricapi r_vent = 504 px. Koyu gomme halkasi kubbenin hemen
    # disinda kalir; render'da golge olarak okunur ve dokuyu kirletmez.
    vcx, vcy = cover_px(VENT_X, VENT_Z)
    draw.ellipse([vcx - r_vent - 36, vcy - r_vent - 36,
                  vcx + r_vent + 36, vcy + r_vent + 36], fill=GRAPHITE)
    draw.ellipse([vcx - r_vent - 38, vcy - r_vent - 38,
                  vcx + r_vent + 38, vcy + r_vent + 38],
                 outline=(206, 216, 228, 255), width=4)
    draw.ellipse([vcx - r_vent + 2, vcy - r_vent + 2,
                  vcx + r_vent - 2, vcy + r_vent - 2], fill=(12, 15, 20, 255))

    # --- Alarm LED yuvasi --------------------------------------------------
    lcx, lcy = cover_px(LED_X, LED_Z)
    draw.ellipse([lcx - r_led - 26, lcy - r_led - 26,
                  lcx + r_led + 26, lcy + r_led + 26],
                 fill=(16, 20, 26, 255), outline=(88, 96, 108, 255), width=4)
    # Ic halka lens tabanini siki sarar: lens neredeyse gomme oldugu icin
    # (0.3 mm) ince bir koyu oturma cizgisi yeterli, genis halka kayma izlenimi verir.
    draw.ellipse([lcx - r_led - 8, lcy - r_led - 8,
                  lcx + r_led + 8, lcy + r_led + 8],
                 fill=(52, 20, 18, 255), outline=(150, 160, 172, 255), width=3)
    f_micro = load_font(FONT_MONO, 26)
    draw_center_ink(draw, lcx, lcy + r_led + 56, "ALARM", f_micro, INK_SOFT)

    # Not: kubbe 28 mm capiyla on yuzun alt kenarina 8 px kalana kadar iner;
    # bu yuzden kubbe altina aciklama satiri konmaz (plaka ile cakisirdi).

    # --- Alt etiket plakasi ------------------------------------------------
    px0, py0, px1, py1 = PLATE_PX
    track_rect((px0, py0, px1, py1), "Etiket plakasi")
    draw.rectangle([px0, py0, px1, py1], fill=PLATE_DARK,
                   outline=(78, 90, 104, 255), width=5)
    draw.rectangle([px0, py0, px0 + 20, py1], fill=AMBER)
    draw.rectangle([px0 + 12, py0 + 12, px1 - 12, py1 - 12],
                   outline=(58, 68, 80, 255), width=3)

    LX = px0 + 56
    RX = px1 - 56

    y = py0 + 30
    f_title = fit_font(draw, "SEC-GD 400", FONT_SANS, 760, 96, 48)
    bb = draw_left_ink(draw, LX, y, "SEC-GD 400", f_title, WHITE)
    f_tag = load_font(FONT_MONO, 30)
    draw_right_ink(draw, RX, y + 8, "Ex II 2G", f_tag, AMBER)
    y = bb[3] + 12

    f_sub = fit_font(draw, "CATALYTIC GAS DETECTOR", FONT_MONO, 760, 40, 22)
    bb = draw_left_ink(draw, LX, y, "CATALYTIC GAS DETECTOR", f_sub, COOL_LIGHT)
    y = bb[3] + 14

    draw.rectangle([LX, y, RX, y + 3], fill=(96, 108, 122, 255))
    y += 20

    f_spec = load_font(FONT_MONO, 34)
    bb = draw_left_ink(draw, LX, y, "CH4   0-100 %LEL   T90 < 30 s", f_spec, COOL_LIGHT)
    y = bb[3] + 40
    bb = draw_left_ink(draw, LX, y, "ALARM 20 %LEL   12-24 VDC", f_spec, COOL_LIGHT)
    y = bb[3] + 18

    draw.rectangle([LX, y, RX, y + 3], fill=(96, 108, 122, 255))
    y += 20

    f_m = load_font(FONT_MONO, 28)
    f_micro2 = load_font(FONT_MONO, 25)
    bb = draw_left_ink(draw, LX, y, "CE EN 60079-29-1  -  RoHS 2011/65/EU  -  IP54",
                       f_micro2, COOL_SOFT)
    draw_right_ink(draw, RX, y + 1, "SN 38-GD-002941", f_micro2, COOL_SOFT)
    y = bb[3] + 26

    bb = draw_left_ink(draw, LX, y, "MADE IN EU   -   REV 1.2", f_m, COOL_SOFT)
    bc_x0 = RX - 286
    draw_barcode(draw, bc_x0, y - 4, 286, max(46, py1 - 14 - (y - 4)),
                 dark=(240, 244, 249, 255), light=PLATE_DARK)


# ---------------------------------------------------------------- BANT-2: Delikli kapak
def draw_vent_band(draw):
    """Delikli koruyucu kapak: es merkezli delik halkalari + capraz koruma orgusu."""
    x0, y0, x1, y1 = REGION_VENT
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = (x1 - x0) / 2.0
    draw.rectangle([x0, y0, x1, y1], fill=(38, 43, 51, 255))

    # Dis bilezik (metalik kenar)
    draw.ellipse([cx - r * 0.99, cy - r * 0.99, cx + r * 0.99, cy + r * 0.99],
                 outline=(176, 186, 198, 255), width=10)
    draw.ellipse([cx - r * 0.93, cy - r * 0.93, cx + r * 0.93, cy + r * 0.93],
                 outline=(96, 106, 118, 255), width=5)

    # Es merkezli delik halkalari (altigen dizilim)
    hole_r = r * 0.030
    step = r * 0.108
    rings = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.2)
    for ri, ring in enumerate(rings):
        radius = ring * step
        count = 1 if ring == 0.0 else int(6 * ring if ring < 8 else 6 * 8)
        for k in range(count):
            ang = math.radians(360.0 * k / count + (ri * 11.0))
            hx = cx + math.cos(ang) * radius
            hy = cy + math.sin(ang) * radius
            if (hx - cx) ** 2 + (hy - cy) ** 2 > (r * 0.88) ** 2:
                continue
            draw.ellipse([hx - hole_r, hy - hole_r, hx + hole_r, hy + hole_r],
                         fill=(8, 10, 13, 255), outline=(92, 100, 112, 255), width=2)

    # Merkez sensör gozu (katalitik pelet)
    draw.ellipse([cx - r * 0.10, cy - r * 0.10, cx + r * 0.10, cy + r * 0.10],
                 fill=(24, 28, 34, 255), outline=(150, 158, 170, 255), width=4)


# ---------------------------------------------------------------- BANT-3: Alarm lensi
def draw_led_band(draw):
    x0, y0, x1, y1 = REGION_LED
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = (x1 - x0) / 2.0
    draw.rectangle([x0, y0, x1, y1], fill=(60, 16, 12, 255))
    draw.ellipse([cx - r * 0.98, cy - r * 0.98, cx + r * 0.98, cy + r * 0.98],
                 fill=(150, 28, 20, 255), outline=(232, 96, 72, 255), width=8)
    draw.ellipse([cx - r * 0.58, cy - r * 0.58, cx + r * 0.58, cy + r * 0.58],
                 fill=(228, 74, 48, 255), outline=(250, 140, 112, 255), width=6)
    draw.ellipse([cx - r * 0.30, cy - r * 0.30, cx + r * 0.30, cy + r * 0.30],
                 fill=(255, 110, 85, 255))


# ---------------------------------------------------------------- BANT-4: Renk alanlari
def draw_detail(draw):
    x0, y0, x1, y1 = REGION_DETAIL
    draw.rectangle([x0, y0, x1, y1], fill=BODY_LIGHT)
    sw, gap = 272, 12
    labels = (("BODY RAL 7035", BODY_LIGHT, INK_TEXT),
              ("SIDE TONE", BODY_MID, INK_TEXT),
              ("DARK SLATE", PLATE_DARK_2, WHITE),
              ("GRILLE SLATE", (38, 43, 51, 255), WHITE),
              ("METAL TRIM", (176, 186, 198, 255), INK_TEXT))
    for i, (lbl, col, ink) in enumerate(labels):
        sx = x0 + 8 + i * (sw + gap)
        draw.rectangle([sx, y0 + 16, sx + sw, y0 + 252], fill=col,
                       outline=(132, 144, 158, 255), width=4)
        f = load_font(FONT_MONO, 26)
        draw_center_ink(draw, sx + sw / 2.0, y0 + 266, lbl, f, ink)


def generate_textures():
    img = Image.new("RGB", (ATLAS_W, ATLAS_H), (128, 132, 140))
    draw = ImageDraw.Draw(img)

    draw_cover(draw)
    draw_vent_band(draw)
    draw_led_band(draw)
    draw_detail(draw)

    verify_layout()
    verify_plate()
    report_ink_heights()

    img.save(ATLAS_PATH, "PNG")
    print(f"[OK] Atlas kaydedildi: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")
    print(f"[OK] Cover: {COVER_W * 1000:.0f} x {COVER_H * 1000:.0f} mm -> "
          f"{REGION_COVER[2] - REGION_COVER[0]} x {REGION_COVER[3] - REGION_COVER[1]} px "
          f"({(REGION_COVER[2] - REGION_COVER[0]) / (COVER_W * 1000.0):.2f} px/mm)")
    print(f"[OK] Plaka (px): {PLATE_PX[0]:.0f},{PLATE_PX[1]:.0f} - "
          f"{PLATE_PX[2]:.0f},{PLATE_PX[3]:.0f}")
    print(f"[OK] Metin bloklari: {len(_TEXT_BOXES)}  |  dekoratif blok: {len(_GRAPHIC_BOXES)}")


if __name__ == "__main__":
    generate_textures()



