"""
=============================================================================
Security CCTV Asset Production Suite - Asset 21
Asset Name: SEC_Conduit_Straight_2m
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
    """Draw a clean industrial barcode."""
    rng = random.Random(212026)
    draw.rectangle([x, y, x + w, y + h], fill=(235, 238, 242))
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
    draw.rectangle([max_x - 3, y + 4, max_x, y + h - 16], fill=(20, 22, 26))
    bbox = draw.textbbox((0, 0), code_text, font=font_xs)
    tw = bbox[2] - bbox[0]
    draw.text((x + (w - tw)//2, y + h - 14), code_text, fill=(20, 22, 26), font=font_xs)


def generate_conduit_texture():
    """Generate 2048x1024 high-resolution galvanized steel conduit texture."""
    f_lg, f_md, f_sm, f_xs = get_fonts()
    im = Image.new("RGBA", (2048, 1024), (165, 172, 182, 255))
    draw = ImageDraw.Draw(im)

    # 1. Base Galvanized Steel Zinc Spangle / Brushed Grain
    rng = random.Random(42)
    # Horizontal brushed steel streaks
    for y in range(0, 1024):
        tint = 160 + rng.randint(-12, 14)
        draw.line([0, y, 2048, y], fill=(tint, tint + 3, tint + 7, 255), width=1)

    # Zinc spangles (crystalline polygonal mottling characteristic of galvanized steel)
    for _ in range(350):
        sx = rng.randint(0, 2048)
        sy = rng.randint(0, 1024)
        rad = rng.randint(12, 35)
        v = rng.randint(145, 195)
        # Random crystal facet polygon
        pts = [
            (sx + int(rad * math.cos(math.radians(a) + rng.uniform(-0.2, 0.2))),
             sy + int(rad * 0.6 * math.sin(math.radians(a) + rng.uniform(-0.2, 0.2))))
            for a in range(0, 360, rng.choice([60, 72]))
        ]
        draw.polygon(pts, fill=(v, v + 2, v + 5, 60))

    # =========================================================================
    # ZONE 0: PIPE BODY WITH INDUSTRIAL INKJET MARKING STAMP (Y: 0 to 720)
    # =========================================================================
    # Laser / inkjet printed technical conduit run text
    # Placed in the center of the outer cylinder mapping (Y approx 320 to 420)
    stamp_y = 330
    draw.line([40, stamp_y - 20, 2008, stamp_y - 20], fill=(130, 138, 148), width=1)
    draw.line([40, stamp_y + 90, 2008, stamp_y + 90], fill=(130, 138, 148), width=1)

    # Continuous industrial conduit specification stamp
    stamp_text_1 = "SEC-CONDUIT EMT 25MM  ●  GALVANIZED STEEL ELECTRICAL METALLIC TUBING  ●  UL 797 / EN 61386-21"
    stamp_text_2 = "HEAVY GAUGE ZINC COATED  ●  2.000 METERS  ●  CCTV & SECURITY INFRASTRUCTURE  ●  ▶▶ CABLE ROUTE ▶▶"
    
    draw.text((60, stamp_y - 8), stamp_text_1, fill=(28, 32, 38), font=f_md)
    draw.text((60, stamp_y + 26), stamp_text_2, fill=(40, 46, 54), font=f_sm)

    # Certification logos and barcode
    draw_barcode(draw, 1450, stamp_y - 12, 220, 60, "*SEC2026-EMT25-2M*", f_xs)
    draw.text((1700, stamp_y + 6), "CE  UL  UKCA  RoHS  ⏚", fill=(25, 30, 36), font=f_md)

    # Secondary repeated marking at opposite side (Y: 120)
    draw.text((80, 110), "SEC-TECH INDUSTRIAL POWER & SURVEILLANCE RACEWAY SYSTEMS  -  25MM RIGID STEEL EMT", fill=(75, 82, 92), font=f_xs)
    draw.text((80, 560), "HOT-DIP GALVANIZED CORROSION RESISTANT CLASS 4  ●  FIRE RATED E90 DIN 4102-12", fill=(75, 82, 92), font=f_xs)

    # =========================================================================
    # ZONE 1: END COLLARS & COUPLINGS (Y: 730 to 890)
    # =========================================================================
    # Machined steel coupler sleeves with threads, knurling and hex wrench flats
    draw.rectangle([0, 730, 2048, 890], fill=(148, 154, 164), outline=(100, 106, 116), width=2)
    
    # Thread grooves
    for tx in range(0, 2048, 18):
        draw.line([tx, 732, tx, 888], fill=(108, 114, 124), width=3)
        draw.line([tx + 4, 732, tx + 4, 888], fill=(185, 192, 202), width=2)

    # Center hex wrench band
    draw.rectangle([0, 785, 2048, 835], fill=(175, 182, 192), outline=(90, 96, 105), width=2)
    for hx in range(0, 2048, 256):
        draw.line([hx, 785, hx, 835], fill=(70, 75, 84), width=3)
        draw.line([hx + 4, 785, hx + 4, 835], fill=(225, 232, 240), width=2)
        draw.text((hx + 30, 798), "25MM EMT COUPLER", fill=(45, 50, 58), font=f_sm)

    # =========================================================================
    # ZONE 2: HOLLOW INNER BORE & END RIMS (Y: 900 to 1024)
    # =========================================================================
    # Darker interior bore cavity with longitudinal draw marks
    draw.rectangle([0, 900, 2048, 1024], fill=(75, 80, 88), outline=(50, 55, 60), width=1)
    for y in range(900, 1024, 2):
        shade = 65 + (y % 6) * 3
        draw.line([0, y, 2048, y], fill=(shade, shade + 2, shade + 4), width=1)

    # Save Texture
    im.save(TEXTURE_PATH, "PNG", optimize=True)
    print(f"[OK] Saved Conduit Metal Texture: {TEXTURE_PATH} ({im.size[0]}x{im.size[1]})")


if __name__ == "__main__":
    generate_conduit_texture()
