"""
=============================================================================
Security CCTV Asset Production Suite - Asset 24 (High Detail Upgrade)
Asset Name: SEC_Ceiling_Conduit_Clamp
Texture Generation Script (Standalone System Python + Pillow)
Outputs:
    - exports/T_Metal.png (2048x1024)
=============================================================================
"""

import os
import sys
import math
import random
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

TEXTURE_PATH = os.path.join(EXPORTS_DIR, "T_Metal.png")


def get_fonts():
    """Load clean technical industrial fonts with fallbacks."""
    f_lg = f_md = f_sm = f_xs = None
    font_paths = [
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf"
    ]
    primary = None
    for p in font_paths:
        if os.path.exists(p):
            primary = p
            break

    if primary:
        try:
            f_lg = ImageFont.truetype(primary, 36)
            f_md = ImageFont.truetype(primary, 24)
            f_sm = ImageFont.truetype(primary, 18)
            f_xs = ImageFont.truetype(primary, 13)
        except Exception as e:
            print(f"[WARN] Font load error: {e}")

    if f_lg is None:
        f_lg = f_md = f_sm = f_xs = ImageFont.load_default()

    return f_lg, f_md, f_sm, f_xs


def draw_hex_bolt_texture(draw, cx, cy, rad=36, f_xs=None):
    """Draw a realistic high-strength hex bolt head with grade 8.8 markings."""
    draw.ellipse([cx - rad - 8, cy - rad - 8, cx + rad + 8, cy + rad + 8], fill=(120, 125, 132))
    # Outer flanged washer
    draw.ellipse([cx - rad - 3, cy - rad - 3, cx + rad + 3, cy + rad + 3], fill=(185, 190, 198), outline=(100, 104, 110), width=1)
    
    # Hexagon
    hex_pts = []
    for i in range(6):
        ang = i * (math.pi / 3.0) + math.pi / 6.0
        hex_pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(hex_pts, fill=(205, 210, 218), outline=(85, 90, 96), width=2)

    # Facet highlights
    for i in range(6):
        ang1 = i * (math.pi / 3.0) + math.pi / 6.0
        ang2 = ((i + 1) % 6) * (math.pi / 3.0) + math.pi / 6.0
        p1 = (cx + rad * math.cos(ang1), cy + rad * math.sin(ang1))
        p2 = (cx + rad * math.cos(ang2), cy + rad * math.sin(ang2))
        p_cen = (cx, cy)
        col = (190 + i * 4, 195 + i * 4, 202 + i * 4)
        draw.polygon([p_cen, p1, p2], fill=col)

    draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=(175, 180, 188))
    if f_xs:
        draw.text((cx - 11, cy - 8), "8.8", fill=(45, 50, 56), font=f_xs)


