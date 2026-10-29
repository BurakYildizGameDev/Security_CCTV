"""
Security CCTV Asset Production Suite - Asset 58
Asset Name: SEC_Network_Fiber_Patch_Panel (1U 12-Port Dubleks Fiber Patch Panel)
Mathematically-Locked Zero-Shift Texture Atlas Generator (2048x2048)
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
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), (20, 22, 26, 255))
    draw = ImageDraw.Draw(img)

    for y in range(0, ATLAS_H, 4):
        tint = (y * 5) % 8
        draw.line([(0, y), (ATLAS_W, y)], fill=(18 + tint, 20 + tint, 24 + tint, 255), width=1)

    # =========================================================================
    # 1. FRONT 1U FIBER PANEL (74, 30) to (1974, 220) -> 1900 x 190 px (10.0:1)
    # Physical: 440mm x 44mm (X: -0.220 to +0.220, Z: -0.022 to +0.022)
    # =========================================================================
    fx0, fy0, fx1, fy1 = 74, 30, 1974, 220
    draw.rectangle([fx0, fy0, fx1, fy1], fill=(24, 27, 34, 255), outline=(50, 60, 75, 255), width=2)
    draw.line([(fx0 + 2, fy0 + 2), (fx1 - 2, fy0 + 2)], fill=(75, 85, 105, 255), width=2)
    draw.line([(fx0 + 2, fy1 - 2), (fx1 - 2, fy1 - 2)], fill=(12, 14, 18, 255), width=2)

    # Left & Right Rack Ears (74..170 and 1878..1974)
    draw.rectangle([fx0, fy0, fx0 + 96, fy1], fill=(34, 38, 46, 255), outline=(55, 65, 80, 255), width=2)
    draw.rectangle([fx1 - 96, fy0, fx1, fy1], fill=(34, 38, 46, 255), outline=(55, 65, 80, 255), width=2)
    for rx in [fx0 + 48, fx1 - 48]:
        draw.rounded_rectangle([rx - 12, fy0 + 35, rx + 12, fy1 - 35], radius=6, fill=(12, 14, 18, 255), outline=(170, 180, 195, 255), width=2)

    # -------------------------------------------------------------------------
    # ZONE A: TOP HEADER (fy0 + 5 to fy0 + 60) -> Z: +0.008 to +0.022
    # Sits COMPLETELY ABOVE the adapters!
    # -------------------------------------------------------------------------
    # Left Branding
    draw.text((fx0 + 115, fy0 + 8), "SEC-VISION", fill=(255, 255, 255, 255), font=load_font(FONT_SANS, 18))
    draw.text((fx0 + 115, fy0 + 30), "12-PORT DUPLEX LC FIBER PATCH PANEL | OM4 MULTIMODE 50/125µm 100G", fill=(45, 200, 245, 255), font=load_font(FONT_MONO, 11))

    # Right Laser Warning & Model
    draw.text((fx1 - 380, fy0 + 8), "MODEL: SEC-FP12-LC", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 12))
    draw.text((fx1 - 380, fy0 + 30), "▲ CLASS 1 LASER PRODUCT | LOSS < 0.15dB", fill=(245, 185, 25, 255), font=load_font(FONT_MONO, 11))

    # -------------------------------------------------------------------------
    # ZONE B: 12 ADAPTER BEZELS (Center Y: fy0 + 90 = 120) -> Z = 0.000m
    # Mathematical positions: X_i = -0.154 + i * 0.028m (i = 0..11)
    # -------------------------------------------------------------------------
    adapter_cx_px = []
    for i in range(12):
        cx_m = -0.154 + i * 0.028
        # Formula: 74 + ((cx_m + 0.220) / 0.440) * 1900
        cx_px = int(round(74 + ((cx_m + 0.220) / 0.440) * 1900))
        adapter_cx_px.append((cx_m, cx_px))
        cy_px = 120 # Exactly Z = 0.000m

        # Cutout pocket on front plate
        draw.rectangle([cx_px - 34, cy_px - 26, cx_px + 34, cy_px + 26], fill=(12, 14, 18, 255), outline=(45, 55, 68, 255), width=2)
        # Stainless steel spring ear retention tabs on left & right of cutout
        draw.rectangle([cx_px - 38, cy_px - 10, cx_px - 34, cy_px + 10], fill=(185, 195, 210, 255))
        draw.rectangle([cx_px + 34, cy_px - 10, cx_px + 38, cy_px + 10], fill=(185, 195, 210, 255))

    # -------------------------------------------------------------------------
    # ZONE C: TIA-598-C LABEL STRIP (fy0 + 130 to fy0 + 180) -> Z: -0.020 to -0.008
    # Sits COMPLETELY BELOW the adapters!
    # -------------------------------------------------------------------------
    # Label strip bar spans from X = -0.170 to +0.170 in 3D:
    ls_x0_m, ls_x1_m = -0.170, 0.170
    ls_x0_px = int(round(74 + ((ls_x0_m + 0.220) / 0.440) * 1900)) # 290 px
    ls_x1_px = int(round(74 + ((ls_x1_m + 0.220) / 0.440) * 1900)) # 1758 px
    ls_y0, ls_y1 = fy0 + 130, fy0 + 180

    # Clean white/creme industrial label strip
    draw.rectangle([ls_x0_px, ls_y0, ls_x1_px, ls_y1], fill=(245, 246, 250, 255), outline=(150, 160, 175, 255), width=2)

    fiber_colors = [
        (0, 110, 220), (245, 120, 25), (35, 175, 65), (140, 80, 40),
        (140, 145, 155), (255, 255, 255), (225, 35, 35), (25, 25, 28),
        (245, 225, 25), (155, 45, 185), (230, 125, 165), (25, 185, 210)
    ]

    for i, (cx_m, cx_px) in enumerate(adapter_cx_px):
        # Color bar indicator above each port number
        draw.rectangle([cx_px - 28, ls_y0 + 2, cx_px + 28, ls_y0 + 14], fill=fiber_colors[i], outline=(80, 85, 95, 255), width=1)
        # Port number text centered exactly on adapter X
        draw_center_text(draw, cx_px, ls_y0 + 32, f"{i+1:02d}", load_font(FONT_MONO, 14), (15, 18, 24, 255))

    # =========================================================================
    # 2. DEDICATED DUPLEX LC ADAPTER TEXTURE (74, 250) to (600, 550)
    # Maps onto front faces of Adapter_01..12!
    # =========================================================================
    ax0, ay0, ax1, ay1 = 74, 250, 600, 550
    draw.rounded_rectangle([ax0, ay0, ax1, ay1], radius=16, fill=(18, 175, 195, 255), outline=(10, 110, 125, 255), width=6)
    draw.rounded_rectangle([ax0 + 16, ay0 + 16, ax1 - 16, ay1 - 16], radius=12, fill=(15, 145, 165, 255))
    draw.rectangle([ax0 + 60, ay0 + 6, ax1 - 60, ay0 + 22], fill=(210, 218, 230, 255), outline=(120, 130, 145, 255), width=2)
    draw.rectangle([ax0 + 60, ay1 - 22, ax1 - 60, ay1 - 6], fill=(210, 218, 230, 255), outline=(120, 130, 145, 255), width=2)

    for ap_x0, ap_x1, ch_lbl in [(ax0 + 40, ax0 + 240, "A / TX"), (ax1 - 240, ax1 - 40, "B / RX")]:
        draw.rectangle([ap_x0, ay0 + 45, ap_x1, ay1 - 45], fill=(12, 14, 18, 255), outline=(25, 30, 40, 255), width=4)
        cs_cx = (ap_x0 + ap_x1) // 2
        cs_cy = (ay0 + ay1) // 2
        draw.ellipse([cs_cx - 45, cs_cy - 45, cs_cx + 45, cs_cy + 45], fill=(245, 245, 250, 255), outline=(190, 195, 205, 255), width=4)
        draw.ellipse([cs_cx - 16, cs_cy - 16, cs_cx + 16, cs_cy + 16], fill=(10, 12, 15, 255), outline=(100, 105, 115, 255), width=2)
        draw.polygon([(cs_cx - 25, ay0 + 48), (cs_cx + 25, ay0 + 48), (cs_cx, ay0 + 72)], fill=(25, 30, 40, 255))
        draw_center_text(draw, cs_cx, ay1 - 32, ch_lbl, load_font(FONT_MONO, 14), (200, 240, 250, 255))

    # =========================================================================
    # 3. DEDICATED CABLE MANAGER TEXTURE (650, 250) to (1974, 550)
    # =========================================================================
    cx0, cy0, cx1, cy1 = 650, 250, 1974, 550
    draw.rectangle([cx0, cy0, cx1, cy1], fill=(30, 33, 40, 255), outline=(55, 62, 75, 255), width=3)
    draw.text((cx0 + 30, cy0 + 20), "1U FIBER OPTIC CABLE MANAGEMENT HORIZONTAL BAR", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 15))
    for y in range(cy0 + 55, cy1 - 40, 20):
        draw.line([(cx0 + 20, y), (cx1 - 20, y)], fill=(40, 44, 54, 255), width=6)
    for lx in range(cx0 + 60, cx1 - 60, 180):
        draw.rounded_rectangle([lx, cy0 + 80, lx + 120, cy1 - 50], radius=8, fill=(18, 20, 25, 255), outline=(85, 95, 110, 255), width=3)
        draw.text((lx + 20, cy0 + 130), "LOOP", fill=(130, 140, 155, 255), font=load_font(FONT_MONO, 12))

    # =========================================================================
    # 4. REAR FIBER TRAY & TOP COVER (74, 600) to (1974, 1100)
    # =========================================================================
    rx0, ry0, rx1, ry1 = 74, 600, 1974, 1100
    draw.rectangle([rx0, ry0, rx1, ry1], fill=(24, 27, 33, 255), outline=(60, 70, 85, 255), width=3)
    draw.text((rx0 + 30, ry0 + 25), "TOP COVER & REAR SPLICING CASSETTE INTERFACE", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 16))

    tri_cx, tri_cy = rx0 + 200, ry0 + 180
    draw.polygon([(tri_cx, tri_cy - 80), (tri_cx - 70, tri_cy + 50), (tri_cx + 70, tri_cy + 50)], fill=(245, 185, 25, 255), outline=(15, 15, 15, 255), width=6)
    draw.polygon([(tri_cx, tri_cy - 55), (tri_cx - 50, tri_cy + 38), (tri_cx + 50, tri_cy + 38)], fill=(15, 15, 15, 255))
    draw.text((tri_cx - 30, tri_cy - 20), "LASER", fill=(245, 185, 25, 255), font=load_font(FONT_MONO, 16))

    draw.rectangle([rx0 + 320, ry0 + 100, rx0 + 1150, ry0 + 280], fill=(16, 18, 22, 255), outline=(245, 185, 25, 255), width=3)
    draw.text((rx0 + 340, ry0 + 120), "CAUTION: INVISIBLE LASER RADIATION", fill=(245, 185, 25, 255), font=load_font(FONT_MONO, 18))
    draw.text((rx0 + 340, ry0 + 160), "AVOID DIRECT EXPOSURE TO OPTICAL BEAM", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 14))
    draw.text((rx0 + 340, ry0 + 195), "DO NOT VIEW DIRECTLY WITH OPTICAL INSTRUMENTS", fill=(190, 200, 215, 255), font=load_font(FONT_MONO, 12))
    draw.text((rx0 + 340, ry0 + 230), "IEC 60825-1:2014 / CLASS 1 LASER PRODUCT", fill=(55, 205, 255, 255), font=load_font(FONT_MONO, 12))

    sp_x0 = rx0 + 1200
    draw.rectangle([sp_x0, ry0 + 100, rx1 - 40, ry0 + 320], fill=(14, 16, 20, 255), outline=(70, 80, 95, 255), width=2)
    draw.text((sp_x0 + 25, ry0 + 120), "ANTIGRAVITY OPTICAL NETWORKS", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 14))
    draw.text((sp_x0 + 25, ry0 + 150), "1U 12x DUPLEX LC/UPC DISTRIBUTION RACK", fill=(45, 200, 245, 255), font=load_font(FONT_MONO, 12))
    draw.text((sp_x0 + 25, ry0 + 180), "TIA-568-C.3 | ISO/IEC 11801 | GR-326-CORE", fill=(175, 185, 200, 255), font=load_font(FONT_MONO, 11))
    draw.text((sp_x0 + 25, ry0 + 210), "SERIAL NO: *FP12LC202688194C*", fill=(255, 255, 255, 255), font=load_font(FONT_MONO, 12))
    for bx in range(sp_x0 + 25, rx1 - 60, 6):
        w = 2 if (bx % 12 == 0) else 4
        draw.rectangle([bx, ry0 + 250, bx + w, ry0 + 300], fill=(225, 230, 240, 255))

    # =========================================================================
    # 5. MATERIAL SWATCHES (74..1974, 1200..2000)
    # =========================================================================
    draw.rectangle([74, 1500, 500, 2000], fill=(24, 27, 34, 255))
    draw.rectangle([540, 1500, 960, 2000], fill=(175, 185, 200, 255))
    draw.rectangle([1000, 1500, 1480, 2000], fill=(18, 175, 195, 255))
    draw.rectangle([1520, 1500, 2020, 2000], fill=(30, 33, 40, 255))

    img.save(ATLAS_PATH, "PNG")
    print(f"[Atlas] Upgraded mathematically-locked: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

if __name__ == "__main__":
    generate_atlas()
