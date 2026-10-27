"""
=============================================================================
Security CCTV Asset Production Suite - Asset 48
Asset Name: SEC_Lock_Door_Closer (Kapi Kapatici Mekanizma)
Texture Generation Script v1 (2048 x 2048)

ATLAS REGIONS:
    REGION_BODY_FRONT  (64, 64)    - (1984, 564)   1920 x 500 px (Closer front & valve plate)
    REGION_BODY_TOP    (64, 620)   - (1984, 1020)  1920 x 400 px (Closer top & spindle hub)
    REGION_ARMS        (64, 1080)  - (1080, 1580)  1016 x 500 px (Articulated arm textures)
    REGION_BRACKET     (1140, 1080)- (1640, 1580)  500 x 500 px (Frame shoe mounting bracket)
    REGION_SWATCHES    (64, 1640)  - (2016, 2016)  Swatches & plain metallic fills
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

REGION_BODY_FRONT = (64, 64, 1984, 564)
REGION_BODY_TOP = (64, 620, 1984, 1020)
REGION_ARMS = (64, 1080, 1080, 1580)
REGION_BRACKET = (1140, 1080, 1640, 1580)
REGION_SWATCHES = (64, 1640, 2016, 2016)

# Colors
ALUM_LIGHT = (222, 226, 232, 255)
ALUM_BASE = (205, 210, 218, 255)
ALUM_DARK = (165, 172, 180, 255)
STEEL_DARK = (55, 60, 68, 255)
BRASS_VALVE = (210, 175, 75, 255)
INK_DARK = (20, 24, 30, 255)
INK_TEXT = (38, 44, 54, 255)
INK_SOFT = (85, 95, 110, 255)
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

def draw_valve(draw, cx, cy, radius, label):
    # Recessed circular port
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(45, 50, 58, 255), outline=(130, 138, 148, 255), width=3)
    # Brass needle screw
    r_in = radius - 6
    draw.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], fill=BRASS_VALVE, outline=(150, 120, 40, 255), width=2)
    # Slotted screwdriver drive
    draw.line([cx - r_in + 4, cy, cx + r_in - 4, cy], fill=(30, 25, 10, 255), width=4)
    # Label
    f_vl = load_font(FONT_MONO, 18)
    draw_center_ink(draw, cx, cy + radius + 8, label, f_vl, INK_DARK)

def build_atlas():
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), (35, 38, 44, 255))
    draw = ImageDraw.Draw(img)

    # 1. Swatches (Bottom)
    sx0, sy0, sx1, sy1 = REGION_SWATCHES
    draw.rectangle([sx0, sy0, sx1, sy1], fill=(50, 55, 62, 255))
    draw.rectangle([sx0 + 20, sy0 + 20, sx0 + 400, sy1 - 20], fill=ALUM_BASE)
    draw.rectangle([sx0 + 420, sy0 + 20, sx0 + 800, sy1 - 20], fill=ALUM_LIGHT)
    draw.rectangle([sx0 + 820, sy0 + 20, sx0 + 1200, sy1 - 20], fill=ALUM_DARK)
    draw.rectangle([sx0 + 1220, sy0 + 20, sx0 + 1600, sy1 - 20], fill=STEEL_DARK)
    draw.rectangle([sx0 + 1620, sy0 + 20, sx1 - 20, sy1 - 20], fill=BRASS_VALVE)

    # 2. BODY FRONT (1920 x 500)
    bx0, by0, bx1, by1 = REGION_BODY_FRONT
    draw.rectangle([bx0, by0, bx1, by1], fill=ALUM_BASE)
    # Horizontal brushed lines
    for y in range(by0, by1, 5):
        c = 205 + (y % 12)
        draw.line([bx0 + 6, y, bx1 - 6, y], fill=(c, c + 2, c + 5, 255), width=2)
    # Chamfer borders
    draw.rectangle([bx0, by0, bx1, by1], outline=(140, 146, 156, 255), width=4)
    draw.rectangle([bx0 + 6, by0 + 6, bx1 - 6, by1 - 6], outline=(240, 245, 252, 255), width=2)

    # Mounting screw indicators on far left & right flanges
    draw_screw_head(draw, bx0 + 60, by0 + 100, 32)
    draw_screw_head(draw, bx0 + 60, by1 - 100, 32)
    draw_screw_head(draw, bx1 - 60, by0 + 100, 32)
    draw_screw_head(draw, bx1 - 60, by1 - 100, 32)

    # Left Section: SEC-LOK Branding & Certifications
    f_brand = load_font(FONT_SANS, 48)
    f_sub = load_font(FONT_MONO, 26)
    f_code = load_font(FONT_MONO, 20)

    draw_left_ink(draw, bx0 + 160, by0 + 110, "SEC-LOK HARDWARE", f_brand, INK_DARK)
    draw_left_ink(draw, bx0 + 160, by0 + 175, "HEAVY DUTY HYDRAULIC DOOR CLOSER", f_sub, INK_TEXT)
    draw_left_ink(draw, bx0 + 160, by0 + 220, "SERIES DC-480 / ADJUSTABLE POWER EN 2-4", f_code, INK_SOFT)
    draw_left_ink(draw, bx0 + 160, by0 + 255, "ANSI/BHMA A156.4 GRADE 1 - UL 10C 3HR FIRE RATED", f_code, INK_DARK)
    draw_left_ink(draw, bx0 + 160, by0 + 295, "CE 1121 - CERTIFIRE CF 521 - ROHS COMPLIANT", f_code, INK_SOFT)

    draw.line([bx0 + 160, by0 + 340, bx0 + 950, by0 + 340], fill=(150, 156, 166, 255), width=3)
    draw.line([bx0 + 160, by0 + 342, bx0 + 950, by0 + 342], fill=WHITE, width=1)
    draw_left_ink(draw, bx0 + 160, by0 + 360, "NON-HANDED / UNIVERSAL APPLICATION (REGULAR, TOP JAMB, PARALLEL)", f_code, INK_DARK)

    # Right Section: Hydraulic Adjustment Valve Cluster
    vx_start = bx0 + 1200
    vy_valves = by0 + 200
    draw.rectangle([vx_start - 40, by0 + 50, bx1 - 140, by1 - 50], fill=(225, 230, 238, 255), outline=(130, 138, 148, 255), width=3)
    draw_center_ink(draw, (vx_start - 40 + bx1 - 140) // 2, by0 + 75, "SPEED ADJUSTMENT VALVES", f_sub, INK_DARK)

    # 3 Adjustment Valves: 1: Sweep, 2: Latch, 3: Backcheck
    valves = [
        ("1: SWEEP", vx_start + 60),
        ("2: LATCH", vx_start + 260),
        ("3: BC",    vx_start + 460)
    ]
    for v_name, cx in valves:
        draw_valve(draw, cx, vy_valves, 32, v_name)

    draw_center_ink(draw, (vx_start - 40 + bx1 - 140) // 2, by1 - 100, "(+) SLOWER  /  (-) FASTER", f_code, INK_TEXT)

    # 3. BODY TOP (1920 x 400)
    tx0, ty0, tx1, ty1 = REGION_BODY_TOP
    draw.rectangle([tx0, ty0, tx1, ty1], fill=ALUM_BASE)
    for y in range(ty0, ty1, 5):
        c = 208 + (y % 10)
        draw.line([tx0 + 6, y, tx1 - 6, y], fill=(c, c + 2, c + 5, 255), width=2)
    draw.rectangle([tx0, ty0, tx1, ty1], outline=(140, 146, 156, 255), width=4)

    # Spindle Hub indicator at top left (corresponds to physical Arm_Pivot_A at X = +0.060)
    hub_cx = tx0 + int(0.20 * (tx1 - tx0))
    hub_cy = ty0 + int((1.0 - 0.615) * (ty1 - ty0))
    draw.ellipse([hub_cx - 90, hub_cy - 90, hub_cx + 90, hub_cy + 90], fill=ALUM_DARK, outline=STEEL_DARK, width=4)
    draw.ellipse([hub_cx - 50, hub_cy - 50, hub_cx + 50, hub_cy + 50], fill=STEEL_DARK, outline=(180, 186, 196, 255), width=3)
    draw_center_ink(draw, hub_cx, hub_cy - 12, "PINION", f_code, WHITE)

    # Caution label on top right (above adjustment valves)
    draw_center_ink(draw, tx1 - 600, ty0 + 130, "CAUTION: HIGH SPRING TENSION", f_sub, (180, 30, 20, 255))
    draw_center_ink(draw, tx1 - 600, ty0 + 180, "DO NOT REMOVE END CAPS OR OVER-UNSCREW VALVES", f_code, INK_DARK)
    draw_center_ink(draw, tx1 - 600, ty0 + 220, "FACTORY SEALED HYDRAULIC FLUID UNIT", f_code, INK_SOFT)

    # 4. ARMS TEXTURE (1016 x 500)
    ax0, ay0, ax1, ay1 = REGION_ARMS
    draw.rectangle([ax0, ay0, ax1, ay1], fill=ALUM_LIGHT)
    for y in range(ay0, ay1, 6):
        c = 216 + (y % 10)
        draw.line([ax0 + 4, y, ax1 - 4, y], fill=(c, c + 2, c + 4, 255), width=2)
    draw.rectangle([ax0, ay0, ax1, ay1], outline=(130, 136, 146, 255), width=3)
    # Stamped text on main arm
    draw_center_ink(draw, (ax0 + ax1) // 2, ay0 + 180, "SEC-LOK FORGED STEEL ARM", f_sub, INK_DARK)
    draw_center_ink(draw, (ax0 + ax1) // 2, ay0 + 230, "PATENT PENDING - ASSEMBLE PINION ARROW TOWARDS HINGE", f_code, INK_SOFT)

    # 5. FRAME SHOE BRACKET (500 x 500)
    kx0, ky0, kx1, ky1 = REGION_BRACKET
    draw.rectangle([kx0, ky0, kx1, ky1], fill=ALUM_BASE)
    draw.rectangle([kx0 + 10, ky0 + 10, kx1 - 10, ky1 - 10], outline=(130, 136, 146, 255), width=3)
    kcx = (kx0 + kx1) // 2
    draw_center_ink(draw, kcx, ky0 + 50, "FRAME SHOE BRACKET", f_sub, INK_DARK)
    draw_screw_head(draw, kcx - 120, ky0 + 250, 45)
    draw_screw_head(draw, kcx + 120, ky0 + 250, 45)
    draw_center_ink(draw, kcx, ky1 - 80, "TOP JAMB / DOOR FRAME MOUNT", f_code, INK_SOFT)

    img.save(ATLAS_PATH, "PNG")
    print(f"Atlas texture generated: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

if __name__ == "__main__":
    build_atlas()
