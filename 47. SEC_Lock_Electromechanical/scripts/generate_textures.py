"""
=============================================================================
Security CCTV Asset Production Suite - Asset 47
Asset Name: SEC_Lock_Electromechanical (Elektromekanik Kapi Kilidi)
Texture Generation Script v1 (2048 x 2048)

ATLAS REGIONS:
    REGION_FACEPLATE   (64, 64)    - (464, 1984)   400 x 1920 px (24 x 160 mm faceplate)
    REGION_HOUSING_SIDE(520, 64)   - (1320, 964)   800 x 900 px (Solenoid spec label & wiring)
    REGION_LATCH       (520, 1024) - (1020, 1984)  500 x 960 px (Solid latch bolt face)
    REGION_SCREWS      (1080, 1024)- (1580, 1524)  500 x 500 px (Mounting screws & details)
    REGION_SWATCHES    (1080, 1560)- (2016, 2016)  Swatches & fills
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

REGION_FACEPLATE = (64, 64, 464, 1984)
REGION_HOUSING_SIDE = (520, 64, 1320, 964)
REGION_LATCH = (520, 1024, 1020, 1984)
REGION_SCREWS = (1080, 1024, 1580, 1524)
REGION_SWATCHES = (1080, 1560, 2016, 2016)

# Colors
METAL_BASE = (220, 224, 230, 255)
METAL_BRUSH = (212, 216, 222, 255)
METAL_DARK = (45, 50, 58, 255)
METAL_ZINC = (165, 172, 180, 255)
CHROME_HI = (250, 252, 255, 255)
INK_DARK = (22, 26, 32, 255)
INK_TEXT = (38, 44, 54, 255)
INK_SOFT = (85, 95, 110, 255)
ACCENT_GREEN = (32, 160, 64, 255)
ACCENT_RED = (200, 40, 32, 255)
ACCENT_AMBER = (220, 160, 24, 255)
WHITE = (255, 255, 255, 255)

_FONT_CACHE = {}

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

def draw_left_ink(draw, x, ink_top, text, font, fill):
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    draw.text((x - l, ink_top - t), text, font=font, fill=fill)
    return (x, ink_top, x + (r - l), ink_top + (b - t))

def draw_center_ink(draw, cx, ink_top, text, font, fill):
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    w = r - l
    x = cx - w / 2.0
    draw.text((x - l, ink_top - t), text, font=font, fill=fill)
    return (x, ink_top, x + w, ink_top + (b - t))

def draw_screw_head(draw, cx, cy, radius):
    for r in range(radius, 0, -1):
        ratio = r / float(radius)
        c = int(145 + 75 * ratio)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(c, c + 2, c + 5, 255))
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=(95, 100, 108, 255), width=3)
    sw = max(2, radius // 5)
    sl = int(radius * 0.72)
    draw.line([cx - sl, cy, cx + sl, cy], fill=(35, 40, 48, 255), width=sw)
    draw.line([cx, cy - sl, cx, cy + sl], fill=(35, 40, 48, 255), width=sw)
    draw.line([cx - sl, cy + 1, cx + sl, cy + 1], fill=(230, 235, 240, 255), width=1)
    draw.line([cx + 1, cy - sl, cx + 1, cy + sl], fill=(230, 235, 240, 255), width=1)

def build_atlas():
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), (35, 38, 44, 255))
    draw = ImageDraw.Draw(img)

    # 1. Swatches
    sx0, sy0, sx1, sy1 = REGION_SWATCHES
    draw.rectangle([sx0, sy0, sx1, sy1], fill=(50, 55, 62, 255))
    draw.rectangle([sx0 + 20, sy0 + 20, sx1 - 20, sy0 + 100], fill=METAL_BASE)
    draw.rectangle([sx0 + 20, sy0 + 120, sx1 - 20, sy0 + 200], fill=METAL_BRUSH)
    draw.rectangle([sx0 + 20, sy0 + 220, sx1 - 20, sy0 + 300], fill=METAL_ZINC)
    draw.rectangle([sx0 + 20, sy0 + 320, sx1 - 20, sy0 + 400], fill=(25, 28, 32, 255))

    # 2. FACEPLATE (400 x 1920)
    fx0, fy0, fx1, fy1 = REGION_FACEPLATE
    draw.rectangle([fx0, fy0, fx1, fy1], fill=METAL_BASE)
    for y in range(fy0, fy1, 6):
        shade = 214 + (y % 11)
        draw.line([fx0 + 4, y, fx1 - 4, y], fill=(shade, shade + 2, shade + 5, 255), width=2)
    draw.rectangle([fx0, fy0, fx1, fy1], outline=(150, 155, 165, 255), width=4)
    draw.rectangle([fx0 + 4, fy0 + 4, fx1 - 4, fy1 - 4], outline=(245, 248, 252, 255), width=2)

    fcx = (fx0 + fx1) // 2

    # Screw locator markings on faceplate (screws will sit directly over these at Z = +/- 0.0700m)
    draw_screw_head(draw, fcx, fy0 + 120, 36)
    draw_screw_head(draw, fcx, fy1 - 120, 36)

    # Top text
    f_brand = load_font(FONT_SANS, 34)
    f_sub = load_font(FONT_MONO, 22)
    f_tiny = load_font(FONT_MONO, 18)

    draw_center_ink(draw, fcx, fy0 + 195, "SEC-LOK", f_brand, INK_DARK)
    draw_center_ink(draw, fcx, fy0 + 240, "ELECTROMECHANICAL", f_sub, INK_TEXT)
    draw_center_ink(draw, fcx, fy0 + 275, "ANSI GRADE 1 MORTISE", f_tiny, INK_SOFT)
    draw.line([fcx - 120, fy0 + 305, fcx + 120, fy0 + 305], fill=(160, 166, 175, 255), width=3)
    draw.line([fcx - 120, fy0 + 307, fcx + 120, fy0 + 307], fill=WHITE, width=1)

    # Central Latch Slot cutout preview
    cut_w = 240
    cut_h = 480
    cut_y0 = (fy0 + fy1) // 2 - cut_h // 2
    cut_y1 = cut_y0 + cut_h
    cut_x0 = fcx - cut_w // 2
    cut_x1 = fcx + cut_w // 2

    draw.rectangle([cut_x0, cut_y0, cut_x1, cut_y1], fill=(25, 28, 34, 255))
    draw.rectangle([cut_x0, cut_y0, cut_x1, cut_y1], outline=(110, 116, 126, 255), width=4)
    draw_center_ink(draw, fcx, (cut_y0 + cut_y1) // 2 - 12, "LATCH SLOT", f_tiny, (110, 120, 135, 255))

    # Bottom markings
    draw.line([fcx - 120, fy1 - 290, fcx + 120, fy1 - 290], fill=(160, 166, 175, 255), width=3)
    draw.line([fcx - 120, fy1 - 288, fcx + 120, fy1 - 288], fill=WHITE, width=1)
    draw_center_ink(draw, fcx, fy1 - 275, "12V DC  0.35A", f_sub, INK_DARK)
    draw_center_ink(draw, fcx, fy1 - 245, "SOLENOID DRIVEN", f_tiny, INK_TEXT)
    draw_center_ink(draw, fcx, fy1 - 220, "CE  RoHS  UL-10C", f_sub, INK_DARK)
    draw_center_ink(draw, fcx, fy1 - 180, "MODEL: EM-240-PRO", f_tiny, INK_SOFT)

    # 3. HOUSING SIDE (Solenoid case label & diagram)
    hx0, hy0, hx1, hy1 = REGION_HOUSING_SIDE
    draw.rectangle([hx0, hy0, hx1, hy1], fill=METAL_ZINC)
    draw.rectangle([hx0 + 12, hy0 + 12, hx1 - 12, hy1 - 12], outline=(120, 128, 138, 255), width=3)

    lbl_x0, lbl_y0, lbl_x1, lbl_y1 = hx0 + 40, hy0 + 40, hx1 - 40, hy1 - 40
    draw.rectangle([lbl_x0, lbl_y0, lbl_x1, lbl_y1], fill=(242, 245, 248, 255))
    draw.rectangle([lbl_x0, lbl_y0, lbl_x1, lbl_y1], outline=(40, 45, 55, 255), width=4)

    hcx = (lbl_x0 + lbl_x1) // 2
    f_h1 = load_font(FONT_SANS, 34)
    f_h2 = load_font(FONT_MONO, 22)
    f_code = load_font(FONT_MONO, 20)

    draw_center_ink(draw, hcx, lbl_y0 + 25, "SEC-LOK MORTISE LOCKSET", f_h1, INK_DARK)
    draw_center_ink(draw, hcx, lbl_y0 + 68, "CONTINUOUS DUTY ELECTROMECHANICAL LOCK", f_h2, INK_TEXT)
    draw.line([lbl_x0 + 30, lbl_y0 + 105, lbl_x1 - 30, lbl_y0 + 105], fill=INK_DARK, width=2)

    specs = [
        "TYPE:         FAIL-SECURE SOLENOID MORTISE",
        "INPUT:        12V DC +/- 10% (0.35A NOMINAL)",
        "LATCH BOLT:   SOLID STAINLESS STEEL (19mm THROW)",
        "STATUS SENSOR:INTERNAL LATCH MONITOR SWITCH",
        "BACKSET:      60 mm (2-3/8 in) STANDARD",
        "CYCLE RATING: 1,000,000 OPERATIONS UL CERTIFIED"
    ]
    cur_y = lbl_y0 + 125
    for s in specs:
        draw_left_ink(draw, lbl_x0 + 40, cur_y, s, f_code, INK_DARK)
        cur_y += 36

    # Wiring diagram
    diag_y0 = cur_y + 20
    diag_y1 = lbl_y1 - 90
    draw.rectangle([lbl_x0 + 40, diag_y0, lbl_x1 - 40, diag_y1], fill=WHITE, outline=INK_TEXT, width=2)
    draw_left_ink(draw, lbl_x0 + 55, diag_y0 + 15, "TERMINAL CONNECTION DIAGRAM:", f_code, INK_DARK)

    terms = ["SOL (+)", "SOL (-)", "SW COM", "SW NO", "SW NC"]
    bx = lbl_x0 + 65
    by = diag_y0 + 55
    for i, t in enumerate(terms):
        tx = bx + i * 118
        draw.rectangle([tx, by, tx + 95, by + 50], fill=(232, 238, 244, 255), outline=INK_DARK, width=2)
        draw_center_ink(draw, tx + 47, by + 12, t, f_code, INK_DARK)

    draw_left_ink(draw, lbl_x0 + 65, by + 75, "SOLENOID: 12V DC | SWITCH: 30V DC 1A MAX STATUS SIGNAL", f_tiny, INK_SOFT)

    draw.line([lbl_x0 + 30, lbl_y1 - 65, lbl_x1 - 30, lbl_y1 - 65], fill=INK_DARK, width=2)
    draw_center_ink(draw, hcx, lbl_y1 - 45, "MADE FOR COMMERCIAL SECURITY ACCESS CONTROL - CE RoHS", f_code, INK_DARK)

    # 4. LATCH BOLT (500 x 960)
    lx0, ly0, lx1, ly1 = REGION_LATCH
    draw.rectangle([lx0, ly0, lx1, ly1], fill=METAL_BASE)
    for y in range(ly0, ly1, 8):
        c = 210 + (y % 15)
        draw.line([lx0 + 10, y, lx1 - 10, y], fill=(c, c + 2, c + 5, 255), width=3)
    draw.rectangle([lx0, ly0, lx1, ly1], outline=(120, 126, 135, 255), width=4)
    lcx = (lx0 + lx1) // 2
    draw_center_ink(draw, lcx, ly0 + 50, "SOLID STEEL LATCH", f_sub, INK_DARK)
    draw_center_ink(draw, lcx, ly1 - 70, "BEVELED STRIKE FACE", f_tiny, INK_SOFT)

    # 5. SCREWS & HARDWARE (500 x 500)
    scx0, scy0, scx1, scy1 = REGION_SCREWS
    draw.rectangle([scx0, scy0, scx1, scy1], fill=METAL_BRUSH)
    draw_screw_head(draw, scx0 + 150, scy0 + 150, 100)
    draw_screw_head(draw, scx0 + 350, scy0 + 350, 100)

    img.save(ATLAS_PATH, "PNG")
    print(f"Atlas texture generated: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

if __name__ == "__main__":
    build_atlas()
