"""
Generate 2048x2048 high-resolution procedural texture atlas (T_Security_Atlas.png)
for SEC_Alarm_Siren_Beacon using PIL / Pillow.
"""

import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)
OUT_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")


def get_fonts():
    """Load crisp industrial fonts with standard fallbacks."""
    f_xl = f_lg = f_md = f_sm = f_xs = None
    t_xl = t_lg = t_md = t_sm = t_xs = None

    font_paths = [
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\calibri.ttf"
    ]
    primary_font = None
    bold_font = r"C:\Windows\Fonts\arialbd.ttf" if os.path.exists(r"C:\Windows\Fonts\arialbd.ttf") else None

    for p in font_paths:
        if os.path.exists(p):
            primary_font = p
            break

    if primary_font:
        try:
            f_xl = ImageFont.truetype(primary_font, 56)
            f_lg = ImageFont.truetype(primary_font, 40)
            f_md = ImageFont.truetype(primary_font, 28)
            f_sm = ImageFont.truetype(primary_font, 22)
            f_xs = ImageFont.truetype(primary_font, 18)

            bf = bold_font if bold_font else primary_font
            t_xl = ImageFont.truetype(bf, 64)
            t_lg = ImageFont.truetype(bf, 46)
            t_md = ImageFont.truetype(bf, 32)
            t_sm = ImageFont.truetype(bf, 24)
            t_xs = ImageFont.truetype(bf, 20)
        except Exception as e:
            print(f"[WARN] Failed loading TTF fonts: {e}")

    if f_xl is None:
        f_xl = f_lg = f_md = f_sm = f_xs = ImageFont.load_default()
        t_xl = t_lg = t_md = t_sm = t_xs = ImageFont.load_default()

    return f_xl, f_lg, f_md, f_sm, f_xs, t_xl, t_lg, t_md, t_sm, t_xs