def generate_metal_texture():
    """Generate industrial stamped galvanized steel texture for conduit clamp."""
    W, H = 2048, 1024
    img = Image.new("RGBA", (W, H), (185, 190, 196, 255))
    draw = ImageDraw.Draw(img)
    f_lg, f_md, f_sm, f_xs = get_fonts()

    rng = random.Random(242026)

    # 1. Base Stamped Steel Surface Mottling
    print("[1/5] Synthesizing cold-rolled stamped steel grain...")
    for _ in range(7000):
        px = rng.randint(0, W - 1)
        py = rng.randint(0, H - 1)
        lum = rng.randint(165, 215)
        draw.point((px, py), fill=(lum, lum + 1, lum + 3, 210))

    # 2. Base Ceiling Plate Texture Region (UV V: 0.55 to 0.96 -> Y: 40 to 460, X: 40 to 1000)
    print("[2/5] Designing ceiling base plate details...")
    bp_x1, bp_y1, bp_x2, bp_y2 = 40, 40, 1000, 460
    draw.rounded_rectangle([bp_x1, bp_y1, bp_x2, bp_y2], radius=35, fill=(178, 183, 190), outline=(110, 115, 122), width=3)

    # Mounting anchor slots
    for sx in [bp_x1 + 110, bp_x2 - 110]:
        draw.rounded_rectangle([sx - 28, 230, sx + 28, 275], radius=16, fill=(40, 44, 50), outline=(130, 135, 142), width=2)
        draw.ellipse([sx - 38, 220, sx + 38, 285], outline=(150, 155, 164), width=1)

    # Conduit seating channel indicator
    mid_bp_x = (bp_x1 + bp_x2) // 2
    draw.rectangle([mid_bp_x - 140, bp_y1 + 15, mid_bp_x + 140, bp_y2 - 15], outline=(135, 140, 148), width=2)
    draw.text((mid_bp_x - 110, bp_y1 + 45), "CONDUIT SEATING CHANNEL", fill=(70, 75, 82), font=f_sm)
    draw.text((mid_bp_x - 90, bp_y1 + 80), "Ø 25MM EMT PIPE", fill=(85, 90, 98), font=f_xs)

    # Stamped specs on Base Plate
    draw.text((bp_x1 + 60, bp_y2 - 80), "SEC-CLAMP-C25  ZINC-PLATED HEAVY STEEL  GRADE A", fill=(40, 44, 50), font=f_sm)
    draw.text((bp_x1 + 60, bp_y2 - 50), "MAX STATIC VERTICAL LOAD: 45 KG (100 LBS)  ●  CEILING MOUNT ONLY", fill=(55, 60, 68), font=f_xs)

    # 3. U-Clamp Saddle Band Graphic Region (UV V: 0.55 to 0.96 -> Y: 40 to 460, X: 1050 to 2000)
    print("[3/5] Designing U-clamp curved saddle band...")
    cb_x1, cb_y1, cb_x2, cb_y2 = 1050, 40, 2000, 460
    draw.rounded_rectangle([cb_x1, cb_y1, cb_x2, cb_y2], radius=30, fill=(182, 187, 194), outline=(115, 120, 128), width=2)

    # Stamped stiffening rib along center of saddle band
    draw.rectangle([cb_x1 + 40, 235, cb_x2 - 40, 275], fill=(160, 165, 172), outline=(95, 100, 108), width=1)
    draw.line([(cb_x1 + 40, 236), (cb_x2 - 40, 236)], fill=(225, 230, 238), width=2)

    # Stamped specs on Saddle Band
    mid_cb_x = (cb_x1 + cb_x2) // 2
    draw.text((mid_cb_x - 220, cb_y1 + 50), "SEC HEAVY-DUTY CONDUIT CLAMP", fill=(35, 38, 44), font=f_lg)
    draw.text((mid_cb_x - 175, cb_y1 + 105), "FOR 25MM O.D. EMT / RIGID STEEL CONDUIT", fill=(50, 55, 62), font=f_md)
    draw.text((mid_cb_x - 145, cb_y1 + 150), "TIGHTEN M6 HARDWARE TO 5.5 N·m (48 IN-LB)", fill=(65, 70, 78), font=f_sm)

    draw.text((cb_x1 + 60, cb_y2 - 75), "PN: SEC-CL-25M  ●  HEAT: 2026-08B  ●  EN 61386-21 COMPLIANT", fill=(45, 50, 56), font=f_xs)

    # 4. Hardware Bolts Region (UV V: 0.10 to 0.40 -> Y: 600 to 920)
    print("[4/5] Synthesizing realistic grade 8.8 hex bolt heads...")
    draw.rectangle([0, 520, W, 1024], fill=(172, 177, 184))

    # Bolt 1 and Bolt 2 Head Textures
    draw_hex_bolt_texture(draw, 300, 750, rad=55, f_xs=f_sm)
    draw_hex_bolt_texture(draw, 700, 750, rad=55, f_xs=f_sm)

    draw.text((230, 835), "M6 HEX BOLT (LEFT)", fill=(35, 38, 44), font=f_sm)
    draw.text((630, 835), "M6 HEX BOLT (RIGHT)", fill=(35, 38, 44), font=f_sm)

    # 5. Threaded Screw Shank & Washer Texture Region (X: 1050 to 2000, Y: 550 to 950)
    print("[5/5] Synthesizing threaded shank and washer zone...")
    for ty in range(560, 940, 8):
        draw.line([(1050, ty), (2000, ty)], fill=(60, 65, 72), width=2)
        draw.line([(1050, ty + 2), (2000, ty + 2)], fill=(220, 225, 232), width=2)

    img.save(TEXTURE_PATH, "PNG")
    print(f"[OK] Asset 24 texture generated: {TEXTURE_PATH} ({W}x{H})\n")


if __name__ == "__main__":
    generate_metal_texture()
