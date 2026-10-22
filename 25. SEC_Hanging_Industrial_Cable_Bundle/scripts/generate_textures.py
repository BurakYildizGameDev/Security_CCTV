"""
=============================================================================
Security CCTV Asset Production Suite - Asset 25
Asset Name: SEC_Hanging_Industrial_Cable_Bundle
Texture Generation Script (Standalone System Python + Pillow)
Outputs:
    - exports/T_Security_Atlas.png (2048x1024)
    - exports/T_Metal.png (1024x1024)
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

ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")
METAL_PATH = os.path.join(EXPORTS_DIR, "T_Metal.png")


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
        except Exception:
            pass

    if f_lg is None:
        f_lg = f_md = f_sm = f_xs = ImageFont.load_default()

    return f_lg, f_md, f_sm, f_xs


def generate_security_atlas():
    """Generate high-resolution cable sheath and connector atlas."""
    W, H = 2048, 1024
    img = Image.new("RGBA", (W, H), (45, 48, 52, 255))
    draw = ImageDraw.Draw(img)
    f_lg, f_md, f_sm, f_xs = get_fonts()
    rng = random.Random(252026)

    # 1. Cable Sheath Zone (UV V: 0.50 to 1.00 -> Y: 0 to 512)
    # Dark matte PVC / polyurethane cable rubber
    for y in range(0, 512):
        lum = int(42 + 8 * math.sin(y * 0.15))
        draw.line([(0, y), (W, y)], fill=(lum, lum + 1, lum + 3, 255))

    # Subtle extrusion draw lines
    for _ in range(800):
        y_pos = rng.randint(0, 511)
        x_start = rng.randint(0, W // 2)
        x_len = rng.randint(200, 1000)
        c_val = rng.randint(35, 55)
        draw.line([(x_start, y_pos), (min(W, x_start + x_len), y_pos)], fill=(c_val, c_val + 1, c_val + 2, 80))

    # Continuous Cable Inkjet Markings along X
    # Track 1: RG-59 Coaxial Video Cable
    text_coax = "▶▶  SEC-CABLE RG-59/U COAXIAL  75 OHM  O.D. 6.1MM  ●  SOLID COPPER CORE  ●  CCTV VIDEO CH-1  ●  BATCH #2026-CX  ▶▶"
    draw.text((60, 60), text_coax, fill=(180, 184, 190), font=f_sm)
    draw.text((1100, 60), text_coax, fill=(180, 184, 190), font=f_sm)

    # Track 2: CAT-6 UTP Ethernet Cable
    text_cat6 = "SEC-NET CAT.6 UTP 4-PAIR 24AWG  ●  TIA/EIA-568-C.2  ●  VERIFIED GIGABIT ETHERNET  ●  POE+ 802.3at  ●  LOT #2026-E4"
    draw.text((60, 180), text_cat6, fill=(195, 200, 208), font=f_sm)
    draw.text((1100, 180), text_cat6, fill=(195, 200, 208), font=f_sm)

    # Track 3: 18AWG DC Power Cable
    text_pwr = "SEC-POWER 2x1.0mm² (18AWG) 300V HEAVY-DUTY FLEXIBLE  ●  POLARITY: RED(+) / BLK(-)  ●  MAX 5A  ●  CE/RoHS"
    draw.text((60, 300), text_pwr, fill=(210, 215, 222), font=f_sm)
    draw.text((1100, 300), text_pwr, fill=(210, 215, 222), font=f_sm)

    # Yellow Wrap-around Identification Flag Tags (X: 100 to 1900, Y: 400 to 500)
    tag_colors = [(245, 195, 20), (245, 195, 20), (245, 195, 20)]
    tag_labels = [
        ("CAM-01 / VIDEO FEED [BNC]", "CH-01 AHD/TVI 1080P"),
        ("12V DC AUX POWER INPUT", "MAIN DISTRIBUTION PNL"),
        ("IP-CAMERA 04 [RJ45 / POE]", "PORT 08 / VLAN-10")
    ]
    for idx, (l1, l2) in enumerate(tag_labels):
        tx1 = 120 + idx * 640
        draw.rectangle([tx1, 410, tx1 + 540, 490], fill=(245, 195, 20), outline=(25, 25, 28), width=2)
        # Barcode
        draw.rectangle([tx1 + 15, 420, tx1 + 120, 480], fill=(255, 255, 255))
        for bx in range(tx1 + 22, tx1 + 115, 5):
            draw.rectangle([bx, 424, bx + 2, 476], fill=(20, 20, 22))
        draw.text((tx1 + 135, 425), l1, fill=(20, 22, 25), font=f_sm)
        draw.text((tx1 + 135, 455), l2, fill=(45, 50, 58), font=f_xs)

    # 2. Connector Plastics & Boots Zone (UV V: 0.00 to 0.50 -> Y: 512 to 1024)
    # Zone A: DC Barrel Jack Black Molded Body (X: 0 to 600, Y: 520 to 800)
    draw.rectangle([0, 520, 600, 800], fill=(30, 32, 36))
    # Strain relief ribs
    for ry in range(540, 780, 14):
        draw.line([(40, ry), (560, ry)], fill=(18, 20, 22), width=4)
        draw.line([(40, ry + 4), (560, ry + 4)], fill=(65, 68, 74), width=2)

    # Zone B: RJ-45 Modular Plug Body (X: 620 to 1300, Y: 520 to 800)
    # Clear / smoked polycarbonate body
    draw.rectangle([620, 520, 1300, 800], fill=(75, 82, 92), outline=(45, 50, 56), width=2)
    # 8 Gold Pin Contacts
    for pin_idx in range(8):
        px = 660 + pin_idx * 75
        draw.rectangle([px, 540, px + 40, 640], fill=(215, 175, 35), outline=(135, 105, 15), width=2)
        draw.line([(px + 4, 545), (px + 4, 635)], fill=(255, 225, 90), width=2)
    draw.text((680, 720), "CAT-6 RJ-45 MODULAR PLUG  -  50µ GOLD PLATED CONTACTS", fill=(190, 195, 205), font=f_sm)

    # Zone C: Stripped Wire Internal Conductors (X: 1320 to 2048, Y: 520 to 800)
    # Red, Black, Copper wire sections
    draw.rectangle([1320, 520, 1550, 800], fill=(185, 35, 30))  # Red wire
    draw.rectangle([1560, 520, 1790, 800], fill=(25, 26, 28))   # Black wire
    draw.rectangle([1800, 520, 2040, 800], fill=(195, 120, 55)) # Bare Copper Strands
    # Copper wire fine twisted lines
    for cy in range(530, 790, 6):
        draw.line([(1810, cy), (2030, cy + 3)], fill=(235, 165, 85), width=2)
        draw.line([(1810, cy + 3), (2030, cy)], fill=(145, 80, 30), width=1)

    # Bottom border zone: Clean neutral rubber
    draw.rectangle([0, 820, W, 1024], fill=(55, 58, 64))

    img.save(ATLAS_PATH, "PNG")
    print(f"[OK] Asset 25 Security Atlas generated: {ATLAS_PATH} ({W}x{H})")


def generate_metal_texture():
    """Generate metal texture for BNC plugs, terminal blocks, and cable anchor."""
    W, H = 1024, 1024
    img = Image.new("RGBA", (W, H), (185, 190, 196, 255))
    draw = ImageDraw.Draw(img)
    f_lg, f_md, f_sm, f_xs = get_fonts()
    rng = random.Random(252027)

    # Brushed nickel / chrome texture
    for y in range(H):
        lum = int(180 + 15 * math.sin(y * 0.2))
        draw.line([(0, y), (W, y)], fill=(lum, lum + 1, lum + 3, 255))

    for _ in range(800):
        y_pos = rng.randint(0, H - 1)
        x_start = rng.randint(0, W // 2)
        x_len = rng.randint(150, 700)
        c_val = rng.randint(165, 215)
        draw.line([(x_start, y_pos), (min(W, x_start + x_len), y_pos)], fill=(c_val, c_val + 1, c_val + 3, 70))

    # Knurled BNC Coupling Ring (Y: 100 to 350)
    draw.rectangle([0, 100, W, 350], fill=(160, 164, 170))
    for kx in range(0, W, 8):
        draw.line([(kx, 100), (kx + 80, 350)], fill=(85, 88, 94), width=1)
        draw.line([(kx, 350), (kx + 80, 100)], fill=(215, 220, 226), width=1)
    draw.text((50, 365), "BNC 75 OHM CRIMP PLUG  -  MIL-C-39012 SPECIFIED", fill=(40, 44, 50), font=f_sm)

    # Brass Center Pin and Terminal Screws (Y: 450 to 750)
    draw.rectangle([0, 450, W, 750], fill=(210, 175, 75)) # Brass sheen
    for y in range(450, 750):
        lum = int(195 + 15 * math.sin(y * 0.3))
        draw.line([(0, y), (W, y)], fill=(lum + 10, lum, lum - 70, 230))
    draw.text((50, 765), "INDUSTRIAL TERMINAL SCREWS  -  M3.5 BRASS PLATED", fill=(40, 44, 50), font=f_sm)

    # Anchor clamp steel plate (Y: 820 to 1024)
    draw.rectangle([0, 820, W, 1024], fill=(170, 174, 180), outline=(110, 114, 120), width=2)
    draw.text((50, 850), "SEC-ANCHOR-CB6  STAINLESS STEEL CABLE CLAMP  MAX 15 KG", fill=(35, 38, 44), font=f_sm)

    img.save(METAL_PATH, "PNG")
    print(f"[OK] Asset 25 Metal Texture generated: {METAL_PATH} ({W}x{H})\n")


if __name__ == "__main__":
    generate_security_atlas()
    generate_metal_texture()
