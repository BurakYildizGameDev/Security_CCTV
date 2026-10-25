"""
=============================================================================
Security CCTV Asset Production Suite - Asset 36
Asset Name: SEC_Sensor_Vibration (Titresim Sensoru / Vibration Sensor)
Texture Generation Script v1 (Ultra-High Resolution 2048 x 2048)
Output:
    - exports/T_Security_Atlas.png (2048 x 2048)

ATLAS YERLESIMI (piksel):
    BANT-1 COVER    (32, 32) - (2016, 1416)   1984 x 1384 -> 43.0 x 30.0 mm (46.1 px/mm)
    BANT-2 TERMINAL (32, 1490) - (632, 1817)   600 x  327 -> 22.0 x 12.0 mm (27.3 px/mm)
    BANT-3 LED      (700, 1478) - (880, 1658)  180 x  180 -> durum LED'i lensi
    BANT-4 RENK     (680, 1680) - (1990, 1990) duz renk alanlari (govde/pah/metal)

ON YUZ KURALI: +Y normaline bakan yuzler flip_u=True ile haritalanir. Bu
dosyadaki cover_px() fonksiyonu ayni eslemeyi kullanarak gomme LED yuvasini
dogru piksel konumuna cizer.
=============================================================================
"""

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
REGION_COVER = (32, 32, 2016, 1416)      # 1984 x 1384 px -> 43.0 x 30.0 mm
REGION_TERMINAL = (32, 1490, 632, 1817)  # 600 x 327 px  -> 22.0 x 12.0 mm
REGION_LED = (700, 1478, 880, 1658)      # 180 x 180 px  -> LED lensi (kare)
REGION_DETAIL = (32, 1450, 2016, 2016)   # detay bandi (arka plan)

# ---------------------------------------------------------------- Geometri esleme (m)
COVER_W, COVER_H = 0.0430, 0.0300
TERMINAL_W, TERMINAL_H = 0.0220, 0.0120
TERMINAL_CENTER_Z = -0.0245
CLAIM_SCREW_X = 0.0055
CLAIM_SCREW_Z = -0.0245

# Duz renk UV noktalari (piksel)
PIX_FLAT_BODY = (840, 1835)
PIX_FLAT_SIDE = (1170, 1835)
PIX_FLAT_DARK = (1500, 1835)
PIX_FLAT_METAL = (1830, 1835)
PIX_LED_RIM = (708, 1560)

# Renk Paleti
BODY_LIGHT = (245, 248, 251, 255)
BODY_MID = (228, 234, 242, 255)
BRUSH_LINE = (236, 241, 247, 255)
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
    problems = []
    for (tx0, ty0, tx1, ty1, txt) in _TEXT_BOXES:
        cx, cy = (tx0 + tx1) / 2.0, (ty0 + ty1) / 2.0
        if REGION_COVER[0] <= cx <= REGION_COVER[2] and REGION_COVER[1] <= cy <= REGION_COVER[3]:
            rx0, ry0, rx1, ry1 = REGION_COVER
        elif REGION_TERMINAL[0] <= cx <= REGION_TERMINAL[2] and REGION_TERMINAL[1] <= cy <= REGION_TERMINAL[3]:
            rx0, ry0, rx1, ry1 = REGION_TERMINAL
        else:
            rx0, ry0, rx1, ry1 = REGION_DETAIL
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

    # Dekoratif bloklar sus cercevesinin (x0+30 / y1-30) icine sigmali; tasan
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
    draw.rectangle([x0, y0, x0 + 26, y1], fill=accent)
    draw.rectangle([x0 + 12, y0 + 12, x1 - 12, y1 - 12], outline=(58, 68, 80, 255), width=3)


