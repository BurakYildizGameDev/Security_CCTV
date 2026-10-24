"""
=============================================================================
Security CCTV Asset Production Suite - Asset 35
Asset Name: SEC_Sensor_Door_Contact (Manyetik Kapı Kontağı)
Texture Generation Script v3 (Ultra-High Resolution 2048 x 2048)
Output:
    - exports/T_Security_Atlas.png (2048 x 2048)

RESOLUTION & CLARITY UPGRADE:
- Atlas resolution: 2048 x 2048 (45 px/mm on front label plate!)
- Front Label: SEC-DC 400 (88pt Arial Bold), MAGNETIC DOOR CONTACT (50pt)
- Backplate Label: SEC-DC 400 SPECIFICATIONS (60pt), terminal block with brass screws
- Magnet Face: SEC-DC 400-M MAGNET BLOCK (92pt), ALIGNMENT ARROW, OPERATING GAP
- Status LED Lens: High-detail optical Fresnel lens texture (crimson rim, ruby core, specular glare)
=============================================================================
"""

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

# ---------------------------------------------------------------- UV bantları (2048x2048)
REGION_FRONT  = (32, 32, 2016, 410)     # 1984 x 378 px -> 44.0 x 8.4 mm (45.1 px/mm)
REGION_BACK   = (32, 450, 2016, 878)    # 1984 x 428 px -> 68.0 x 14.7 mm (29.2 px/mm)
REGION_MAGNET = (32, 906, 2016, 1326)   # 1984 x 420 px -> 50.4 x 10.66 mm (39.4 px/mm)
REGION_DETAIL = (32, 1354, 2016, 2016)  # 1984 x 662 px

# LED lens penceresi (DETAIL banti icinde, kare bolge)
REGION_LED = (92, 1440, 260, 1608)

# Duz renk UV noktalari (piksel)
PIX_FLAT_BODY = (1080, 1870)
PIX_FLAT_SIDE = (1360, 1870)

# Renk Paleti
BODY_LIGHT   = (248, 250, 253, 255)
BODY_MID     = (232, 238, 245, 255)
PLATE_DARK   = (18, 22, 28, 255)
PLATE_DARK_2 = (30, 36, 44, 255)
AMBER        = (225, 170, 35, 255)
INK_DARK     = (18, 22, 28, 255)
INK_TEXT     = (48, 56, 68, 255)
INK_SOFT     = (96, 108, 122, 255)
WHITE        = (255, 255, 255, 255)
COOL_LIGHT   = (175, 195, 215, 255)
COOL_SOFT    = (145, 168, 192, 255)

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

def text_w(draw, text, font):
    try:
        return draw.textlength(text, font=font)
    except Exception:
        return draw.textlength(text)

def draw_left(draw, x, y, text, font, fill):
    draw.text((x, y), text, font=font, fill=fill)

def draw_center(draw, cx, y, text, font, fill):
    draw.text((cx - text_w(draw, text, font) / 2.0, y), text, font=font, fill=fill)

def draw_barcode(draw, x0, y0, width, height, dark=INK_DARK, light=(255, 255, 255, 255)):
    x = x0
    idx = 0
    while x < x0 + width:
        thick = 4 + (idx * 7) % 5
        col = dark if (idx % 3 == 0 or idx % 7 == 0) else light
        draw.line([(x, y0), (x, y0 + height)], fill=col, width=thick)
        x += 10
        idx += 1

def draw_placard(draw, box, accent=True, fill=PLATE_DARK):
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=fill, outline=(75, 86, 100, 255), width=4)
    if accent:
        draw.rectangle([x0 + 4, y0 + 4, x1 - 4, y0 + 16], fill=AMBER)

