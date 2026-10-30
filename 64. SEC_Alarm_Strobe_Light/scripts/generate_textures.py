"""
Security CCTV Asset Production Suite - Asset 64
Asset Name: SEC_Alarm_Strobe_Light (Industrial Fire Alarm Strobe Light)
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
    # Base safety red polymer
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), (195, 22, 28, 255))
    draw = ImageDraw.Draw(img)

    # Subtle injection molded polymer texture
    for y in range(0, ATLAS_H, 3):
        noise = ((y * 7) % 6) - 3
        draw.line([(0, y), (ATLAS_W, y)], fill=(195 + noise, 22 + noise, 28 + noise, 255), width=1)

    # =========================================================================
    # 1. BEACON HOUSING COLLAR WRAP (50, 50) to (1450, 650) -> 1400 x 600 px
    # Red sloped collar with bold molded "FIRE" text, candela rating, compliance
    # =========================================================================
    cx0, cy0, cx1, cy1 = 50, 50, 1450, 650
    draw.rectangle([cx0, cy0, cx1, cy1], fill=(190, 20, 26, 255), outline=(135, 14, 18, 255), width=4)

    # Upper and Lower Highlight Ribs
    draw.line([(cx0 + 10, cy0 + 12), (cx1 - 10, cy0 + 12)], fill=(235, 55, 62, 255), width=3)
    draw.line([(cx0 + 10, cy1 - 12), (cx1 - 10, cy1 - 12)], fill=(120, 12, 16, 255), width=3)

    # Bold "FIRE" Molded Lettering (repeated twice around collar)
    for pos_x in [cx0 + 260, cx0 + 960]:
        draw_center_text(draw, pos_x, cy0 + 120, "F I R E", load_font(FONT_SANS, 64), (255, 255, 255, 255))
        draw_center_text(draw, pos_x, cy0 + 175, "SEC-STROBE 110 CD • EMERGENCY ALARM", load_font(FONT_MONO, 16), (245, 195, 35, 255))

    # Candela Rating Selector Window
    cand_x0 = cx0 + 550
    cand_x1 = cand_x0 + 160
    draw.rounded_rectangle([cand_x0, cy0 + 80, cand_x1, cy0 + 200], radius=10, fill=(24, 28, 34, 255), outline=(180, 190, 205, 255), width=2)
    draw_center_text(draw, (cand_x0 + cand_x1)//2, cy0 + 105, "CANDELA", load_font(FONT_MONO, 12), (180, 195, 215, 255))
    draw_center_text(draw, (cand_x0 + cand_x1)//2, cy0 + 140, "[ 110 cd ]", load_font(FONT_SANS, 22), (255, 255, 255, 255))
    draw_center_text(draw, (cand_x0 + cand_x1)//2, cy0 + 175, "15 | 30 | 75 | 110", load_font(FONT_MONO, 11), (245, 195, 35, 255))

    # Technical Specifications & Regulatory Text
    draw.rectangle([cx0 + 40, cy0 + 280, cx1 - 40, cy1 - 40], fill=(24, 28, 35, 255), outline=(90, 15, 20, 255), width=2)
    draw.text((cx0 + 65, cy0 + 310), "MODEL: SEC-STRB-110R  |  SYNCHRONIZED AUDIBLE/VISIBLE STROBE", fill=(255, 255, 255, 255), font=load_font(FONT_SANS, 20))
    draw.text((cx0 + 65, cy0 + 345), "OPERATING VOLTAGE: 16-33V DC / FWR  |  CURRENT: 145mA @ 24VDC", fill=(200, 215, 235, 255), font=load_font(FONT_MONO, 15))
    draw.text((cx0 + 65, cy0 + 375), "FLASH RATE: 1 Hz (60 FLASHES / MINUTE)  |  LIGHT OUTPUT: 110 cd ON-AXIS", fill=(200, 215, 235, 255), font=load_font(FONT_MONO, 15))
    draw.text((cx0 + 65, cy0 + 405), "CERTIFICATIONS: EN 54-23 TYPE B (OPEN CLASS) | UL 1971 / UL 1638 | NFPA 72", fill=(245, 195, 35, 255), font=load_font(FONT_MONO, 15))
    draw.text((cx0 + 65, cy0 + 435), "SERIAL NO: *STRB110-20268841-EXP*  |  CE 0832  |  IP21C INDOOR/OUTDOOR", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 15))

    # =========================================================================
    # 2. SPECULAR CHROME PARABOLIC REFLECTOR DISH (1500, 50) to (2000, 750)
    # Gleaming mirror chrome finish with multi-faceted radial segments
    # =========================================================================
    rx0, ry0, rx1, ry1 = 1500, 50, 2000, 750
    draw.rectangle([rx0, ry0, rx1, ry1], fill=(235, 240, 248, 255), outline=(140, 150, 165, 255), width=4)
    # Radial chrome facet highlights
    rcx = (rx0 + rx1) // 2
    rcy = (ry0 + ry1) // 2
    for r in range(30, 220, 20):
        draw.ellipse([rcx - r, rcy - r, rcx + r, rcy + r], outline=(255, 255, 255, 200), width=2)
    for a in range(0, 360, 22):
        rad = math.radians(a)
        draw.line([(rcx, rcy), (rcx + int(210 * math.cos(rad)), rcy + int(210 * math.sin(rad)))], fill=(190, 200, 215, 180), width=2)
    # Center aperture for xenon tube
    draw.ellipse([rcx - 45, rcy - 45, rcx + 45, rcy + 45], fill=(28, 32, 40, 255), outline=(100, 110, 125, 255), width=3)
    draw_center_text(draw, rcx, rcy, "PARABOLIC DISH", load_font(FONT_MONO, 11), (200, 215, 235, 255))

    # =========================================================================
    # 3. FRESNEL OPTICAL LENS PRISM FLUTES (50, 720) to (1450, 1450)
    # Vertical refractive flutes and concentric prism rings for translucent dome
    # =========================================================================
    fx0, fy0, fx1, fy1 = 50, 720, 1450, 1450
    # Clear ruby-red optical tint
    draw.rectangle([fx0, fy0, fx1, fy1], fill=(235, 60, 68, 255), outline=(180, 25, 32, 255), width=3)

    # Vertical refractive flutes (prismatic columns)
    for x in range(fx0 + 15, fx1 - 15, 18):
        draw.line([(x, fy0 + 10), (x, fy1 - 10)], fill=(255, 150, 155, 200), width=3)
        draw.line([(x + 2, fy0 + 10), (x + 2, fy1 - 10)], fill=(160, 18, 24, 200), width=2)

    # Concentric circular Fresnel rings
    fcx = (fx0 + fx1) // 2
    fcy = (fy0 + fy1) // 2
    for r in range(40, 320, 25):
        draw.ellipse([fcx - r, fcy - r, fcx + r, fcy + r], outline=(255, 210, 215, 180), width=3)
    draw_center_text(draw, fcx, fy0 + 50, "FRESNEL PRISMATIC OPTICAL DOME", load_font(FONT_MONO, 18), (255, 255, 255, 255))
    draw_center_text(draw, fcx, fy1 - 50, "HIGH-TRANSMISSION OPTICAL POLYCARBONATE • UV STABILIZED", load_font(FONT_MONO, 14), (255, 235, 240, 255))

    # =========================================================================
    # 4. MOUNT BASE & CEILING FLANGE (1500, 800) to (2000, 1450)
    # =========================================================================
    mx0, my0, mx1, my1 = 1500, 800, 2000, 1450
    draw.rectangle([mx0, my0, mx1, my1], fill=(185, 20, 26, 255), outline=(130, 14, 18, 255), width=3)
    mcx = (mx0 + mx1) // 2
    mcy = (my0 + my1) // 2
    draw.ellipse([mcx - 140, mcy - 140, mcx + 140, mcy + 140], fill=(170, 18, 24, 255), outline=(225, 45, 52, 255), width=3)
    # Screw tabs
    for sy in [mcy - 100, mcy + 100]:
        draw.ellipse([mcx - 22, sy - 22, mcx + 22, sy + 22], fill=(25, 28, 35, 255), outline=(140, 150, 165, 255), width=2)
        draw.ellipse([mcx - 10, sy - 10, mcx + 10, sy + 10], fill=(180, 190, 205, 255))
    draw_center_text(draw, mcx, mcy - 40, "UNIVERSAL MOUNTING FLANGE", load_font(FONT_MONO, 13), (255, 255, 255, 255))
    draw_center_text(draw, mcx, mcy + 40, "4-INCH OCTAGONAL BOX / WALL", load_font(FONT_MONO, 11), (245, 195, 35, 255))

    # =========================================================================
    # 5. MATERIAL SWATCHES (50..2000, 1500..2020)
    # =========================================================================
    draw.rectangle([50, 1500, 500, 2000], fill=(195, 22, 28, 255))   # Safety Red Polymer
    draw.rectangle([550, 1500, 1000, 2000], fill=(235, 240, 248, 255)) # Chrome Reflector
    draw.rectangle([1050, 1500, 1500, 2000], fill=(255, 255, 255, 255)) # Xenon Pure White
    draw.rectangle([1550, 1500, 2000, 2000], fill=(22, 25, 30, 255))   # Base Dark Gasket

    img.save(ATLAS_PATH, "PNG")
    print(f"[Atlas] Generated: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

if __name__ == "__main__":
    generate_atlas()
