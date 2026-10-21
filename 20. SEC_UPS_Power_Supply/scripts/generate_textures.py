"""
=============================================================================
Security CCTV Asset Production Suite - Asset 20
Asset Name: SEC_UPS_Power_Supply
Texture Generation Script (Standalone System Python + Pillow)
Master Quality Revision - Photo-Realistic Connectors & Exact Alignment
Outputs:
    - exports/T_Security_Atlas.png (2048x2048)
    - exports/T_Screen.png (1024x512)
=============================================================================
"""

import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")
SCREEN_PATH = os.path.join(EXPORTS_DIR, "T_Screen.png")


def get_fonts():
    """Load clean industrial fonts with fallbacks."""
    f_xl = f_lg = f_md = f_sm = f_xs = None
    t_xl = t_lg = t_md = t_sm = t_xs = None

    font_paths = [
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\calibri.ttf"
    ]
    primary = None
    bold = r"C:\Windows\Fonts\arialbd.ttf" if os.path.exists(r"C:\Windows\Fonts\arialbd.ttf") else None

    for p in font_paths:
        if os.path.exists(p):
            primary = p
            break

    if primary:
        try:
            f_xl = ImageFont.truetype(primary, 48)
            f_lg = ImageFont.truetype(primary, 34)
            f_md = ImageFont.truetype(primary, 24)
            f_sm = ImageFont.truetype(primary, 18)
            f_xs = ImageFont.truetype(primary, 14)

            bf = bold if bold else primary
            t_xl = ImageFont.truetype(bf, 54)
            t_lg = ImageFont.truetype(bf, 36)
            t_md = ImageFont.truetype(bf, 25)
            t_sm = ImageFont.truetype(bf, 19)
            t_xs = ImageFont.truetype(bf, 15)
        except Exception as e:
            print(f"[WARN] Error loading TTF fonts: {e}")

    if f_xl is None:
        f_xl = f_lg = f_md = f_sm = f_xs = ImageFont.load_default()
        t_xl = t_lg = t_md = t_sm = t_xs = ImageFont.load_default()

    return f_xl, f_lg, f_md, f_sm, f_xs, t_xl, t_lg, t_md, t_sm, t_xs


