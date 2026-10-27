"""
=============================================================================
Security CCTV Asset Production Suite - Asset 46
Asset Name: SEC_Lock_Electric_Strike (Elektrikli Kapi Karsiligi)
Texture Generation Script v1 (2048 x 2048)

ATLAS REGIONS:
    REGION_FACEPLATE   (64, 64)    - (464, 1984)   400 x 1920 px (25 x 160 mm faceplate)
    REGION_HOUSING_SIDE(520, 64)   - (1320, 964)   800 x 900 px (Spec label & wiring)
    REGION_KEEPER      (520, 1024) - (1020, 1984)  500 x 960 px (Keeper jaw plate)
    REGION_TERMINAL    (1080, 1024)- (1580, 1524)  500 x 500 px (Terminal markings)
    REGION_SWATCHES    (1080, 1560)- (2016, 2016)  Swatches & plain metal fills
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

# Regions
REGION_FACEPLATE = (64, 64, 464, 1984)
REGION_HOUSING_SIDE = (520, 64, 1320, 964)
REGION_KEEPER = (520, 1024, 1020, 1984)
REGION_TERMINAL = (1080, 1024, 1580, 1524)
REGION_SWATCHES = (1080, 1560, 2016, 2016)

# Swatch coordinates
PIX_METAL_LIGHT = (1850, 1650)
PIX_METAL_MID = (1850, 1750)
PIX_METAL_DARK = (1850, 1850)
PIX_CAVITY = (1850, 1950)

# Colors
METAL_BASE = (215, 220, 226, 255)
METAL_BRUSH = (205, 212, 218, 255)
METAL_DARK = (45, 50, 58, 255)
METAL_HOUSING = (85, 92, 102, 255)
CHROME_HI = (248, 250, 252, 255)
INK_DARK = (20, 24, 30, 255)
INK_TEXT = (35, 42, 52, 255)
INK_SOFT = (80, 90, 105, 255)
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
    x = cx - w / 2.0
    draw.text((x - l, ink_top - t), text, font=font, fill=fill)
    box = (x, ink_top, x + w, ink_top + (b - t))
    _track_text(box[0], box[1], box[2], box[3], text)
    return box

def draw_screw_head(draw, cx, cy, radius):
    for r in range(radius, 0, -1):
        ratio = r / float(radius)
        c = int(140 + 75 * ratio)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(c, c + 3, c + 6, 255))
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=(90, 95, 102, 255), width=3)
    sw = max(2, radius // 5)
    sl = int(radius * 0.70)
    draw.line([cx - sl, cy, cx + sl, cy], fill=(40, 44, 50, 255), width=sw)
    draw.line([cx, cy - sl, cx, cy + sl], fill=(40, 44, 50, 255), width=sw)
    draw.line([cx - sl, cy + 1, cx + sl, cy + 1], fill=(220, 225, 230, 255), width=1)
    draw.line([cx + 1, cy - sl, cx + 1, cy + sl], fill=(220, 225, 230, 255), width=1)

def build_atlas():
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), (35, 38, 44, 255))
    draw = ImageDraw.Draw(img)

    # 1. Swatches
    sx0, sy0, sx1, sy1 = REGION_SWATCHES
    draw.rectangle([sx0, sy0, sx1, sy1], fill=(50, 55, 62, 255))
    draw.rectangle([sx0 + 20, sy0 + 20, sx1 - 20, sy0 + 100], fill=METAL_BASE)
    draw.rectangle([sx0 + 20, sy0 + 120, sx1 - 20, sy0 + 200], fill=METAL_BRUSH)
    draw.rectangle([sx0 + 20, sy0 + 220, sx1 - 20, sy0 + 300], fill=METAL_HOUSING)
    draw.rectangle([sx0 + 20, sy0 + 320, sx1 - 20, sy0 + 400], fill=(20, 22, 26, 255))

    # 2. FACEPLATE (400 x 1920)
    fx0, fy0, fx1, fy1 = REGION_FACEPLATE
    draw.rectangle([fx0, fy0, fx1, fy1], fill=METAL_BASE)
    # Brushed texture lines
    for y in range(fy0, fy1, 6):
        shade = 210 + (y % 13)
        draw.line([fx0 + 4, y, fx1 - 4, y], fill=(shade, shade + 3, shade + 6, 255), width=2)
    # Beveled edge
    draw.rectangle([fx0, fy0, fx1, fy1], outline=(150, 155, 165, 255), width=4)
    draw.rectangle([fx0 + 4, fy0 + 4, fx1 - 4, fy1 - 4], outline=(240, 245, 250, 255), width=2)

    fcx = (fx0 + fx1) // 2

    # Top & Bottom Screws
    draw_screw_head(draw, fcx, fy0 + 110, 36)
    draw_screw_head(draw, fcx, fy1 - 110, 36)

    # Top branding and engravings
    f_brand = load_font(FONT_SANS, 34)
    f_sub = load_font(FONT_MONO, 22)
    f_tiny = load_font(FONT_MONO, 18)

    draw_center_ink(draw, fcx, fy0 + 180, "SEC-LOK", f_brand, INK_DARK)
    draw_center_ink(draw, fcx, fy0 + 225, "ELECTRIC STRIKE", f_sub, INK_TEXT)
    draw_center_ink(draw, fcx, fy0 + 258, "HEAVY DUTY - ANSI", f_tiny, INK_SOFT)
    draw.line([fcx - 120, fy0 + 290, fcx + 120, fy0 + 290], fill=(160, 166, 175, 255), width=3)
    draw.line([fcx - 120, fy0 + 292, fcx + 120, fy0 + 292], fill=WHITE, width=1)

    # Keeper Cutout Area representation on faceplate (Center)
    # 16 mm x 44 mm cutout -> in pixels ~256 x 528 px
    cut_w = 260
    cut_h = 530
    cut_y0 = (fy0 + fy1) // 2 - cut_h // 2
    cut_y1 = cut_y0 + cut_h
    cut_x0 = fcx - cut_w // 2
    cut_x1 = fcx + cut_w // 2

    draw.rectangle([cut_x0, cut_y0, cut_x1, cut_y1], fill=(30, 34, 40, 255))
    draw.rectangle([cut_x0, cut_y0, cut_x1, cut_y1], outline=(120, 126, 136, 255), width=4)
    # Latch ramp indicators
    draw.rectangle([cut_x0 + 15, cut_y0 + 15, cut_x1 - 15, cut_y1 - 15], outline=(60, 66, 75, 255), width=2)
    draw_center_ink(draw, fcx, (cut_y0 + cut_y1) // 2 - 12, "LATCH CAVITY", f_tiny, (110, 120, 135, 255))

    # Bottom ratings and markings
    draw.line([fcx - 120, fy1 - 290, fcx + 120, fy1 - 290], fill=(160, 166, 175, 255), width=3)
    draw.line([fcx - 120, fy1 - 288, fcx + 120, fy1 - 288], fill=WHITE, width=1)
    draw_center_ink(draw, fcx, fy1 - 275, "12V DC / 24V AC", f_sub, INK_DARK)
    draw_center_ink(draw, fcx, fy1 - 245, "FAIL-SECURE (NC)", f_tiny, INK_TEXT)
    draw_center_ink(draw, fcx, fy1 - 220, "CE  RoHS  UL1034", f_sub, INK_DARK)
    draw_center_ink(draw, fcx, fy1 - 180, "SN: ES-9824-A", f_tiny, INK_SOFT)

    # 3. HOUSING SIDE SPECIFICATION LABEL (800 x 900)
    hx0, hy0, hx1, hy1 = REGION_HOUSING_SIDE
    draw.rectangle([hx0, hy0, hx1, hy1], fill=METAL_HOUSING)
    draw.rectangle([hx0 + 10, hy0 + 10, hx1 - 10, hy1 - 10], outline=(120, 130, 145, 255), width=3)
    # Metal plate backing
    lbl_x0, lbl_y0, lbl_x1, lbl_y1 = hx0 + 40, hy0 + 40, hx1 - 40, hy1 - 40
    draw.rectangle([lbl_x0, lbl_y0, lbl_x1, lbl_y1], fill=(240, 243, 246, 255))
    draw.rectangle([lbl_x0, lbl_y0, lbl_x1, lbl_y1], outline=(40, 45, 55, 255), width=4)

    hcx = (lbl_x0 + lbl_x1) // 2
    f_h1 = load_font(FONT_SANS, 36)
    f_h2 = load_font(FONT_MONO, 24)
    f_code = load_font(FONT_MONO, 20)

    draw_center_ink(draw, hcx, lbl_y0 + 25, "SEC-LOK SECURITY SYSTEMS", f_h1, INK_DARK)
    draw_center_ink(draw, hcx, lbl_y0 + 70, "ELECTRIC STRIKE - FAIL SECURE / FAIL SAFE", f_h2, INK_TEXT)
    draw.line([lbl_x0 + 30, lbl_y0 + 110, lbl_x1 - 30, lbl_y0 + 110], fill=INK_DARK, width=2)

    # Specs table
    specs = [
        "MODEL:        SEC-ES160-PRO",
        "INPUT VOLT:   12V DC / 24V AC +/- 10%",
        "CURRENT:      12V/280mA - 24V/140mA",
        "HOLDING FORCE: 800 kg / 1760 lbs",
        "ENDURANCE:    500,000 CYCLES TESTED",
        "MODE SELECT:  FAIL-SECURE (FIELD REVERSIBLE)",
        "STANDARDS:    CE / ANSI / BHMA A156.31"
    ]
    cur_y = lbl_y0 + 130
    for s in specs:
        draw_left_ink(draw, lbl_x0 + 40, cur_y, s, f_code, INK_DARK)
        cur_y += 36

    # Wiring diagram illustration
    diag_y0 = cur_y + 20
    diag_y1 = lbl_y1 - 100
    draw.rectangle([lbl_x0 + 40, diag_y0, lbl_x1 - 40, diag_y1], fill=(255, 255, 255, 255), outline=INK_TEXT, width=2)
    draw_left_ink(draw, lbl_x0 + 55, diag_y0 + 15, "WIRING & MODE SELECTION DIAGRAM:", f_code, INK_DARK)

    # Terminal blocks in diagram
    bx = lbl_x0 + 80
    by = diag_y0 + 55
    terms = ["+", "-", "NO", "COM", "NC"]
    for i, t in enumerate(terms):
        tx = bx + i * 115
        draw.rectangle([tx, by, tx + 85, by + 50], fill=(230, 235, 240, 255), outline=INK_DARK, width=2)
        draw_center_ink(draw, tx + 42, by + 12, t, f_code, INK_DARK)

    draw_left_ink(draw, lbl_x0 + 80, by + 75, "RED: 12V(+) | BLK: GND(-) | WHT: COM | GRN: NO | YEL: NC", f_tiny, INK_SOFT)

    # Bottom certification bar
    draw.line([lbl_x0 + 30, lbl_y1 - 70, lbl_x1 - 30, lbl_y1 - 70], fill=INK_DARK, width=2)
    draw_center_ink(draw, hcx, lbl_y1 - 50, "MADE FOR HEAVY COMMERCIAL ACCESS CONTROL - CE RoHS", f_code, INK_DARK)

    # 4. KEEPER JAW PLATE (500 x 960)
    kx0, ky0, kx1, ky1 = REGION_KEEPER
    draw.rectangle([kx0, ky0, kx1, ky1], fill=METAL_BASE)
    # Keeper serrations and grip grooves
    for y in range(ky0 + 40, ky1 - 40, 24):
        draw.line([kx0 + 30, y, kx1 - 30, y], fill=(160, 166, 175, 255), width=4)
        draw.line([kx0 + 30, y + 2, kx1 - 30, y + 2], fill=WHITE, width=2)
    draw.rectangle([kx0, ky0, kx1, ky1], outline=(110, 115, 125, 255), width=4)
    kcx = (kx0 + kx1) // 2
    draw_center_ink(draw, kcx, ky0 + 60, "HARDENED STAINLESS JAW", f_tiny, INK_DARK)
    draw_center_ink(draw, kcx, ky1 - 80, "LATCH GUIDE RAMP", f_tiny, INK_DARK)

    # 5. TERMINAL COVER (500 x 500)
    tx0, ty0, tx1, ty1 = REGION_TERMINAL
    draw.rectangle([tx0, ty0, tx1, ty1], fill=METAL_HOUSING)
    draw.rectangle([tx0 + 15, ty0 + 15, tx1 - 15, ty1 - 15], outline=(130, 140, 150, 255), width=3)
    tcx = (tx0 + tx1) // 2
    draw_center_ink(draw, tcx, ty0 + 40, "TERMINAL COVER", f_h2, WHITE)
    draw_center_ink(draw, tcx, ty0 + 80, "POWER & RELAY INTERFACE", f_tiny, (200, 210, 225, 255))

    # Screw markings on terminal cover
    draw_screw_head(draw, tx0 + 60, ty0 + 60, 18)
    draw_screw_head(draw, tx1 - 60, ty0 + 60, 18)
    draw_screw_head(draw, tx0 + 60, ty1 - 60, 18)
    draw_screw_head(draw, tx1 - 60, ty1 - 60, 18)

    # Port diagram
    for i, t in enumerate(["1: +12V", "2: GND", "3: LATCH_MON"]):
        draw_left_ink(draw, tx0 + 80, ty0 + 150 + i * 65, t, f_code, WHITE)

    img.save(ATLAS_PATH, "PNG")
    print(f"Atlas texture successfully generated: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

if __name__ == "__main__":
    build_atlas()
