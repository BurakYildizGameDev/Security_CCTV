"""
=============================================================================
Security CCTV Asset Production Suite - Asset 44
Asset Name: SEC_Access_Card_Reader_Rugged (Endustriyel RFID Okuyucu)
Texture Generation Script v1 (2048 x 2048)

ATLAS YERLESIMI:
    BANT-1 HOUSING   (32, 32)    - (1032, 2016)  1000 x 1984 -> 56 x 116 mm (~17.5 px/mm)
    BANT-2 CARD_ZONE (1100, 32)  - (1700, 712)   600 x 680 -> 46 x 52 mm kart alani
    BANT-3 SWATCHES  (1100, 800) - (2016, 2016)  antrasit, kaucuk bumper, metal swatch'lar
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
REGION_HOUSING = (32, 32, 1032, 2016)         # 1000 x 1984 px -> 56 x 116 mm
REGION_CARD = (1100, 32, 1700, 712)           # 600 x 680 px -> kart alani
REGION_SWATCHES = (1100, 800, 2016, 2016)

HOUSING_W, HOUSING_H = 0.0560, 0.1160         # 56 x 116 mm on govde
CARD_W, CARD_H = 0.0460, 0.0520               # 46 x 52 mm kart alani
CARD_Z = -0.0060

# Renkler (agir endustriyel dayanikli RFID okuyucu paleti)
BODY_DARK = (28, 33, 40, 255)                # Antrasit polikarbonat
BODY_MID = (38, 44, 54, 255)
BUMPER_RUBBER = (18, 22, 26, 255)            # Siyah kaucuk tampon
CARD_POCKET = (20, 24, 30, 255)
METAL_ACCENT = (195, 205, 215, 255)
INK_DARK = (15, 18, 22, 255)
INK_TEXT = (220, 228, 238, 255)              # Koyu zemin uzerine acik yazi
INK_SOFT = (145, 160, 178, 255)
ACCENT_BLUE = (30, 130, 230, 255)            # RFID dalga rengi
ACCENT_GREEN = (40, 200, 75, 255)
ACCENT_RED = (220, 45, 35, 255)
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

PX_PER_MM = (REGION_HOUSING[2] - REGION_HOUSING[0]) / (HOUSING_W * 1000.0)

def housing_px(x_m, z_m):
    """+Y normali on yuz haritalamasi (flip_u=True)."""
    x0, y0, x1, y1 = REGION_HOUSING
    nx = (x_m + HOUSING_W / 2.0) / HOUSING_W
    nz = (z_m + HOUSING_H / 2.0) / HOUSING_H
    return (x1 - nx * (x1 - x0), y1 - nz * (y1 - y0))

def draw_rfid_symbol(draw, cx, cy, radius, color):
    """NFC / RFID yay dalgalari ikonu."""
    for r in range(radius - 20, radius + 25, 16):
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=220, end=320, fill=color, width=4)
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=40, end=140, fill=color, width=4)
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=color)

def draw_housing(draw):
    x0, y0, x1, y1 = REGION_HOUSING
    # Antrasit dayanikli polikarbonat zemin
    draw.rectangle([x0, y0, x1, y1], fill=BODY_DARK)

    # Koruyucu kaucuk yan tampon seritleri
    draw.rectangle([x0 + 10, y0 + 10, x1 - 10, y1 - 10], outline=BUMPER_RUBBER, width=8)
    draw.rectangle([x0 + 24, y0 + 24, x1 - 24, y1 - 24], outline=(50, 58, 70, 255), width=3)

    # Ust bolum: Model ve urun kimligi
    f_title = fit_font(draw, "SEC-CR 440", FONT_SANS, 500, 44, 28)
    f_sub = fit_font(draw, "RUGGED RFID READER", FONT_MONO, 500, 22, 16)
    f_spec = load_font(FONT_MONO, 18)

    LX = x0 + 44
    bb = draw_left_ink(draw, LX, y0 + 48, "SEC-CR 440", f_title, INK_TEXT)
    bb = draw_left_ink(draw, LX, bb[3] + 10, "RUGGED RFID READER", f_sub, INK_SOFT)
    draw_left_ink(draw, LX, bb[3] + 8, "13.56 MHz / NFC", f_spec, ACCENT_BLUE)

    # IK10 / IP67 Rozeti (sag ust)
    RX = x1 - 44
    draw.rectangle([RX - 110, y0 + 48, RX, y0 + 88], outline=ACCENT_BLUE, width=2)
    f_badge = load_font(FONT_MONO, 19)
    draw_center_ink(draw, RX - 55, y0 + 58, "IK10", f_badge, INK_TEXT)

    # Durum LED'leri altindaki etiketler (Z = +0.038)
    led_l_x, led_l_y = housing_px(-0.0130, 0.0380)
    led_r_x, led_r_y = housing_px(0.0130, 0.0380)

    f_led = load_font(FONT_MONO, 18)
    # LED yuvalari (koyu halkalar)
    for lx in (led_l_x, led_r_x):
        draw.ellipse([lx - 34, led_l_y - 34, lx + 34, led_l_y + 34], fill=BUMPER_RUBBER, outline=(70, 80, 95, 255), width=3)

    draw_center_ink(draw, led_l_x, led_l_y + 40, "STATUS", f_led, INK_SOFT)
    draw_center_ink(draw, led_r_x, led_r_y + 40, "ACCESS", f_led, INK_SOFT)

    # Kart Alani (Card_Area) Yuva Cebi
    kcx, kcy = housing_px(0.0, CARD_Z)
    kw = (CARD_W * 1000.0 * PX_PER_MM) / 2.0
    kh = (CARD_H * 1000.0 * PX_PER_MM) / 2.0

    # Koyu kart yuva girintisi
    draw.rounded_rectangle([kcx - kw - 8, kcy - kh - 8, kcx + kw + 8, kcy + kh + 8],
                           radius=20, fill=CARD_POCKET, outline=(60, 72, 88, 255), width=3)

    # RFID Dalga sembolu
    draw_rfid_symbol(draw, kcx, kcy - 30, 65, ACCENT_BLUE)

    f_card = load_font(FONT_SANS, 26)
    f_card_sub = load_font(FONT_MONO, 19)
    draw_center_ink(draw, kcx, kcy + 85, "TAP CARD HERE", f_card, INK_TEXT)
    draw_center_ink(draw, kcx, kcy + 125, "MIFARE / DESFire", f_card_sub, INK_SOFT)

    # Alt kimlik ve barkod
    f_sn = load_font(FONT_MONO, 22)
    draw_left_ink(draw, x0 + 44, y1 - 92, "SN 44-CR-003819", f_sn, INK_SOFT)
    draw_center_ink(draw, x1 - 130, y1 - 92, "CE EN 50133-1", f_sn, INK_SOFT)

    # Barkod
    bx, by = x0 + 44, y1 - 58
    for idx in range(30):
        col = INK_TEXT if (idx % 3 == 0 or idx % 7 == 0) else BODY_DARK
        draw.line([(bx + idx * 7, by), (bx + idx * 7, by + 26)], fill=col, width=3)


def draw_card_area_band(draw):
    """Yukseltilmis Kart Alani Mesh'i Dokusu (BANT-2)."""
    x0, y0, x1, y1 = REGION_CARD
    draw.rectangle([x0, y0, x1, y1], fill=BODY_MID)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0

    draw.rounded_rectangle([x0 + 16, y0 + 16, x1 - 16, y1 - 16], radius=24,
                           fill=CARD_POCKET, outline=ACCENT_BLUE, width=4)
    draw_rfid_symbol(draw, cx, cy - 40, 75, ACCENT_BLUE)

    f_card = load_font(FONT_SANS, 28)
    f_card_sub = load_font(FONT_MONO, 20)
    draw_center_ink(draw, cx, cy + 85, "RFID READ ZONE", f_card, INK_TEXT)
    draw_center_ink(draw, cx, cy + 125, "ISO 14443A", f_card_sub, INK_SOFT)


