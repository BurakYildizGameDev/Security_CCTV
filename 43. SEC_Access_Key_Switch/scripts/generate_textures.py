"""
=============================================================================
Security CCTV Asset Production Suite - Asset 43
Asset Name: SEC_Access_Key_Switch (Anahtarli Guvenlik Salteri)
Texture Generation Script v1 (2048 x 2048)

ATLAS YERLESIMI:
    BANT-1 FACEPLATE (32, 32)    - (1432, 1432)  1400 x 1400 -> 70 x 70 mm (20 px/mm)
    BANT-2 CYLINDER  (1480, 32)  - (1980, 532)   500 x 500 -> Ø22 mm kilit gobegi
    BANT-3 KEY       (1480, 580) - (1980, 1080)  500 x 500 -> anahtar yuzu
    BANT-4 SWATCHES  (1480, 1140)- (2016, 2016)  duz metal ve kaplama swatch'lari
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

# UV bolgeleri (piksel)
REGION_FACEPLATE = (32, 32, 1432, 1432)        # 1400 x 1400 px -> 70 x 70 mm (20 px/mm)
REGION_CYLINDER = (1480, 32, 1980, 532)        # 500 x 500 px
REGION_KEY = (1480, 580, 1980, 1080)           # 500 x 500 px
REGION_SWATCHES = (1480, 1140, 2016, 2016)

PLATE_W, PLATE_H = 0.0700, 0.0700             # 70 x 70 mm on plaka
CYL_X, CYL_Z, CYL_R = 0.0, 0.0, 0.0110         # Ø22 mm silindir

# Duz renk ornekleme noktalari
PIX_METAL_LIGHT = (1650, 1250)
PIX_METAL_MID = (1850, 1250)
PIX_METAL_DARK = (1650, 1550)
PIX_CHROME = (1850, 1550)

# Renkler (endustriyel paslanmaz celik ve guvenlik paleti)
METAL_BASE = (218, 224, 230, 255)
METAL_BRUSH = (210, 216, 224, 255)
METAL_DARK = (48, 54, 62, 255)
CHROME_HI = (248, 250, 252, 255)
INK_DARK = (20, 24, 30, 255)
INK_TEXT = (42, 50, 60, 255)
INK_SOFT = (90, 100, 115, 255)
ACCENT_GREEN = (32, 160, 64, 255)
ACCENT_RED = (200, 40, 32, 255)
ACCENT_AMBER = (220, 160, 24, 255)
WHITE = (255, 255, 255, 255)

_FONT_CACHE = {}
_TEXT_BOXES = []

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

def fit_font(draw, text, path, max_width, start_size, min_size=16):
    size = start_size
    while size > min_size:
        f = load_font(path, size)
        if text_w(draw, text, f) <= max_width:
            return f
        size -= 2
    return load_font(path, min_size)

def _track_text(x, y, r, b, text):
    _TEXT_BOXES.append((x, y, r, b, text))

def draw_left_ink(draw, x, ink_top, text, font, fill):
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    draw.text((x - l, ink_top - t), text, font=font, fill=fill)
    box = (x, ink_top, x + (r - l), ink_top + (b - t))
    _track_text(box[0], box[1], box[2], box[3], text)
    return box

def draw_center_ink(draw, cx, ink_top, text, font, fill):
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    w = r - l
    x = cx - (l + r) / 2.0
    draw.text((x, ink_top - t), text, font=font, fill=fill)
    box = (cx - w / 2.0, ink_top, cx + w / 2.0, ink_top + (b - t))
    _track_text(box[0], box[1], box[2], box[3], text)
    return box

PX_PER_MM = (REGION_FACEPLATE[2] - REGION_FACEPLATE[0]) / (PLATE_W * 1000.0)

def plate_px(x_m, z_m):
    """+Y normali on yuz haritalamasi (flip_u=True)."""
    x0, y0, x1, y1 = REGION_FACEPLATE
    nx = (x_m + PLATE_W / 2.0) / PLATE_W
    nz = (z_m + PLATE_H / 2.0) / PLATE_H
    return (x1 - nx * (x1 - x0), y1 - nz * (y1 - y0))

def draw_faceplate(draw):
    x0, y0, x1, y1 = REGION_FACEPLATE
    # Paslanmaz fircali metal zemin
    draw.rectangle([x0, y0, x1, y1], fill=METAL_BASE)
    for yy in range(y0 + 4, y1, 6):
        draw.line([(x0, yy), (x1, yy)], fill=METAL_BRUSH)

    # Dis dekoratif cerceve
    draw.rectangle([x0 + 16, y0 + 16, x1 - 16, y1 - 16], outline=(175, 185, 195, 255), width=4)
    draw.rectangle([x0 + 26, y0 + 26, x1 - 26, y1 - 26], outline=(235, 240, 245, 255), width=2)

    # Ust baslik ve kimlik
    f_t = fit_font(draw, "SEC-KS 100", FONT_SANS, 650, 48, 30)
    f_s = fit_font(draw, "KEY ACCESS SWITCH", FONT_MONO, 650, 26, 18)
    f_p = load_font(FONT_MONO, 20)

    LX = x0 + 52
    bb = draw_left_ink(draw, LX, y0 + 50, "SEC-KS 100", f_t, INK_DARK)
    bb = draw_left_ink(draw, LX, bb[3] + 12, "KEY ACCESS SWITCH", f_s, INK_TEXT)
    draw_left_ink(draw, LX, bb[3] + 8, "250 VAC  10A", f_p, INK_SOFT)

    # Sag ust guvenlik/sinif rozeti
    RX = x1 - 52
    draw.rectangle([RX - 120, y0 + 50, RX, y0 + 90], outline=INK_DARK, width=2)
    f_badge = load_font(FONT_MONO, 20)
    draw_center_ink(draw, RX - 60, y0 + 60, "IP65", f_badge, INK_DARK)

    # Silindir merkezi (0, 0)
    cx, cy = plate_px(0.0, 0.0)
    r_cyl = CYL_R * 1000.0 * PX_PER_MM  # 11 mm * 20 = 220 px

    # Silindir yuvasi arkasi koyu cep (3D kilit gobeginin alti)
    draw.ellipse([cx - r_cyl - 18, cy - r_cyl - 18, cx + r_cyl + 18, cy + r_cyl + 18],
                 fill=METAL_DARK, outline=(160, 170, 182, 255), width=4)
    draw.ellipse([cx - r_cyl - 2, cy - r_cyl - 2, cx + r_cyl + 2, cy + r_cyl + 2],
                 fill=(22, 26, 32, 255))

    # --- Pozisyon Isaretleri (0° OFF, +45° ON, -45° BYPASS) ---
    # Radius of markings
    r_mark = r_cyl + 75
    f_pos = load_font(FONT_SANS, 34)
    f_pos_sub = load_font(FONT_MONO, 22)

    # 12 o'clock (0° - Dikey) -> OFF
    p_off_x = cx
    p_off_y = cy - r_mark
    draw.line([(cx, cy - r_cyl - 22), (cx, cy - r_cyl - 48)], fill=INK_DARK, width=6)
    draw_center_ink(draw, p_off_x, p_off_y - 46, "OFF", f_pos, ACCENT_RED)
    draw_center_ink(draw, p_off_x, p_off_y - 12, "0", f_pos_sub, INK_SOFT)

    # +45° (Saat 1:30 yonu - saga dogru) -> ON / RUN
    # Not: flip_u=True oldugu icin dunya +45° rotasyonu (Y etrafinda) atlas acisinda sola/saga dikkat edilmelidir.
    # Standart on gorus: saat ibresi yonunde +45 deg (sag taraf).
    ang_rad_r = math.radians(-45) # -45 deg from top (sag ust)
    dx_on = math.sin(math.radians(45)) * r_mark
    dy_on = -math.cos(math.radians(45)) * r_mark
    draw.line([(cx + math.sin(math.radians(45)) * (r_cyl + 22),
                cy - math.cos(math.radians(45)) * (r_cyl + 22)),
               (cx + math.sin(math.radians(45)) * (r_cyl + 48),
                cy - math.cos(math.radians(45)) * (r_cyl + 48))], fill=INK_DARK, width=6)
    draw_center_ink(draw, cx + dx_on + 28, cy + dy_on - 30, "ON", f_pos, ACCENT_GREEN)
    draw_center_ink(draw, cx + dx_on + 28, cy + dy_on + 4, "I", f_pos_sub, INK_SOFT)

    # -45° (Saat 10:30 yonu - sola dogru) -> BYPASS
    dx_bp = -math.sin(math.radians(45)) * r_mark
    dy_bp = -math.cos(math.radians(45)) * r_mark
    draw.line([(cx - math.sin(math.radians(45)) * (r_cyl + 22),
                cy - math.cos(math.radians(45)) * (r_cyl + 22)),
               (cx - math.sin(math.radians(45)) * (r_cyl + 48),
                cy - math.cos(math.radians(45)) * (r_cyl + 48))], fill=INK_DARK, width=6)
    draw_center_ink(draw, cx + dx_bp - 36, cy + dy_bp - 30, "BYPASS", f_pos, ACCENT_AMBER)
    draw_center_ink(draw, cx + dx_bp - 36, cy + dy_bp + 4, "II", f_pos_sub, INK_SOFT)

    # Alt kimlik ve barkod
    f_sn = load_font(FONT_MONO, 24)
    draw_left_ink(draw, x0 + 52, y1 - 85, "SN 43-KS-001284", f_sn, INK_SOFT)
    draw_center_ink(draw, x1 - 140, y1 - 85, "CE EN 60947-5-1", f_sn, INK_SOFT)

    # Alt barkod
    bx, by = x0 + 52, y1 - 50
    for idx in range(32):
        col = INK_DARK if (idx % 3 == 0 or idx % 7 == 0) else METAL_BASE
        draw.line([(bx + idx * 7, by), (bx + idx * 7, by + 24)], fill=col, width=3)


def draw_cylinder_band(draw):
    """Silindir on yuzu ve anahtar deligi yuvası (BANT-2)."""
    x0, y0, x1, y1 = REGION_CYLINDER
    draw.rectangle([x0, y0, x1, y1], fill=METAL_BASE)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = 210

    # Krom parlak gobek halkalari
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(195, 202, 210, 255), outline=CHROME_HI, width=6)
    draw.ellipse([cx - r + 30, cy - r + 30, cx + r - 30, cy + r - 30],
                 fill=(225, 230, 238, 255), outline=(150, 160, 172, 255), width=4)

    # Anahtar giris yarigi (keyway - dikey kilit slit'i)
    draw.rounded_rectangle([cx - 16, cy - 110, cx + 16, cy + 110], radius=8, fill=(12, 14, 18, 255))
    draw.line([(cx, cy - 100), (cx, cy + 100)], fill=(35, 40, 50, 255), width=4)
    # Anahtar kilavuz centigi
    draw.polygon([(cx - 24, cy - 60), (cx - 16, cy - 80), (cx - 16, cy - 40)], fill=(12, 14, 18, 255))


def draw_key_band(draw):
    """Anahtar basligi ve tutamak dokusu (BANT-3)."""
    x0, y0, x1, y1 = REGION_KEY
    draw.rectangle([x0, y0, x1, y1], fill=METAL_BASE)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0

    # Anahtar basligi / sap geometrisi dokusu
    draw.rounded_rectangle([cx - 140, cy - 180, cx + 140, cy + 180], radius=40,
                           fill=(180, 188, 196, 255), outline=(130, 140, 150, 255), width=6)
    # Anahtarlik deligi
    draw.ellipse([cx - 45, cy - 140, cx + 45, cy - 50], fill=(225, 230, 238, 255), outline=(120, 130, 140, 255), width=4)

    # Tirtikli tutamak deseni
    for y_grip in range(int(cy - 20), int(cy + 130), 16):
        draw.line([(cx - 110, y_grip), (cx + 110, y_grip)], fill=(150, 158, 168, 255), width=4)

    f_key = load_font(FONT_MONO, 24)
    draw_center_ink(draw, cx, cy + 138, "SEC-LOCK", f_key, INK_DARK)


def draw_swatches(draw):
    """Duz renk / malzeme ornekleme alanlari (BANT-4)."""
    x0, y0, x1, y1 = REGION_SWATCHES
    draw.rectangle([x0, y0, x1, y1], fill=(240, 242, 245, 255))

    # Swatch 1: Paslanmaz Celik / Govde Metal (1650, 1250)
    draw.rectangle([1550, 1180, 1750, 1380], fill=METAL_BASE, outline=(180, 190, 200, 255), width=2)
    # Swatch 2: Orta Metal (1850, 1250)
    draw.rectangle([1780, 1180, 1980, 1380], fill=METAL_BRUSH, outline=(160, 170, 180, 255), width=2)
    # Swatch 3: Koyu Grafit / Vida (1650, 1550)
    draw.rectangle([1550, 1450, 1750, 1650], fill=METAL_DARK, outline=(30, 35, 42, 255), width=2)
    # Swatch 4: Parlak Krom / Anahtar (1850, 1550)
    draw.rectangle([1780, 1450, 1980, 1650], fill=CHROME_HI, outline=(210, 220, 230, 255), width=2)


def verify_layout():
    """Metin bloklarinin cakismasiz oldugunu dogrular."""
    boxes = sorted(_TEXT_BOXES)
    problems = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            ax0, ay0, ax1, ay1, at = boxes[i]
            bx0, by0, bx1, by1, bt = boxes[j]
            ox = min(ax1, bx1) - max(ax0, bx0)
            oy = min(ay1, by1) - max(ay0, by0)
            if ox > 4 and oy > 4:
                problems.append(f"'{at}' ile '{bt}' cakisti ({ox:.0f}x{oy:.0f} px)")
    if problems:
        for p in problems:
            print("[LAYOUT-FAIL] " + p)
        raise AssertionError(f"Tipografi yerlesim hatasi: {len(problems)}")
    print(f"[LAYOUT-OK] {len(_TEXT_BOXES)} metin blogu yerlestirildi, cakisma yok.")


def main():
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), (230, 235, 242, 255))
    draw = ImageDraw.Draw(img)

    draw_faceplate(draw)
    draw_cylinder_band(draw)
    draw_key_band(draw)
    draw_swatches(draw)

    verify_layout()

    img.save(ATLAS_PATH, "PNG")
    print(f"[OK] Atlas uretildi: {ATLAS_PATH}")


if __name__ == "__main__":
    main()
