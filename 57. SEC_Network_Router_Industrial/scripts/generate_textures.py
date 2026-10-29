"""
Security CCTV Asset Production Suite - Asset 57
Asset Name: SEC_Network_Router_Industrial (Endüstriyel Güvenlik Router'ı)
Upgraded Ultra-Detail Texture Atlas Generator (2048x2048)
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
    # Base dark brushed chassis background
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), (24, 26, 32, 255))
    draw = ImageDraw.Draw(img)

    # Background subtle horizontal brushed grain
    for y in range(0, ATLAS_H, 4):
        tint = (y * 7) % 8
        draw.line([(0, y), (ATLAS_W, y)], fill=(22 + tint, 24 + tint, 30 + tint, 255), width=1)

    # =========================================================================
    # 1. FRONT PANEL FACEPLATE (80, 60) to (1280, 960) -> 1200 x 900 px (1.333:1)
    # =========================================================================
    fx0, fy0, fx1, fy1 = 80, 60, 1280, 960
    # Deep slate-navy industrial powdercoat
    draw.rectangle([fx0, fy0, fx1, fy1], fill=(28, 32, 42, 255), outline=(60, 72, 90, 255), width=4)
    # Subtle inner bevel
    draw.line([(fx0 + 3, fy0 + 3), (fx1 - 3, fy0 + 3)], fill=(85, 100, 125, 255), width=3)
    draw.line([(fx0 + 3, fy1 - 3), (fx1 - 3, fy1 - 3)], fill=(15, 17, 22, 255), width=3)

    # Vivid Orange industrial safety banner at top
    draw.rectangle([fx0 + 6, fy0 + 6, fx1 - 6, fy0 + 26], fill=(245, 115, 30, 255))
    draw.rectangle([fx0 + 6, fy0 + 24, fx1 - 6, fy0 + 26], fill=(180, 75, 15, 255))

    # --- Header Branding & Model ---
    draw.text((fx0 + 40, fy0 + 42), "SEC-VISION", fill=(255, 255, 255, 255), font=load_font(FONT_SANS, 36))
    draw.text((fx0 + 40, fy0 + 88), "INDUSTRIAL CCTV & VPN SECURITY ROUTER", fill=(55, 205, 255, 255), font=load_font(FONT_MONO, 17))
    draw.text((fx0 + 40, fy0 + 118), "MODEL: SEC-IR400-PRO  |  DUAL-BAND 4G/5G LTE GATEWAY", fill=(175, 185, 200, 255), font=load_font(FONT_MONO, 14))

    # Industrial Badge Top Right
    draw.rounded_rectangle([fx1 - 280, fy0 + 42, fx1 - 40, fy0 + 105], radius=6, fill=(16, 20, 28, 255), outline=(180, 190, 205, 255), width=2)
    draw_center_text(draw, fx1 - 160, fy0 + 62, "HEAVY INDUSTRIAL", load_font(FONT_MONO, 13), (255, 255, 255, 255))
    draw_center_text(draw, fx1 - 160, fy0 + 86, "IP40 / -40°C..+75°C", load_font(FONT_MONO, 12), (55, 205, 255, 255))

    # --- Section A: 10 Status LED Cluster Box (Y: 155..310) ---
    led_box_y0, led_box_y1 = fy0 + 155, fy0 + 310
    draw.rounded_rectangle([fx0 + 30, led_box_y0, fx1 - 30, led_box_y1], radius=8, fill=(18, 21, 28, 255), outline=(50, 60, 75, 255), width=2)
    draw.text((fx0 + 50, led_box_y0 + 12), "SYSTEM & TELEMETRY STATUS INDICATORS", fill=(230, 235, 245, 255), font=load_font(FONT_MONO, 14))

    led_labels = [
        ("PWR", (45, 235, 90)), ("SYS", (45, 235, 90)), ("WAN", (40, 160, 255)),
        ("LAN 1", (45, 235, 90)), ("LAN 2", (45, 235, 90)), ("LAN 3", (45, 235, 90)),
        ("2.4G", (45, 200, 255)), ("5.0G", (40, 160, 255)), ("SIM", (255, 185, 30)), ("VPN", (45, 235, 90))
    ]
    led_spacing = (fx1 - fx0 - 120) // len(led_labels)
    for i, (lbl, col) in enumerate(led_labels):
        lx = fx0 + 60 + i * led_spacing + led_spacing // 2
        ly = led_box_y0 + 75
        # Outer bezel ring
        draw.ellipse([lx - 15, ly - 15, lx + 15, ly + 15], fill=(12, 14, 18, 255), outline=(130, 140, 155, 255), width=2)
        # Glowing LED dome
        draw.ellipse([lx - 10, ly - 10, lx + 10, ly + 10], fill=col)
        draw.ellipse([lx - 5, ly - 5, lx + 2, ly + 2], fill=(255, 255, 255, 200))
        draw_center_text(draw, lx, ly + 36, lbl, load_font(FONT_MONO, 12), (240, 245, 255, 255))

    # --- Section B: Port Bed (Y: 335..870) ---
    port_bed_y0 = fy0 + 335
    port_bed_y1 = fy1 - 30
    draw.rounded_rectangle([fx0 + 30, port_bed_y0, fx1 - 30, port_bed_y1], radius=8, fill=(16, 19, 25, 255), outline=(50, 60, 75, 255), width=2)

    # WAN Bed (Left)
    draw.rectangle([fx0 + 50, port_bed_y0 + 20, fx0 + 260, port_bed_y1 - 20], fill=(20, 25, 35, 255), outline=(45, 115, 225, 255), width=2)
    draw_center_text(draw, fx0 + 155, port_bed_y0 + 45, "WAN (PoE IN)", load_font(FONT_MONO, 14), (80, 185, 255, 255))
    draw.rectangle([fx0 + 75, port_bed_y0 + 85, fx0 + 235, port_bed_y0 + 305], fill=(10, 12, 15, 255), outline=(100, 115, 135, 255), width=2)
    draw_center_text(draw, fx0 + 155, port_bed_y0 + 340, "10/100/1000M", load_font(FONT_MONO, 12), (180, 190, 205, 255))
    draw.rectangle([fx0 + 90, port_bed_y0 + 375, fx0 + 220, port_bed_y0 + 445], fill=(12, 14, 18, 255), outline=(70, 80, 95, 255), width=2)
    draw_center_text(draw, fx0 + 155, port_bed_y0 + 475, "USB DIAG / 5V 1A", load_font(FONT_MONO, 11), (140, 150, 165, 255))

    # LAN Bed (Ports 1 to 4)
    lan_x0 = fx0 + 290
    lan_x1 = fx1 - 50
    draw.rectangle([lan_x0, port_bed_y0 + 20, lan_x1, port_bed_y1 - 20], fill=(20, 24, 32, 255), outline=(60, 70, 85, 255), width=2)
    draw.text((lan_x0 + 30, port_bed_y0 + 40), "GIGABIT LAN PORTS (PoE 802.3at PSE OUT)", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 14))

    for port_idx in range(4):
        px0 = lan_x0 + 30 + port_idx * 195
        px1 = px0 + 160
        draw.rectangle([px0, port_bed_y0 + 85, px1, port_bed_y0 + 305], fill=(10, 12, 15, 255), outline=(100, 115, 135, 255), width=2)
        draw_center_text(draw, (px0 + px1) // 2, port_bed_y0 + 335, f"LAN {port_idx+1}", load_font(FONT_MONO, 14), (255, 255, 255, 255))
        draw_center_text(draw, (px0 + px1) // 2, port_bed_y0 + 370, "PoE+ 30W", load_font(FONT_MONO, 11), (55, 205, 255, 255))
        draw_center_text(draw, (px0 + px1) // 2, port_bed_y0 + 400, "1000BASE-T", load_font(FONT_MONO, 10), (140, 150, 165, 255))

    draw.text((fx0 + 50, fy1 - 18), "DEFAULT IP: 192.168.1.1  |  MAC: 70:B3:D5:4B:92:00  |  ANTIGRAVITY SYSTEMS", fill=(120, 130, 145, 255), font=load_font(FONT_MONO, 11))

    # =========================================================================
    # 2. DEDICATED RJ-45 SHIELDED JACK TEXTURE (1320, 50) to (1680, 450)
    # =========================================================================
    rx0, ry0, rx1, ry1 = 1320, 50, 1680, 450
    draw.rectangle([rx0, ry0, rx1, ry1], fill=(185, 195, 210, 255), outline=(240, 245, 255, 255), width=4)
    draw.rectangle([rx0 + 20, ry0 + 20, rx1 - 20, ry1 - 20], fill=(14, 16, 20, 255), outline=(80, 90, 105, 255), width=4)
    draw.rectangle([rx0 + 90, ry1 - 80, rx1 - 90, ry1 - 20], fill=(8, 9, 12, 255), outline=(60, 68, 80, 255), width=2)
    prong_w = 16
    prong_space = 36
    prong_start_x = rx0 + 50
    for p in range(8):
        px = prong_start_x + p * prong_space
        draw.rectangle([px, ry0 + 35, px + prong_w, ry0 + 170], fill=(225, 185, 45, 255), outline=(255, 230, 110, 255), width=1)
        draw.line([(px + 4, ry0 + 40), (px + 4, ry0 + 165)], fill=(255, 245, 180, 255), width=2)
    draw.rectangle([rx0 + 30, ry0 + 205, rx0 + 65, ry0 + 235], fill=(45, 235, 90, 255), outline=(200, 255, 210, 255), width=2)
    draw.rectangle([rx1 - 65, ry0 + 205, rx1 - 30, ry0 + 235], fill=(245, 175, 25, 255), outline=(255, 230, 160, 255), width=2)
    draw.text((rx0 + 30, ry0 + 250), "LNK", fill=(160, 255, 180, 255), font=load_font(FONT_MONO, 11))
    draw.text((rx1 - 65, ry0 + 250), "ACT", fill=(255, 210, 120, 255), font=load_font(FONT_MONO, 11))

    # =========================================================================
    # 3. DEDICATED USB 3.0 PORT TEXTURE (1320, 480) to (1680, 620)
    # =========================================================================
    draw.rectangle([1320, 480, 1680, 620], fill=(160, 170, 185, 255), outline=(220, 230, 245, 255), width=4)
    draw.rectangle([1340, 500, 1660, 600], fill=(10, 12, 16, 255), outline=(50, 60, 75, 255), width=3)
    draw.rectangle([1360, 535, 1640, 575], fill=(25, 95, 220, 255), outline=(60, 140, 255, 255), width=2)
    for p in range(4):
        px = 1400 + p * 65
        draw.rectangle([px, 545, px + 25, 565], fill=(225, 185, 45, 255))

    # =========================================================================
    # 4. DEDICATED GLOWING STATUS LED TEXTURES (1320, 650) to (1680, 960)
    # =========================================================================
    # Green LED Lens (1320, 650, 1490, 800)
    draw.rectangle([1320, 650, 1490, 800], fill=(12, 14, 18, 255), outline=(60, 70, 85, 255), width=3)
    draw.ellipse([1340, 670, 1470, 780], fill=(40, 240, 90, 255), outline=(180, 255, 200, 255), width=5)
    draw.ellipse([1365, 695, 1445, 755], fill=(210, 255, 220, 255))

    # Amber/Yellow LED Lens (1510, 650, 1680, 800)
    draw.rectangle([1510, 650, 1680, 800], fill=(12, 14, 18, 255), outline=(60, 70, 85, 255), width=3)
    draw.ellipse([1530, 670, 1660, 780], fill=(255, 180, 25, 255), outline=(255, 235, 160, 255), width=5)
    draw.ellipse([1555, 695, 1635, 755], fill=(255, 245, 210, 255))

    # Blue LED Lens (1320, 810, 1490, 960)
    draw.rectangle([1320, 810, 1490, 960], fill=(12, 14, 18, 255), outline=(60, 70, 85, 255), width=3)
    draw.ellipse([1340, 830, 1470, 940], fill=(40, 160, 255, 255), outline=(180, 230, 255, 255), width=5)
    draw.ellipse([1365, 855, 1445, 915], fill=(220, 245, 255, 255))

    # Cyan LED Lens (1510, 810, 1680, 960)
    draw.rectangle([1510, 810, 1680, 960], fill=(12, 14, 18, 255), outline=(60, 70, 85, 255), width=3)
    draw.ellipse([1530, 830, 1660, 940], fill=(45, 215, 255, 255), outline=(190, 245, 255, 255), width=5)
    draw.ellipse([1555, 855, 1635, 915], fill=(230, 255, 255, 255))

    # =========================================================================
    # 5. ANTENNA TEXTURE REGION (1720, 50) to (2020, 960)
    # =========================================================================
    # Brass Knurled SMA Connector Base (1720, 50, 2020, 300)
    draw.rectangle([1720, 50, 2020, 300], fill=(205, 170, 60, 255), outline=(245, 215, 110, 255), width=4)
    for kx in range(1720, 2020, 10):
        draw.line([(kx, 50), (kx + 60, 300)], fill=(160, 130, 40, 255), width=2)
        draw.line([(kx + 60, 50), (kx, 300)], fill=(140, 110, 30, 255), width=2)
    draw.text((1740, 70), "SMA-FEMALE BRASS", fill=(80, 60, 10, 255), font=load_font(FONT_MONO, 14))

    # Matte Ribbed Rubber Antenna Shaft (1720, 320, 2020, 960)
    draw.rectangle([1720, 320, 2020, 960], fill=(30, 32, 38, 255), outline=(65, 70, 82, 255), width=3)
    for gy in range(350, 940, 16):
        draw.line([(1730, gy), (2010, gy)], fill=(18, 20, 24, 255), width=4)
        draw.line([(1730, gy + 3), (2010, gy + 3)], fill=(50, 54, 65, 255), width=2)
    draw.text((1740, 420), "5G / 4G / DUAL-BAND", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 15))
    draw.text((1740, 450), "HIGH GAIN OMNI 5dBi", fill=(55, 205, 255, 255), font=load_font(FONT_MONO, 13))
    draw.text((1740, 480), "FREQ: 698-3800 MHz", fill=(200, 210, 225, 255), font=load_font(FONT_MONO, 12))

    # =========================================================================
    # 6. REAR DIN-RAIL & POWER PANEL (80, 1000) to (1280, 1400)
    # =========================================================================
    rx0, ry0, rx1, ry1 = 80, 1000, 1280, 1400
    draw.rectangle([rx0, ry0, rx1, ry1], fill=(22, 25, 32, 255), outline=(60, 70, 85, 255), width=4)
    draw.text((rx0 + 30, ry0 + 20), "REAR POWER & INDUSTRIAL BUS INTERFACE", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 15))

    draw.rectangle([rx0 + 30, ry0 + 55, rx0 + 380, ry0 + 355], fill=(16, 18, 24, 255), outline=(45, 185, 80, 255), width=3)
    draw_center_text(draw, rx0 + 205, ry0 + 85, "POWER 9-48V DC (DUAL INPUT)", load_font(FONT_MONO, 13), (255, 255, 255, 255))
    for t, t_name in enumerate(["V1+", "V1-", "V2+", "V2-", "GND"]):
        tx = rx0 + 65 + t * 65
        draw.rectangle([tx - 22, ry0 + 130, tx + 22, ry0 + 230], fill=(35, 140, 60, 255), outline=(80, 220, 110, 255), width=2)
        draw.ellipse([tx - 12, ry0 + 150, tx + 12, ry0 + 174], fill=(180, 190, 205, 255), outline=(40, 50, 60, 255), width=2)
        draw.line([(tx - 8, ry0 + 162), (tx + 8, ry0 + 162)], fill=(40, 50, 60, 255), width=3)
        draw_center_text(draw, tx, ry0 + 270, t_name, load_font(FONT_MONO, 13), (55, 205, 255, 255))

    sp_x0 = rx0 + 420
    draw.rectangle([sp_x0, ry0 + 55, rx1 - 30, ry0 + 355], fill=(16, 18, 24, 255), outline=(70, 80, 95, 255), width=2)
    draw.text((sp_x0 + 25, ry0 + 80), "SEC-VISION INDUSTRIAL GATEWAY ROUTER", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 14))
    draw.text((sp_x0 + 25, ry0 + 115), "INPUT: 9-48V DC, 2.5A MAX  |  IEEE 802.3af/at PSE", fill=(175, 185, 200, 255), font=load_font(FONT_MONO, 13))
    draw.text((sp_x0 + 25, ry0 + 150), "STANDARDS: EN 50121-4, IEC 61000-6-2/4, CE, FCC CLASS A", fill=(175, 185, 200, 255), font=load_font(FONT_MONO, 12))
    draw.text((sp_x0 + 25, ry0 + 185), "DIN-RAIL TS-35 MOUNT COMPLIANT  |  IP40 ALUMINUM HOUSING", fill=(55, 205, 255, 255), font=load_font(FONT_MONO, 12))
    draw.text((sp_x0 + 25, ry0 + 225), "SERIAL NO: *IR400-2026-9932B*", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 14))
    for bx in range(sp_x0 + 25, rx1 - 60, 6):
        w = 2 if (bx % 12 == 0) else 4
        draw.rectangle([bx, ry0 + 265, bx + w, ry0 + 325], fill=(225, 230, 240, 255))

    # =========================================================================
    # 7. SIDE HEATSINK LOUVERS (1320..2020, 1000..1500)
    # =========================================================================
    hx0, hy0, hx1, hy1 = 1320, 1000, 2020, 1500
    draw.rectangle([hx0, hy0, hx1, hy1], fill=(20, 23, 28, 255), outline=(60, 70, 85, 255), width=3)
    draw.text((hx0 + 30, hy0 + 20), "EXTRUDED ALUMINUM HEATSINK FINS", fill=(180, 190, 205, 255), font=load_font(FONT_MONO, 14))
    for fin in range(12):
        fy = hy0 + 55 + fin * 36
        draw.rectangle([hx0 + 20, fy, hx1 - 20, fy + 22], fill=(38, 45, 58, 255), outline=(65, 78, 98, 255), width=2)
        draw.line([(hx0 + 24, fy + 3), (hx1 - 24, fy + 3)], fill=(95, 110, 135, 255), width=2)

    # =========================================================================
    # 8. CLEAN METAL & PLASTIC SWATCHES (80..2020, 1550..2000)
    # =========================================================================
    draw.rectangle([80, 1550, 500, 2000], fill=(26, 29, 36, 255))
    draw.rectangle([540, 1550, 960, 2000], fill=(175, 185, 200, 255))
    draw.rectangle([1000, 1550, 1480, 2000], fill=(12, 14, 18, 255))
    draw.rectangle([1520, 1550, 2020, 2000], fill=(32, 35, 42, 255))

    img.save(ATLAS_PATH, "PNG")
    print(f"[Atlas] Upgraded: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

if __name__ == "__main__":
    generate_atlas()