def draw_cert_box(draw, box, label, sub=None):
    """Sertifika kutusu: etiket + alt yazi dikeyde ortalanmis blok olarak durur."""
    x0, y0, x1, y1 = box
    track_rect(box, "Sertifika kutusu " + label)
    draw.rectangle([x0, y0, x1, y1], fill=(238, 242, 247, 255),
                   outline=(132, 144, 158, 255), width=4)
    f = fit_font(draw, label, FONT_SANS, (x1 - x0) - 30, 40, 20)
    f2 = fit_font(draw, sub, FONT_MONO, (x1 - x0) - 14, 26, 18) if sub else None
    lh = ink_size(draw, label, f)[1]
    sh = ink_size(draw, sub, f2)[1] if sub else 0
    gap = 18 if sub else 0
    top = y0 + (y1 - y0 - (lh + sh + gap)) / 2.0
    draw_center_ink(draw, (x0 + x1) / 2.0, top, label, f, INK_DARK)
    if sub:
        draw_center_ink(draw, (x0 + x1) / 2.0, top + lh + gap, sub, f2, INK_SOFT)


def draw_axis_triad(draw, cx, cy, arm=112):
    """3 eksenli olcum sembolu.

    Oklar ve X / Y / Z etiketleri dis halka icine sigar: etiket yaricapi
    halka yaricapindan kucuk tutulur, aksi halde harfler halka cizgisine biner.
    """
    ring = arm + 42
    draw.ellipse([cx - ring, cy - ring, cx + ring, cy + ring],
                 outline=(196, 206, 218, 255), width=4)
    axes = [((1.00, 0.34), "X"), ((-0.80, 0.50), "Y"), ((0.00, -1.00), "Z")]
    f = load_font(FONT_SANS, 40)
    lw, lh = ink_size(draw, "X", f)
    for (dx, dy), lbl in axes:
        ln = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / ln, dy / ln
        tip = (cx + ux * arm, cy + uy * arm)
        draw.line([(cx, cy), tip], fill=(58, 68, 82, 255), width=8)
        px, py = -uy, ux
        head = 26
        draw.polygon([(tip[0], tip[1]),
                      (tip[0] - ux * head + px * 13, tip[1] - uy * head + py * 13),
                      (tip[0] - ux * head - px * 13, tip[1] - uy * head - py * 13)],
                     fill=(58, 68, 82, 255))
        # Etiketi ok ucu ile halka arasinda, hicbir cizgiye binmeyecek sekilde ortala.
        half = ((lw / 2.0) ** 2 + (lh / 2.0) ** 2) ** 0.5
        r_lbl = ((arm + 10) + (ring - 10 - half)) / 2.0
        draw_center_ink(draw, cx + ux * r_lbl, cy + uy * r_lbl - lh / 2.0, lbl, f, INK_TEXT)
    draw.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=(58, 68, 82, 255))



def draw_warning(draw, x, y, size):
    draw.polygon([(x + size / 2, y), (x + size, y + size), (x, y + size)],
                 fill=AMBER, outline=(150, 108, 12, 255))
    f = fit_font(draw, "!", FONT_SANS, size * 0.5, int(size * 0.62))
    draw_center(draw, x + size / 2, y + size * 0.30, "!", f, PLATE_DARK)


def cover_px(x_m, z_m):
    """Cover on yuzundeki (X, Z) metre konumunu atlas pikseline cevirir."""
    x0, y0, x1, y1 = REGION_COVER
    nx = (x_m + COVER_W / 2.0) / COVER_W
    nz = (z_m + COVER_H / 2.0) / COVER_H
    return (x1 - nx * (x1 - x0), y1 - nz * (y1 - y0))


def terminal_px(x_m, z_m):
    """Terminal blogu on yuzundeki (X, Z) konumunu atlas pikseline cevirir."""
    x0, y0, x1, y1 = REGION_TERMINAL
    nx = (x_m + TERMINAL_W / 2.0) / TERMINAL_W
    nz = (z_m - (TERMINAL_CENTER_Z - TERMINAL_H / 2.0)) / TERMINAL_H
    return (x1 - nx * (x1 - x0), y1 - nz * (y1 - y0))