def draw_front_label(draw):
    """
    BANT-1: Label_Plate on yuzu (1984 x 378 px).
    Ultra-high resolution typography.
    LED lens penceresi model x = +15 mm -> 316 px.
    """
    x0, y0, x1, y1 = REGION_FRONT
    draw.rectangle([x0, y0, x1, y1], fill=BODY_LIGHT)

    # --- LED lens yuvasi (model +X ucu) ---
    lcx, lcy = x0 + 316, y0 + 188
    draw.ellipse([lcx - 132, lcy - 132, lcx + 132, lcy + 132], fill=(230, 235, 242, 255),
                 outline=(180, 190, 202, 255), width=5)
    draw.ellipse([lcx - 112, lcy - 112, lcx + 112, lcy + 112], fill=(28, 32, 38, 255),
                 outline=(125, 138, 152, 255), width=5)
    f_mini = load_font(FONT_MONO, 34)
    draw_center(draw, lcx, y0 + 312, "STATUS", f_mini, INK_SOFT)

    # --- Koyu marka plakasi ---
    px0, py0, px1, py1 = x0 + 500, y0 + 28, x0 + 1400, y0 + 350
    draw_placard(draw, (px0, py0, px1, py1))

    draw_left(draw, px0 + 44, py0 + 32, "SEC-DC 400", load_font(FONT_SANS, 88), WHITE)
    draw_left(draw, px0 + 48, py0 + 148, "MAGNETIC DOOR CONTACT", load_font(FONT_MONO, 50), COOL_LIGHT)
    draw_left(draw, px0 + 48, py0 + 208, "REED SWITCH  /  NC CONTACT", load_font(FONT_MONO, 44), COOL_SOFT)
    draw_left(draw, px0 + 48, py0 + 260, "12 V DC  •  100 mA  •  IP66", load_font(FONT_MONO, 44), AMBER)

    # --- Sag blok: barkod ve standartlar ---
    bx0 = x0 + 1444
    draw_barcode(draw, bx0, y0 + 44, 488, 148)
    f_s = load_font(FONT_MONO, 36)
    draw_left(draw, bx0, y0 + 212, "LOT 35 / 75", f_s, INK_TEXT)
    draw_left(draw, bx0, y0 + 260, "EN 50131-2-6 GRADE 2", f_s, INK_TEXT)
    draw_left(draw, bx0, y0 + 308, "CE    RoHS    IP66", f_s, INK_SOFT)

def draw_back_label(draw):
    """BANT-2: Backplate arka yuzu (1984 x 428 px) - fabrika teknik etiketi."""
    x0, y0, x1, y1 = REGION_BACK
    draw.rectangle([x0, y0, x1, y1], fill=BODY_LIGHT)
    draw.rectangle([x0 + 8, y0 + 8, x1 - 8, y1 - 8], outline=(195, 205, 218, 255), width=4)

    draw_left(draw, x0 + 48, y0 + 32, "SEC-DC 400  —  TECHNICAL SPECIFICATIONS",
              load_font(FONT_SANS, 60), INK_DARK)

    f_m = load_font(FONT_MONO, 42)
    draw_left(draw, x0 + 52, y0 + 124, "12 V DC MAX 100 mA  •  NC ALARM + NC TAMPER", f_m, INK_TEXT)
    draw_left(draw, x0 + 52, y0 + 180, "ABS UL94-V0  •  IP66  •  EN 50131-2-6 GRADE 2", f_m, INK_TEXT)
    draw_left(draw, x0 + 52, y0 + 236, "SERIAL: SECDC400-26001  •  BATCH: 2026-W42",
              load_font(FONT_MONO, 38), INK_SOFT)

    # Klemens baglanti semasi (ALM / COM / TMP)
    tx0, ty0, tx1, ty1 = x0 + 1320, y0 + 60, x1 - 48, y0 + 372
    draw.rectangle([tx0, ty0, tx1, ty1], fill=(234, 240, 248, 255),
                   outline=(165, 178, 192, 255), width=3)
    draw_center(draw, (tx0 + tx1) / 2, ty0 + 16, "WIRING TERMINAL BLOCK", load_font(FONT_MONO, 30), INK_DARK)
    f_t = load_font(FONT_MONO, 34)
    terminals = [("ALM", "NC"), ("COM", "COMMON"), ("TMP", "TAMPER")]
    for i, (lbl, sub) in enumerate(terminals):
        cx = tx0 + 80 + i * 144
        draw.ellipse([cx - 40, ty0 + 70, cx + 40, ty0 + 150], fill=(195, 204, 215, 255),
                     outline=(90, 102, 115, 255), width=3)
        draw.line([(cx, ty0 + 86), (cx, ty0 + 134)], fill=(55, 62, 70, 255), width=5)
        draw_center(draw, cx, ty0 + 168, lbl, f_t, INK_DARK)
        draw_center(draw, cx, ty0 + 208, sub, load_font(FONT_MONO, 24), INK_SOFT)

    draw_barcode(draw, x0 + 52, y0 + 316, 500, 88)
    draw_left(draw, x0 + 600, y0 + 336, "MADE IN EU  •  REV 2.4", load_font(FONT_MONO, 36), INK_SOFT)

