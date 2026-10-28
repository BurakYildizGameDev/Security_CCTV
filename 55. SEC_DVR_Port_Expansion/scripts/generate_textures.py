"""
=============================================================================
Security CCTV Asset Production Suite - Asset 55
Asset Name: SEC_DVR_Port_Expansion (CCTV Port Genisletme Modulu)
Texture Atlas Generator (2048x2048)
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

# Colors
CHASSIS_BLACK = (22, 24, 28, 255)
FRONT_FASCIA = (30, 34, 42, 255)
STEEL_METAL = (150, 160, 175, 255)
GOLD_PIN = (215, 175, 45, 255)
LED_GREEN = (40, 230, 80, 255)
LED_AMBER = (245, 175, 25, 255)
LED_BLUE = (35, 145, 245, 255)
LED_RED = (235, 45, 35, 255)
WHITE = (255, 255, 255, 255)
INK_TEXT = (220, 228, 238, 255)
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

def draw_center_text(draw, cx, cy, text, font, fill):
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = cx - w // 2 - bbox[0]
    y = cy - h // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=fill)

def generate_atlas():
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), CHASSIS_BLACK)
    draw = ImageDraw.Draw(img)

    # =========================================================================
    # 1. FRONT 1U FASCIA PANEL (20..1960, 20..240)
    # 440mm x 44mm (10:1 ratio, 1940 x 220 px)
    # =========================================================================
    fx0, fy0, fx1, fy1 = 20, 20, 1960, 240
    draw.rectangle([fx0, fy0, fx1, fy1], fill=FRONT_FASCIA, outline=(55, 62, 75, 255), width=2)
    draw.line([(fx0 + 4, fy0 + 4), (fx1 - 4, fy0 + 4)], fill=(75, 85, 100, 255), width=2)
    draw.line([(fx0 + 4, fy1 - 4), (fx1 - 4, fy1 - 4)], fill=(15, 18, 22, 255), width=2)

    # Rack mount ear indicator marks
    for rx in [fx0 + 35, fx1 - 35]:
        draw.rounded_rectangle([rx - 12, fy0 + 40, rx + 12, fy1 - 40], radius=6, fill=(12, 14, 16, 255), outline=STEEL_METAL, width=2)

    # Left Section: Branding & Device Info
    draw.text((fx0 + 90, fy0 + 35), "SEC-VISION", fill=WHITE, font=load_font(FONT_SANS, 24))
    draw.text((fx0 + 90, fy0 + 72), "PORT EXPANSION MODULE | MODEL EXP-1600-PRO", fill=INK_SOFT, font=load_font(FONT_MONO, 14))
    draw.text((fx0 + 90, fy0 + 102), "16-CH BNC / RS-485 / DUAL HOST BUS MULTIPLEXER", fill=(45, 190, 240, 255), font=load_font(FONT_MONO, 12))

    # Center Section: Power & System Status Indicators
    draw.ellipse([fx0 + 580, fy0 + 65, fx0 + 596, fy0 + 81], fill=LED_GREEN)
    draw.text((fx0 + 606, fy0 + 63), "PWR", fill=WHITE, font=load_font(FONT_MONO, 13))

    draw.ellipse([fx0 + 660, fy0 + 65, fx0 + 676, fy0 + 81], fill=LED_BLUE)
    draw.text((fx0 + 686, fy0 + 63), "HOST", fill=WHITE, font=load_font(FONT_MONO, 13))

    draw.ellipse([fx0 + 745, fy0 + 65, fx0 + 761, fy0 + 81], fill=LED_AMBER)
    draw.text((fx0 + 771, fy0 + 63), "SYNC", fill=WHITE, font=load_font(FONT_MONO, 13))

    # Right Section: Recessed cavity for Front_LED_Array (X: 880 to 1840)
    draw.rounded_rectangle([fx0 + 880, fy0 + 25, fx0 + 1840, fy1 - 25], radius=6, fill=(10, 12, 16, 255), outline=(45, 52, 65, 255), width=2)

    # =========================================================================
    # 2. FRONT LED ARRAY DEDICATED MESH TEXTURE (20..1960, 260..460)
    # =========================================================================
    lx0, ly0, lx1, ly1 = 20, 260, 1960, 460
    draw.rounded_rectangle([lx0, ly0, lx1, ly1], radius=8, fill=(16, 18, 24, 255), outline=(50, 58, 72, 255), width=2)
    draw.text((lx0 + 50, ly0 + 25), "PORT LINK / ACTIVITY [CH 01 - 16]:", fill=WHITE, font=load_font(FONT_MONO, 18))
    for i in range(16):
        cx = lx0 + 65 + i * 115
        cy = ly0 + 80
        draw.ellipse([cx, cy, cx + 24, cy + 24], fill=LED_GREEN)
        draw_center_text(draw, cx + 12, cy + 55, f"{i+1:02d}", load_font(FONT_MONO, 14), INK_TEXT)

    # =========================================================================
    # 3. REAR 1U I/O PANEL (20..1960, 500..740)
    # 16x BNC Video Ports, Host High-Density Connector, RS-485, DC Power
    # =========================================================================
    rx0, ry0, rx1, ry1 = 20, 500, 1960, 740
    draw.rectangle([rx0, ry0, rx1, ry1], fill=(24, 27, 32, 255), outline=(55, 62, 75, 255), width=2)

    # 16x BNC Ports (2 rows of 8)
    draw.text((rx0 + 30, ry0 + 15), "EXPANSION BNC VIDEO IN/OUT (1 - 16)", fill=WHITE, font=load_font(FONT_MONO, 13))
    for r in range(2):
        for c in range(8):
            bx = rx0 + 40 + c * 82
            by = ry0 + 45 + r * 85
            # Outer steel ring
            draw.ellipse([bx, by, bx + 52, by + 52], fill=(38, 42, 50, 255), outline=STEEL_METAL, width=3)
            # Gold center dielectric & pin
            draw.ellipse([bx + 16, by + 16, bx + 36, by + 36], fill=(12, 14, 16, 255), outline=GOLD_PIN, width=2)
            draw.ellipse([bx + 23, by + 23, bx + 29, by + 29], fill=GOLD_PIN)

    # Host PCIe / SAS High Density Bus Port
    draw.text((rx0 + 750, ry0 + 15), "HOST INTERFACE (EXP-BUS 1 / 2)", fill=WHITE, font=load_font(FONT_MONO, 13))
    draw.rectangle([rx0 + 750, ry0 + 50, rx0 + 920, ry0 + 120], fill=(15, 18, 22, 255), outline=STEEL_METAL, width=2)
    draw_center_text(draw, rx0 + 835, ry0 + 85, "EXP-BUS 1", load_font(FONT_MONO, 13), INK_TEXT)

    draw.rectangle([rx0 + 750, ry0 + 135, rx0 + 920, ry0 + 205], fill=(15, 18, 22, 255), outline=STEEL_METAL, width=2)
    draw_center_text(draw, rx0 + 835, ry0 + 170, "EXP-BUS 2", load_font(FONT_MONO, 13), INK_TEXT)

    # RS-485 Terminal Blocks (PTZ Loop)
    draw.text((rx0 + 960, ry0 + 15), "RS-485 TELEMETRY LOOP", fill=WHITE, font=load_font(FONT_MONO, 13))
    draw.rectangle([rx0 + 960, ry0 + 50, rx0 + 1200, ry0 + 150], fill=(20, 60, 35, 255), outline=(50, 110, 70, 255), width=2)
    for t in range(6):
        tx = rx0 + 975 + t * 36
        draw.rectangle([tx, ry0 + 65, tx + 24, ry0 + 125], fill=(10, 20, 12, 255), outline=STEEL_METAL, width=1)
        draw.ellipse([tx + 5, ry0 + 85, tx + 19, ry0 + 99], fill=GOLD_PIN)

    # Power Input: DC 12V 5A & Grounding Lug
    px0 = rx1 - 360
    draw.rectangle([px0, ry0 + 40, rx1 - 40, ry0 + 200], fill=(12, 14, 18, 255), outline=(55, 62, 75, 255), width=2)
    draw.text((px0 + 20, ry0 + 55), "DC 12V IN --- 5A  [GND]", fill=WHITE, font=load_font(FONT_MONO, 12))
    # DC Barrel Jack
    draw.ellipse([px0 + 50, ry0 + 95, px0 + 110, ry0 + 155], fill=(20, 22, 26, 255), outline=STEEL_METAL, width=3)
    draw.ellipse([px0 + 72, ry0 + 117, px0 + 88, ry0 + 133], fill=GOLD_PIN)
    # Earth Ground Lug
    draw.ellipse([px0 + 170, ry0 + 105, px0 + 210, ry0 + 145], fill=(200, 180, 50, 255), outline=WHITE, width=2)
    draw.text((px0 + 225, ry0 + 115), "⏚ EARTH", fill=INK_TEXT, font=load_font(FONT_MONO, 12))

    # =========================================================================
    # 4. FLAT COLOR & MATERIAL SWATCHES (20..2000, 800..2000)
    # =========================================================================
    # Clean non-labeled swatches for seamless 3D UV mapping:
    # Chassis solid dark metal at (50, 1500, 450, 1900)
    draw.rectangle([50, 1500, 450, 1900], fill=CHASSIS_BLACK)
    # Pure dark recess at (550, 1500, 950, 1900)
    draw.rectangle([550, 1500, 950, 1900], fill=(10, 12, 16, 255))

    swatches = [
        ((20, 800, 480, 1100), CHASSIS_BLACK, "CHASSIS_BLACK"),
        ((520, 800, 980, 1100), FRONT_FASCIA, "FRONT_FASCIA"),
        ((1020, 800, 1480, 1100), STEEL_METAL, "STEEL_METAL"),
        ((1520, 800, 1980, 1100), (12, 14, 18, 255), "INNER_RECESS"),
        ((20, 1140, 480, 1440), (40, 230, 80, 255), "EMIT_GREEN"),
        ((520, 1140, 980, 1440), GOLD_PIN, "GOLD_TERMINAL"),
        ((1020, 1140, 1480, 1440), (60, 68, 80, 255), "RACK_EAR_METAL"),
        ((1520, 1140, 1980, 1440), (10, 12, 14, 255), "PORT_DARK")
    ]
    for box, col, name in swatches:
        draw.rectangle(box, fill=col)
        draw.text((box[0] + 20, box[1] + 20), name, fill=WHITE, font=load_font(FONT_MONO, 16))

    img.save(ATLAS_PATH, "PNG")
    print(f"[Atlas] Generated: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

if __name__ == "__main__":
    generate_atlas()