def generate_atlas():
    w, h = 2048, 2048
    img = Image.new("RGBA", (w, h), (28, 32, 38, 255))
    draw = ImageDraw.Draw(img)
    f_xl, f_lg, f_md, f_sm, f_xs, t_xl, t_lg, t_md, t_sm, t_xs = get_fonts()

    # =========================================================================
    # ZONE 1: FRONT SIREN FASCIA & WARNING GRAPHICS (X: 0..1100, Y: 0..1100)
    # =========================================================================
    draw.rectangle([0, 0, 1100, 1100], fill=(238, 242, 246, 255))
    draw.line([(0, 0), (1100, 0)], fill=(255, 255, 255, 255), width=4)
    draw.line([(0, 1096), (1100, 1096)], fill=(180, 190, 200, 255), width=4)
    draw.line([(0, 0), (0, 1100)], fill=(255, 255, 255, 255), width=4)
    draw.line([(1096, 0), (1096, 1100)], fill=(180, 190, 200, 255), width=4)

    # Top Warning Header Banner
    draw.rectangle([40, 50, 1060, 210], fill=(205, 25, 25, 255), outline=(150, 15, 15, 255), width=3)
    draw.rectangle([50, 60, 1050, 200], fill=(220, 30, 30, 255))
    draw.text((100, 75), "SECURITY WARNING", fill=(255, 255, 255, 255), font=t_xl)
    draw.text((105, 150), "24HR ELECTRONIC INTRUDER ALARM & CCTV SYSTEM", fill=(255, 240, 240, 255), font=t_sm)

    # Strobe Hazard Warning Triangle (Yellow / Black ISO Warning)
    tri_x, tri_y = 550, 420
    tri_r = 130
    p1 = (tri_x, tri_y - tri_r)
    p2 = (tri_x + int(tri_r * 1.15), tri_y + int(tri_r * 0.75))
    p3 = (tri_x - int(tri_r * 1.15), tri_y + int(tri_r * 0.75))
    draw.polygon([p1, p2, p3], fill=(250, 200, 20, 255), outline=(20, 20, 20, 255))
    p1_in = (tri_x, tri_y - tri_r + 14)
    p2_in = (tri_x + int(tri_r * 1.15) - 12, tri_y + int(tri_r * 0.75) - 8)
    p3_in = (tri_x - int(tri_r * 1.15) + 12, tri_y + int(tri_r * 0.75) - 8)
    draw.polygon([p1_in, p2_in, p3_in], outline=(20, 20, 20, 255), width=6)

    # Flash lightning bolt symbol
    bolt = [
        (tri_x + 10, tri_y - 65),
        (tri_x - 30, tri_y + 10),
        (tri_x + 5,  tri_y + 10),
        (tri_x - 12, tri_y + 70),
        (tri_x + 35, tri_y - 5),
        (tri_x + 2,  tri_y - 5)
    ]
    draw.polygon(bolt, fill=(20, 20, 20, 255))

    # Product Brand & Specification Badges
    draw.text((230, 600), "SEC-SOUNDER 350-X", fill=(20, 30, 45, 255), font=t_lg)
    draw.text((150, 665), "115dB TWIN PIEZO & HIGH-INTENSITY XENON BEACON", fill=(70, 85, 105, 255), font=t_sm)
    draw.text((250, 710), "GRADE 3 ENVIRONMENTAL CLASS IV", fill=(100, 115, 135, 255), font=f_md)

    # Dual Tamper / System Status Indicators
    draw.rectangle([120, 780, 980, 890], fill=(225, 230, 238, 255), outline=(180, 190, 205, 255), width=2)
    # Left: SYS OK (Green)
    draw.ellipse([160, 810, 210, 860], fill=(35, 210, 65, 255), outline=(20, 140, 40, 255), width=3)
    draw.ellipse([175, 825, 195, 845], fill=(180, 255, 190, 255))
    draw.text((230, 822), "SYSTEM ARMED / OK", fill=(25, 35, 45, 255), font=t_sm)
    # Right: TAMPER / ALARM (Red)
    draw.ellipse([610, 810, 660, 860], fill=(235, 35, 35, 255), outline=(160, 20, 20, 255), width=3)
    draw.ellipse([625, 825, 645, 845], fill=(255, 180, 180, 255))
    draw.text((680, 822), "TAMPER PROTECTED", fill=(25, 35, 45, 255), font=t_sm)

    # Bottom Security Accent Navy Band
    draw.rectangle([0, 960, 1100, 1100], fill=(18, 35, 68, 255))
    draw.line([(0, 960), (1100, 960)], fill=(240, 180, 20, 255), width=5)
    draw.text((160, 1010), "ACTIVE ALARM SURVEILLANCE NETWORK", fill=(255, 255, 255, 255), font=t_md)

    # =========================================================================
    # ZONE 2: SPEAKER GRILLE ACOUSTIC PERFORATED PATTERN (X: 1140..2048, Y: 0..900)
    # =========================================================================
    draw.rectangle([1140, 0, 2048, 900], fill=(16, 18, 22, 255))
    for gy in range(40, 860, 32):
        for gx in range(1180, 2020, 32):
            shift = 16 if (gy // 32) % 2 == 1 else 0
            px = gx + shift
            if px < 2010:
                draw.ellipse([px - 8, gy - 8, px + 8, gy + 8], fill=(6, 8, 10, 255), outline=(45, 52, 62, 255), width=2)
                draw.ellipse([px - 4, gy - 4, px + 4, gy + 4], fill=(0, 0, 0, 255))
    for ly in range(100, 800, 160):
        draw.rectangle([1140, ly, 2048, ly + 25], fill=(10, 12, 15, 255))
        draw.line([(1140, ly + 25), (2048, ly + 25)], fill=(65, 75, 90, 255), width=2)

    # =========================================================================
    # ZONE 3: TECHNICAL RATING & COMPLIANCE LABEL (X: 0..1200, Y: 1140..1700)
    # =========================================================================
    draw.rectangle([0, 1140, 1200, 1700], fill=(230, 235, 240, 255))
    draw.rectangle([15, 1155, 1185, 1685], fill=(242, 245, 250, 255), outline=(50, 60, 75, 255), width=3)
    draw.rectangle([25, 1165, 1175, 1250], fill=(24, 32, 45, 255))
    draw.text((45, 1180), "INDUSTRIAL SECURITY SOUNDER & STROBE BEACON", fill=(255, 255, 255, 255), font=t_md)
    draw.text((45, 1220), "MODEL: SEC-ALM-350X  |  GRADE 3 EN 50131-4", fill=(180, 200, 225, 255), font=f_sm)

    specs = [
        "OPERATING VOLTAGE: 9.0 - 15.0 VDC (NOMINAL 12V DC)",
        "CURRENT DRAW: 25mA STANDBY  |  350mA FULL ALARM",
        "ACOUSTIC OUTPUT: 115 dB(A) @ 1 METRE (DUAL PIEZO)",
        "STROBE BEACON: 1W XENON FLASH TUBE @ 1Hz (60 FPM)",
        "ENVIRONMENTAL: IP65 WEATHERPROOF / UV RESISTANT",
        "BACKUP BATTERY: 7.2V 250mAh Ni-MH RECHARGEABLE"
    ]
    for i, sp in enumerate(specs):
        sy = 1275 + i * 42
        draw.text((45, sy), sp, fill=(20, 25, 35, 255), font=f_sm)

    draw.rectangle([45, 1540, 520, 1630], fill=(255, 255, 255, 255), outline=(80, 90, 100, 255), width=2)
    for bx in range(65, 500, 7):
        if (bx * 13) % 17 < 11:
            draw.line([(bx, 1550), (bx, 1605)], fill=(15, 20, 30, 255), width=4)
    draw.text((160, 1610), "*ALM202688941S*", fill=(20, 25, 35, 255), font=f_xs)

    certs = ["CE", "FCC", "UKCA", "RoHS", "WEEE", "UL"]
    for i, c in enumerate(certs):
        cx = 620 + (i % 3) * 180
        cy = 1540 + (i // 3) * 55
        draw.rectangle([cx, cy, cx + 150, cy + 45], fill=(225, 230, 240, 255), outline=(70, 80, 95, 255), width=2)
        draw.text((cx + 35, cy + 10), c, fill=(20, 25, 35, 255), font=t_sm)

    # =========================================================================
    # ZONE 4: FRESNEL PRISMS & REFLECTOR CHROME (X: 1220..2048, Y: 920..1700)
    # =========================================================================
    draw.rectangle([1220, 920, 2048, 1700], fill=(160, 25, 25, 255))
    for fx in range(1220, 2048, 16):
        draw.line([(fx, 920), (fx, 1700)], fill=(220, 45, 45, 255), width=6)
        draw.line([(fx + 8, 920), (fx + 8, 1700)], fill=(120, 15, 15, 255), width=6)
    draw.line([(1220, 1310), (2048, 1310)], fill=(255, 180, 180, 255), width=12)

    # =========================================================================
    # ZONE 5: ISOLATED NEUTRAL BUFFERS
    # =========================================================================
    # 5.1 Pure White Casing Buffer: (X: 1980..2048, Y: 1980..2048) -> UV (0.967, 0.000, 1.000, 0.033) in Blender
    draw.rectangle([1980, 1980, 2048, 2048], fill=(238, 242, 246, 255))
    # 5.2 Dark Anthracite Metal Buffer: (X: 1980..2048, Y: 1900..1968)
    draw.rectangle([1980, 1900, 2048, 1968], fill=(32, 36, 42, 255))

    img.save(OUT_PATH, format="PNG")
    print(f"[INFO] Generated 2048x2048 T_Security_Atlas.png: {OUT_PATH}")
    return OUT_PATH


if __name__ == "__main__":
    generate_atlas()
