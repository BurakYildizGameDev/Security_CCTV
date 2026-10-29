"""
Security CCTV Asset Production Suite - Asset 59
Asset Name: SEC_Power_Distribution_Unit (Rack Güç Dağıtım Ünitesi - PDU)
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

def create_pdu_atlas(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    size = (2048, 2048)
    img = Image.new("RGBA", size, (26, 28, 33, 255))
    draw = ImageDraw.Draw(img)

    # Base texture brushed metal
    for y in range(0, 2048, 4):
        shade = 25 + (y * 3) % 7
        draw.line([(0, y), (2048, y)], fill=(shade, shade + 2, shade + 4, 255), width=1)

    # =========================================================================
    # REGION 1: Front Vertical PDU Strip (20, 20) to (492, 2028)
    # Physical: 48mm x 600mm (aspect approx 1:12.5)
    # =========================================================================
    draw.rectangle([20, 20, 492, 2028], fill=(22, 24, 28, 255), outline=(60, 68, 80, 255), width=3)
    draw.line([(24, 24), (488, 24)], fill=(85, 95, 110, 255), width=2)
    draw.line([(24, 2024), (488, 2024)], fill=(12, 14, 16, 255), width=2)

    # Top & Bottom Safety Warning Bands
    for hx in range(24, 480, 24):
        draw.polygon([(hx, 24), (hx + 12, 24), (hx + 24, 38), (hx + 12, 38)], fill=(245, 185, 25, 255))
        draw.polygon([(hx, 2010), (hx + 12, 2010), (hx + 24, 2024), (hx + 12, 2024)], fill=(245, 185, 25, 255))

    # Top Branding Header (Y: 45 to 195)
    draw.rectangle([30, 45, 482, 195], fill=(16, 18, 22, 255), outline=(50, 56, 68, 255), width=2)
    draw.rectangle([35, 50, 477, 56], fill=(220, 45, 35, 255)) # Safety red line
    draw.text((45, 65), "SEC-POWER", fill=(255, 255, 255, 255), font=load_font(FONT_SANS, 24))
    draw.text((45, 95), "HEAVY DUTY 0U/1U VERTICAL PDU", fill=(45, 195, 245, 255), font=load_font(FONT_MONO, 12))
    draw.text((45, 115), "RATING: 250V~ 16A 50/60Hz 4000W MAX", fill=(220, 225, 235, 255), font=load_font(FONT_MONO, 12))
    draw.text((45, 135), "SURGE SUPPRESSION & EMI/RFI FILTER", fill=(175, 185, 200, 255), font=load_font(FONT_MONO, 11))
    draw.text((45, 155), "IEC 60320 / TUV / CE / RoHS COMPLIANT", fill=(130, 140, 155, 255), font=load_font(FONT_MONO, 10))

    # Main Rocker Switch Bed (Y: 210 to 365)
    draw.rectangle([36, 210, 476, 365], fill=(14, 16, 20, 255), outline=(55, 62, 75, 255), width=2)
    draw_center_text(draw, 256, 230, "MAIN POWER / CIRCUIT BREAKER", load_font(FONT_MONO, 12), (230, 235, 245, 255))
    # Rocker switch cutout pocket
    draw.rectangle([190, 250, 322, 350], fill=(10, 11, 14, 255), outline=(85, 95, 110, 255), width=3)
    draw_center_text(draw, 256, 265, "16A RESET", load_font(FONT_MONO, 10), (220, 70, 60, 255))
    draw_center_text(draw, 256, 335, "OFF", load_font(FONT_MONO, 10), (140, 150, 165, 255))

    # Digital LCD Power Meter Display (Y: 375 to 455)
    draw.rectangle([36, 375, 476, 455], fill=(10, 12, 14, 255), outline=(40, 180, 220, 255), width=2)
    draw.rectangle([42, 380, 470, 450], fill=(8, 28, 34, 255)) # Backlit LCD teal glass
    draw.text((50, 388), "230.4 V   4.25 A   979 W", fill=(60, 240, 255, 255), font=load_font(FONT_MONO, 13))
    draw.text((50, 408), "50.0 Hz   PF:0.99  0142.8 kWh", fill=(60, 240, 255, 255), font=load_font(FONT_MONO, 12))
    draw.text((50, 428), "STATUS: NORMAL [■■■■□□□□] 42%", fill=(120, 255, 180, 255), font=load_font(FONT_MONO, 11))

    # Status LED Panel (Y: 465 to 540)
    draw.rectangle([36, 465, 476, 540], fill=(14, 16, 20, 255), outline=(50, 58, 70, 255), width=2)
    leds = [
        ("SURGE OK", 100, (45, 240, 95)),
        ("GROUND OK", 256, (45, 240, 95)),
        ("OVERLOAD", 412, (245, 60, 45))
    ]
    for lbl, lx, col in leds:
        draw.ellipse([lx - 12, 492 - 12, lx + 12, 492 + 12], fill=(10, 12, 16), outline=(90, 100, 115), width=2)
        draw.ellipse([lx - 8, 492 - 8, lx + 8, 492 + 8], fill=col)
        draw.ellipse([lx - 4, 492 - 4, lx + 2, 492 + 2], fill=(255, 255, 255, 200))
        draw_center_text(draw, lx, 518, lbl, load_font(FONT_MONO, 10), (220, 225, 235, 255))

    # 8 Sockets on Front Strip (Y: 550 to 1860) -> step approx 162px
    for i in range(8):
        sy = 555 + i * 163
        draw.rectangle([36, sy, 476, sy + 152], fill=(16, 18, 22, 255), outline=(45, 52, 65, 255), width=2)
        # Port number & max power
        draw.text((48, sy + 6), f"OUTPUT {i+1}", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 13))
        draw.text((380, sy + 6), "16A MAX", fill=(45, 195, 245, 255), font=load_font(FONT_MONO, 11))

        # Socket circular pocket preview
        scx, scy = 256, sy + 82
        draw.ellipse([scx - 55, scy - 55, scx + 55, scy + 55], fill=(10, 11, 14, 255), outline=(40, 46, 56, 255), width=3)
        # Ground clips
        draw.rectangle([scx - 10, scy - 52, scx + 10, scy - 36], fill=(225, 185, 55, 255))
        draw.rectangle([scx - 10, scy + 36, scx + 10, scy + 52], fill=(225, 185, 55, 255))
        # Pin holes
        draw.ellipse([scx - 32, scy - 12, scx - 8, scy + 12], fill=(4, 5, 6, 255), outline=(60, 68, 80, 255), width=2)
        draw.ellipse([scx + 8, scy - 12, scx + 32, scy + 12], fill=(4, 5, 6, 255), outline=(60, 68, 80, 255), width=2)

    # Bottom Spec Plate (Y: 1870 to 2015)
    draw.rectangle([36, 1870, 476, 2015], fill=(14, 16, 20, 255), outline=(60, 68, 80, 255), width=2)
    draw.text((50, 1885), "MODEL: SEC-PDU-08V-16A", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 13))
    draw.text((50, 1908), "ANTIGRAVITY INDUSTRIAL POWER SYSTEMS", fill=(175, 185, 200, 255), font=load_font(FONT_MONO, 11))
    draw.text((50, 1930), "SN: *PDU-2026-59-902184B* [CE] [RoHS] [TUV]", fill=(45, 195, 245, 255), font=load_font(FONT_MONO, 11))
    for bx in range(50, 460, 6):
        w = 2 if (bx % 12 == 0) else 4
        draw.rectangle([bx, 1955, bx + w, 2000], fill=(220, 225, 235, 255))

    # =========================================================================
    # REGION 2: DEDICATED HIGH-DETAIL SOCKET TEXTURE (550, 50) to (1050, 550)
    # This maps directly onto Socket_01..08 front faces!
    # =========================================================================
    draw.rectangle([550, 50, 1050, 550], fill=(14, 16, 19, 255), outline=(75, 85, 100, 255), width=4)
    # Outer chamfer ring
    draw.ellipse([580, 80, 1020, 520], fill=(22, 25, 30, 255), outline=(65, 75, 90, 255), width=6)
    # Deep recessed well
    draw.ellipse([630, 130, 970, 470], fill=(10, 12, 15, 255), outline=(35, 42, 52, 255), width=5)
    # Brass Ground Clips with metallic specular reflection
    draw.rectangle([775, 140, 825, 210], fill=(225, 190, 55, 255), outline=(255, 230, 120, 255), width=2)
    draw.rectangle([775, 390, 825, 460], fill=(225, 190, 55, 255), outline=(255, 230, 120, 255), width=2)
    # Dual Plug Receptacles
    for px in [680, 870]:
        draw.ellipse([px, 270, px + 60, 330], fill=(4, 5, 6, 255), outline=(50, 58, 70, 255), width=4)
        draw.ellipse([px + 15, 285, px + 45, 315], fill=(2, 2, 3, 255))
    draw_center_text(draw, 800, 280, "16A", load_font(FONT_MONO, 15), (100, 110, 125, 255))
    draw_center_text(draw, 800, 310, "250V~", load_font(FONT_MONO, 14), (100, 110, 125, 255))

    # =========================================================================
    # REGION 3: DEDICATED HIGH-DETAIL ROCKER SWITCH (550, 600) to (1050, 1100)
    # =========================================================================
    draw.rectangle([550, 600, 1050, 1100], fill=(20, 22, 26, 255), outline=(75, 85, 100, 255), width=4)
    # Outer switch bezel
    draw.rectangle([570, 620, 1030, 1080], fill=(15, 17, 20, 255), outline=(40, 46, 56, 255), width=5)
    # Red Translucent Rocker Button Body
    draw.rectangle([600, 650, 1000, 1050], fill=(205, 30, 30, 255), outline=(255, 80, 80, 255), width=5)
    # Center pivot divider step
    draw.line([(600, 850), (1000, 850)], fill=(130, 15, 15, 255), width=8)
    # Crisp laser printed "I" (Upper) and "O" (Lower)
    draw.line([(800, 710), (800, 800)], fill=(255, 255, 255, 255), width=18)
    draw.ellipse([750, 900, 850, 1000], fill=(205, 30, 30, 255), outline=(255, 255, 255, 255), width=18)

    # =========================================================================
    # REGION 4: DEDICATED GLOWING STATUS LED LENS (550, 1150) to (1050, 1450)
    # =========================================================================
    draw.rectangle([550, 1150, 1050, 1450], fill=(12, 14, 18, 255), outline=(60, 70, 85, 255), width=4)
    draw.ellipse([640, 1180, 960, 1420], fill=(40, 245, 95, 255), outline=(190, 255, 210, 255), width=10)
    draw.ellipse([720, 1240, 880, 1360], fill=(225, 255, 235, 255))

    # =========================================================================
    # REGION 5: DARK POWDER COAT & EXTRUDED METAL HOUSING (1100, 0) to (2048, 1024)
    # =========================================================================
    draw.rectangle([1100, 0, 2048, 1024], fill=(30, 33, 38, 255))
    for x in range(1100, 2048, 6):
        t = (x * 7) % 12
        draw.line([(x, 0), (x, 1024)], fill=(30 + t, 33 + t, 38 + t, 255), width=1)
    # Screws along sides
    for my in range(120, 950, 200):
        for mx in [1160, 1980]:
            draw.ellipse([mx - 18, my - 18, mx + 18, my + 18], fill=(15, 17, 20), outline=(90, 100, 115), width=2)
            draw.line([(mx - 10, my), (mx + 10, my)], fill=(160, 170, 185), width=3)

    # =========================================================================
    # REGION 6: GALVANIZED STEEL MOUNTING BRACKETS & WARNINGS (1100, 1050) to (2048, 2048)
    # =========================================================================
    draw.rectangle([1100, 1050, 2048, 2048], fill=(68, 72, 80, 255))
    # Warning decal
    draw.rectangle([1200, 1150, 1950, 1450], fill=(245, 185, 25, 255), outline=(15, 15, 15, 255), width=8)
    draw.text((1240, 1190), "DANGER - HIGH VOLTAGE", fill=(10, 10, 10, 255), font=load_font(FONT_SANS, 26))
    draw.text((1240, 1250), "DISCONNECT MAINS POWER BEFORE SERVICING", fill=(10, 10, 10, 255), font=load_font(FONT_MONO, 16))
    draw.text((1240, 1290), "SUITABLE FOR 19 INCH RACK / 0U VERTICAL POSTS", fill=(10, 10, 10, 255), font=load_font(FONT_MONO, 14))
    draw.text((1240, 1330), "MAX CONTINUOUS LOAD: 16A @ 250V AC", fill=(10, 10, 10, 255), font=load_font(FONT_MONO, 14))

    img.save(output_path, "PNG")
    print(f"[Atlas] Upgraded PDU atlas: {output_path}")

if __name__ == "__main__":
    out = os.path.abspath(r"C:\Users\Burak\Desktop\Security_CCTV\59. SEC_Power_Distribution_Unit\exports\T_Security_Atlas.png")
    create_pdu_atlas(out)