# ---------------------------------------------------------------- BANT-1: Kapak
def draw_cover(draw):
    x0, y0, x1, y1 = REGION_COVER
    draw.rectangle([x0, y0, x1, y1], fill=BODY_LIGHT)

    # Fircalanmis dovme aluminyum mikro dokusu
    for yy in range(y0 + 4, y1, 9):
        draw.line([(x0, yy), (x1, yy)], fill=BRUSH_LINE)
    draw.rectangle([x0 + 16, y0 + 16, x1 - 16, y1 - 16], outline=FRAME_LINE, width=6)
    draw.rectangle([x0 + 30, y0 + 30, x1 - 30, y1 - 30],
                   outline=(214, 222, 232, 255), width=3)

    # ------------------------------------------------------------ Marka plakasi
    # Tum satirlar ortak sol kenar (LX) ve olculen murekkep kutusuna gore dizilir;
    # araliklar sabit oldugu icin punto degisse de dikey ritim bozulmaz.
    px0, py0, px1, py1 = x0 + 70, y0 + 70, x0 + 1180, y0 + 720
    draw_placard(draw, (px0, py0, px1, py1))
    LX = px0 + 92
    inner_w = (px1 - 26) - LX

    f_title = fit_font(draw, "SEC-VS 200", FONT_SANS, inner_w, 132)
    b = draw_left_ink(draw, LX, py0 + 75, "SEC-VS 200", f_title, WHITE)

    f_sub = fit_font(draw, "VIBRATION SENSOR", FONT_MONO, inner_w, 56)
    b = draw_left_ink(draw, LX, b[3] + 30, "VIBRATION SENSOR", f_sub, COOL_LIGHT)

    t_amber = "IEPE ACCELEROMETER  -  100 mV/g"
    b = draw_left_ink(draw, LX, b[3] + 22, t_amber,
                      fit_font(draw, t_amber, FONT_MONO, inner_w, 42), AMBER)

    # Iki teknik satir tek bir liste gibi davranir: sabit 44 px leading.
    t1 = "RANGE 0.5 - 10 kHz  -  RESONANCE 32 kHz"
    b = draw_left_ink(draw, LX, b[3] + 24, t1,
                      fit_font(draw, t1, FONT_MONO, inner_w, 38), COOL_SOFT)
    t2 = "BIAS 10-12 VDC  -  2-WIRE IEPE OUTPUT"
    b = draw_left_ink(draw, LX, b[1] + 44, t2,
                      fit_font(draw, t2, FONT_MONO, inner_w, 38), COOL_SOFT)

    # Barkod: plakanin tum ic genisligi (alt sag alan artik bos kalmaz),
    # ustten t2'nin altina, alttan seri numarasinin ustune baglanir.
    sn_font = load_font(FONT_MONO, 34)
    sn_h = ink_size(draw, "SN *VS2026488127*", sn_font)[1]
    sn_top = py1 - 28 - sn_h
    bc_y = b[3] + 42
    draw_barcode(draw, LX, bc_y, inner_w, sn_top - 26 - bc_y,
                 dark=(240, 244, 249, 255), light=PLATE_DARK)
    draw_left_ink(draw, LX, sn_top, "SN *VS2026488127*", sn_font, COOL_LIGHT)

    # ------------------------------------------------------------ 3-eksen sembolu
    RCX = x1 - 412                       # sag sutun merkezi (sertifika satiriyla hizali)
    draw_axis_triad(draw, RCX, y0 + 250, 112)
    draw_center_ink(draw, RCX, y0 + 424, "3-AXIS MEASUREMENT",
                    load_font(FONT_MONO, 34), INK_TEXT)

    # ------------------------------------------------------------ Sertifikasyonlar
    boxes = [("CE", "EN 61326"), ("UKCA", "UK SI 2016"),
             ("RoHS", "2011/65/EU"), ("IP67", "IEC 60529")]
    box_w, box_gap = 158, 8
    bx = (x1 - 52) - (4 * box_w + 3 * box_gap)     # sag kenar: satirlarla ayni
    for lbl, sub in boxes:
        draw_cert_box(draw, (bx, y0 + 470, bx + box_w, y0 + 604), lbl, sub)
        bx += box_w + box_gap

    b = draw_center_ink(draw, RCX, y0 + 622, "MADE IN EU  -  REV 2.4",
                        load_font(FONT_MONO, 30), INK_SOFT)
    draw_center_ink(draw, RCX, b[3] + 16, "SEC-TECH INDUSTRIAL",
                    load_font(FONT_MONO, 30), INK_SOFT)

    # ------------------------------------------------------------ Gomme LED yuvasi
    lcx, lcy = cover_px(0.0135, -0.0085)
    lcx, lcy = int(lcx), int(lcy)
    draw.ellipse([lcx - 150, lcy - 150, lcx + 150, lcy + 150], fill=(206, 214, 224, 255))
    draw.ellipse([lcx - 134, lcy - 134, lcx + 134, lcy + 134],
                 outline=(146, 158, 174, 255), width=8)
    draw.ellipse([lcx - 112, lcy - 112, lcx + 112, lcy + 112], fill=(38, 44, 52, 255))
    draw.arc([lcx - 112, lcy - 112, lcx + 112, lcy + 112], 200, 340,
             fill=(92, 102, 116, 255), width=6)
    draw_center_ink(draw, lcx, lcy + 170, "STATUS LED",
                    load_font(FONT_MONO, 32), INK_SOFT)

    # ------------------------------------------------------------ Alt teknik kunye
    bx0, bx1 = x0 + 548, x1 - 52
    rows = [
        ("MOUNTING", "M8 STUD / ADHESIVE PAD / MAGNET BASE"),
        ("OUTPUT", "IEPE 2-WIRE - SHIELDED TWINAX - M12"),
        ("TEMP", "-55 degC ... +120 degC - IP67 SEALED"),
    ]
    row_h, row_gap = 136, 8
    ry = y0 + 800
    for lbl, val in rows:
        draw.rectangle([bx0, ry, bx1, ry + row_h], fill=(238, 242, 248, 255),
                       outline=(198, 208, 220, 255), width=3)
        track_rect((bx0, ry, bx1, ry + row_h), "Teknik satir " + lbl)
        draw.rectangle([bx0, ry, bx0 + 14, ry + row_h], fill=(120, 134, 152, 255))
        f_lbl = fit_font(draw, lbl, FONT_MONO, 320, 34)
        f_val = fit_font(draw, val, FONT_MONO, (bx1 - bx0) - 96, 50)
        lh = ink_size(draw, lbl, f_lbl)[1]
        vh = ink_size(draw, val, f_val)[1]
        top = ry + (row_h - (lh + 14 + vh)) / 2.0
        draw_left_ink(draw, bx0 + 44, top, lbl, f_lbl, INK_TEXT)
        draw_left_ink(draw, bx0 + 44, top + lh + 14, val, f_val, INK_DARK)
        ry += row_h + row_gap

    # ------------------------------------------------------------ Uyari bandi
    # Bant, kapak sus cercevesinin (y1-30) icine tamamen sigar.
    wy0, wy1 = ry, y1 - 40
    track_rect((bx0, wy0, bx1, wy1), "Uyari bandi")
    draw.rectangle([bx0, wy0, bx1, wy1], fill=(250, 246, 232, 255),
                   outline=(176, 132, 18, 255), width=5)
    draw.rectangle([bx0, wy0, bx0 + 16, wy1], fill=AMBER)
    icon = wy1 - wy0 - 28
    draw_warning(draw, bx0 + 46, wy0 + 14, icon)

    tw1 = "2.5 N.m MAX TORQUE - DO NOT OVER-TORQUE"
    tw2 = "USE SHIELDED TWINAX CABLE ONLY"
    tx = bx0 + 170
    tw_max = bx1 - tx - 28
    f1 = fit_font(draw, tw1, FONT_MONO, tw_max, 46)
    f2 = fit_font(draw, tw2, FONT_MONO, tw_max, 34)
    h1 = ink_size(draw, tw1, f1)[1]
    h2 = ink_size(draw, tw2, f2)[1]
    top = wy0 + (wy1 - wy0 - (h1 + 14 + h2)) / 2.0
    draw_left_ink(draw, tx, top, tw1, f1, ALERT_RED)
    draw_left_ink(draw, tx, top + h1 + 14, tw2, f2, INK_SOFT)




