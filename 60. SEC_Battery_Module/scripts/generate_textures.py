"""
Security CCTV Asset Production Suite - Asset 60
Asset Name: SEC_Battery_Module (Rack Yedek Batarya Modülü - 2U)
Upgraded Ultra-Detail Texture Atlas Generator (2048x2048)
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

FONT_MONO = r"C:\Windows\Fonts\consolab.ttf"
FONT_SANS = r"C:\Windows\Fonts\arialbd.ttf"

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

def create_battery_atlas(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    size = (2048, 2048)
    img = Image.new("RGBA", size, (24, 26, 30, 255))
    draw = ImageDraw.Draw(img)

    for y in range(0, 2048, 4):
        tint = (y * 5) % 8
        draw.line([(0, y), (2048, y)], fill=(22 + tint, 24 + tint, 28 + tint, 255), width=1)

    # =========================================================================
    # REGION 1: Front Panel Fascia (40, 40) to (1960, 420) -> 1920 x 380 px
    # =========================================================================
    draw.rectangle([40, 40, 1960, 420], fill=(22, 24, 28, 255), outline=(65, 75, 90, 255), width=3)
    draw.line([(44, 44), (1956, 44)], fill=(80, 92, 110, 255), width=2)
    draw.line([(44, 416), (1956, 416)], fill=(12, 14, 16, 255), width=2)

    # Rack Ears: Left (40..140) and Right (1860..1960)
    draw.rectangle([40, 40, 140, 420], fill=(36, 40, 48, 255), outline=(65, 72, 85, 255), width=2)
    draw.rectangle([1860, 40, 1960, 420], fill=(36, 40, 48, 255), outline=(65, 72, 85, 255), width=2)
    for ey in [110, 350]:
        draw.rounded_rectangle([68, ey - 22, 112, ey + 22], radius=8, fill=(12, 14, 18, 255), outline=(175, 185, 200, 255), width=3)
        draw.rounded_rectangle([1888, ey - 22, 1932, ey + 22], radius=8, fill=(12, 14, 18, 255), outline=(175, 185, 200, 255), width=3)

    # Vivid Yellow Industrial Safety Stripe Across Top
    draw.rectangle([140, 44, 1860, 56], fill=(245, 185, 25, 255))

    # --- LEFT SECTION: Branding, BMS Display & Controls (150 to 650) ---
    draw.text((160, 68), "SEC-BATTERY LFP-48V", fill=(255, 255, 255, 255), font=load_font(FONT_SANS, 24))
    draw.text((160, 98), "INDUSTRIAL 2U RACKMOUNT LiFePO4 ENERGY STORAGE", fill=(55, 205, 255, 255), font=load_font(FONT_MONO, 12))
    draw.text((160, 118), "CAPACITY: 48V DC NOMINAL | 100Ah | 4800Wh | 1C RATE", fill=(175, 185, 200, 255), font=load_font(FONT_MONO, 11))

    # High-Tech BMS OLED Status Display (160, 145) to (620, 260)
    draw.rectangle([160, 145, 620, 260], fill=(10, 12, 16, 255), outline=(40, 180, 220, 255), width=2)
    draw.rectangle([166, 150, 614, 255], fill=(6, 24, 30, 255))
    draw.text((178, 158), "SEC-LFP-48100  |  BATT: 99.8% [SOC]", fill=(60, 240, 255, 255), font=load_font(FONT_MONO, 13))
    draw.text((178, 180), "VOLT: 53.6V   CURR: +0.0A   TEMP: 24.5°C", fill=(60, 240, 255, 255), font=load_font(FONT_MONO, 12))
    draw.text((178, 202), "CELL DELTA: 0.008V  |  SOH: 100% EXCELLENT", fill=(120, 255, 180, 255), font=load_font(FONT_MONO, 11))
    draw.text((178, 226), "STATUS: FLOAT CHG  [■■■■■■■■] NORMAL", fill=(120, 255, 180, 255), font=load_font(FONT_MONO, 12))

    # Dual RS-485 / CAN Bus Daisy Chain Ports & 125A DC Breaker (160, 275) to (620, 395)
    draw.rectangle([160, 275, 380, 395], fill=(16, 18, 22, 255), outline=(55, 65, 80, 255), width=2)
    draw_center_text(draw, 270, 290, "CAN / RS-485 BUS", load_font(FONT_MONO, 11), (200, 210, 225, 255))
    # Dual RJ-45 jacks
    for jx, jlbl in [(190, "LINK IN"), (285, "LINK OUT")]:
        draw.rectangle([jx, 310, jx + 65, 370], fill=(10, 12, 15, 255), outline=(150, 160, 175, 255), width=2)
        draw.rectangle([jx + 12, 350, jx + 53, 370], fill=(5, 6, 8, 255))
        draw_center_text(draw, jx + 32, 385, jlbl, load_font(FONT_MONO, 9), (55, 205, 255, 255))

    # DC Breaker (400, 275) to (620, 395)
    draw.rectangle([400, 275, 620, 395], fill=(16, 18, 22, 255), outline=(60, 68, 80, 255), width=2)
    draw_center_text(draw, 510, 292, "125A DC BREAKER", load_font(FONT_MONO, 11), (255, 255, 255, 255))
    draw.rectangle([440, 315, 580, 370], fill=(25, 27, 32, 255), outline=(220, 45, 35, 255), width=3)
    draw.rectangle([485, 325, 535, 360], fill=(220, 45, 35, 255))
    draw_center_text(draw, 510, 342, "ON", load_font(FONT_MONO, 12), (255, 255, 255, 255))

    # --- CENTER SECTION: Recessed Pull Handle Pocket (660 to 1260) ---
    draw.rectangle([660, 75, 1260, 385], fill=(14, 16, 19, 255), outline=(50, 58, 70, 255), width=2)
    draw.rectangle([670, 85, 1250, 375], fill=(8, 9, 12, 255), outline=(35, 40, 48, 255), width=3)

    # Yellow Safety Decal Inside Handle Pocket
    draw.rectangle([760, 115, 1160, 205], fill=(245, 185, 25, 255), outline=(15, 15, 15, 255), width=3)
    draw_center_text(draw, 960, 140, "CAUTION: HEAVY WEIGHT", load_font(FONT_SANS, 16), (10, 10, 10, 255))
    draw_center_text(draw, 960, 168, "TWO PERSON LIFT REQUIRED - 32 KG", load_font(FONT_MONO, 13), (10, 10, 10, 255))
    draw_center_text(draw, 960, 190, "GRIP PULL HANDLE FIRMLY", load_font(FONT_MONO, 11), (20, 20, 20, 255))

    draw_center_text(draw, 960, 340, "FOLD-DOWN EXTRACTION HANDLE", load_font(FONT_MONO, 12), (120, 130, 145, 255))

    # --- RIGHT SECTION: High-Current DC Terminals & Vents (1280 to 1840) ---
    draw.rectangle([1280, 75, 1640, 385], fill=(16, 18, 22, 255), outline=(55, 65, 80, 255), width=2)

    # Positive Terminal Bed (1300 to 1620, Y: 95 to 225)
    draw.rectangle([1300, 95, 1620, 225], fill=(32, 14, 16, 255), outline=(220, 40, 40, 255), width=2)
    draw.ellipse([1430, 120, 1490, 180], fill=(215, 30, 30, 255), outline=(255, 110, 110, 255), width=3)
    draw_center_text(draw, 1460, 150, "+", load_font(FONT_SANS, 28), (255, 255, 255, 255))
    draw_center_text(draw, 1460, 205, "(+) POSITIVE 48V DC", load_font(FONT_MONO, 12), (255, 110, 110, 255))

    # Negative Terminal Bed (1300 to 1620, Y: 245 to 375)
    draw.rectangle([1300, 245, 1620, 375], fill=(14, 18, 26, 255), outline=(45, 110, 225, 255), width=2)
    draw.ellipse([1430, 270, 1490, 330], fill=(22, 26, 34, 255), outline=(80, 150, 255, 255), width=3)
    draw_center_text(draw, 1460, 300, "-", load_font(FONT_SANS, 32), (255, 255, 255, 255))
    draw_center_text(draw, 1460, 355, "(-) NEGATIVE 0V DC", load_font(FONT_MONO, 12), (110, 180, 255, 255))

    # Right Exhaust Heat Louvers (1660 to 1835)
    for vy in range(95, 370, 16):
        draw.rectangle([1665, vy, 1830, vy + 9], fill=(10, 11, 14, 255), outline=(40, 46, 56, 255), width=1)

    # =========================================================================
    # REGION 2: DEDICATED PULL HANDLE TEXTURE (40, 480) to (800, 880)
    # =========================================================================
    draw.rectangle([40, 480, 800, 880], fill=(24, 26, 32, 255), outline=(65, 75, 90, 255), width=3)
    draw.text((60, 495), "PULL HANDLE METAL & RUBBER TEXTURE", fill=(200, 210, 225, 255), font=load_font(FONT_MONO, 13))
    # Non-slip rubber ribbed grip
    draw.rectangle([100, 535, 740, 825], fill=(28, 30, 36, 255), outline=(45, 50, 60, 255), width=2)
    for gx in range(120, 720, 18):
        draw.line([(gx, 545), (gx, 815)], fill=(16, 18, 22, 255), width=5)
        draw.line([(gx + 4, 545), (gx + 4, 815)], fill=(50, 55, 66, 255), width=3)
    draw_center_text(draw, 420, 855, "[ ◄ PULL TO EXTRACT ► ]", load_font(FONT_MONO, 14), (245, 185, 25, 255))

    # =========================================================================
    # REGION 3: DEDICATED POSITIVE TERMINAL BOSS (850, 480) to (1250, 880)
    # =========================================================================
    draw.rectangle([850, 480, 1250, 880], fill=(18, 20, 24, 255), outline=(65, 75, 90, 255), width=3)
    # Hexagonal / Circular Red Insulator Boss
    draw.ellipse([880, 510, 1220, 850], fill=(205, 30, 30, 255), outline=(255, 95, 95, 255), width=8)
    draw.ellipse([940, 570, 1160, 790], fill=(150, 20, 20, 255), outline=(225, 190, 60, 255), width=5)
    # Threaded Copper Stud & Hex Nut
    draw.ellipse([1010, 640, 1090, 720], fill=(225, 160, 50, 255), outline=(255, 225, 120, 255), width=4)
    draw_center_text(draw, 1050, 545, "( + ) 48V", load_font(FONT_MONO, 14), (255, 230, 230, 255))

    # =========================================================================
    # REGION 4: DEDICATED NEGATIVE TERMINAL BOSS (1300, 480) to (1700, 880)
    # =========================================================================
    draw.rectangle([1300, 480, 1700, 880], fill=(18, 20, 24, 255), outline=(65, 75, 90, 255), width=3)
    # Dark Insulator Boss
    draw.ellipse([1330, 510, 1670, 850], fill=(32, 36, 44, 255), outline=(75, 85, 105, 255), width=8)
    draw.ellipse([1390, 570, 1610, 790], fill=(20, 22, 28, 255), outline=(225, 190, 60, 255), width=5)
    # Threaded Copper Stud & Hex Nut
    draw.ellipse([1460, 640, 1540, 720], fill=(225, 160, 50, 255), outline=(255, 225, 120, 255), width=4)
    draw_center_text(draw, 1500, 545, "( - ) 0V", load_font(FONT_MONO, 14), (200, 225, 255, 255))

    # =========================================================================
    # REGION 5: TOP SHEET METAL & HAZARD LABELS (40, 950) to (2008, 1500)
    # =========================================================================
    draw.rectangle([40, 950, 2008, 1500], fill=(30, 33, 38, 255))
    for x in range(40, 2008, 6):
        col = 30 + (x * 7) % 10
        draw.line([(x, 950), (x, 1500)], fill=(col, col, col + 2, 255), width=1)

    # Top Cover Big Hazard Triangle & Banner
    draw.rectangle([180, 1020, 1100, 1420], fill=(245, 185, 25, 255), outline=(15, 15, 15, 255), width=8)
    # Triangle icon
    draw.polygon([(260, 1060), (200, 1160), (320, 1160)], fill=(15, 15, 15, 255))
    draw.polygon([(260, 1080), (218, 1150), (302, 1150)], fill=(245, 185, 25, 255))
    draw.text((254, 1095), "!", fill=(15, 15, 15, 255), font=load_font(FONT_SANS, 34))

    draw.text((350, 1060), "DANGER: HIGH ENERGY LITHIUM STORAGE", fill=(10, 10, 10, 255), font=load_font(FONT_SANS, 24))
    draw.text((350, 1105), "RISK OF ELECTRIC SHOCK AND FIRE HAZARD - SHORT CIRCUIT CURRENT > 2000A", fill=(15, 15, 15, 255), font=load_font(FONT_MONO, 13))
    draw.text((350, 1135), "DO NOT SHORT CIRCUIT, CRUSH, INCINERATE OR IMMERSE IN LIQUIDS", fill=(15, 15, 15, 255), font=load_font(FONT_MONO, 13))
    draw.text((200, 1195), "STANDARD COMPLIANCE: UN 38.3 / IEC 62619 / UL 1973 / CE / RoHS / ISO 9001", fill=(10, 10, 10, 255), font=load_font(FONT_MONO, 13))
    draw.text((200, 1225), "QUALIFIED SERVICE PERSONNEL ONLY - DISCONNECT DC BREAKER BEFORE HANDLING", fill=(10, 10, 10, 255), font=load_font(FONT_MONO, 13))

    # Top ventilation arrays
    for px in range(1200, 1920, 28):
        for py in range(1010, 1440, 22):
            draw.ellipse([px, py, px + 12, py + 12], fill=(14, 16, 20, 255))

    # =========================================================================
    # REGION 6: INDUSTRIAL SPEC PLATE (40, 1550) to (2008, 2008)
    # =========================================================================
    draw.rectangle([40, 1550, 2008, 2008], fill=(60, 65, 72, 255))
    draw.rectangle([100, 1620, 1100, 1960], fill=(245, 246, 250, 255), outline=(25, 28, 34, 255), width=4)
    draw.text((130, 1645), "ANTIGRAVITY BATTERY SYSTEMS INC.", fill=(10, 12, 16, 255), font=load_font(FONT_SANS, 20))
    draw.text((130, 1685), "PRODUCT: 2U RACKMOUNT LiFePO4 CARTRIDGE", fill=(20, 25, 32, 255), font=load_font(FONT_MONO, 14))
    draw.text((130, 1715), "MODEL: SEC-BAT-48100-2U  |  48V DC 100Ah 4800Wh", fill=(20, 25, 32, 255), font=load_font(FONT_MONO, 13))
    draw.text((130, 1745), "MAX CHARGE/DISCHARGE: 100A CONT / 150A PEAK 10s", fill=(20, 25, 32, 255), font=load_font(FONT_MONO, 13))
    draw.text((130, 1775), "SERIAL NUMBER: *SN-2026-BAT-60-8472910B*", fill=(10, 12, 16, 255), font=load_font(FONT_MONO, 13))
    for bx in range(130, 1050, 8):
        w = 3 if (bx % 16 == 0) else 5
        draw.rectangle([bx, 1815, bx + w, 1930], fill=(10, 12, 16, 255))

    img.save(output_path, "PNG")
    print(f"[Atlas] Upgraded Battery Module atlas: {output_path}")

if __name__ == "__main__":
    out = os.path.abspath(r"C:\Users\Burak\Desktop\Security_CCTV\60. SEC_Battery_Module\exports\T_Security_Atlas.png")
    create_battery_atlas(out)
