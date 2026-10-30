"""
Security CCTV Asset Production Suite - Asset 61
Asset Name: SEC_Alarm_Control_Panel (Fire & Security Alarm Control Panel)
Texture Atlas Generator (2048x2048)
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
    # Base metal chassis dark background
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), (24, 27, 32, 255))
    draw = ImageDraw.Draw(img)

    # Subtle metal grain texture
    for y in range(0, ATLAS_H, 4):
        tint = (y * 7) % 6
        draw.line([(0, y), (ATLAS_W, y)], fill=(22 + tint, 25 + tint, 30 + tint, 255), width=1)

    # =========================================================================
    # 1. FRONT DOOR EXTERIOR (50, 50) to (950, 1150) -> 900 x 1100 px
    # Physical door: 0.380m W x 0.460m H (Ratio ~0.82:1)
    # Safety Red Powder-Coated Steel
    # =========================================================================
    dx0, dy0, dx1, dy1 = 50, 50, 950, 1150
    # Outer red door plate
    draw.rectangle([dx0, dy0, dx1, dy1], fill=(175, 25, 32, 255), outline=(135, 18, 24, 255), width=6)
    # Beveled highlight inner edge
    draw.line([(dx0 + 8, dy0 + 8), (dx1 - 8, dy0 + 8)], fill=(215, 55, 62, 255), width=3)
    draw.line([(dx0 + 8, dy0 + 8), (dx0 + 8, dy1 - 8)], fill=(215, 55, 62, 255), width=3)
    draw.line([(dx0 + 8, dy1 - 8), (dx1 - 8, dy1 - 8)], fill=(110, 15, 20, 255), width=3)
    draw.line([(dx1 - 8, dy0 + 8), (dx1 - 8, dy1 - 8)], fill=(110, 15, 20, 255), width=3)

    # Top Brand Header
    draw.rectangle([dx0 + 40, dy0 + 35, dx1 - 40, dy0 + 130], fill=(22, 25, 30, 255), outline=(195, 35, 42, 255), width=2)
    draw.text((dx0 + 65, dy0 + 50), "SEC-ALERT 8000", fill=(255, 255, 255, 255), font=load_font(FONT_SANS, 34))
    draw.text((dx0 + 65, dy0 + 92), "INTEGRATED FIRE & SECURITY CONTROL SYSTEM", fill=(240, 195, 35, 255), font=load_font(FONT_MONO, 16))

    # Inspection Window Cutout Decal (where user sees display from outside)
    wx0, wy0, wx1, wy1 = dx0 + 60, dy0 + 160, dx1 - 60, dy0 + 560
    draw.rectangle([wx0, wy0, wx1, wy1], fill=(16, 18, 22, 255), outline=(65, 75, 90, 255), width=4)
    draw.text((wx0 + 30, wy0 + 20), "GLASS INSPECTION WINDOW", fill=(90, 105, 125, 255), font=load_font(FONT_MONO, 14))

    # Inner preview frame of LCD
    draw.rectangle([wx0 + 40, wy0 + 60, wx1 - 40, wy0 + 200], fill=(10, 30, 22, 255), outline=(35, 90, 65, 255), width=2)
    draw.text((wx0 + 60, wy0 + 80), "SEC-ALERT CP-8000  *NORMAL*", fill=(65, 240, 140, 255), font=load_font(FONT_MONO, 16))
    draw.text((wx0 + 60, wy0 + 110), "ZONE 01: MAIN ENTRY - OK", fill=(55, 215, 120, 255), font=load_font(FONT_MONO, 15))
    draw.text((wx0 + 60, wy0 + 138), "ZONE 02: PERIMETER - SECURE", fill=(55, 215, 120, 255), font=load_font(FONT_MONO, 15))
    draw.text((wx0 + 60, wy0 + 165), "AC: NORMAL | BATT: 27.6V FLOAT", fill=(45, 185, 105, 255), font=load_font(FONT_MONO, 14))

    # LED preview strip
    led_labels = ["PWR", "ALM", "SUPV", "TRBL", "GND", "SIL", "DIS", "BAT"]
    led_cols = [(40, 220, 90), (240, 40, 40), (240, 200, 30), (240, 200, 30),
                (240, 200, 30), (240, 200, 30), (240, 200, 30), (40, 220, 90)]
    for i, (lbl, col) in enumerate(zip(led_labels, led_cols)):
        lx = wx0 + 60 + i * 85
        ly = wy0 + 260
        draw.ellipse([lx - 12, ly - 12, lx + 12, ly + 12], fill=col, outline=(255, 255, 255, 200), width=2)
        draw_center_text(draw, lx, ly + 25, lbl, load_font(FONT_MONO, 12), (200, 210, 225, 255))

    # Operating Instructions Box
    ix0, iy0, ix1, iy1 = dx0 + 60, dy0 + 590, dx1 - 180, dy0 + 880
    draw.rectangle([ix0, iy0, ix1, iy1], fill=(245, 246, 250, 255), outline=(130, 20, 25, 255), width=3)
    draw.rectangle([ix0, iy0, ix1, iy0 + 35], fill=(175, 25, 32, 255))
    draw.text((ix0 + 15, iy0 + 8), "OPERATING INSTRUCTIONS", fill=(255, 255, 255, 255), font=load_font(FONT_SANS, 16))

    instructions = [
        "1. ALARM: Evacuate immediately if bell sounds.",
        "2. SILENCE: Turn key, press [ALARM SILENCE].",
        "3. RESET: Clear condition, press [SYSTEM RESET].",
        "4. DRILL: Press [MANUAL EVAC] for 3 seconds.",
        "5. SERVICE: Qualified personnel only."
    ]
    for idx, inst in enumerate(instructions):
        draw.text((ix0 + 15, iy0 + 50 + idx * 36), inst, fill=(20, 22, 28, 255), font=load_font(FONT_MONO, 13))

    # Right Key Cylinder Area
    kx = dx1 - 100
    ky = dy0 + 720
    draw.ellipse([kx - 38, ky - 38, kx + 38, ky + 38], fill=(185, 192, 205, 255), outline=(110, 115, 125, 255), width=3)
    draw.ellipse([kx - 24, ky - 24, kx + 24, ky + 24], fill=(140, 145, 155, 255), outline=(85, 90, 100, 255), width=2)
    # Keyhole slot
    draw.rectangle([kx - 4, ky - 14, kx + 4, ky + 14], fill=(15, 18, 22, 255))
    draw.ellipse([kx - 8, ky - 14, kx + 8, ky - 2], fill=(15, 18, 22, 255))
    draw_center_text(draw, kx, ky - 50, "LOCK", load_font(FONT_MONO, 12), (240, 240, 240, 255))
    draw_center_text(draw, kx, ky + 52, "SEC-KEY-01", load_font(FONT_MONO, 11), (230, 230, 230, 255))

    # Bottom Standard Compliance & Barcode
    bx0, by0, bx1, by1 = dx0 + 60, dy0 + 910, dx1 - 60, dy1 - 40
    draw.rectangle([bx0, by0, bx1, by1], fill=(22, 25, 30, 255), outline=(60, 68, 80, 255), width=2)
    draw.text((bx0 + 25, by0 + 20), "NFPA 72 | EN 54-2 | UL 864 10th ED. LISTED", fill=(245, 195, 35, 255), font=load_font(FONT_MONO, 13))
    draw.text((bx0 + 25, by0 + 46), "SERIES: CP8000-ADR-2L | SUPPLY: 230VAC 50/60Hz 1.5A", fill=(195, 205, 220, 255), font=load_font(FONT_MONO, 11))
    draw.text((bx0 + 25, by0 + 72), "SERIAL: *SEC-CP8000-20268841-EXP*", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 12))

    for bc in range(bx0 + 25, bx1 - 25, 5):
        w = 2 if (bc % 10 == 0) else 3
        draw.rectangle([bc, by0 + 100, bc + w, by0 + 135], fill=(235, 240, 248, 255))

    # =========================================================================
    # 2. INTERNAL OPERATOR PANEL (1020, 50) to (1980, 1150) -> 960 x 1100 px
    # Under-the-door operator control chassis (Beige/Industrial Slate)
    # =========================================================================
    ox0, oy0, ox1, oy1 = 1020, 50, 1980, 1150
    draw.rectangle([ox0, oy0, ox1, oy1], fill=(36, 40, 48, 255), outline=(75, 85, 100, 255), width=4)

    # Upper LCD Screen Bay (1060, 90) to (1940, 390)
    sx0, sy0, sx1, sy1 = ox0 + 40, oy0 + 40, ox1 - 40, oy0 + 340
    draw.rectangle([sx0, sy0, sx1, sy1], fill=(18, 22, 28, 255), outline=(55, 65, 80, 255), width=3)
    # Screen inner display area
    draw.rectangle([sx0 + 25, sy0 + 25, sx1 - 25, sy1 - 25], fill=(8, 28, 20, 255), outline=(25, 75, 50, 255), width=3)
    draw.text((sx0 + 45, sy0 + 45), "** SEC-ALERT 8000 INTELLIGENT FACP **", fill=(75, 255, 155, 255), font=load_font(FONT_MONO, 20))
    draw.text((sx0 + 45, sy0 + 85), "STATUS: SYSTEM NORMAL - ALL ZONES SECURE", fill=(65, 240, 140, 255), font=load_font(FONT_MONO, 17))
    draw.text((sx0 + 45, sy0 + 125), "LOOP 1: 48 DETECTORS OK | LOOP 2: 36 DETECTORS OK", fill=(55, 220, 130, 255), font=load_font(FONT_MONO, 15))
    draw.text((sx0 + 45, sy0 + 165), "PRIMARY AC: 230.4 VAC | STANDBY BATT: 27.6 VDC FLOAT", fill=(55, 220, 130, 255), font=load_font(FONT_MONO, 15))
    draw.text((sx0 + 45, sy0 + 205), "TIME: 2026-10-31  22:00:00  [SUPERVISORY MODE]", fill=(240, 200, 35, 255), font=load_font(FONT_MONO, 15))

    # Middle LED Array Housing (1060, 420) to (1940, 560)
    lx0, ly0, lx1, ly1 = ox0 + 40, oy0 + 370, ox1 - 40, oy0 + 510
    draw.rectangle([lx0, ly0, lx1, ly1], fill=(24, 28, 34, 255), outline=(60, 70, 85, 255), width=2)
    draw.text((lx0 + 25, ly0 + 15), "SYSTEM ANNUNCIATOR STATUS LEDS", fill=(210, 220, 235, 255), font=load_font(FONT_MONO, 14))

    for i, (lbl, col) in enumerate(zip(led_labels, led_cols)):
        cx = lx0 + 60 + i * 105
        cy = ly0 + 65
        # LED bezel
        draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(12, 14, 18, 255), outline=(90, 100, 115, 255), width=2)
        # Glowing LED lens
        draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=col, outline=(255, 255, 255, 180), width=1)
        draw_center_text(draw, cx, cy + 32, lbl, load_font(FONT_MONO, 12), (230, 235, 245, 255))

    # Function Buttons Bar (1060, 590) to (1940, 770)
    btn_defs = [
        ("ALARM SILENCE", (210, 40, 45)),
        ("SYSTEM RESET", (195, 30, 35)),
        ("TROUBLE ACK", (225, 175, 25)),
        ("MANUAL EVAC", (30, 130, 235)),
        ("DRILL MODE", (40, 180, 85)),
        ("LAMP TEST", (140, 145, 160))
    ]
    for i, (btn_name, btn_col) in enumerate(btn_defs):
        row = i // 3
        col = i % 3
        bx = ox0 + 50 + col * 295
        by = oy0 + 540 + row * 85
        bw = 270
        bh = 65
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=btn_col, outline=(250, 250, 250, 220), width=2)
        draw_center_text(draw, bx + bw // 2, by + bh // 2, btn_name, load_font(FONT_SANS, 14), (255, 255, 255, 255))

    # Numeric Entry Keypad (1060, 790) to (1940, 1080)
    keys = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
        ["*", "0", "#"]
    ]
    k_ox = ox0 + 260
    k_oy = oy0 + 720
    draw.rectangle([k_ox - 20, k_oy - 15, k_ox + 420, k_oy + 340], fill=(22, 25, 30, 255), outline=(65, 75, 90, 255), width=2)
    draw.text((k_ox, k_oy), "ACCESS KEYPAD", fill=(180, 190, 205, 255), font=load_font(FONT_MONO, 13))

    for r in range(4):
        for c in range(3):
            kx = k_ox + 15 + c * 130
            ky = k_oy + 35 + r * 70
            draw.rounded_rectangle([kx, ky, kx + 110, ky + 55], radius=6, fill=(45, 50, 60, 255), outline=(100, 110, 125, 255), width=2)
            draw_center_text(draw, kx + 55, ky + 27, keys[r][c], load_font(FONT_MONO, 24), (255, 255, 255, 255))

    # =========================================================================
    # 3. CABINET SIDES & REAR CHASSIS (50, 1200) to (1980, 1650)
    # Conduit knockouts, rear keyhole hangers, cooling vents
    # =========================================================================
    cx0, cy0, cx1, cy1 = 50, 1200, 1980, 1650
    draw.rectangle([cx0, cy0, cx1, cy1], fill=(28, 32, 38, 255), outline=(55, 62, 75, 255), width=3)
    draw.text((cx0 + 30, cy0 + 25), "CABINET SIDES, TOP CONDUIT KNOCKOUTS & REAR MOUNTING SLOTS", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 16))

    # Conduit knockouts
    for idx, kx in enumerate(range(cx0 + 80, cx0 + 800, 140)):
        draw.ellipse([kx - 45, cy0 + 120 - 45, kx + 45, cy0 + 120 + 45], fill=(20, 22, 26, 255), outline=(85, 95, 110, 255), width=4)
        draw.ellipse([kx - 30, cy0 + 120 - 30, kx + 30, cy0 + 120 + 30], fill=(26, 29, 35, 255), outline=(65, 75, 90, 255), width=2)
        draw_center_text(draw, kx, cy0 + 190, f"Ø28mm K/O", load_font(FONT_MONO, 12), (180, 190, 205, 255))

    # Louver vents
    vx0, vy0, vx1, vy1 = cx0 + 900, cy0 + 70, cx1 - 60, cy0 + 400
    draw.rectangle([vx0, vy0, vx1, vy1], fill=(20, 22, 26, 255), outline=(50, 60, 75, 255), width=2)
    draw.text((vx0 + 25, vy0 + 20), "INTERNAL HEAT EXHAUST LOUVERS", fill=(175, 185, 200, 255), font=load_font(FONT_MONO, 14))
    for vy in range(vy0 + 55, vy1 - 30, 18):
        draw.line([(vx0 + 30, vy), (vx1 - 30, vy)], fill=(12, 14, 18, 255), width=6)
        draw.line([(vx0 + 30, vy + 3), (vx1 - 30, vy + 3)], fill=(55, 65, 80, 255), width=2)

    # =========================================================================
    # 4. MATERIAL SWATCHES (50..1980, 1700..2020)
    # =========================================================================
    draw.rectangle([50, 1700, 500, 2020], fill=(175, 25, 32, 255)) # Safety Red Door
    draw.rectangle([540, 1700, 1000, 2020], fill=(36, 40, 48, 255)) # Dark Grey Cabinet
    draw.rectangle([1040, 1700, 1500, 2020], fill=(185, 192, 205, 255)) # Stainless Steel / Metal
    draw.rectangle([1540, 1700, 2000, 2020], fill=(15, 18, 22, 255)) # Deep Black Cutout

    img.save(ATLAS_PATH, "PNG")
    print(f"[Atlas] Generated: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

if __name__ == "__main__":
    generate_atlas()
