"""
=============================================================================
Security CCTV Asset Production Suite - Asset 45
Asset Name: SEC_Access_Bio_Terminal_Desktop (Masaustu Biyometrik Terminal)
Texture Generation Script v1 (2048 x 2048)

ATLAS YERLESIMI:
    BANT-1 HOUSING   (32, 32)    - (1032, 1500)  1000 x 1468 -> 68 x 100 mm on baslik
    BANT-2 SCREEN    (1100, 32)  - (1800, 500)   700 x 468   -> 48 x 32 mm LCD ekran
    BANT-3 PRISM     (1100, 540) - (1600, 1040)  500 x 500   -> 22 x 26 mm optik prizma
    BANT-4 SWATCHES  (1100, 1080)- (2016, 2016)  masaustu gri polimer, kaucuk ayak swatch'lari
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
REGION_HOUSING = (32, 32, 1032, 1500)
REGION_SCREEN = (1100, 32, 1800, 500)
REGION_PRISM = (1100, 540, 1600, 1040)
REGION_SWATCHES = (1100, 1080, 2016, 2016)

HOUSING_W, HOUSING_H = 0.0680, 0.1000         # 68 x 100 mm baslik on yuzu
SCREEN_W, SCREEN_H = 0.0480, 0.0320           # 48 x 32 mm LCD
FINGER_W, FINGER_H = 0.0220, 0.0260           # 22 x 26 mm optik cam

# Renkler (modern profesyonel biyometrik cihaz dili)
BODY_GRAY = (45, 52, 62, 255)                 # Koyu grafit govde
BODY_LIGHT = (215, 222, 230, 255)
DARK_BEZEL = (24, 28, 34, 255)
SCREEN_BG = (12, 28, 40, 255)                 # Koyu LCD tonu
PRISM_GLASS = (18, 50, 42, 255)               # Yesil optik cam tonu
INK_TEXT = (235, 240, 248, 255)
INK_SOFT = (150, 165, 182, 255)
ACCENT_CYAN = (30, 170, 210, 255)
ACCENT_GREEN = (40, 210, 85, 255)
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
    x0, y0, x1, y1 = REGION_HOUSING
    nx = (x_m + HOUSING_W / 2.0) / HOUSING_W
    nz = (z_m + HOUSING_H / 2.0) / HOUSING_H
    return (x1 - nx * (x1 - x0), y1 - nz * (y1 - y0))

def draw_housing(draw):
    x0, y0, x1, y1 = REGION_HOUSING
    draw.rectangle([x0, y0, x1, y1], fill=BODY_GRAY)

    # Ince pah ve cerceve cizgileri
    draw.rectangle([x0 + 12, y0 + 12, x1 - 12, y1 - 12], outline=(65, 75, 90, 255), width=4)
    draw.rectangle([x0 + 22, y0 + 22, x1 - 22, y1 - 22], outline=(30, 36, 44, 255), width=2)

    # Ust kimlik bandi
    f_title = fit_font(draw, "SEC-BT 450", FONT_SANS, 550, 44, 28)
    f_sub = fit_font(draw, "BIO TERMINAL DESKTOP", FONT_MONO, 550, 22, 16)
    f_spec = load_font(FONT_MONO, 18)

    LX = x0 + 44
    bb = draw_left_ink(draw, LX, y0 + 48, "SEC-BT 450", f_title, INK_TEXT)
    bb = draw_left_ink(draw, LX, bb[3] + 10, "BIO TERMINAL DESKTOP", f_sub, INK_SOFT)
    draw_left_ink(draw, LX, bb[3] + 8, "500 DPI OPTICAL", f_spec, ACCENT_CYAN)

    # Sag ust FIPS/PIV Rozeti
    RX = x1 - 44
    draw.rectangle([RX - 110, y0 + 48, RX, y0 + 88], outline=ACCENT_CYAN, width=2)
    f_badge = load_font(FONT_MONO, 19)
    draw_center_ink(draw, RX - 55, y0 + 58, "FIPS", f_badge, INK_TEXT)

    # Ekran Yuvasi Cebi (Z = +0.0180)
    scx, scy = housing_px(0.0, 0.0180)
    sw = (SCREEN_W * 1000.0 * PX_PER_MM) / 2.0
    sh = (SCREEN_H * 1000.0 * PX_PER_MM) / 2.0
    draw.rectangle([scx - sw - 12, scy - sh - 12, scx + sw + 12, scy + sh + 12],
                   fill=DARK_BEZEL, outline=(60, 70, 85, 255), width=3)
    draw.rectangle([scx - sw, scy - sh, scx + sw, scy + sh], fill=SCREEN_BG)

    # Parmak Izi Optik Prizma Yuvasi Cebi (Z = -0.0230)
    fcx, fcy = housing_px(0.0, -0.0230)
    fw = (FINGER_W * 1000.0 * PX_PER_MM) / 2.0
    fh = (FINGER_H * 1000.0 * PX_PER_MM) / 2.0
    draw.rounded_rectangle([fcx - fw - 16, fcy - fh - 16, fcx + fw + 16, fcy + fh + 16],
                           radius=12, fill=DARK_BEZEL, outline=ACCENT_GREEN, width=3)
    draw.rounded_rectangle([fcx - fw, fcy - fh, fcx + fw, fcy + fh],
                           radius=8, fill=PRISM_GLASS)

    # Parmak izi yonlendirme ikonu ve metni
    f_hint = load_font(FONT_MONO, 20)
    gap_mid_y = (scy + sh + 12 + fcy - fh - 16) / 2.0 - 10
    draw_center_ink(draw, fcx, gap_mid_y, "SCAN FINGER", f_hint, ACCENT_GREEN)

    # Alt kimlik ve barkod
    f_sn = load_font(FONT_MONO, 22)
    draw_left_ink(draw, x0 + 44, y1 - 85, "SN 45-BT-001920", f_sn, INK_SOFT)
    draw_center_ink(draw, x1 - 130, y1 - 85, "CE EN 60950-1", f_sn, INK_SOFT)

    # Barkod
    bx, by = x0 + 44, y1 - 52
    for idx in range(30):
        col = INK_TEXT if (idx % 3 == 0 or idx % 7 == 0) else BODY_GRAY
        draw.line([(bx + idx * 7, by), (bx + idx * 7, by + 24)], fill=col, width=3)


def draw_screen_band(draw):
    """M_Screen Dokusu: Renkli LCD GUI (BANT-2)."""
    x0, y0, x1, y1 = REGION_SCREEN
    draw.rectangle([x0, y0, x1, y1], fill=(14, 30, 48, 255))
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0

    # GUI Durum Satiri
    draw.rectangle([x0 + 10, y0 + 10, x1 - 10, y0 + 50], fill=(22, 45, 70, 255))
    f_gui_top = load_font(FONT_MONO, 22)
    draw_left_ink(draw, x0 + 20, y0 + 18, "SEC-SYS ONLINE", f_gui_top, ACCENT_CYAN)
    draw_left_ink(draw, x1 - 120, y0 + 18, "12:45", f_gui_top, WHITE)

    # Ana GUI Alani: Kulanici Durumu
    f_msg = load_font(FONT_SANS, 34)
    f_sub_msg = load_font(FONT_MONO, 22)
    draw_center_ink(draw, cx, cy - 25, "READY TO SCAN", f_msg, WHITE)
    draw_center_ink(draw, cx, cy + 30, "VERIFY IDENTIFICATION", f_sub_msg, ACCENT_CYAN)

    # Alt Durum cubugu
    draw.rectangle([x0 + 10, y1 - 40, x1 - 10, y1 - 10], fill=(22, 45, 70, 255))
    f_bot = load_font(FONT_MONO, 18)
    draw_center_ink(draw, cx, y1 - 32, "TAP CARD OR SCAN FINGER", f_bot, INK_SOFT)


def draw_prism_band(draw):
    """M_Emission Dokusu: Biyometrik Optik Prizma (BANT-3)."""
    x0, y0, x1, y1 = REGION_PRISM
    draw.rectangle([x0, y0, x1, y1], fill=(10, 40, 30, 255))
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0

    # Optik cam yuzeyi parlamasi
    draw.rounded_rectangle([x0 + 20, y0 + 20, x1 - 20, y1 - 20], radius=30,
                           fill=(18, 70, 48, 255), outline=(50, 220, 120, 255), width=6)

    # Parmak izi desen yaylari (fingerprint ridges)
    for r in range(40, 180, 22):
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=160, end=380,
                 fill=(60, 250, 140, 255), width=4)
        draw.arc([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8], start=180, end=360,
                 fill=(40, 180, 100, 255), width=2)


def draw_swatches(draw):
    """Masaustu Ayak ve Govde Swatch'lari (BANT-4)."""
    x0, y0, x1, y1 = REGION_SWATCHES
    draw.rectangle([x0, y0, x1, y1], fill=(24, 28, 35, 255))

    # Swatch 1: Govde Grafit (1250, 1200)
    draw.rectangle([1150, 1100, 1350, 1300], fill=BODY_GRAY, outline=(70, 80, 95, 255), width=2)
    # Swatch 2: Koyu Cerceve (1500, 1200)
    draw.rectangle([1400, 1100, 1600, 1300], fill=DARK_BEZEL, outline=(45, 52, 62, 255), width=2)
    # Swatch 3: Metalik Aksan (1250, 1500)
    draw.rectangle([1150, 1400, 1350, 1600], fill=BODY_LIGHT, outline=(170, 180, 195, 255), width=2)
    # Swatch 4: Kaucuk Ayak (1500, 1500)
    draw.rectangle([1400, 1400, 1600, 1600], fill=(16, 18, 22, 255), outline=(35, 40, 48, 255), width=2)


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
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), (24, 28, 35, 255))
    draw = ImageDraw.Draw(img)

    draw_housing(draw)
    draw_screen_band(draw)
    draw_prism_band(draw)
    draw_swatches(draw)

    verify_layout()

    img.save(ATLAS_PATH, "PNG")
    print(f"[OK] Atlas uretildi: {ATLAS_PATH}")


if __name__ == "__main__":
    main()
