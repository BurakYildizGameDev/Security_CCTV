"""
=============================================================================
Security CCTV Asset Production Suite - Asset 49
Asset Name: SEC_Lock_Rack_Cabinet (Guvenlik Rack Kabini)
Texture Generation Script v1 (2048 x 2048)

ATLAS REGIONS:
    REGION_DOOR        (64, 64)    - (1024, 1984)  960 x 1920 px (Front door, lock, perf mesh)
    REGION_SIDE_PANEL  (1080, 64)  - (1720, 1280)  640 x 1216 px (Side panel with vents & latch)
    REGION_TOP_FAN     (1080, 1340)- (1720, 1984)  640 x 644 px (Roof exhaust fan vents)
    REGION_SWATCHES    (1760, 64)  - (2016, 2016)  Anthracite texture, 19in rails, hardware
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

REGION_DOOR = (64, 64, 1024, 1984)
REGION_SIDE_PANEL = (1080, 64, 1720, 1280)
REGION_TOP_FAN = (1080, 1340, 1720, 1984)
REGION_SWATCHES = (1760, 64, 2016, 2016)

# Colors (Endustriyel Guvenlik Rack Paleti - RAL 7016 Antrasit)
RACK_DARK = (36, 40, 46, 255)
RACK_MID = (46, 52, 60, 255)
RACK_LIGHT = (65, 72, 82, 255)
MESH_DARK = (24, 26, 30, 255)
METAL_RAIL = (180, 186, 195, 255)
LOCK_CHROME = (220, 225, 232, 255)
ACCENT_BLUE = (35, 120, 220, 255)
ACCENT_GREEN = (40, 180, 70, 255)
ACCENT_AMBER = (220, 160, 25, 255)
WHITE = (255, 255, 255, 255)
INK_TEXT = (210, 218, 228, 255)
INK_SOFT = (140, 150, 165, 255)

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

def build_atlas():
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), (28, 30, 35, 255))
    draw = ImageDraw.Draw(img)

    # 1. Swatches (Right column)
    sx0, sy0, sx1, sy1 = REGION_SWATCHES
    draw.rectangle([sx0, sy0, sx1, sy1], fill=RACK_DARK)
    draw.rectangle([sx0 + 20, sy0 + 20, sx1 - 20, sy0 + 400], fill=RACK_MID)
    draw.rectangle([sx0 + 20, sy0 + 420, sx1 - 20, sy0 + 800], fill=RACK_LIGHT)
    draw.rectangle([sx0 + 20, sy0 + 820, sx1 - 20, sy0 + 1200], fill=METAL_RAIL)
    draw.rectangle([sx0 + 20, sy0 + 1220, sx1 - 20, sy0 + 1600], fill=MESH_DARK)
    draw.rectangle([sx0 + 20, sy0 + 1620, sx1 - 20, sy1 - 20], fill=LOCK_CHROME)

    # 2. FRONT DOOR (960 x 1920)
    dx0, dy0, dx1, dy1 = REGION_DOOR
    draw.rectangle([dx0, dy0, dx1, dy1], fill=RACK_MID)
    # Heavy outer frame bevel
    draw.rectangle([dx0, dy0, dx1, dy1], outline=(20, 22, 26, 255), width=6)
    draw.rectangle([dx0 + 6, dy0 + 6, dx1 - 6, dy1 - 6], outline=RACK_LIGHT, width=3)

    # Top Brand Bar on Door
    dcx = (dx0 + dx1) // 2
    f_h1 = load_font(FONT_SANS, 38)
    f_h2 = load_font(FONT_MONO, 24)
    f_code = load_font(FONT_MONO, 18)

    draw.rectangle([dx0 + 25, dy0 + 25, dx1 - 25, dy0 + 150], fill=RACK_DARK, outline=RACK_LIGHT, width=2)
    draw_center_ink(draw, dcx, dy0 + 40, "SEC-LOK INFRASTRUCTURE", f_h1, WHITE)
    draw_center_ink(draw, dcx, dy0 + 88, "19-INCH INDUSTRIAL CCTV SERVER ENCLOSURE", f_h2, ACCENT_BLUE)
    draw_center_ink(draw, dcx, dy0 + 120, "MODEL: SR-18U-6060  |  MAX LOAD 800 KG  |  IP20 / EN 60529", f_code, INK_SOFT)

    # Perforated Hexagonal Mesh Center Window (dy0 + 170 to dy1 - 170, dx0 + 40 to dx1 - 180)
    # Leaving space on the right for the electronic lock handle
    mx0 = dx0 + 50
    my0 = dy0 + 170
    mx1 = dx1 - 190
    my1 = dy1 - 170

    draw.rectangle([mx0, my0, mx1, my1], fill=MESH_DARK, outline=(20, 22, 26, 255), width=4)
    # Hex vent pattern imitation
    for y in range(my0 + 12, my1 - 12, 16):
        shift = 8 if (y // 16) % 2 == 1 else 0
        for x in range(mx0 + 12 + shift, mx1 - 12, 16):
            draw.rectangle([x, y, x + 7, y + 7], fill=(42, 46, 54, 255))

    # Rack Unit Height Rulers (1U .. 18U) along the mesh inner sides
    f_u = load_font(FONT_MONO, 15)
    u_h = (my1 - my0) / 18.0
    for u in range(1, 19):
        uy = my1 - int(u * u_h) + 6
        draw_left_ink(draw, mx0 + 12, uy, f"{u:02d}U", f_u, METAL_RAIL)
        draw_left_ink(draw, mx1 - 38, uy, f"{u:02d}U", f_u, METAL_RAIL)

    # Swing Handle Lock on right stile (dx1 - 170 to dx1 - 30)
    lx0 = dx1 - 165
    ly0 = (dy0 + dy1) // 2 - 300
    lx1 = dx1 - 35
    ly1 = ly0 + 600

    draw.rectangle([lx0, ly0, lx1, ly1], fill=RACK_DARK, outline=(15, 18, 22, 255), width=4)
    draw.rectangle([lx0 + 6, ly0 + 6, lx1 - 6, ly1 - 6], outline=(75, 82, 92, 255), width=2)

    lcx = (lx0 + lx1) // 2
    # Lock brand & digital display
    draw_center_ink(draw, lcx, ly0 + 20, "SEC-LOK", load_font(FONT_SANS, 22), WHITE)
    draw_center_ink(draw, lcx, ly0 + 45, "DIGITAL CAM", load_font(FONT_MONO, 14), ACCENT_BLUE)

    # Keypad & RFID zone
    disp_y0 = ly0 + 75
    draw.rectangle([lx0 + 15, disp_y0, lx1 - 15, disp_y0 + 90], fill=(15, 18, 22, 255), outline=ACCENT_BLUE, width=2)
    draw_center_ink(draw, lcx, disp_y0 + 20, "CARD / PIN", load_font(FONT_MONO, 18), ACCENT_GREEN)
    draw_center_ink(draw, lcx, disp_y0 + 55, "[ LOCKED ]", load_font(FONT_MONO, 16), (220, 40, 30, 255))

    # Swing handle lever body
    lever_y0 = disp_y0 + 115
    lever_y1 = ly1 - 60
    draw.rectangle([lx0 + 20, lever_y0, lx1 - 20, lever_y1], fill=LOCK_CHROME, outline=(50, 55, 62, 255), width=3)
    draw.line([lcx, lever_y0 + 30, lcx, lever_y1 - 30], fill=(140, 148, 158, 255), width=4)

    # Key cylinder override
    cyl_y = lever_y1 - 50
    draw.ellipse([lcx - 18, cyl_y - 18, lcx + 18, cyl_y + 18], fill=(30, 34, 40, 255), outline=LOCK_CHROME, width=2)
    draw.rectangle([lcx - 3, cyl_y - 10, lcx + 3, cyl_y + 10], fill=(10, 12, 15, 255))

    # Bottom Certification Bar on Door
    draw.rectangle([dx0 + 25, dy1 - 150, dx1 - 25, dy1 - 25], fill=RACK_DARK, outline=RACK_LIGHT, width=2)
    draw_center_ink(draw, dcx, dy1 - 135, "EARTHING & GROUNDING COMPLIANT: EN 60950-1", f_code, ACCENT_AMBER)
    draw_center_ink(draw, dcx, dy1 - 105, "CE  RoHS  REACH  EIA-310-D  IEC 60297-3", f_h2, INK_TEXT)
    draw_center_ink(draw, dcx, dy1 - 70, "WARNING: RESTRICTED ACCESS AREA - AUTHORIZED SERVICE ONLY", f_code, INK_SOFT)

    # 3. SIDE PANEL (640 x 1216)
    px0, py0, px1, py1 = REGION_SIDE_PANEL
    draw.rectangle([px0, py0, px1, py1], fill=RACK_MID)
    draw.rectangle([px0, py0, px1, py1], outline=(20, 22, 26, 255), width=5)
    draw.rectangle([px0 + 6, py0 + 6, px1 - 6, py1 - 6], outline=RACK_LIGHT, width=2)

    pcx = (px0 + px1) // 2
    # Top quick-release slam latch
    draw.rectangle([pcx - 50, py0 + 40, pcx + 50, py0 + 110], fill=RACK_DARK, outline=(15, 18, 22, 255), width=3)
    draw_center_ink(draw, pcx, py0 + 55, "PULL LATCH", f_code, INK_SOFT)
    draw.ellipse([pcx - 12, py0 + 82, pcx + 12, py0 + 106], fill=(18, 20, 24, 255))

    # Cooling louvers (vent slots) in two banks
    for bank_y in [py0 + 160, py0 + 650]:
        draw.rectangle([px0 + 50, bank_y, px1 - 50, bank_y + 360], fill=RACK_DARK, outline=(20, 22, 26, 255), width=3)
        draw_center_ink(draw, pcx, bank_y + 12, "VENTILATION SLOTS", f_code, INK_SOFT)
        for ly in range(bank_y + 45, bank_y + 340, 18):
            draw.rectangle([px0 + 70, ly, px1 - 70, ly + 8], fill=(15, 18, 22, 255), outline=RACK_LIGHT, width=1)

    # Grounding warning at bottom
    draw_center_ink(draw, pcx, py1 - 60, "CHASSIS GROUND CONNECTION STUD INSIDE", f_code, ACCENT_AMBER)

    # 4. ROOF TOP FAN EXHAUST (640 x 644)
    rx0, ry0, rx1, ry1 = REGION_TOP_FAN
    draw.rectangle([rx0, ry0, rx1, ry1], fill=RACK_MID)
    draw.rectangle([rx0, ry0, rx1, ry1], outline=(20, 22, 26, 255), width=4)
    rcx = (rx0 + rx1) // 2
    rcy = (ry0 + ry1) // 2

    draw_center_ink(draw, rcx, ry0 + 30, "DUAL 120mm THERMOSTAT EXHAUST FANS", f_h2, INK_TEXT)
    # Dual fan circles
    for fc in [rcx - 150, rcx + 150]:
        draw.ellipse([fc - 110, rcy - 110, fc + 110, rcy + 110], fill=RACK_DARK, outline=(15, 18, 22, 255), width=4)
        for r in range(95, 20, -20):
            draw.ellipse([fc - r, rcy - r, fc + r, rcy + r], outline=RACK_LIGHT, width=2)
        draw.ellipse([fc - 25, rcy - 25, fc + 25, rcy + 25], fill=MESH_DARK)

    # Cable gland brush strip at rear
    draw.rectangle([rx0 + 80, ry1 - 90, rx1 - 80, ry1 - 40], fill=MESH_DARK, outline=RACK_LIGHT, width=2)
    draw_center_ink(draw, rcx, ry1 - 72, "CABLE ENTRY BRUSH STRIP", f_code, WHITE)

    img.save(ATLAS_PATH, "PNG")
    print(f"Atlas texture generated: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

if __name__ == "__main__":
    build_atlas()