# ---------------------------------------------------------------- BANT-2: Terminal
def draw_terminal(draw):
    x0, y0, x1, y1 = REGION_TERMINAL
    draw.rectangle([x0, y0, x1, y1], fill=PLATE_DARK_2)
    draw.rectangle([x0 + 6, y0 + 6, x1 - 6, y1 - 6], outline=(62, 72, 86, 255), width=4)

    draw_center(draw, (x0 + x1) / 2.0, y0 + 14, "TERMINAL BLOCK  1  2",
                fit_font(draw, "TERMINAL BLOCK  1  2", FONT_MONO, (x1 - x0) - 40, 34),
                COOL_LIGHT)

    for sx, lbl in ((CLAIM_SCREW_X, "1  +"), (-CLAIM_SCREW_X, "2  -")):
        px, py = terminal_px(sx, CLAIM_SCREW_Z)
        px, py = int(px), int(py)
        draw.ellipse([px - 54, py - 54, px + 54, py + 54], fill=(48, 56, 68, 255))
        draw.ellipse([px - 46, py - 46, px + 46, py + 46],
                     outline=(148, 158, 172, 255), width=5)
        draw_center(draw, px, py + 62, lbl, load_font(FONT_SANS, 34), AMBER)

    draw_left(draw, x0 + 14, y1 - 44, "24V DC  IEC 61076-2-101",
              fit_font(draw, "24V DC  IEC 61076-2-101", FONT_MONO, (x1 - x0) - 28, 26, 16),
              INK_SOFT)