def draw_barcode(draw, x, y, w, h, code_text, font_xs):
    """Draw a clean Code 128 style industrial barcode."""
    import random
    rng = random.Random(992026)
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    bar_x = x + 14
    max_x = x + w - 14
    draw.rectangle([bar_x, y + 6, bar_x + 3, y + h - 18], fill=(0, 0, 0))
    bar_x += 6
    while bar_x < max_x - 8:
        bar_w = rng.choice([2, 3, 4, 5])
        space = rng.choice([2, 3, 4])
        if bar_x + bar_w > max_x:
            break
        draw.rectangle([bar_x, y + 6, bar_x + bar_w, y + h - 18], fill=(0, 0, 0))
        bar_x += bar_w + space

    draw.rectangle([max_x - 3, y + 6, max_x, y + h - 18], fill=(0, 0, 0))
    text_bbox = draw.textbbox((0, 0), code_text, font=font_xs)
    tw = text_bbox[2] - text_bbox[0]
    draw.text((x + (w - tw) // 2, y + h - 16), code_text, fill=(0, 0, 0), font=font_xs)


def draw_realistic_c13_outlet(draw, cx, cy, w, h, label="OUTPUT 1", sublabel="230V~ 10A MAX", f_sm=None, f_xs=None):
    """Draw a highly detailed, photo-realistic IEC 60320 C13 female outlet."""
    # 1. Outer mounting body / flange (matte dark PBT plastic)
    draw.rounded_rectangle([cx - w//2 - 10, cy - h//2 - 10, cx + w//2 + 10, cy + h//2 + 10], radius=8, fill=(14, 16, 20), outline=(52, 58, 68), width=2)
    # Side mounting snap clips / latches
    for sx in [cx - w//2 - 9, cx + w//2 + 5]:
        draw.rectangle([sx, cy - 25, sx + 4, cy + 25], fill=(32, 36, 45), outline=(58, 65, 78), width=1)

    # 2. Main socket face with characteristic C13 beveled top
    chamfer = 34
    w_top = w - 2 * chamfer

    poly_outer = [
        (cx - w_top//2, cy - h//2),
        (cx + w_top//2, cy - h//2),
        (cx + w//2, cy - h//2 + chamfer),
        (cx + w//2, cy + h//2),
        (cx - w//2, cy + h//2),
        (cx - w//2, cy - h//2 + chamfer)
    ]
    draw.polygon(poly_outer, fill=(24, 27, 34), outline=(76, 84, 98))

    # Inner stepped recess (depth illusion)
    step = 8
    poly_inner = [
        (cx - w_top//2 + 4, cy - h//2 + step),
        (cx + w_top//2 - 4, cy - h//2 + step),
        (cx + w//2 - step, cy - h//2 + chamfer + 2),
        (cx + w//2 - step, cy + h//2 - step),
        (cx - w//2 + step, cy + h//2 - step),
        (cx - w//2 + step, cy - h//2 + chamfer + 2)
    ]
    draw.polygon(poly_inner, fill=(8, 10, 14), outline=(42, 46, 55))

    # Deep cavity core
    step2 = 16
    poly_core = [
        (cx - w_top//2 + 10, cy - h//2 + step2),
        (cx + w_top//2 - 10, cy - h//2 + step2),
        (cx + w//2 - step2, cy - h//2 + chamfer + 6),
        (cx + w//2 - step2, cy + h//2 - step2),
        (cx - w//2 + step2, cy + h//2 - step2),
        (cx - w//2 + step2, cy - h//2 + chamfer + 6)
    ]
    draw.polygon(poly_core, fill=(3, 4, 6))

    # 3. Three Terminal Receptacle Slots (Vertical brass contact sleeves)
    # Earth (Top center)
    e_y0, e_y1 = cy - h//2 + 30, cy - h//2 + 60
    e_x0, e_x1 = cx - 7, cx + 7
    draw.rounded_rectangle([e_x0 - 2, e_y0 - 2, e_x1 + 2, e_y1 + 2], radius=2, fill=(18, 20, 26), outline=(65, 72, 85))
    draw.rectangle([e_x0, e_y0, e_x1, e_y1], fill=(0, 0, 0))
    draw.rectangle([e_x0 + 2, e_y0 + 4, e_x0 + 4, e_y1 - 4], fill=(215, 175, 55))
    draw.rectangle([e_x1 - 4, e_y0 + 4, e_x1 - 2, e_y1 - 4], fill=(215, 175, 55))
    draw.line([e_x0 + 3, e_y0 + 6, e_x0 + 3, e_y1 - 6], fill=(255, 230, 140))

    # Neutral (Bottom Left)
    n_y0, n_y1 = cy + 12, cy + 42
    n_x0, n_x1 = cx - 44, cx - 30
    draw.rounded_rectangle([n_x0 - 2, n_y0 - 2, n_x1 + 2, n_y1 + 2], radius=2, fill=(18, 20, 26), outline=(65, 72, 85))
    draw.rectangle([n_x0, n_y0, n_x1, n_y1], fill=(0, 0, 0))
    draw.rectangle([n_x0 + 2, n_y0 + 4, n_x0 + 4, n_y1 - 4], fill=(215, 175, 55))
    draw.rectangle([n_x1 - 4, n_y0 + 4, n_x1 - 2, n_y1 - 4], fill=(215, 175, 55))
    draw.line([n_x0 + 3, n_y0 + 6, n_x0 + 3, n_y1 - 6], fill=(255, 230, 140))

    # Line (Bottom Right)
    l_x0, l_x1 = cx + 30, cx + 44
    draw.rounded_rectangle([l_x0 - 2, n_y0 - 2, l_x1 + 2, n_y1 + 2], radius=2, fill=(18, 20, 26), outline=(65, 72, 85))
    draw.rectangle([l_x0, n_y0, l_x1, n_y1], fill=(0, 0, 0))
    draw.rectangle([l_x0 + 2, n_y0 + 4, l_x0 + 4, n_y1 - 4], fill=(215, 175, 55))
    draw.rectangle([l_x1 - 4, n_y0 + 4, l_x1 - 2, n_y1 - 4], fill=(215, 175, 55))
    draw.line([l_x0 + 3, n_y0 + 6, l_x0 + 3, n_y1 - 6], fill=(255, 230, 140))

    # Embossed rating text on socket face
    draw.text((cx - 28, cy - 2), "10A 250V~", fill=(72, 78, 90), font=f_xs)
    draw.text((cx - 42, cy - 18), "N", fill=(62, 68, 80), font=f_xs)
    draw.text((cx + 32, cy - 18), "L", fill=(62, 68, 80), font=f_xs)
    draw.text((cx - 6, cy - h//2 + 14), "⏚", fill=(68, 75, 88), font=f_xs)

    # 4. Outlet label below
    draw.rectangle([cx - 56, cy + h//2 + 16, cx + 56, cy + h//2 + 42], fill=(16, 20, 28), outline=(62, 70, 84))
    draw.text((cx - 42, cy + h//2 + 20), label, fill=(255, 255, 255), font=f_sm)
    draw.text((cx - 56, cy + h//2 + 45), sublabel, fill=(165, 180, 200), font=f_xs)


def draw_realistic_c14_inlet(draw, cx, cy, w, h, f_xs=None):
    """Draw realistic IEC 60320 C14 male chassis inlet (power in) with metallic prongs."""
    # Outer mounting plate with flange ears
    draw.rounded_rectangle([cx - w//2 - 24, cy - h//2 - 6, cx + w//2 + 24, cy + h//2 + 6], radius=6, fill=(14, 16, 20), outline=(55, 60, 72), width=2)
    # Screw rivets on left and right ears
    for sx in [cx - w//2 - 12, cx + w//2 + 12]:
        draw.ellipse([sx - 6, cy - 6, sx + 6, cy + 6], fill=(120, 125, 135), outline=(40, 42, 48))
        draw.line([sx - 4, cy, sx + 4, cy], fill=(30, 32, 36), width=1)
        draw.line([sx, cy - 4, sx, cy + 4], fill=(30, 32, 36), width=1)

    chamfer = 28
    w_top = w - 2 * chamfer
    poly_outer = [
        (cx - w_top//2, cy - h//2),
        (cx + w_top//2, cy - h//2),
        (cx + w//2, cy - h//2 + chamfer),
        (cx + w//2, cy + h//2),
        (cx - w//2, cy + h//2),
        (cx - w//2, cy - h//2 + chamfer)
    ]
    draw.polygon(poly_outer, fill=(22, 25, 32), outline=(70, 78, 90))

    poly_inner = [
        (cx - w_top//2 + 8, cy - h//2 + 8),
        (cx + w_top//2 - 8, cy - h//2 + 8),
        (cx + w//2 - 8, cy - h//2 + chamfer + 4),
        (cx + w//2 - 8, cy + h//2 - 8),
        (cx - w//2 + 8, cy + h//2 - 8),
        (cx - w//2 + 8, cy - h//2 + chamfer + 4)
    ]
    draw.polygon(poly_inner, fill=(6, 8, 12), outline=(35, 40, 48))

    # 3 Solid Nickel/Brass Male Prongs (Pins with 3D drop shadow)
    # Earth (Top Center)
    ep_x0, ep_y0, ep_x1, ep_y1 = cx - 6, cy - h//2 + 22, cx + 6, cy - h//2 + 50
    draw.rectangle([ep_x0 + 3, ep_y0 + 3, ep_x1 + 4, ep_y1 + 4], fill=(0, 0, 0))
    draw.rectangle([ep_x0, ep_y0, ep_x1, ep_y1], fill=(210, 185, 80), outline=(130, 110, 35))
    draw.line([ep_x0 + 2, ep_y0 + 2, ep_x0 + 2, ep_y1 - 2], fill=(255, 245, 170), width=1)

    # Neutral (Bottom Left)
    np_x0, np_y0, np_x1, np_y1 = cx - 44, cy + 12, cx - 32, cy + 40
    draw.rectangle([np_x0 + 3, np_y0 + 3, np_x1 + 4, np_y1 + 4], fill=(0, 0, 0))
    draw.rectangle([np_x0, np_y0, np_x1, np_y1], fill=(210, 185, 80), outline=(130, 110, 35))
    draw.line([np_x0 + 2, np_y0 + 2, np_x0 + 2, np_y1 - 2], fill=(255, 245, 170), width=1)

    # Line (Bottom Right)
    lp_x0, lp_y0, lp_x1, lp_y1 = cx + 32, cy + 12, cx + 44, cy + 40
    draw.rectangle([lp_x0 + 3, lp_y0 + 3, lp_x1 + 4, lp_y1 + 4], fill=(0, 0, 0))
    draw.rectangle([lp_x0, lp_y0, lp_x1, lp_y1], fill=(210, 185, 80), outline=(130, 110, 35))
    draw.line([lp_x0 + 2, lp_y0 + 2, lp_x0 + 2, lp_y1 - 2], fill=(255, 245, 170), width=1)

    draw.text((cx - 28, cy - 2), "10A 250V~", fill=(60, 68, 80), font=f_xs)


def draw_realistic_breaker(draw, cx, cy, rad=36, f_xs=None, f_md=None):
    """Draw realistic 10A push-to-reset thermal circuit breaker button."""
    # Outer threaded barrel collar with knurled ring
    draw.ellipse([cx - rad - 8, cy - rad - 8, cx + rad + 8, cy + rad + 8], fill=(16, 18, 22), outline=(50, 55, 65), width=2)
    # Knurls
    for a in range(0, 360, 20):
        ra = math.radians(a)
        kx = cx + int((rad + 5) * math.cos(ra))
        ky = cy + int((rad + 5) * math.sin(ra))
        draw.line([cx + int((rad + 2) * math.cos(ra)), cy + int((rad + 2) * math.sin(ra)), kx, ky], fill=(70, 78, 90), width=2)

    # Silver nut ring
    draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(120, 126, 138), outline=(60, 64, 72), width=2)
    draw.ellipse([cx - rad + 4, cy - rad + 4, cx + rad - 4, cy + rad - 4], fill=(18, 20, 25), outline=(40, 44, 52))

    # Red actuator button
    b_rad = rad - 10
    draw.ellipse([cx - b_rad, cy - b_rad, cx + b_rad, cy + b_rad], fill=(195, 30, 22), outline=(240, 90, 80), width=2)
    draw.ellipse([cx - b_rad + 3, cy - b_rad + 3, cx + b_rad - 3, cy + b_rad - 3], fill=(165, 22, 16))
    # Stamped "10" on button face
    draw.text((cx - 10, cy - 10), "10", fill=(255, 255, 255), font=f_md)


def draw_realistic_usb_b(draw, cx, cy, w=76, h=76):
    """Draw realistic shielded USB Type-B female connector."""
    # Metal shield enclosure (nickel-plated silver)
    draw.rounded_rectangle([cx - w//2 - 6, cy - h//2 - 6, cx + w//2 + 6, cy + h//2 + 6], radius=4, fill=(130, 138, 150), outline=(70, 75, 85), width=2)
    # Retention spring dimples
    draw.rectangle([cx - 8, cy - h//2 - 5, cx + 8, cy - h//2 - 3], fill=(70, 75, 85))
    draw.rectangle([cx - 8, cy + h//2 + 3, cx + 8, cy + h//2 + 5], fill=(70, 75, 85))

    # USB-B characteristic beveled aperture
    ch = 14
    poly_aperture = [
        (cx - w//2 + ch, cy - h//2),
        (cx + w//2 - ch, cy - h//2),
        (cx + w//2, cy - h//2 + ch),
        (cx + w//2, cy + h//2),
        (cx - w//2, cy + h//2),
        (cx - w//2, cy - h//2 + ch)
    ]
    draw.polygon(poly_aperture, fill=(6, 8, 10), outline=(40, 45, 55))

    # Inner black plastic tongue
    tw, th = w - 24, h - 34
    draw.rectangle([cx - tw//2, cy - th//2 + 4, cx + tw//2, cy + th//2 + 4], fill=(26, 28, 34), outline=(55, 60, 70))
    # 4 Gold contact spring fingers
    for p in range(4):
        px = cx - 18 + p * 12
        draw.rectangle([px - 2, cy - th//2 + 8, px + 2, cy + th//2], fill=(225, 185, 55))
        draw.line([px, cy - th//2 + 8, px, cy + th//2], fill=(255, 240, 160))


def draw_realistic_rj45(draw, cx, cy, w=84, h=72, label="NETWORK IN", f_xs=None):
    """Draw realistic shielded RJ-45 Ethernet modular jack."""
    # Outer metal shield
    draw.rounded_rectangle([cx - w//2 - 4, cy - h//2 - 4, cx + w//2 + 4, cy + h//2 + 4], radius=3, fill=(140, 148, 160), outline=(75, 80, 92), width=2)
    # Grounding tabs
    draw.rectangle([cx - w//2 - 3, cy - 10, cx - w//2 - 1, cy + 10], fill=(60, 65, 75))
    draw.rectangle([cx + w//2 + 1, cy - 10, cx + w//2 + 3, cy + 10], fill=(60, 65, 75))

    # Inner black jack cavity
    draw.rectangle([cx - w//2 + 4, cy - h//2 + 4, cx + w//2 - 4, cy + h//2 - 4], fill=(8, 10, 14), outline=(35, 40, 50))

    # Retaining clip notch (bottom inverted T shape)
    draw.rectangle([cx - 16, cy + 6, cx + 16, cy + h//2 - 4], fill=(18, 20, 26))
    draw.rectangle([cx - 24, cy + 16, cx + 24, cy + h//2 - 4], fill=(18, 20, 26))

    # 8 Gold contact wire comb (top)
    for p in range(8):
        px = cx - 24 + p * 7
        draw.rectangle([px - 1, cy - h//2 + 8, px + 1, cy - 2], fill=(225, 185, 55))
        draw.line([px, cy - h//2 + 8, px, cy - 2], fill=(255, 240, 160))

    # Activity LEDs at top corners
    draw.rectangle([cx - w//2 + 8, cy - h//2 + 7, cx - w//2 + 16, cy - h//2 + 13], fill=(30, 220, 60), outline=(15, 90, 25))
    draw.rectangle([cx + w//2 - 16, cy - h//2 + 7, cx + w//2 - 8, cy - h//2 + 13], fill=(255, 165, 20), outline=(120, 70, 10))

    # Label below
    draw.text((cx - 44, cy + h//2 + 8), label, fill=(220, 230, 245), font=f_xs)


def draw_fan_grille(draw, cx, cy, radius, f_xs=None):
    """Draw 80mm industrial fan exhaust grille with circular symmetry."""
    draw.rectangle([cx - radius - 8, cy - radius - 8, cx + radius + 8, cy + radius + 8], fill=(16, 18, 22), outline=(60, 65, 75), width=2)
    for dx in [-radius - 2, radius + 2]:
        for dy in [-radius - 2, radius + 2]:
            draw.ellipse([cx + dx - 5, cy + dy - 5, cx + dx + 5, cy + dy + 5], fill=(110, 115, 125), outline=(30, 30, 30))
            draw.line([cx + dx - 3, cy + dy, cx + dx + 3, cy + dy], fill=(40, 40, 40), width=1)
            draw.line([cx + dx, cy + dy - 3, cx + dx, cy + dy + 3], fill=(40, 40, 40), width=1)

    for r in range(20, radius, 18):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(75, 80, 95), width=2)

    for a in range(0, 360, 45):
        rad = math.radians(a)
        x2 = cx + int((radius - 2) * math.cos(rad))
        y2 = cy + int((radius - 2) * math.sin(rad))
        draw.line([cx, cy, x2, y2], fill=(70, 75, 90), width=2)

    draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(24, 28, 34), outline=(90, 100, 115), width=2)
    draw.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=(12, 14, 18), outline=(50, 55, 65))
    draw.text((cx - 18, cy - 8), "12V DC", fill=(130, 140, 155), font=f_xs)


def generate_security_atlas():
    """Generate 2048x2048 T_Security_Atlas.png texture atlas with exact 1:1 pixel aspect ratios."""
    f_xl, f_lg, f_md, f_sm, f_xs, t_xl, t_lg, t_md, t_sm, t_xs = get_fonts()
    im = Image.new("RGBA", (2048, 2048), (20, 22, 26, 255))
    draw = ImageDraw.Draw(im)

    # Subtle industrial metal micro-grain
    for y in range(0, 2048, 3):
        v = 20 + (y % 4)
        draw.line([0, y, 2048, y], fill=(v, v + 2, v + 5, 255), width=1)

    # =========================================================================
    # ZONE 0: FRONT PANEL FASCIA & GRAPHICS
    # Exact 1:1 Proportional Mapping: Width 820 px, Height 1750 px
    # Bounds: X in [40, 860], Y in [40, 1790]
    # In 3D: X in [-0.050, +0.050] (0.100m), Z in [0.006, 0.220] (0.214m)
    # =========================================================================
    fx0, fy0, fx1, fy1 = 40, 40, 860, 1790
    draw.rounded_rectangle([fx0, fy0, fx1, fy1], radius=14, fill=(16, 18, 22), outline=(55, 60, 72), width=3)

    # 1. TOP HEADER SECTION (Y: 40 to 220) - Sits cleanly above the 3D screen
    draw.rectangle([fx0 + 10, fy0 + 10, fx1 - 10, fy0 + 130], fill=(11, 13, 17))
    draw.line([fx0 + 10, fy0 + 130, fx1 - 10, fy0 + 130], fill=(0, 190, 240), width=3)

    draw.text((fx0 + 30, fy0 + 22), "SEC-UPS 1500 PRO", fill=(255, 255, 255), font=t_lg)
    draw.text((fx0 + 520, fy0 + 26), "1500VA / 900W", fill=(0, 220, 255), font=t_md)
    draw.text((fx0 + 30, fy0 + 72), "TRUE SINE WAVE INTELLIGENT TOWER UPS", fill=(175, 190, 205), font=f_sm)
    draw.text((fx0 + 30, fy0 + 98), "CONTINUOUS POWER INFRASTRUCTURE", fill=(110, 125, 140), font=f_xs)

    # System Status LED indicators (Y: 145 to 220) - Completely above the 3D screen!
    led_labels = [
        ("LINE OK", (30, 235, 65)),
        ("ON BATT", (255, 175, 15)),
        ("OVERLOAD", (255, 50, 30)),
        ("FAULT", (240, 30, 20))
    ]
    led_start_x = fx0 + 55
    led_y = fy0 + 185
    for i, (name, color) in enumerate(led_labels):
        lx = led_start_x + i * 195
        draw.ellipse([lx - 10, led_y - 10, lx + 10, led_y + 10], fill=(10, 12, 15), outline=(75, 82, 95), width=2)
        draw.ellipse([lx - 6, led_y - 6, lx + 6, led_y + 6], fill=color, outline=(255, 255, 255, 180), width=1)
        draw.ellipse([lx - 14, led_y - 14, lx + 14, led_y + 14], outline=(*color[:3], 60), width=1)
        draw.text((lx + 18, led_y - 9), name, fill=(240, 245, 255), font=t_xs)

    # 2. DISPLAY WINDOW APERTURE (Y: 260 to 710)
    # The 3D Status_Display mesh sits here. We draw only the clean recessed bezel frame!
    bx0, by0, bx1, by1 = fx0 + 50, fy0 + 260, fx1 - 50, fy0 + 710
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=8, fill=(8, 10, 14), outline=(65, 75, 90), width=3)
    draw.rounded_rectangle([bx0 + 6, by0 + 6, bx1 - 6, by1 - 6], radius=4, fill=(5, 6, 8), outline=(30, 35, 45), width=2)

    # 3. MID CONTROL SHELF (Mathematical 1:1 alignment with 3D buttons)
    # In 3D: cz = 0.114m -> Y = 1790 - (0.114 - 0.006)/0.214 * 1750 = 907 px
    # In 3D: cx = 0.000m -> X = 450 px
    # In 3D: btn_m_x = +0.024m (observer's left) -> X = 253 px
    # In 3D: btn_d_x = -0.024m (observer's right) -> X = 647 px
    btn_y = 907
    p_cx = 450
    m_cx = 253
    d_cx = 647

    # Center Power Button Cavity (radius 74 px for concentric 8px clearance around 66px 3D button)
    draw.ellipse([p_cx - 74, btn_y - 74, p_cx + 74, btn_y + 74], fill=(12, 14, 18), outline=(58, 64, 76), width=2)
    draw.ellipse([p_cx - 68, btn_y - 68, p_cx + 68, btn_y + 68], fill=(6, 8, 11), outline=(32, 36, 45), width=1)
    # Power Button Label - Strictly BELOW button well!
    draw.text((p_cx - 68, btn_y + 82), "POWER / STANDBY", fill=(220, 235, 250), font=t_xs)
    draw.text((p_cx - 44, btn_y + 104), "PRESS 1 SEC", fill=(120, 132, 146), font=f_xs)

    # Left Button Cavity (MUTE / TEST) - at (253, 907)
    draw.rounded_rectangle([m_cx - 48, btn_y - 36, m_cx + 48, btn_y + 36], radius=5, fill=(10, 12, 15), outline=(50, 56, 68), width=2)
    draw.rounded_rectangle([m_cx - 44, btn_y - 32, m_cx + 44, btn_y + 32], radius=4, fill=(6, 8, 10))
    # Label strictly BELOW button well!
    draw.text((m_cx - 48, btn_y + 44), "MUTE / TEST", fill=(235, 242, 252), font=t_xs)
    draw.text((m_cx - 42, btn_y + 68), "HOLD 3 SEC", fill=(120, 132, 146), font=f_xs)

    # Right Button Cavity (DISP SELECT) - at (647, 907)
    draw.rounded_rectangle([d_cx - 48, btn_y - 36, d_cx + 48, btn_y + 36], radius=5, fill=(10, 12, 15), outline=(50, 56, 68), width=2)
    draw.rounded_rectangle([d_cx - 44, btn_y - 32, d_cx + 44, btn_y + 32], radius=4, fill=(6, 8, 10))
    # Label strictly BELOW button well!
    draw.text((m_cx_disp := d_cx - 50, btn_y + 44), "DISP SELECT", fill=(235, 242, 252), font=t_xs)
    draw.text((d_cx - 42, btn_y + 68), "TELEMETRY", fill=(120, 132, 146), font=f_xs)

    # 4. HORIZONTAL ARCHITECTURAL SHADOW GROOVE (Y: 1060 to 1090)
    draw.rectangle([fx0 + 15, fy0 + 1065, fx1 - 15, fy0 + 1085], fill=(8, 10, 14), outline=(35, 40, 50))

    # Battery compartment door label (Y: 1100 to 1135)
    draw.text((fx0 + 35, fy0 + 1100), "HOT-SWAPPABLE BATTERY BAY: 2x 12V 9Ah VRLA", fill=(150, 165, 180), font=f_xs)
    draw.text((fx1 - 250, fy0 + 1100), "SYSTEM ENERGIZED", fill=(0, 200, 240), font=f_xs)

    # 5. VENT GRILLE CAVITY (Y: 1145 to 1690)
    # The 3D Vent_Grille sits here. Clean dark intake cavity backing:
    draw.rectangle([fx0 + 30, fy0 + 1145, fx1 - 30, fy0 + 1690], fill=(8, 9, 12), outline=(35, 40, 48))

    # 6. BOTTOM CHIN (Y: 1700 to 1780)
    draw.rectangle([fx0 + 20, fy1 - 75, fx1 - 20, fy1 - 15], fill=(12, 14, 18), outline=(40, 45, 55))
    # Yellow hazard chevron bar
    for x in range(fx0 + 25, fx1 - 25, 36):
        draw.polygon([(x, fy1 - 70), (x + 12, fy1 - 70), (x + 4, fy1 - 58), (x - 8, fy1 - 58)], fill=(225, 175, 25))
    draw.text((fx0 + 40, fy1 - 50), "▲ CAUTION: DUAL POWER SOURCE - DISCONNECT ALL BEFORE SERVICING ▲", fill=(240, 240, 240), font=t_xs)
    draw.text((fx0 + 40, fy1 - 30), "RISK OF ELECTRIC SHOCK - REFER SERVICING TO QUALIFIED PERSONNEL", fill=(155, 165, 175), font=f_xs)

    # =========================================================================
    # ZONE 2: REAR PANEL I/O CONNECTIONS
    # Exact 1:1 Proportional Mapping: Width 790 px, Height 1750 px
    # Bounds: X in [890, 1680], Y in [40, 1790]
    # In 3D: X in [-0.046, +0.046] (0.092m), Z in [0.010, 0.214] (0.204m)
    # =========================================================================
    rx0, ry0, rx1, ry1 = 890, 40, 1680, 1790
    draw.rectangle([rx0, ry0, rx1, ry1], fill=(18, 20, 24), outline=(65, 70, 80), width=3)

    # Header - Distinct 2 lines
    draw.rectangle([rx0 + 10, ry0 + 10, rx1 - 10, ry0 + 90], fill=(10, 12, 16))
    draw.text((rx0 + 25, ry0 + 18), "REAR I/O INTERFACE", fill=(255, 255, 255), font=t_lg)
    draw.text((rx0 + 25, ry0 + 58), "230V AC 50/60Hz  ●  MAX LOAD: 900W / 1500VA", fill=(0, 210, 250), font=t_sm)
    draw.text((rx1 - 220, ry0 + 58), "CLASS B EMC", fill=(255, 180, 20), font=t_xs)

    # Top Section: Cooling Fan & AC Inlet (Y: 110 to 600)
    # 1. Circular Cooling Fan (radius = 140 px) -> PERFECT CIRCLE!
    fan_cx, fan_cy = rx0 + 200, ry0 + 250
    draw_fan_grille(draw, fan_cx, fan_cy, 140, f_xs)
    draw.text((fan_cx - 95, fan_cy + 155), "12V BRUSHLESS EXHAUST FAN", fill=(160, 170, 185), font=f_xs)

    # 2. AC Mains Input & Circuit Breaker (Right side of fan)
    in_box_x0 = rx0 + 400
    in_box_y0 = ry0 + 120
    draw.rectangle([in_box_x0, in_box_y0, rx1 - 20, in_box_y0 + 360], fill=(12, 14, 18), outline=(55, 60, 70), width=2)
    draw.text((in_box_x0 + 20, in_box_y0 + 18), "MAINS AC INPUT: 220-240V ~", fill=(220, 230, 240), font=t_xs)
    draw.text((in_box_x0 + 20, in_box_y0 + 38), "50/60Hz, 7.5A MAX", fill=(150, 160, 170), font=f_xs)

    # Realistic IEC C14 Inlet
    draw_realistic_c14_inlet(draw, in_box_x0 + 115, in_box_y0 + 130, 150, 100, f_xs)

    # Realistic Thermal Breaker button
    brk_cx, brk_cy = in_box_x0 + 285, in_box_y0 + 130
    draw_realistic_breaker(draw, brk_cx, brk_cy, 36, f_xs, f_md)
    draw.text((brk_cx - 44, brk_cy + 48), "BREAKER 10A", fill=(185, 195, 205), font=f_xs)
    draw.text((brk_cx - 40, brk_cy + 68), "PUSH RESET", fill=(145, 155, 165), font=f_xs)

    # Middle Section: Telemetry & Network Surge Protection (Y: 520 to 710)
    comm_y0 = ry0 + 510
    draw.rectangle([rx0 + 20, comm_y0, rx1 - 20, comm_y0 + 180], fill=(12, 14, 18), outline=(50, 55, 65), width=2)
    draw.text((rx0 + 30, comm_y0 + 14), "INTELLIGENT TELEMETRY & NETWORK SURGE PROTECTION", fill=(0, 210, 250), font=t_xs)

    # Realistic USB Type-B Port
    u_cx, u_cy = rx0 + 140, comm_y0 + 95
    draw_realistic_usb_b(draw, u_cx, u_cy, 76, 76)
    draw.text((u_cx - 36, comm_y0 + 142), "USB COMM", fill=(190, 200, 215), font=f_xs)

    # Realistic Shielded RJ45 Surge Ports (IN / OUT)
    for idx, name in enumerate(["NETWORK IN", "NETWORK OUT"]):
        rj_cx = rx0 + 390 + idx * 220
        rj_cy = comm_y0 + 95
        draw_realistic_rj45(draw, rj_cx, rj_cy, 88, 74, name, f_xs)

    # Bottom Section: AC Outlets (Y: 720 to 1720)
    out_y0 = ry0 + 720

    # Group A: Battery Backup & Surge (4 Outlets in 2x2 grid)
    draw.rectangle([rx0 + 20, out_y0, rx0 + 490, ry1 - 30], fill=(14, 16, 20), outline=(225, 175, 25), width=2)
    draw.rectangle([rx0 + 20, out_y0, rx0 + 490, out_y0 + 45], fill=(225, 175, 25))
    draw.text((rx0 + 35, out_y0 + 12), "BATTERY BACKUP & SURGE PROTECTED", fill=(0, 0, 0), font=t_xs)

    for r in range(2):
        for c in range(2):
            ocx = rx0 + 135 + c * 230
            ocy = out_y0 + 180 + r * 380
            draw_realistic_c13_outlet(draw, ocx, ocy, 156, 168, f"OUTPUT {r*2 + c + 1}", "230V~ 10A MAX", f_sm, f_xs)

    # Group B: Surge Only (2 Outlets in 2 rows)
    draw.rectangle([rx0 + 515, out_y0, rx1 - 20, ry1 - 30], fill=(14, 16, 20), outline=(75, 80, 92), width=2)
    draw.rectangle([rx0 + 515, out_y0, rx1 - 20, out_y0 + 45], fill=(42, 48, 58))
    draw.text((rx0 + 530, out_y0 + 12), "SURGE ONLY (NO BATT)", fill=(255, 255, 255), font=t_xs)

    for r in range(2):
        ocx = rx0 + 645
        ocy = out_y0 + 180 + r * 380
        draw_realistic_c13_outlet(draw, ocx, ocy, 156, 168, f"OUTPUT {r + 5}", "SURGE ONLY", f_sm, f_xs)

    # Ground Terminal (Chassis GND)
    gnd_cx, gnd_cy = rx1 - 70, ry1 - 80
    draw.ellipse([gnd_cx - 22, gnd_cy - 22, gnd_cx + 22, gnd_cy + 22], fill=(215, 175, 50), outline=(90, 70, 15), width=2)
    draw.line([gnd_cx - 15, gnd_cy, gnd_cx + 15, gnd_cy], fill=(30, 30, 30), width=3)
    draw.text((gnd_cx - 32, gnd_cy + 26), "GND ⏚", fill=(210, 220, 235), font=t_xs)

    # =========================================================================
    # ZONE 1: POWER BUTTON TEXTURE
    # Bounds: X in [1720, 2020], Y in [40, 340]
    # =========================================================================
    bx0, by0, bx1, by1 = 1720, 40, 2020, 340
    b_cx, b_cy = (bx0 + bx1)//2, (by0 + by1)//2
    b_rad = 140

    for r in range(b_rad, 0, -2):
        shade = 24 + int(28 * (1.0 - r / b_rad))
        draw.ellipse([b_cx - r, b_cy - r, b_cx + r, b_cy + r], fill=(shade, shade + 3, shade + 6))

    draw.ellipse([b_cx - b_rad, b_cy - b_rad, b_cx + b_rad, b_cy + b_rad], outline=(180, 190, 205), width=6)
    draw.ellipse([b_cx - b_rad + 6, b_cy - b_rad + 6, b_cx + b_rad - 6, b_cy + b_rad - 6], outline=(55, 60, 70), width=3)

    # Standby Power Symbol (⏻)
    sym_rad = 65
    draw.arc([b_cx - sym_rad, b_cy - sym_rad, b_cx + sym_rad, b_cy + sym_rad], start=-60, end=240, fill=(0, 245, 255), width=16)
    draw.line([b_cx, b_cy - sym_rad - 18, b_cx, b_cy - 10], fill=(0, 245, 255), width=16)
    draw.arc([b_cx - sym_rad, b_cy - sym_rad, b_cx + sym_rad, b_cy + sym_rad], start=-60, end=240, fill=(255, 255, 255), width=4)
    draw.line([b_cx, b_cy - sym_rad - 16, b_cx, b_cy - 12], fill=(255, 255, 255), width=4)

    # =========================================================================
    # ZONE 3: TECHNICAL RATING PLATE & BARCODE
    # Aspect Ratio 2.8:1 -> Width 640 px, Height 228 px
    # Bounds: X in [40, 680], Y in [1810, 2038]
    # In 3D: Y in [-0.070, +0.070] (0.140m), Z in [0.035, 0.085] (0.050m)
    # =========================================================================
    tx0, ty0, tx1, ty1 = 40, 1810, 680, 2038
    draw.rectangle([tx0, ty0, tx1, ty1], fill=(238, 240, 244), outline=(25, 28, 32), width=3)

    draw.rectangle([tx0 + 6, ty0 + 6, tx1 - 6, ty0 + 48], fill=(20, 23, 28))
    draw.text((tx0 + 16, ty0 + 12), "SEC-TECH INDUSTRIAL POWER SYSTEMS", fill=(255, 255, 255), font=t_md)
    draw.text((tx0 + 16, ty0 + 34), "TOWER UPS - CCTV INFRASTRUCTURE GRADE", fill=(0, 210, 250), font=f_xs)

    specs_c1 = [
        ("MODEL: SEC-UPS-1500VA-PRO", "INPUT: 220-240V~ 7.5A 50/60Hz"),
        ("CAPACITY: 1500VA / 900W", "OUTPUT: 230V~ 6.5A TRUE SINE"),
        ("BATT: 2x 12V 9Ah VRLA", "TRANSFER TIME: 2-4 ms TYPICAL")
    ]
    for idx, (col1, col2) in enumerate(specs_c1):
        draw.text((tx0 + 16, ty0 + 58 + idx * 24), col1, fill=(30, 35, 42), font=t_xs)
        draw.text((tx0 + 260, ty0 + 58 + idx * 24), col2, fill=(30, 35, 42), font=f_xs)

    draw.text((tx0 + 16, ty0 + 135), "CE   FCC   UKCA   RoHS   WEEE", fill=(20, 25, 30), font=t_md)
    draw_barcode(draw, tx1 - 180, ty0 + 125, 170, 75, "*UPS202688412B*", f_xs)

    draw.line([tx0 + 6, ty1 - 25, tx1 - 6, ty1 - 25], fill=(175, 180, 185), width=1)
    draw.text((tx0 + 16, ty1 - 20), "CAUTION: HIGH STORED VOLTAGE. PROFESSIONAL USE ONLY.", fill=(190, 30, 20), font=f_xs)

    # =========================================================================
    # ZONE 4: SIDE LOUVER VENTS (for side panels)
    # Bounds: X in [720, 1720], Y in [1810, 2038]
    # =========================================================================
    lx0, ly0, lx1, ly1 = 720, 1810, 1720, 2038
    draw.rectangle([lx0, ly0, lx1, ly1], fill=(18, 20, 24), outline=(48, 52, 60), width=2)
    draw.text((lx0 + 25, ly0 + 12), "CHASSIS COOLING INTAKE LOUVERS  -  AIR FLOW ▶▶", fill=(130, 140, 155), font=t_xs)

    for i in range(6):
        sy = ly0 + 40 + i * 30
        draw.rectangle([lx0 + 20, sy, lx1 - 20, sy + 18], fill=(6, 8, 10), outline=(32, 36, 44), width=1)
        draw.polygon([(lx0 + 22, sy + 2), (lx1 - 22, sy + 2), (lx1 - 22, sy + 8), (lx0 + 22, sy + 8)], fill=(36, 40, 48))
        draw.line([lx0 + 22, sy + 8, lx1 - 22, sy + 8], fill=(55, 60, 72), width=1)

    # =========================================================================
    # ZONE 5: NEUTRAL DARK METAL BUFFER (UV Safe Zone)
    # Bounds: X in [1740, 2040], Y in [380, 2040]
    # =========================================================================
    nx0, ny0, nx1, ny1 = 1740, 380, 2040, 2040
    draw.rectangle([nx0, ny0, nx1, ny1], fill=(20, 22, 26), outline=(35, 38, 45), width=1)

    im.save(ATLAS_PATH, "PNG", optimize=True)
    print(f"[OK] Saved Atlas: {ATLAS_PATH} ({im.size[0]}x{im.size[1]})")


def generate_screen_texture():
    """Generate 1024x512 T_Screen.png telemetry display texture with crystal-clear digits."""
    f_xl, f_lg, f_md, f_sm, f_xs, t_xl, t_lg, t_md, t_sm, t_xs = get_fonts()
    im = Image.new("RGBA", (1024, 512), (4, 14, 26, 255))
    draw = ImageDraw.Draw(im)

    for y in range(0, 512, 3):
        draw.line([0, y, 1024, y], fill=(2, 8, 16, 120), width=1)

    draw.rounded_rectangle([12, 12, 1012, 500], radius=10, outline=(0, 220, 255), width=2)
    draw.rounded_rectangle([18, 18, 1006, 494], radius=8, outline=(0, 110, 150), width=1)

    # Top Status Bar
    draw.rectangle([20, 20, 1004, 80], fill=(6, 24, 46))
    draw.line([20, 80, 1004, 80], fill=(0, 230, 255), width=2)

    draw.text((40, 28), "SEC-UPS 1500", fill=(255, 255, 255), font=t_md)
    draw.text((320, 32), "MODE: ONLINE ● NORMAL", fill=(0, 255, 180), font=t_sm)
    draw.text((740, 32), "AVR STABILIZER: ACTIVE", fill=(140, 205, 245), font=f_xs)

    # Col 1: INPUT TELEMETRY
    c1_x0, c1_x1 = 30, 320
    draw.rounded_rectangle([c1_x0, 95, c1_x1, 485], radius=6, fill=(6, 20, 36), outline=(0, 150, 190), width=1)
    draw.rectangle([c1_x0, 95, c1_x1, 135], fill=(0, 150, 190))
    draw.text((c1_x0 + 65, 102), "MAINS INPUT", fill=(4, 14, 26), font=t_sm)

    draw.text((c1_x0 + 35, 160), "230.4 V", fill=(0, 245, 255), font=t_xl)
    draw.text((c1_x0 + 40, 240), "FREQ: 50.0 Hz", fill=(180, 230, 255), font=t_sm)
    draw.text((c1_x0 + 40, 285), "STATUS: STABLE", fill=(0, 255, 160), font=f_sm)

    sine_y = 370
    draw.line([c1_x0 + 20, sine_y, c1_x1 - 20, sine_y], fill=(0, 85, 130), width=1)
    pts = []
    for px in range(c1_x0 + 20, c1_x1 - 20):
        t = (px - (c1_x0 + 20)) / (c1_x1 - c1_x0 - 40) * 4 * math.pi
        py = sine_y - int(28 * math.sin(t))
        pts.append((px, py))
    draw.line(pts, fill=(0, 245, 255), width=3)
    draw.text((c1_x0 + 55, 420), "AC SINE WAVE ~ OK", fill=(140, 215, 245), font=f_xs)

    # Col 2: BATTERY & RUNTIME TELEMETRY
    c2_x0, c2_x1 = 335, 685
    draw.rounded_rectangle([c2_x0, 95, c2_x1, 485], radius=6, fill=(6, 20, 36), outline=(0, 150, 190), width=1)
    draw.rectangle([c2_x0, 95, c2_x1, 135], fill=(0, 150, 190))
    draw.text((c2_x0 + 80, 102), "BATTERY SYSTEM", fill=(4, 14, 26), font=t_sm)

    bat_x0, bat_y0, bat_x1, bat_y1 = c2_x0 + 40, 165, c2_x1 - 60, 220
    draw.rectangle([bat_x0, bat_y0, bat_x1, bat_y1], outline=(0, 230, 255), width=2)
    draw.rectangle([bat_x1, bat_y0 + 12, bat_x1 + 10, bat_y1 - 12], fill=(0, 230, 255))
    seg_w = (bat_x1 - bat_x0 - 18) // 5
    for s in range(5):
        sx0 = bat_x0 + 4 + s * (seg_w + 3)
        draw.rectangle([sx0, bat_y0 + 4, sx0 + seg_w, bat_y1 - 4], fill=(0, 255, 175))

    draw.text((c2_x0 + 110, 235), "100% [CHARGED]", fill=(0, 255, 175), font=t_xs)
    draw.text((c2_x0 + 50, 280), "VOLTAGE: 27.4 VDC", fill=(180, 230, 255), font=t_sm)
    draw.text((c2_x0 + 50, 320), "HEALTH: EXCELLENT", fill=(0, 255, 160), font=f_sm)

    # Runtime callout box
    draw.rectangle([c2_x0 + 30, 380, c2_x1 - 30, 465], fill=(2, 10, 20), outline=(0, 200, 240), width=2)
    draw.text((c2_x0 + 45, 388), "ESTIMATED RUNTIME:", fill=(140, 210, 245), font=f_xs)
    draw.text((c2_x0 + 45, 412), "52 MINUTES", fill=(255, 255, 255), font=t_lg)

    # Col 3: UPS INVERTER LOAD
    c3_x0, c3_x1 = 700, 995
    draw.rounded_rectangle([c3_x0, 95, c3_x1, 485], radius=6, fill=(6, 20, 36), outline=(0, 150, 190), width=1)
    draw.rectangle([c3_x0, 95, c3_x1, 135], fill=(0, 150, 190))
    draw.text((c3_x0 + 65, 102), "UPS INVERTER LOAD", fill=(4, 14, 26), font=t_sm)

    draw.text((c3_x0 + 35, 160), "230.0 V", fill=(0, 245, 255), font=t_xl)
    draw.text((c3_x0 + 38, 240), "LOAD: 380W (42%)", fill=(180, 230, 255), font=t_sm)

    # Load bar
    draw.rectangle([c3_x0 + 35, 285, c3_x1 - 35, 325], outline=(0, 230, 255), width=2)
    draw.rectangle([c3_x0 + 38, 288, c3_x0 + 38 + int((c3_x1 - c3_x0 - 76) * 0.42), 322], fill=(120, 240, 160))
    draw.text((c3_x0 + 35, 335), "0%", fill=(120, 180, 210), font=f_xs)
    draw.text((c3_x1 - 70, 335), "100%", fill=(120, 180, 210), font=f_xs)

    draw.text((c3_x0 + 40, 385), "OUTPUT: PROTECTED", fill=(0, 255, 160), font=t_xs)
    draw.text((c3_x0 + 40, 420), "SURGE SUPPRESSOR: ACTIVE", fill=(140, 210, 245), font=f_xs)

    im.save(SCREEN_PATH, "PNG", optimize=True)
    print(f"[OK] Saved Screen Texture: {SCREEN_PATH} ({im.size[0]}x{im.size[1]})")


if __name__ == "__main__":
    generate_security_atlas()
    generate_screen_texture()
