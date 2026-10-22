"""
=============================================================================
Security CCTV Asset Production Suite - Asset 22 (Refined High Detail)
Asset Name: SEC_Conduit_Corner_90
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


def draw_barcode(draw, x, y, w, h, code_text, font_xs):
    """Draw a crisp industrial asset tracking barcode."""
    rng = random.Random(222026)
    draw.rectangle([x, y, x + w, y + h], fill=(242, 245, 248))
    bx = x + 10
    max_x = x + w - 10
    draw.rectangle([bx, y + 4, bx + 3, y + h - 16], fill=(20, 22, 26))
    bx += 6
    while bx < max_x - 6:
        bw = rng.choice([2, 3, 4])
        sp = rng.choice([2, 3])
        if bx + bw > max_x:
            break
        draw.rectangle([bx, y + 4, bx + bw, y + h - 16], fill=(20, 22, 26))
        bx += bw + sp
    draw.text((x + 12, y + h - 14), code_text, fill=(30, 32, 36), font=font_xs)


def generate_metal_texture():
    """Generate high-fidelity galvanized steel texture for 90-degree conduit elbow."""
    W, H = 2048, 1024
    img = Image.new("RGBA", (W, H), (192, 196, 202, 255))
    draw = ImageDraw.Draw(img)
    f_lg, f_md, f_sm, f_xs = get_fonts()

    rng = random.Random(4222)

    # 1. Base Galvanized Spangle Mottling
    print("[1/5] Synthesizing hot-dip zinc crystallization spangles...")
    for _ in range(750):
        cx = rng.randint(0, W)
        cy = rng.randint(0, H)
        rad = rng.randint(14, 40)
        base_lum = rng.randint(175, 222)
        tint = rng.randint(-2, 2)
        color = (base_lum + tint, base_lum + tint + 2, base_lum + 4, 255)

        num_pts = rng.randint(5, 7)
        poly = []
        for p in range(num_pts):
            ang = p * (2 * math.pi / num_pts) + rng.uniform(-0.25, 0.25)
            r = rad * rng.uniform(0.70, 1.25)
            poly.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        draw.polygon(poly, fill=color)

    # 2. Brushed Metal Extrusion Grain (along X direction)
    print("[2/5] Applying longitudinal extrusion grain...")
    for _ in range(1600):
        y_pos = rng.randint(0, H - 1)
        x_start = rng.randint(0, W // 2)
        x_len = rng.randint(300, 1400)
        c_val = rng.randint(168, 220)
        alpha = rng.randint(25, 65)
        draw.line([(x_start, y_pos), (min(W, x_start + x_len), y_pos)],
                  fill=(c_val, c_val + 2, c_val + 4, alpha), width=1)

    # 3. Inner pipe bore zone (UV V: 0.35 to 0.50 -> Y: 512 to 665)
    print("[3/5] Shading inner pipe bore zone...")
    for y in range(512, 665):
        ratio = (y - 512) / 153.0
        darken = int(45 * (1.0 - math.sin(ratio * math.pi) * 0.4))
        draw.line([(0, y), (W, y)], fill=(95 + darken // 2, 99 + darken // 2, 105 + darken // 2, 240))

    # 4. Technical Markings on Outer Surface (UV V: 0.55 to 0.95 -> Y: 50 to 460)
    print("[4/5] Rendering high-contrast technical conduit stencil markings...")
    # Safety hazard chevron band (black & bright safety yellow)
    band_y1, band_y2 = 120, 160
    draw.rectangle([0, band_y1, W, band_y2], fill=(245, 190, 15))
    for cx in range(0, W, 45):
        draw.polygon([(cx, band_y1), (cx + 22, band_y1), (cx + 38, band_y2), (cx + 16, band_y2)], fill=(25, 25, 28))

    # Main Technical Stencil
    main_text = "▶▶  SEC-CONDUIT  90° EMT ELBOW  25MM O.D. / 21MM I.D.  RADIUS 80MM  ▶▶"
    draw.text((60, 190), main_text, fill=(30, 34, 38), font=f_lg)

    sub_text = "UL-797 / ANSI C80.3 SPECIFIED  ●  HOT-DIP GALVANIZED HEAVY-DUTY STEEL  ●  LOT #2026-CNR90-PRO"
    draw.text((60, 245), sub_text, fill=(45, 50, 56), font=f_md)

    draw.text((1150, 190), "SEC-CONDUIT  [ 90° CORNER SWEEP ]  CERTIFIED", fill=(30, 34, 38), font=f_lg)
    draw.text((1150, 245), "DO NOT CRIMP OR BEND FURTHER  -  IP66 COMPATIBLE COUPLINGS ONLY", fill=(55, 60, 68), font=f_sm)

    # Asset Barcodes
    draw_barcode(draw, 60, 310, 280, 70, "*SEC22-CNR90-A*", f_xs)
    draw_barcode(draw, 1150, 310, 280, 70, "*SEC22-CNR90-B*", f_xs)

    # 5. Threaded Collar Coupler Texture (UV V: 0.05 to 0.30 -> Y: 716 to 972)
    print("[5/5] Synthesizing realistic machined metal coupling textures...")
    draw.rectangle([0, 716, W, 1024], fill=(182, 186, 192))

    # Machined fine surface grain
    for y in range(716, 1024):
        lum = int(176 + 12 * math.sin(y * 0.35))
        draw.line([(0, y), (W, y)], fill=(lum, lum + 2, lum + 3, 245))

    # Subtle machined thread grooves (realistic metallic micro-grooves)
    for ty in range(735, 875, 6):
        draw.line([(0, ty), (W, ty)], fill=(120, 124, 130), width=1)
        draw.line([(0, ty + 1), (W, ty + 1)], fill=(215, 220, 226), width=1)

    # Diamond knurling grip band
    knurl_y1, knurl_y2 = 890, 955
    draw.rectangle([0, knurl_y1, W, knurl_y2], fill=(160, 164, 170))
    for kx in range(0, W, 8):
        draw.line([(kx, knurl_y1), (kx + (knurl_y2 - knurl_y1), knurl_y2)], fill=(95, 98, 104), width=1)
        draw.line([(kx, knurl_y2), (kx + (knurl_y2 - knurl_y1), knurl_y1)], fill=(205, 210, 216), width=1)

    # Screw Head Texture (for 3D set-screw cap)
    # Zone at X: 500 to 700, Y: 965 to 1020
    for sx in [600, 1600]:
        draw.ellipse([sx - 24, 968, sx + 24, 1016], fill=(205, 210, 216), outline=(100, 104, 110), width=2)
        # Deep screwdriver slot
        draw.rectangle([sx - 18, 990, sx + 18, 994], fill=(30, 32, 36))
        draw.line([(sx - 18, 990), (sx + 18, 990)], fill=(70, 74, 80), width=1)

    # Collar technical stamp text
    draw.text((60, 978), "EMT-25 COMPRESSION COUPLER  ●  HEX SET-SCREW TORQUE 4.5 N·m", fill=(30, 34, 38), font=f_sm)
    draw.text((1150, 978), "GALVANIZED STEEL COUPLING SLEEVE  ●  WATER-RESISTANT IP66", fill=(30, 34, 38), font=f_sm)

    img.save(TEXTURE_PATH, "PNG")
    print(f"[OK] Asset 22 texture generated: {TEXTURE_PATH} ({W}x{H})\n")


if __name__ == "__main__":
    generate_metal_texture()