# ---------------------------------------------------------------- BANT-3: LED
def draw_led(draw):
    x0, y0, x1, y1 = REGION_LED
    lcx, lcy = (x0 + x1) // 2, (y0 + y1) // 2
    r = (x1 - x0) // 2
    draw.rectangle([x0, y0, x1, y1], fill=BODY_LIGHT)
    draw.ellipse([x0, y0, x1, y1], fill=(140, 18, 16, 255),
                 outline=(86, 10, 10, 255), width=6)
    draw.ellipse([lcx - int(r * 0.74), lcy - int(r * 0.74),
                  lcx + int(r * 0.74), lcy + int(r * 0.74)], fill=(206, 30, 26, 255))
    draw.ellipse([lcx - int(r * 0.36), lcy - int(r * 0.48),
                  lcx + int(r * 0.16), lcy - int(r * 0.12)], fill=(255, 138, 128, 255))
    # Fresnel mikro halkalari (optik lens dokusu)
    for k in (0.42, 0.58, 0.70):
        rr = int(r * k)
        draw.arc([lcx - rr, lcy - rr, lcx + rr, lcy + rr], 20, 160,
                 fill=(238, 92, 84, 255), width=3)


# ---------------------------------------------------------------- BANT-4: Duz renkler
def draw_detail(draw):
    x0, y0, x1, y1 = REGION_DETAIL
    draw.rectangle([x0, y0, x1, y1], fill=BODY_LIGHT)

    swatches = [
        (680, 1680, 1000, 1990, BODY_LIGHT, "BODY RAL 7035"),
        (1010, 1680, 1330, 1990, (209, 217, 227, 255), "CHAMFER TONE"),
        (1340, 1680, 1660, 1990, PLATE_DARK, "DARK SLATE"),
        (1670, 1680, 1990, 1990, (196, 206, 219, 255), "METAL"),
    ]
    for sx0, sy0, sx1, sy1, col, lbl in swatches:
        draw.rectangle([sx0, sy0, sx1, sy1], fill=col,
                       outline=(178, 189, 203, 255), width=4)
        f = fit_font(draw, lbl, FONT_MONO, (sx1 - sx0) - 24, 34, 18)
        h = ink_size(draw, lbl, f)[1]
        draw_center_ink(draw, (sx0 + sx1) / 2.0, sy1 - 20 - h, lbl, f, INK_SOFT)


def generate_textures():
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), BODY_LIGHT)
    draw = ImageDraw.Draw(img)

    draw_detail(draw)
    draw_cover(draw)
    draw_terminal(draw)
    draw_led(draw)
    verify_layout()

    img.save(ATLAS_PATH, "PNG")
    print(f"[OK] Generated Texture Atlas for Asset 36 (2048x2048): {ATLAS_PATH}")
    print(f"     COVER band  1984 x 1384 px -> 43.0 x 30.0 mm = {1984 / 43.0:.1f} px/mm")
    print(f"     TERMINAL    600 x 327 px   -> 22.0 x 12.0 mm = {600 / 22.0:.1f} px/mm")


if __name__ == "__main__":
    generate_textures()