def draw_magnet_face(draw):
    """BANT-3: Magnet_Block on yuzu (1984 x 420 px)."""
    x0, y0, x1, y1 = REGION_MAGNET
    draw.rectangle([x0, y0, x1, y1], fill=BODY_MID)

    px0, py0, px1, py1 = x0 + 36, y0 + 28, x0 + 1336, y0 + 392
    draw_placard(draw, (px0, py0, px1, py1), fill=PLATE_DARK_2)

    draw_left(draw, px0 + 48, py0 + 44, "SEC-DC 400-M", load_font(FONT_SANS, 92), WHITE)
    draw_left(draw, px0 + 52, py0 + 176, "MAGNET BLOCK UNIT", load_font(FONT_MONO, 52), COOL_LIGHT)
    draw_left(draw, px0 + 52, py0 + 240, "ALIGN WITH SENSOR BODY", load_font(FONT_MONO, 44), COOL_SOFT)
    draw_left(draw, px0 + 52, py0 + 296, "NEODYMIUM N35  •  6 mm NOMINAL GAP", load_font(FONT_MONO, 44), AMBER)

    # Cift yonlu hizalama oku
    ax0, ax1, ay = x0 + 1412, x1 - 60, y0 + 192
    draw.line([(ax0 + 68, ay), (ax1 - 68, ay)], fill=(85, 98, 115, 255), width=8)
    draw.polygon([(ax0 + 12, ay), (ax0 + 84, ay - 32), (ax0 + 84, ay + 32)], fill=(85, 98, 115, 255))
    draw.polygon([(ax1 - 12, ay), (ax1 - 84, ay - 32), (ax1 - 84, ay + 32)], fill=(85, 98, 115, 255))

    f_s = load_font(FONT_MONO, 36)
    draw_center(draw, (ax0 + ax1) / 2.0, y0 + 52, "OPERATING GAP", f_s, INK_DARK)
    draw_center(draw, (ax0 + ax1) / 2.0, y0 + 280, "DOOR FRAME SIDE", f_s, INK_SOFT)

def draw_detail_area(draw):
    """BANT-4: LED lens dokusu ve duz govde renk alanlari."""
    x0, y0, x1, y1 = REGION_DETAIL
    draw.rectangle([x0, y0, x1, y1], fill=BODY_LIGHT)

    # --- Status LED lens dokusu (kirmizi kubbe) ---
    lx0, ly0, lx1, ly1 = REGION_LED
    lcx, lcy = (lx0 + lx1) // 2, (ly0 + ly1) // 2
    r = (lx1 - lx0) // 2
    draw.ellipse([lx0, ly0, lx1, ly1], fill=(145, 18, 16, 255), outline=(85, 10, 10, 255), width=6)
    draw.ellipse([lcx - int(r * 0.72), lcy - int(r * 0.72),
                  lcx + int(r * 0.72), lcy + int(r * 0.72)], fill=(205, 30, 26, 255))
    draw.ellipse([lcx - int(r * 0.34), lcy - int(r * 0.46),
                  lcx + int(r * 0.18), lcy - int(r * 0.10)], fill=(255, 135, 125, 255))
    f_s = load_font(FONT_MONO, 32)
    draw_center(draw, lcx, ly0 - 48, "STATUS LED LENS", f_s, INK_TEXT)

    # --- Duz renk alanlari (govde / pah yuzeyleri) ---
    swatches = [
        (960, 1760, 1200, 1980, BODY_LIGHT, "BODY RAL 9003"),
        (1240, 1760, 1480, 1980, (214, 222, 230, 255), "CHAMFER TONE"),
        (1520, 1760, 1760, 1980, PLATE_DARK, "DARK SLATE"),
        (1800, 1760, 2000, 1980, (195, 205, 218, 255), "METAL"),
    ]
    for sx0, sy0, sx1, sy1, col, lbl in swatches:
        draw.rectangle([sx0, sy0, sx1, sy1], fill=col, outline=(185, 195, 208, 255), width=3)
        draw_center(draw, (sx0 + sx1) / 2, sy1 - 50, lbl, load_font(FONT_MONO, 28), INK_SOFT)

def generate_textures():
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), BODY_LIGHT)
    draw = ImageDraw.Draw(img)

    draw_front_label(draw)
    draw_back_label(draw)
    draw_magnet_face(draw)
    draw_detail_area(draw)

    img.save(ATLAS_PATH, "PNG")
    print(f"[OK] Generated Texture Atlas v3 (2048x2048) for Asset 35: {ATLAS_PATH}")
    print(f"     FRONT band 1984 x 378 px -> 44.0 x 8.4 mm = {1984/44.0:.1f} px/mm")

if __name__ == "__main__":
    generate_textures()
