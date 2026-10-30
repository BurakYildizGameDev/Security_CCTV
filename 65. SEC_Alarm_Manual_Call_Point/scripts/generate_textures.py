"""
Security CCTV Asset Production Suite - Asset 65
Asset Name: SEC_Alarm_Manual_Call_Point (Manual Fire Alarm Break-Glass Call Point)
Ultra-Realistic High-Resolution Texture Atlas Generator (2048x2048)
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
FONT_SANS_REG = r"C:\Windows\Fonts\arial.ttf"

ATLAS_W, ATLAS_H = 2048, 2048

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

def draw_center_text(draw, cx, cy, text, font, fill):
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = cx - w // 2 - bbox[0]
    y = cy - h // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=fill)

def generate_atlas():
    # Base safety red flame-retardant UV-stabilized polymer
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), (195, 22, 28, 255))
    draw = ImageDraw.Draw(img)

    # Subtle injection-molded polymer grain
    for y in range(0, ATLAS_H, 3):
        tint = (y * 5) % 6 - 3
        draw.line([(0, y), (ATLAS_W, y)], fill=(195 + tint, 22 + tint, 28 + tint, 255), width=1)

    # =========================================================================
    # 1. FRONT HOUSING CASING (50, 50) to (1050, 1050) -> 1000 x 1000 px
    # Square 88mm x 88mm front bezel with beveled chamfers and top display banner
    # =========================================================================
    fx0, fy0, fx1, fy1 = 50, 50, 1050, 1050
    draw.rectangle([fx0, fy0, fx1, fy1], fill=(195, 22, 28, 255), outline=(135, 14, 18, 255), width=6)

    # Outer beveled highlights
    draw.line([(fx0 + 8, fy0 + 8), (fx1 - 8, fy0 + 8)], fill=(235, 55, 62, 255), width=5)
    draw.line([(fx0 + 8, fy0 + 8), (fx0 + 8, fy1 - 8)], fill=(235, 55, 62, 255), width=5)
    draw.line([(fx0 + 8, fy1 - 8), (fx1 - 8, fy1 - 8)], fill=(110, 10, 14, 255), width=5)
    draw.line([(fx1 - 8, fy0 + 8), (fx1 - 8, fy1 - 8)], fill=(110, 10, 14, 255), width=5)

    # Top Brand & Symbol Banner (fy0+40 to fy0+170)
    draw.rectangle([fx0 + 40, fy0 + 40, fx1 - 40, fy0 + 170], fill=(22, 25, 30, 255), outline=(140, 16, 20, 255), width=3)
    
    # ISO Fire Flame Symbol in Yellow Triangle
    tri_cx = fx0 + 110
    tri_cy = fy0 + 105
    draw.polygon([(tri_cx, tri_cy - 42), (tri_cx + 38, tri_cy + 34), (tri_cx - 38, tri_cy + 34)], fill=(245, 195, 25, 255), outline=(20, 20, 20, 255))
    draw.polygon([(tri_cx, tri_cy - 20), (tri_cx + 18, tri_cy + 24), (tri_cx - 18, tri_cy + 24)], fill=(225, 30, 30, 255))

    draw.text((fx0 + 175, fy0 + 58), "FIRE ALARM", fill=(255, 255, 255, 255), font=load_font(FONT_SANS, 40))
    draw.text((fx0 + 175, fy0 + 115), "SEC-FIRE MCP-01  •  EN 54-11 TYPE A (INDOOR)", fill=(245, 195, 35, 255), font=load_font(FONT_MONO, 17))

    # Top Alarm LED Surround Ring
    led_cx = fx1 - 120
    led_cy = fy0 + 105
    draw.ellipse([led_cx - 22, led_cy - 22, led_cx + 22, led_cy + 22], fill=(35, 40, 48, 255), outline=(180, 190, 205, 255), width=2)
    draw.ellipse([led_cx - 14, led_cy - 14, led_cx + 14, led_cy + 14], fill=(235, 35, 40, 255), outline=(255, 120, 120, 255), width=2)
    draw_center_text(draw, led_cx, fy0 + 145, "ALARM", load_font(FONT_MONO, 12), (220, 225, 235, 255))

    # Recessed Pocket Cavity Surrounding (fx0+60 to fx1-60, fy0+210 to fy1-160)
    # Deep matte black gasket and bevel
    px0, py0, px1, py1 = fx0 + 60, fy0 + 210, fx1 - 60, fy1 - 160
    draw.rectangle([px0, py0, px1, py1], fill=(16, 18, 22, 255), outline=(80, 90, 105, 255), width=4)

    # Bottom Lower Lip Bezel Instructions (fy1-140 to fy1-35)
    draw.rectangle([fx0 + 40, fy1 - 140, fx1 - 40, fy1 - 35], fill=(24, 26, 32, 255), outline=(130, 15, 20, 255), width=2)
    draw_center_text(draw, (fx0 + fx1)//2, fy1 - 105, "OPERATING INSTRUCTIONS: LIFT COVER • PUSH TARGET ELEMENT", load_font(FONT_SANS, 17), (255, 255, 255, 255))
    draw_center_text(draw, (fx0 + fx1)//2, fy1 - 68, "EN 54-11:2001 | ISO 7240-11 | LPCB CERTIFIED | CE 0832 | IP24D", load_font(FONT_MONO, 14), (245, 195, 35, 255))

    # =========================================================================
    # 2. PRESS_AREA OPERATING ELEMENT (1120, 50) to (1950, 750) -> 830 x 700 px
    # Frangible white target plate with bold EN 54-11 black arrows and clear graphics
    # =========================================================================
    ax0, ay0, ax1, ay1 = 1120, 50, 1950, 750
    draw.rectangle([ax0, ay0, ax1, ay1], fill=(250, 252, 255, 255), outline=(160, 170, 185, 255), width=5)

    # Top yellow-and-black chevron activation indicator banner
    flag_h = 100
    draw.rectangle([ax0 + 10, ay0 + 10, ax1 - 10, ay0 + flag_h], fill=(245, 200, 25, 255), outline=(20, 20, 20, 255), width=3)
    for cx in range(ax0 + 20, ax1, 60):
        draw.polygon([(cx, ay0 + 12), (cx + 30, ay0 + 12), (cx + 5, ay0 + flag_h - 2), (cx - 25, ay0 + flag_h - 2)], fill=(20, 22, 28, 255))
    draw_center_text(draw, (ax0 + ax1)//2, ay0 + 55, "OPERATING ELEMENT", load_font(FONT_SANS, 26), (255, 255, 255, 255))

    center_y = (ay0 + flag_h + ay1) // 2
    center_x = (ax0 + ax1) // 2

    # Bold "PRESS HERE" Title
    draw_center_text(draw, center_x, center_y - 110, "PRESS HERE", load_font(FONT_SANS, 56), (15, 18, 24, 255))

    # Large prominent inward pointing arrows
    arr_w = 190
    arr_h = 55
    head_w = 90
    head_h = 90
    
    # Left arrow pointing right
    draw.polygon([
        (center_x - 300, center_y - arr_h//2),
        (center_x - 120, center_y - arr_h//2),
        (center_x - 120, center_y - head_h//2),
        (center_x - 35,  center_y),
        (center_x - 120, center_y + head_h//2),
        (center_x - 120, center_y + arr_h//2),
        (center_x - 300, center_y + arr_h//2)
    ], fill=(15, 18, 24, 255))

    # Right arrow pointing left
    draw.polygon([
        (center_x + 300, center_y - arr_h//2),
        (center_x + 120, center_y - arr_h//2),
        (center_x + 120, center_y - head_h//2),
        (center_x + 35,  center_y),
        (center_x + 120, center_y + head_h//2),
        (center_x + 120, center_y + arr_h//2),
        (center_x + 300, center_y + arr_h//2)
    ], fill=(15, 18, 24, 255))

    # Center target red bulls-eye and snap crack indicator
    draw.ellipse([center_x - 32, center_y - 32, center_x + 32, center_y + 32], fill=(225, 25, 30, 255), outline=(15, 18, 24, 255), width=4)
    draw.ellipse([center_x - 14, center_y - 14, center_x + 14, center_y + 14], fill=(255, 255, 255, 255))
    draw.ellipse([center_x - 5, center_y - 5, center_x + 5, center_y + 5], fill=(225, 25, 30, 255))

    # Subtitle instructions in multiple languages
    draw_center_text(draw, center_x, center_y + 105, "POUSSER FORTEMENT  •  DRÜCKEN", load_font(FONT_SANS, 22), (50, 55, 65, 255))
    draw_center_text(draw, center_x, center_y + 145, "FRANGIBLE ELEMENT  |  REUSABLE TEST COMPLIANT", load_font(FONT_MONO, 15), (120, 130, 145, 255))

    # =========================================================================
    # 3. BREAKABLE_WINDOW / FLAP GRAPHIC (1120, 800) to (1950, 1150) -> 830 x 350 px
    # Protective transparent cover with BOTTOM yellow lift tab
    # =========================================================================
    wx0, wy0, wx1, wy1 = 1120, 800, 1950, 1150
    draw.rectangle([wx0, wy0, wx1, wy1], fill=(245, 248, 255, 60), outline=(210, 225, 245, 220), width=4)

    # Laser-etched clear acrylic warning markings across center
    draw_center_text(draw, (wx0 + wx1)//2, wy0 + 90, "PROTECTIVE COVER • LIFT TO OPERATE", load_font(FONT_MONO, 22), (255, 255, 255, 230))
    draw_center_text(draw, (wx0 + wx1)//2, wy0 + 135, "BREAK GLASS / COUVERCLE DE PROTECTION", load_font(FONT_MONO, 16), (230, 240, 255, 180))

    # BOTTOM Yellow Finger Grip Tab (wy1 - 100 to wy1 - 15)
    tab_y0 = wy1 - 100
    tab_y1 = wy1 - 15
    draw.rounded_rectangle([wx0 + 120, tab_y0, wx1 - 120, tab_y1], radius=12, fill=(245, 195, 25, 255), outline=(130, 100, 15, 255), width=3)
    # Tactile grip ridges
    for gx in range(wx0 + 150, wx1 - 150, 25):
        draw.line([(gx, tab_y0 + 8), (gx, tab_y0 + 24)], fill=(180, 140, 15, 255), width=2)
    draw_center_text(draw, (wx0 + wx1)//2, (tab_y0 + tab_y1)//2 + 5, "▲  LIFT HERE  ▲", load_font(FONT_SANS, 26), (20, 22, 28, 255))

    # =========================================================================
    # 4. RESET_COVER (TEST KEY SLOT) (50, 1120) to (650, 1400) -> 600 x 280 px
    # Bottom key slot for resetting call point with double keyways
    # =========================================================================
    kx0, ky0, kx1, ky1 = 50, 1120, 650, 1400
    draw.rectangle([kx0, ky0, kx1, ky1], fill=(175, 20, 25, 255), outline=(115, 12, 16, 255), width=4)
    draw.line([(kx0 + 8, ky0 + 8), (kx1 - 8, ky0 + 8)], fill=(225, 50, 55, 255), width=3)

    # Double keyhole slots for standard two-prong test key
    draw.rectangle([kx0 + 170, ky0 + 80, kx0 + 205, ky0 + 185], fill=(15, 18, 24, 255), outline=(75, 85, 100, 255), width=2)
    draw.rectangle([kx1 - 205, ky0 + 80, kx1 - 170, ky0 + 185], fill=(15, 18, 24, 255), outline=(75, 85, 100, 255), width=2)
    draw_center_text(draw, (kx0 + kx1)//2, ky0 + 45, "RESET / TEST KEYWAY", load_font(FONT_MONO, 16), (255, 255, 255, 255))
    draw_center_text(draw, (kx0 + kx1)//2, ky1 - 45, "INSERT KEY FULLY TO RESET", load_font(FONT_MONO, 13), (245, 195, 35, 255))

    # =========================================================================
    # 5. REAR BACKPLATE & TERMINAL DIAGRAM (700, 1120) to (1950, 1650)
    # =========================================================================
    rx0, ry0, rx1, ry1 = 700, 1120, 1950, 1650
    draw.rectangle([rx0, ry0, rx1, ry1], fill=(24, 28, 34, 255), outline=(65, 75, 90, 255), width=3)
    draw.text((rx0 + 35, ry0 + 30), "BACKPLATE WIRING DIAGRAM & TECHNICAL LABEL", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 16))

    specs = [
        "MODEL: SEC-MCP01-R | MANUAL CALL POINT TYPE A (INDOOR)",
        "OPERATING VOLTAGE: 12-30V DC | ALARM CURRENT: 24mA @ 24V",
        "CONTACT RATING: 30V DC 2A | MONITOR RESISTOR: 470 OHM / 680 OHM",
        "STANDARDS: EN 54-11:2001 + A1:2005 | IP RATING: IP24D",
        "SERIAL NO: *MCP01-202688741-EU*"
    ]
    for idx, sp in enumerate(specs):
        draw.text((rx0 + 35, ry0 + 75 + idx * 36), sp, fill=(210, 220, 235, 255), font=load_font(FONT_MONO, 13))

    for bc in range(rx0 + 35, rx1 - 40, 6):
        w = 2 if (bc % 12 == 0) else 4
        draw.rectangle([bc, ry0 + 290, bc + w, ry0 + 350], fill=(235, 240, 250, 255))

    # =========================================================================
    # 6. MATERIAL SWATCHES (50..1950, 1720..2020)
    # =========================================================================
    draw.rectangle([50, 1720, 500, 2020], fill=(195, 22, 28, 255))      # Safety Red Housing
    draw.rectangle([540, 1720, 1000, 2020], fill=(250, 252, 255, 255))  # Target White Plate
    draw.rectangle([1040, 1720, 1500, 2020], fill=(245, 195, 25, 255))  # Caution Yellow
    draw.rectangle([1540, 1720, 2000, 2020], fill=(18, 22, 28, 255))    # Deep Black Pocket

    img.save(ATLAS_PATH, "PNG")
    print(f"[Atlas] Generated: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

if __name__ == "__main__":
    generate_atlas()