def draw_swatches(draw):
    """Malzeme ornekleme alanlari (BANT-3)."""
    x0, y0, x1, y1 = REGION_SWATCHES
    draw.rectangle([x0, y0, x1, y1], fill=(22, 26, 32, 255))

    # Swatch 1: Koyu Polikarbonat (1250, 950)
    draw.rectangle([1150, 850, 1350, 1050], fill=BODY_DARK, outline=(50, 60, 75, 255), width=2)
    # Swatch 2: Kaucuk Bumper (1500, 950)
    draw.rectangle([1400, 850, 1600, 1050], fill=BUMPER_RUBBER, outline=(40, 48, 58, 255), width=2)
    # Swatch 3: Metalik Aksan (1250, 1250)
    draw.rectangle([1150, 1150, 1350, 1350], fill=METAL_ACCENT, outline=(150, 160, 175, 255), width=2)
    # Swatch 4: Kart Cebi (1500, 1250)
    draw.rectangle([1400, 1150, 1600, 1350], fill=CARD_POCKET, outline=(40, 50, 65, 255), width=2)


def verify_layout():
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
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), (20, 24, 30, 255))
    draw = ImageDraw.Draw(img)

    draw_housing(draw)
    draw_card_area_band(draw)
    draw_swatches(draw)

    verify_layout()

    img.save(ATLAS_PATH, "PNG")
    print(f"[OK] Atlas uretildi: {ATLAS_PATH}")


if __name__ == "__main__":
    main()
