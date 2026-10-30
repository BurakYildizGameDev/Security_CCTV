"""
Security CCTV Asset Production Suite - Asset 63
Asset Name: SEC_Alarm_Outdoor_Speaker (Outdoor Re-entrant Horn Speaker - 30W IP66)
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
    # Base weatherproof light grey polymer (RAL 7035)
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), (218, 222, 228, 255))
    draw = ImageDraw.Draw(img)

    # Subtle industrial powder coat noise
    for y in range(0, ATLAS_H, 3):
        noise = ((y * 11) % 7) - 3
        draw.line([(0, y), (ATLAS_W, y)], fill=(218 + noise, 222 + noise, 228 + noise, 255), width=1)

    # =========================================================================
    # 1. DRIVER CYLINDER WRAP (50, 50) to (1450, 650) -> 1400 x 600 px
    # Comprehensive technical specification plate and cooling fin band
    # =========================================================================
    dx0, dy0, dx1, dy1 = 50, 50, 1450, 650
    # Brushed aluminum nameplate band
    draw.rectangle([dx0, dy0, dx1, dy0 + 380], fill=(235, 238, 244, 255), outline=(160, 170, 185, 255), width=3)

    # Upper Blue Header Stripe
    draw.rectangle([dx0 + 10, dy0 + 10, dx1 - 10, dy0 + 80], fill=(18, 48, 95, 255))
    draw.text((dx0 + 35, dy0 + 25), "SEC-VISION ENTERPRISE AUDIO", fill=(255, 255, 255, 255), font=load_font(FONT_SANS, 26))
    draw.text((dx0 + 520, dy0 + 28), "INDUSTRIAL RE-ENTRANT HORN SPEAKER", fill=(245, 195, 35, 255), font=load_font(FONT_MONO, 18))
    draw.text((dx1 - 240, dy0 + 28), "IP66 WEATHERPROOF", fill=(220, 240, 255, 255), font=load_font(FONT_MONO, 16))

    # Spec details 2 columns
    draw.text((dx0 + 40, dy0 + 105), "MODEL: SEC-SP30-WP", fill=(15, 20, 30, 255), font=load_font(FONT_SANS, 20))
    draw.text((dx0 + 40, dy0 + 140), "RATED POWER: 30W RMS  (60W PEAK PROGRAM)", fill=(40, 48, 60, 255), font=load_font(FONT_MONO, 15))
    draw.text((dx0 + 40, dy0 + 170), "LINE VOLTAGE: 70V / 100V CONSTANT VOLTAGE", fill=(40, 48, 60, 255), font=load_font(FONT_MONO, 15))
    draw.text((dx0 + 40, dy0 + 200), "POWER TAPS: 30W - 15W - 7.5W - 3.75W @ 100V", fill=(40, 48, 60, 255), font=load_font(FONT_MONO, 15))
    draw.text((dx0 + 40, dy0 + 230), "SOUND PRESSURE: 108 dB (1W/1m)  •  123 dB MAX", fill=(40, 48, 60, 255), font=load_font(FONT_MONO, 15))
    draw.text((dx0 + 40, dy0 + 260), "FREQUENCY RESPONSE: 250 Hz - 10,000 Hz", fill=(40, 48, 60, 255), font=load_font(FONT_MONO, 15))
    draw.text((dx0 + 40, dy0 + 290), "DISPERSION ANGLE: 110° HORIZONTAL x 90° VERTICAL", fill=(40, 48, 60, 255), font=load_font(FONT_MONO, 15))
    draw.text((dx0 + 40, dy0 + 325), "EN 54-24 CERTIFIED  |  ISO 7240-24  |  UL 1480 UUMW", fill=(200, 25, 30, 255), font=load_font(FONT_MONO, 15))

    # Right Box: Compliance, Wiring & Barcode
    rc_x0 = dx0 + 780
    draw.rectangle([rc_x0, dy0 + 95, dx1 - 30, dy0 + 360], fill=(22, 26, 32, 255), outline=(75, 85, 100, 255), width=2)
    draw.text((rc_x0 + 25, dy0 + 115), "WIRING TERMINAL ASSIGNMENT", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 16))
    draw.text((rc_x0 + 25, dy0 + 145), "[1] COM (BLACK)  •  [2] 100V HOT (WHITE)", fill=(45, 215, 115, 255), font=load_font(FONT_MONO, 14))
    draw.text((rc_x0 + 25, dy0 + 175), "ROTARY TAP SWITCH UNDER WATERPROOF REAR SEAL", fill=(245, 195, 35, 255), font=load_font(FONT_MONO, 12))
    draw.text((rc_x0 + 25, dy0 + 205), "SERIAL NO: *SEC-SP30-20268841-WP*", fill=(235, 240, 250, 255), font=load_font(FONT_MONO, 13))

    # Barcode
    for bc in range(rc_x0 + 25, dx1 - 55, 6):
        w = 2 if (bc % 12 == 0) else 4
        draw.rectangle([bc, dy0 + 245, bc + w, dy0 + 300], fill=(240, 245, 255, 255))
    draw.text((rc_x0 + 25, dy0 + 315), "CE  RoHS  IP66  WEEE  MADE IN GERMANY", fill=(170, 185, 205, 255), font=load_font(FONT_MONO, 13))

    # Lower Dark Band: Driver Chamber Anodized Ribs
    draw.rectangle([dx0, dy0 + 390, dx1, dy1], fill=(32, 36, 44, 255), outline=(65, 75, 90, 255), width=2)
    for ry in range(dy0 + 405, dy1 - 15, 20):
        draw.line([(dx0 + 20, ry), (dx1 - 20, ry)], fill=(55, 65, 80, 255), width=4)
        draw.line([(dx0 + 20, ry + 2), (dx1 - 20, ry + 2)], fill=(15, 18, 22, 255), width=2)

    # =========================================================================
    # 2. U-BRACKET BACKPLATE & TILT SCALE (1500, 50) to (2000, 750) -> 500 x 700 px
    # Part A: Wall Mounting Flange Backplate (1500, 50) to (2000, 500)
    # Part B: Side Pivot Angle Graduation Scale (1500, 520) to (2000, 750)
    # =========================================================================
    # Part A: Wall Plate (1500, 50) to (2000, 500)
    bx0, by0, bx1, by1 = 1500, 50, 2000, 500
    draw.rectangle([bx0, by0, bx1, by1], fill=(180, 186, 196, 255), outline=(105, 115, 130, 255), width=4)
    # Galvanized zinc spangle grain
    for y in range(by0, by1, 4):
        sp = ((y * 17) % 15) - 7
        draw.line([(bx0, y), (bx1, y)], fill=(180 + sp, 186 + sp, 196 + sp, 255), width=2)

    # Outer stamped bevel border
    draw.line([(bx0 + 8, by0 + 8), (bx1 - 8, by0 + 8)], fill=(225, 230, 240, 255), width=3)
    draw.line([(bx0 + 8, by0 + 8), (bx0 + 8, by1 - 8)], fill=(225, 230, 240, 255), width=3)
    draw.line([(bx0 + 8, by1 - 8), (bx1 - 8, by1 - 8)], fill=(110, 120, 135, 255), width=3)
    draw.line([(bx1 - 8, by0 + 8), (bx1 - 8, by1 - 8)], fill=(110, 120, 135, 255), width=3)

    bcx = (bx0 + bx1) // 2

    # Top Keyhole Mounting Slot (by0 + 40 to by0 + 95)
    slot1_y = by0 + 65
    draw.rounded_rectangle([bcx - 90, slot1_y - 18, bcx + 90, slot1_y + 18], radius=16, fill=(24, 28, 35, 255), outline=(85, 95, 110, 255), width=2)
    draw.ellipse([bcx - 80, slot1_y - 13, bcx - 54, slot1_y + 13], fill=(195, 205, 220, 255))
    draw.ellipse([bcx + 54, slot1_y - 13, bcx + 80, slot1_y + 13], fill=(195, 205, 220, 255))
    draw_center_text(draw, bcx, slot1_y - 30, "MOUNTING SLOT (UPPER)", load_font(FONT_MONO, 11), (50, 60, 75, 255))

    # Center Stamped Metal Specification Plaque (by0 + 130 to by0 + 350)
    draw.rectangle([bx0 + 25, by0 + 130, bx1 - 25, by0 + 350], fill=(210, 215, 225, 255), outline=(130, 140, 155, 255), width=2)
    draw_center_text(draw, bcx, by0 + 160, "SEC-AUDIO 30W HORN SPEAKER", load_font(FONT_SANS, 18), (20, 25, 35, 255))
    draw_center_text(draw, bcx, by0 + 195, "HEAVY-GAUGE STAMPED STEEL U-BRACKET", load_font(FONT_MONO, 13), (45, 55, 70, 255))
    draw_center_text(draw, bcx, by0 + 230, "MAX TILT: ±25°  |  MAX LOAD: 15 KG", load_font(FONT_MONO, 13), (200, 25, 30, 255))
    draw_center_text(draw, bcx, by0 + 265, "HOLE SPACING: 60mm C-C  |  EN 54-24 COMPLIANT", load_font(FONT_MONO, 12), (50, 60, 75, 255))
    draw_center_text(draw, bcx, by0 + 300, "CE  •  IP66  •  ROHS  •  SERIAL: *SP30-BRK*", load_font(FONT_MONO, 12), (30, 35, 45, 255))
    draw_center_text(draw, bcx, by0 + 330, "MADE IN GERMANY", load_font(FONT_MONO, 11), (75, 85, 100, 255))

    # Bottom Keyhole Mounting Slot (by1 - 95 to by1 - 40)
    slot2_y = by1 - 65
    draw.rounded_rectangle([bcx - 90, slot2_y - 18, bcx + 90, slot2_y + 18], radius=16, fill=(24, 28, 35, 255), outline=(85, 95, 110, 255), width=2)
    draw.ellipse([bcx - 80, slot2_y - 13, bcx - 54, slot2_y + 13], fill=(195, 205, 220, 255))
    draw.ellipse([bcx + 54, slot2_y - 13, bcx + 80, slot2_y + 13], fill=(195, 205, 220, 255))
    draw_center_text(draw, bcx, slot2_y + 30, "MOUNTING SLOT (LOWER)", load_font(FONT_MONO, 11), (50, 60, 75, 255))

    # Part B: Side Pivot Angle Graduation Scale (1500, 520) to (2000, 750)
    sx0, sy0, sx1, sy1 = 1500, 520, 2000, 750
    draw.rectangle([sx0, sy0, sx1, sy1], fill=(170, 178, 190, 255), outline=(100, 110, 125, 255), width=3)
    scx = (sx0 + sx1) // 2
    scy = (sy0 + sy1) // 2

    # Pivot bolt center hole ring
    draw.ellipse([scx - 45, scy - 45, scx + 45, scy + 45], fill=(30, 35, 45, 255), outline=(220, 230, 245, 255), width=3)
    draw.ellipse([scx - 25, scy - 25, scx + 25, scy + 25], fill=(190, 200, 215, 255))

    # Radial Degree Ticks (-25° to +25°)
    for deg in range(-25, 26, 5):
        rad = math.radians(deg)
        r0 = 65
        r1 = 85 if (deg % 10 == 0) else 75
        x_start = scx + int(r0 * math.sin(rad))
        y_start = scy - int(r0 * math.cos(rad))
        x_end   = scx + int(r1 * math.sin(rad))
        y_end   = scy - int(r1 * math.cos(rad))
        w = 3 if (deg % 10 == 0) else 2
        draw.line([(x_start, y_start), (x_end, y_end)], fill=(20, 25, 35, 255), width=w)

    draw_center_text(draw, scx, scy - 95, "0°", load_font(FONT_MONO, 14), (20, 25, 35, 255))
    draw_center_text(draw, scx - 55, scy - 82, "-15°", load_font(FONT_MONO, 12), (20, 25, 35, 255))
    draw_center_text(draw, scx + 55, scy - 82, "+15°", load_font(FONT_MONO, 12), (20, 25, 35, 255))
    draw_center_text(draw, scx - 85, scy - 45, "-25°", load_font(FONT_MONO, 12), (20, 25, 35, 255))
    draw_center_text(draw, scx + 85, scy - 45, "+25°", load_font(FONT_MONO, 12), (20, 25, 35, 255))
    draw_center_text(draw, scx, scy + 70, "TILT DEGREE SCALE", load_font(FONT_MONO, 13), (30, 35, 45, 255))

    # =========================================================================
    # 3. HORN BELL INTERIOR ACOUSTIC THROAT & RINGS (50, 720) to (1450, 1450)
    # Deep acoustic throat texture with concentric dispersion steps
    # =========================================================================
    hx0, hy0, hx1, hy1 = 50, 720, 1450, 1450
    draw.rectangle([hx0, hy0, hx1, hy1], fill=(210, 214, 222, 255), outline=(150, 160, 175, 255), width=3)
    # Subtle concentric acoustic dispersion grooving
    hcx = (hx0 + hx1) // 2
    hcy = (hy0 + hy1) // 2
    for r in range(40, 320, 25):
        draw.ellipse([hcx - r, hcy - r, hcx + r, hcy + r], outline=(175, 182, 195, 255), width=2)
    # Center throat aperture
    draw.ellipse([hcx - 70, hcy - 70, hcx + 70, hcy + 70], fill=(45, 50, 60, 255), outline=(25, 28, 35, 255), width=4)
    draw.ellipse([hcx - 35, hcy - 35, hcx + 35, hcy + 35], fill=(18, 20, 25, 255))
    draw_center_text(draw, hcx, hy0 + 60, "SEC-VISION HIGH-EFFICIENCY ACOUSTIC RE-ENTRANT HORN", load_font(FONT_SANS, 20), (50, 60, 75, 255))
    draw_center_text(draw, hcx, hy1 - 60, "UV-RESISTANT THERMOPLASTIC • FLAME-RETARDANT UL94V-0", load_font(FONT_MONO, 15), (75, 85, 100, 255))

    # =========================================================================
    # 4. CABLE GLAND & NUT (1500, 800) to (2000, 1200)
    # Black nylon PG-11 waterproof gland, threads and rubber gasket
    # =========================================================================
    gx0, gy0, gx1, gy1 = 1500, 800, 2000, 1200
    draw.rectangle([gx0, gy0, gx1, gy1], fill=(25, 28, 34, 255), outline=(55, 65, 80, 255), width=3)
    # Thread rings
    for y in range(gy0 + 30, gy1 - 30, 18):
        draw.line([(gx0 + 20, y), (gx1 - 20, y)], fill=(45, 55, 68, 255), width=3)
        draw.line([(gx0 + 20, y + 2), (gx1 - 20, y + 2)], fill=(15, 18, 22, 255), width=2)
    draw_center_text(draw, (gx0 + gx1)//2, gy0 + 80, "PG-11 CABLE GLAND", load_font(FONT_MONO, 16), (220, 230, 245, 255))
    draw_center_text(draw, (gx0 + gx1)//2, gy1 - 80, "IP68 WATER SEAL", load_font(FONT_MONO, 14), (45, 215, 115, 255))

    # =========================================================================
    # 5. HORN BELL EXTERIOR CASING & COLLAR (50, 1480) to (1450, 1850) -> 1400 x 370 px
    # Realistic polymer gradient, molded seams, throat collar bolts & brand marking
    # =========================================================================
    ex0, ey0, ex1, ey1 = 50, 1480, 1450, 1850
    # Gradient from throat (darker) to mouth (lighter)
    for y in range(ey0, ey1):
        f = (y - ey0) / (ey1 - ey0)
        c = int(200 + f * 24)
        draw.line([(ex0, y), (ex1, y)], fill=(c, c + 2, c + 6, 255))
    draw.rectangle([ex0, ey0, ex1, ey1], outline=(155, 165, 180, 255), width=3)
    # Throat collar band with hex bolts
    draw.rectangle([ex0, ey0, ex1, ey0 + 60], fill=(185, 192, 202, 255), outline=(130, 140, 155, 255), width=2)
    for bx in range(ex0 + 50, ex1 - 40, 90):
        draw.ellipse([bx - 10, ey0 + 20, bx + 10, ey0 + 40], fill=(130, 138, 150, 255), outline=(90, 100, 115, 255), width=2)
    # Molded center marking
    draw_center_text(draw, (ex0 + ex1)//2, (ey0 + ey1)//2 + 20, "SEC-VISION  •  IP66 OUTDOOR HIGH-OUTPUT HORN  •  30W RMS", load_font(FONT_MONO, 18), (80, 90, 105, 255))
    draw_center_text(draw, (ex0 + ex1)//2, (ey0 + ey1)//2 + 55, "UV-STABILIZED THERMOPLASTIC COMPOSITE  |  EN 54-24", load_font(FONT_MONO, 14), (100, 110, 125, 255))

    # =========================================================================
    # 6. MATERIAL SWATCHES (1500..2000, 1250..2020)
    # =========================================================================
    draw.rectangle([1500, 1250, 1720, 1600], fill=(218, 222, 228, 255)) # Light Grey Polymer
    draw.rectangle([1750, 1250, 2000, 1600], fill=(175, 182, 195, 255)) # Zinc Steel
    draw.rectangle([1500, 1650, 1720, 2000], fill=(32, 36, 44, 255))   # Dark Anodized Aluminum
    draw.rectangle([1750, 1650, 2000, 2000], fill=(22, 25, 30, 255))   # Black Rubber

    img.save(ATLAS_PATH, "PNG")
    print(f"[Atlas] Generated: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

if __name__ == "__main__":
    generate_atlas()
