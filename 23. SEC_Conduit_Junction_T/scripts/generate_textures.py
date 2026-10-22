"""
=============================================================================
Security CCTV Asset Production Suite - Asset 23 (High Detail Upgrade)
Asset Name: SEC_Conduit_Junction_T
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


def draw_screws(draw, cx, cy, rad=16):
    """Draw realistic countersunk slotted machine screws with rubber sealing washer."""
    draw.ellipse([cx - rad - 4, cy - rad - 4, cx + rad + 4, cy + rad + 4], fill=(30, 32, 36))
    draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(215, 220, 228), outline=(120, 125, 132), width=1)
    draw.ellipse([cx - rad + 3, cy - rad + 3, cx + rad - 3, cy + rad - 3], fill=(185, 190, 198))
    # Slotted drive
    draw.rectangle([cx - rad + 4, cy - 2, cx + rad - 4, cy + 2], fill=(40, 42, 46))
    draw.line([(cx - rad + 4, cy - 2), (cx + rad - 4, cy - 2)], fill=(85, 90, 98), width=1)


def generate_metal_texture():
    """Generate industrial cast aluminum / conduit T-box texture."""
    W, H = 2048, 1024
    img = Image.new("RGBA", (W, H), (155, 160, 166, 255))
    draw = ImageDraw.Draw(img)
    f_lg, f_md, f_sm, f_xs = get_fonts()

    rng = random.Random(232026)

    # 1. Cast Metal Sand Texture (Stipple Noise across canvas)
    print("[1/5] Synthesizing sand-cast aluminum grain...")
    for _ in range(9000):
        px = rng.randint(0, W - 1)
        py = rng.randint(0, H - 1)
        lum = rng.randint(125, 195)
        draw.point((px, py), fill=(lum, lum + 1, lum + 3, 220))

    # 2. Cover Plate Graphic Region (UV V: 0.55 to 0.96 -> Y: 40 to 460, X: 40 to 980)
    print("[2/5] Designing inspection cover plate details...")
    cp_x1, cp_y1, cp_x2, cp_y2 = 40, 40, 980, 460
    # Cover plate chamfer rim
    draw.rounded_rectangle([cp_x1, cp_y1, cp_x2, cp_y2], radius=45, fill=(172, 177, 184), outline=(110, 115, 122), width=3)
    # Inner gasket perimeter groove
    draw.rounded_rectangle([cp_x1 + 18, cp_y1 + 18, cp_x2 - 18, cp_y2 - 18], radius=35, outline=(50, 52, 56), width=2)
    # Raised center plate
    draw.rounded_rectangle([cp_x1 + 24, cp_y1 + 24, cp_x2 - 24, cp_y2 - 24], radius=30, fill=(165, 170, 178))

    # Two heavy machine screws on cover plate
    draw_screws(draw, cp_x1 + 70, (cp_y1 + cp_y2) // 2, rad=20)
    draw_screws(draw, cp_x2 - 70, (cp_y1 + cp_y2) // 2, rad=20)

    # Embossed Cover Plate Markings
    mid_x = (cp_x1 + cp_x2) // 2
    draw.text((mid_x - 170, cp_y1 + 55), "SEC CONDUIT TEE", fill=(35, 38, 44), font=f_lg)
    draw.text((mid_x - 145, cp_y1 + 105), "FORM 7  ●  25MM (1 INCH)", fill=(50, 54, 62), font=f_md)
    draw.text((mid_x - 180, cp_y1 + 145), "VOL 12.5 CU.IN. / 205 ML  ●  NEMA 4X / IP66", fill=(65, 70, 78), font=f_sm)

    # Grounding indicator symbol and text
    draw.ellipse([mid_x - 180, cp_y1 + 195, mid_x - 140, cp_y1 + 235], outline=(35, 38, 42), width=2)
    draw.line([(mid_x - 170, cp_y1 + 209), (mid_x - 150, cp_y1 + 209)], fill=(35, 38, 42), width=2)
    draw.line([(mid_x - 166, cp_y1 + 215), (mid_x - 154, cp_y1 + 215)], fill=(35, 38, 42), width=2)
    draw.line([(mid_x - 162, cp_y1 + 221), (mid_x - 158, cp_y1 + 221)], fill=(35, 38, 42), width=2)
    draw.line([(mid_x - 160, cp_y1 + 200), (mid_x - 160, cp_y1 + 209)], fill=(35, 38, 42), width=2)
    draw.text((mid_x - 125, cp_y1 + 207), "INTERNAL GROUND TERMINAL ATTACHED", fill=(40, 44, 50), font=f_sm)

    # Warning Notice Plate (Yellow with black border)
    draw.rectangle([mid_x - 220, cp_y1 + 255, mid_x + 220, cp_y1 + 325], fill=(235, 180, 15), outline=(25, 28, 32), width=2)
    draw.text((mid_x - 195, cp_y1 + 265), "WARNING: DISCONNECT CIRCUITS BEFORE REMOVING COVER", fill=(20, 22, 25), font=f_xs)
    draw.text((mid_x - 175, cp_y1 + 288), "TIGHTEN COVER SCREWS TO 3.5 N·m / 31 IN-LB", fill=(20, 22, 25), font=f_xs)

    # 3. Junction Housing Body Region (UV V: 0.55 to 0.96 -> Y: 40 to 460, X: 1040 to 2000)
    print("[3/5] Shading junction box housing exterior...")
    hb_x1, hb_y1, hb_x2, hb_y2 = 1040, 40, 2000, 460
    draw.rounded_rectangle([hb_x1, hb_y1, hb_x2, hb_y2], radius=40, fill=(150, 155, 162), outline=(105, 109, 115), width=2)
    # Heavy cast ribs / reinforcing flutes
    for rx in range(hb_x1 + 100, hb_x2 - 100, 140):
        draw.rectangle([rx, hb_y1 + 30, rx + 18, hb_y2 - 30], fill=(130, 134, 140), outline=(90, 94, 100), width=1)
        draw.line([(rx + 1, hb_y1 + 30), (rx + 1, hb_y2 - 30)], fill=(190, 195, 202), width=1)

    draw.text((hb_x1 + 60, hb_y2 - 75), "SEC-JCT-T25  CAST ALLOY  MADE IN EU  LOT #2026-T", fill=(45, 50, 56), font=f_sm)
    draw.text((hb_x1 + 60, hb_y2 - 45), "SUITABLE FOR WET LOCATIONS  ●  UL LISTED 514A", fill=(60, 65, 72), font=f_xs)

    # 4. Threaded Conduit Ports Texture Region (UV V: 0.20 to 0.48 -> Y: 532 to 819)
    print("[4/5] Synthesizing threaded conduit hub textures...")
    draw.rectangle([0, 520, W, 820], fill=(165, 170, 176))
    # Thread grooves along Y
    for ty in range(540, 750, 8):
        draw.line([(0, ty), (W, ty)], fill=(55, 60, 66), width=3)
        draw.line([(0, ty + 3), (W, ty + 3)], fill=(220, 225, 232), width=2)
    # Knurled stop shoulder
    for kx in range(0, W, 10):
        draw.line([(kx, 760), (kx + 35, 810)], fill=(80, 84, 90), width=1)
        draw.line([(kx, 810), (kx + 35, 760)], fill=(205, 210, 216), width=1)

    # 5. Internal Cavity Dark Texture (UV V: 0.00 to 0.18 -> Y: 840 to 1024)
    print("[5/5] Shading internal junction box hollow cavity...")
    draw.rectangle([0, 840, W, 1024], fill=(65, 68, 74))
    for y in range(840, 1024):
        lum = int(55 + 15 * math.sin(y * 0.2))
        draw.line([(0, y), (W, y)], fill=(lum, lum + 1, lum + 3, 230))

    img.save(TEXTURE_PATH, "PNG")
    print(f"[OK] Asset 23 texture generated: {TEXTURE_PATH} ({W}x{H})\n")


if __name__ == "__main__":
    generate_metal_texture()
