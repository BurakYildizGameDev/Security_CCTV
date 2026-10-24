"""
=============================================================================
Security CCTV Asset Production Suite - Asset 34
Asset Name: SEC_Sensor_Glass_Break
Texture Generation Script v3 (Ultra-High Resolution 2048 x 2048)
Output:
    - exports/T_Security_Atlas.png (2048 x 2048)

RESOLUTION UPGRADE:
- Atlas resolution: 2048 x 2048 (4x pixel density, 15.3 px/mm)
- Razor-sharp typography: Main header 56pt, Subheaders 28-30pt, Specs 22-24pt
- High-contrast color tuning: Pure white & vibrant cyan on obsidian placards;
  deep slate charcoal (high-contrast) on off-white body.
- Zero stretching: Aspect ratio strictly locked (1:1.72) to physical housing.
=============================================================================
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")

FONT_MONO = r"C:\Windows\Fonts\consolab.ttf"
FONT_SANS = r"C:\Windows\Fonts\arialbd.ttf"

ATLAS_W, ATLAS_H = 2048, 2048

# High-Contrast Industrial Color Palette
BODY_WHITE      = (246, 248, 252, 255)
BODY_SHADOW     = (214, 222, 232, 255)
BODY_BEVEL      = (230, 236, 244, 255)
PLATE_DARK      = (16, 18, 24, 255)
PLATE_DARK_2    = (28, 34, 42, 255)
AMBER_ACCENT    = (235, 175, 30, 255)
CYAN_ACCENT     = (35, 195, 235, 255)
GREEN_LED       = (25, 215, 75, 255)
GREEN_DARK      = (12, 105, 35, 255)
RED_LED         = (235, 35, 30, 255)
RED_DARK        = (115, 16, 14, 255)
INK_SOLID_BLACK = (12, 15, 20, 255)
INK_DARK        = (22, 26, 34, 255)
INK_MUTED       = (65, 75, 90, 255)
INK_LIGHT       = (145, 160, 178, 255)
WHITE           = (255, 255, 255, 255)

_FONT_CACHE = {}

def get_font(path, size):
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

def draw_center(draw, cx, y, text, font, fill):
    w = text_w(draw, text, font)
    draw.text((cx - w / 2.0, y), text, font=font, fill=fill)

def draw_left(draw, x, y, text, font, fill):
    draw.text((x, y), text, font=font, fill=fill)

def draw_right(draw, x, y, text, font, fill):
    w = text_w(draw, text, font)
    draw.text((x - w, y), text, font=font, fill=fill)

def draw_barcode(draw, x0, y0, width, height):
    x = x0
    idx = 0
    while x < x0 + width:
        thick = 4 if (idx % 2 == 0) else (6 if (idx % 5 == 0) else 2)
        col = WHITE if (idx % 3 != 0 and idx % 7 != 0) else PLATE_DARK
        draw.line([(x, y0), (x, y0 + height)], fill=col, width=thick)
        x += 8
        idx += 1

def generate_textures():
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), BODY_WHITE)
    draw = ImageDraw.Draw(img)

    # Separation dividers
    draw.line([(1024, 0), (1024, 1648)], fill=BODY_SHADOW, width=3)
    draw.line([(0, 1656), (2048, 1656)], fill=BODY_SHADOW, width=3)

    # =========================================================================
    # COLUMN 1: FRONT SENSOR FACE ((48, 48) -> (968, 1628)) - Width: 920, Height: 1580
    # =========================================================================
    fx0, fy0, fx1, fy1 = 48, 48, 968, 1628
    fcx = (fx0 + fx1) / 2 # 508

    # Housing surface fill & outer chamfer border
    draw.rectangle([fx0, fy0, fx1, fy1], fill=BODY_WHITE)
    draw.rectangle([fx0 + 16, fy0 + 16, fx1 - 16, fy1 - 16], outline=BODY_SHADOW, width=3)

    # 1. Upper Inset Brand Placard (Y: fy0 + 32 .. fy0 + 472)
    bx0, by0, bx1, by1 = fx0 + 32, fy0 + 32, fx1 - 32, fy0 + 472
    draw.rectangle([bx0, by0, bx1, by1], fill=PLATE_DARK, outline=(75, 88, 104, 255), width=3)
    # Amber top accent bar
    draw.rectangle([bx0 + 3, by0 + 3, bx1 - 3, by0 + 14], fill=AMBER_ACCENT)

    # Bold Brand Title
    draw_center(draw, fcx, by0 + 30, "SEC-GBD 300 PRO", get_font(FONT_SANS, 54), WHITE)
    draw_center(draw, fcx, by0 + 96, "ACOUSTIC GLASS BREAK DETECTOR", get_font(FONT_MONO, 28), CYAN_ACCENT)
    draw_center(draw, fcx, by0 + 138, "DUAL-FREQUENCY AUDIO & FLEX SENSOR", get_font(FONT_MONO, 24), (215, 230, 245, 255))
    draw_center(draw, fcx, by0 + 176, "RANGE: 9.0M (30FT)  •  360° COVERAGE", get_font(FONT_MONO, 23), INK_LIGHT)

    # Dual Frequency Waveform Visualizer
    draw.line([(bx0 + 40, by0 + 230), (bx1 - 40, by0 + 230)], fill=(45, 55, 68, 255), width=2)
    draw_left(draw, bx0 + 40, by0 + 242, "FLEX: 5Hz (SHOCK)", get_font(FONT_MONO, 22), AMBER_ACCENT)
    pts_flex = []
    for x in range(bx0 + 230, bx0 + 430, 4):
        rel_x = (x - (bx0 + 230)) * 0.08
        y = by0 + 256 + math.sin(rel_x) * 16.0
        pts_flex.append((x, y))
    for i in range(len(pts_flex) - 1):
        draw.line([pts_flex[i], pts_flex[i+1]], fill=AMBER_ACCENT, width=3)

    draw_left(draw, bx0 + 460, by0 + 242, "AUDIO: 5kHz (SHATTER)", get_font(FONT_MONO, 22), CYAN_ACCENT)
    pts_audio = []
    for x in range(bx0 + 690, bx1 - 40, 4):
        rel_x = (x - (bx0 + 690)) * 0.40
        env = math.exp(-0.02 * (x - (bx0 + 690)) * 0.5)
        y = by0 + 256 + math.sin(rel_x) * 18.0 * env
        pts_audio.append((x, y))
    for i in range(len(pts_audio) - 1):
        draw.line([pts_audio[i], pts_audio[i+1]], fill=CYAN_ACCENT, width=3)

    # Status spec badge inside placard
    draw.rectangle([bx0 + 30, by0 + 320, bx1 - 30, by0 + 430], fill=PLATE_DARK_2, outline=(65, 78, 92, 255), width=2)
    draw_center(draw, fcx, by0 + 338, "EN 50131-2-7-1 GRADE 2  •  ENVIRONMENTAL CLASS II", get_font(FONT_MONO, 22), WHITE)
    draw_center(draw, fcx, by0 + 376, "OMNI-DIRECTIONAL ACOUSTIC DETECTION CONE", get_font(FONT_MONO, 21), CYAN_ACCENT)

    # 2. Mid Section: Status LED Frame and Legends (Mesh Z=+0.010m -> Y = 666 px)
    led_cy = 666
    # Left Label: [ PWR / ARMED ]
    draw.rectangle([fx0 + 24, led_cy - 48, fcx - 116, led_cy + 48], fill=BODY_BEVEL, outline=BODY_SHADOW, width=2)
    draw.ellipse([fx0 + 42, led_cy - 16, fx0 + 74, led_cy + 16], fill=GREEN_LED, outline=GREEN_DARK, width=3)
    draw_left(draw, fx0 + 90, led_cy - 20, "PWR / ARMED", get_font(FONT_MONO, 26), (15, 125, 45, 255))
    draw_left(draw, fx0 + 90, led_cy + 14, "NORMAL STANDBY", get_font(FONT_MONO, 20), INK_MUTED)

    # Right Label: [ ALARM / TEST ]
    draw.rectangle([fcx + 116, led_cy - 48, fx1 - 24, led_cy + 48], fill=BODY_BEVEL, outline=BODY_SHADOW, width=2)
    draw.ellipse([fcx + 134, led_cy - 16, fcx + 166, led_cy + 16], fill=RED_LED, outline=RED_DARK, width=3)
    draw_left(draw, fcx + 182, led_cy - 20, "ALARM / TEST", get_font(FONT_MONO, 26), (200, 25, 20, 255))
    draw_left(draw, fcx + 182, led_cy + 14, "EVENT LATCHED", get_font(FONT_MONO, 20), INK_MUTED)

    # Center LED mounting bezel graphic (exactly centered on 3D LED at Y = 666)
    draw.rectangle([fcx - 96, led_cy - 44, fcx + 96, led_cy + 44], fill=PLATE_DARK, outline=(80, 92, 105, 255), width=3)
    draw_center(draw, fcx, led_cy - 10, "- BI-COLOR LED -", get_font(FONT_MONO, 18), (160, 175, 190, 255))

    # 3. Test Button Marking (Centered at Y = 800)
    btn_cy = 800
    draw.ellipse([fcx - 52, btn_cy - 52, fcx + 52, btn_cy + 52], fill=BODY_BEVEL, outline=BODY_SHADOW, width=3)
    draw_center(draw, fcx, btn_cy - 24, "TEST", get_font(FONT_MONO, 24), INK_SOLID_BLACK)
    draw_center(draw, fcx, btn_cy + 6, "PUSH", get_font(FONT_MONO, 18), INK_MUTED)

    # 4. Lower Section: Microphone Port Surround (Mesh Z=-0.018m -> Y = 1147 px)
    m_ring_r = 180
    m_cy = 1147
    draw.ellipse([fcx - m_ring_r, m_cy - m_ring_r, fcx + m_ring_r, m_cy + m_ring_r], fill=BODY_BEVEL, outline=BODY_SHADOW, width=3)
    draw.ellipse([fcx - m_ring_r + 20, m_cy - m_ring_r + 20, fcx + m_ring_r - 20, m_cy + m_ring_r - 20], outline=(200, 210, 222, 255), width=2)

    # Surrounding bold text perfectly positioned above and below the 3D microphone
    draw_center(draw, fcx, m_cy - m_ring_r - 54, "ACOUSTIC SENSOR CHAMBER", get_font(FONT_MONO, 28), INK_SOLID_BLACK)
    draw_center(draw, fcx, m_cy + m_ring_r + 34, "MICRO-ELECTRET TRANSDUCER", get_font(FONT_MONO, 24), INK_DARK)

    # 5. Bottom Cover Release & Tamper Warning (Y: fy0 + 1480 .. fy0 + 1560)
    draw.rectangle([fx0 + 60, fy0 + 1480, fx1 - 60, fy0 + 1560], fill=BODY_BEVEL, outline=BODY_SHADOW, width=2)
    draw_center(draw, fcx, fy0 + 1496, "▼ PUSH TO RELEASE COVER", get_font(FONT_MONO, 22), INK_SOLID_BLACK)
    draw_center(draw, fcx, fy0 + 1526, "WALL & COVER TAMPER PROTECTED", get_font(FONT_MONO, 20), INK_MUTED)

    # =========================================================================
    # COLUMN 2: BACKPLATE REAR FACE ((1080, 48) -> (2000, 1640)) - Width: 920, Height: 1592
    # =========================================================================
    rx0, ry0, rx1, ry1 = 1080, 48, 2000, 1640
    rcx = (rx0 + rx1) / 2 # 1540

    draw.rectangle([rx0, ry0, rx1, ry1], fill=BODY_BEVEL)

    # Main dark specification label (with chamfered corners)
    lx0, ly0, lx1, ly1 = rx0 + 20, ry0 + 20, rx1 - 20, ry1 - 20
    draw.rectangle([lx0, ly0, lx1, ly1], fill=PLATE_DARK, outline=(75, 88, 102, 255), width=3)
    draw.rectangle([lx0 + 4, ly0 + 4, lx1 - 4, ly0 + 14], fill=AMBER_ACCENT)

    # Header
    draw_center(draw, rcx, ly0 + 28, "SEC-GBD 300 PRO SPECIFICATIONS", get_font(FONT_SANS, 40), WHITE)
    draw_center(draw, rcx, ly0 + 80, "EN 50131-2-7-1 GRADE 2  •  CLASS II  •  IP31", get_font(FONT_MONO, 24), CYAN_ACCENT)

    # Keyhole screw mount top guide
    draw.ellipse([rcx - 28, ly0 + 120, rcx + 28, ly0 + 176], fill=PLATE_DARK_2, outline=(90, 105, 120, 255), width=2)
    draw.line([(rcx, ly0 + 110), (rcx, ly0 + 186)], fill=AMBER_ACCENT, width=2)
    draw.line([(rcx - 38, ly0 + 148), (rcx + 38, ly0 + 148)], fill=AMBER_ACCENT, width=2)
    draw_center(draw, rcx, ly0 + 184, "⌖ WALL MOUNT KEYHOLE (TOP)", get_font(FONT_MONO, 20), INK_LIGHT)

    # Technical Specs Grid (ly0 + 230 .. ly0 + 540)
    f_spec = get_font(FONT_MONO, 22)
    specs = [
        ("OPERATING VOLTAGE:", "9.0 - 16.0V DC (NOMINAL 12V DC)"),
        ("CURRENT CONSUMPTION:", "18mA STANDBY / 32mA ALARM"),
        ("ALARM RELAY OUTPUT:", "FORM A (NC) SOLID-STATE 30V 100mA"),
        ("TAMPER SWITCH:", "NC COVER & WALL SWITCH 24V 50mA"),
        ("DETECTION COVERAGE:", "RADIUS: 9.0M (30FT)  •  360° CONE"),
        ("GLASS TYPES:", "PLATE, TEMPERED, LAMINATED, WIRE"),
        ("SERIAL / BATCH NO:", "GBD-2026-8841-B  •  REV: 2.4")
    ]
    for idx, (label, val) in enumerate(specs):
        yy = ly0 + 230 + idx * 34
        draw_left(draw, lx0 + 36, yy, label, f_spec, (170, 185, 200, 255))
        draw_left(draw, lx0 + 310, yy, val, f_spec, WHITE if idx % 2 == 0 else (225, 238, 250, 255))

    # Cable knockout entry guide (Center)
    draw.ellipse([rcx - 64, ly0 + 490, rcx + 64, ly0 + 618], fill=PLATE_DARK_2, outline=AMBER_ACCENT, width=2)
    draw.ellipse([rcx - 44, ly0 + 510, rcx + 44, ly0 + 598], outline=(85, 98, 112, 255), width=2)
    draw.line([(rcx, ly0 + 480), (rcx, ly0 + 628)], fill=AMBER_ACCENT, width=2)
    draw.line([(rcx - 74, ly0 + 554), (rcx + 74, ly0 + 554)], fill=AMBER_ACCENT, width=2)
    draw_center(draw, rcx, ly0 + 632, "⌖ CABLE INLET KNOCKOUT Ø 16mm", get_font(FONT_MONO, 20), INK_LIGHT)

    # Barcode
    draw_barcode(draw, lx0 + 70, ly0 + 680, 740, 96)
    draw_center(draw, rcx, ly0 + 788, "*GBD20268841B*", get_font(FONT_MONO, 24), (190, 205, 220, 255))

    # Compliance badges
    badges = ["CE", "FCC", "RoHS", "UKCA", "WEEE"]
    for i, b in enumerate(badges):
        bx = lx0 + 80 + i * 148
        draw.rectangle([bx, ly0 + 836, bx + 128, ly0 + 884], outline=(110, 128, 145, 255), width=2)
        draw_center(draw, bx + 64, ly0 + 848, b, get_font(FONT_SANS, 22), (210, 225, 240, 255))

    # Professional 7-Pole Terminal Block Wiring Guide (ly0 + 920 .. ly0 + 1360)
    tx0, ty0, tx1, ty1 = lx0 + 30, ly0 + 920, lx1 - 30, ly0 + 1360
    draw.rectangle([tx0, ty0, tx1, ty1], fill=(12, 16, 20, 255), outline=(60, 72, 85, 255), width=2)
    draw_left(draw, tx0 + 30, ty0 + 20, "FIELD TERMINAL WIRING CONNECTIONS:", get_font(FONT_MONO, 26), CYAN_ACCENT)

    terminals = [
        ("+12V",  "PWR +",   (225, 55, 45, 255)),
        ("GND",   "PWR -",   (45, 45, 45, 255)),
        ("ALM",   "RELAY NC",(225, 170, 30, 255)),
        ("ALM",   "RELAY C", (225, 170, 30, 255)),
        ("TMP",   "TAMPER",  (40, 160, 230, 255)),
        ("TMP",   "TAMPER",  (40, 160, 230, 255)),
        ("EOL",   "RESISTOR",(130, 142, 155, 255))
    ]
    t_width = (tx1 - tx0 - 60) / len(terminals)
    for i, (name, role, tag_col) in enumerate(terminals):
        bx = tx0 + 30 + i * t_width
        by = ty0 + 70
        # Individual terminal box
        draw.rectangle([bx + 4, by, bx + t_width - 12, by + 320], fill=PLATE_DARK_2, outline=(70, 82, 95, 255), width=2)
        # Terminal color tag
        draw.rectangle([bx + 8, by + 4, bx + t_width - 16, by + 16], fill=tag_col)
        # Screw head graphic
        scx = bx + 4 + (t_width - 16) / 2
        scy = by + 70
        draw.ellipse([scx - 28, scy - 28, scx + 28, scy + 28], fill=(185, 195, 208, 255), outline=(80, 92, 105, 255), width=2)
        draw.line([(scx - 20, scy), (scx + 20, scy)], fill=(45, 50, 58, 255), width=4)
        # Terminal Name
        draw_center(draw, scx, by + 130, name, get_font(FONT_MONO, 24), WHITE)
        # Terminal Role
        draw_center(draw, scx, by + 180, role, get_font(FONT_MONO, 18), (170, 185, 200, 255))
        # Wire insertion port
        draw.rectangle([scx - 20, by + 250, scx + 20, by + 296], fill=(10, 12, 15, 255), outline=(55, 68, 80, 255), width=2)

    # Keyhole screw mount bottom guide
    draw.ellipse([rcx - 28, ly1 - 140, rcx + 28, ly1 - 84], fill=PLATE_DARK_2, outline=(90, 105, 120, 255), width=2)
    draw.line([(rcx, ly1 - 150), (rcx, ly1 - 74)], fill=AMBER_ACCENT, width=2)
    draw.line([(rcx - 38, ly1 - 112), (rcx + 38, ly1 - 112)], fill=AMBER_ACCENT, width=2)
    draw_center(draw, rcx, ly1 - 76, "⌖ WALL MOUNT SCREW (BOTTOM)", get_font(FONT_MONO, 20), INK_LIGHT)

    # =========================================================================
    # ROW 3: DETAIL & TEXTURE STRIP (Y: 1680 -> 2008)
    # =========================================================================
    # 1. Acoustic Microphone Grille: (48, 1680, 408, 2000) -> 360 x 320 px
    draw.rectangle([48, 1680, 408, 2000], fill=(10, 12, 15, 255))
    mcx, mcy = 228, 1840
    mr = 140
    draw.ellipse([mcx - mr, mcy - mr, mcx + mr, mcy + mr], fill=(28, 34, 42, 255), outline=(85, 98, 114, 255), width=5)
    draw.ellipse([mcx - mr + 24, mcy - mr + 24, mcx + mr - 24, mcy + mr - 24], fill=(18, 22, 28, 255), outline=(50, 62, 75, 255), width=3)
    # Concentric rings & mesh
    for rad in range(30, mr - 30, 20):
        draw.ellipse([mcx - rad, mcy - rad, mcx + rad, mcy + rad], outline=(45, 55, 68, 255), width=2)
    for a in range(0, 360, 15):
        ar = math.radians(a)
        draw.line([(mcx, mcy), (mcx + math.cos(ar) * (mr - 32), mcy + math.sin(ar) * (mr - 32))], fill=(42, 50, 62, 255), width=2)
    # Electret capsule
    draw.ellipse([mcx - 44, mcy - 44, mcx + 44, mcy + 44], fill=(8, 10, 12, 255), outline=CYAN_ACCENT, width=2)
    draw.ellipse([mcx - 20, mcy - 20, mcx + 20, mcy + 20], fill=(2, 3, 4, 255))
    draw_center(draw, mcx, mcy + mr - 24, "MIC CAPSULE", get_font(FONT_MONO, 18), (145, 160, 175, 255))

    # 2. Bi-Color LED Lens: (448, 1680, 788, 2000) -> 340 x 320 px
    draw.rectangle([448, 1680, 788, 2000], fill=PLATE_DARK, outline=(75, 88, 100, 255), width=3)
    draw_center(draw, 618, 1692, "STATUS LENS", get_font(FONT_MONO, 20), INK_LIGHT)
    # Green half (Left)
    draw.rectangle([472, 1736, 608, 1964], fill=(25, 165, 55, 255), outline=GREEN_LED, width=3)
    draw.ellipse([492, 1780, 588, 1920], fill=(80, 245, 125, 255))
    draw_center(draw, 540, 1932, "PWR", get_font(FONT_MONO, 20), WHITE)
    # Red half (Right)
    draw.rectangle([628, 1736, 764, 1964], fill=(185, 30, 25, 255), outline=RED_LED, width=3)
    draw.ellipse([648, 1780, 744, 1920], fill=(255, 105, 95, 255))
    draw_center(draw, 696, 1932, "ALM", get_font(FONT_MONO, 20), WHITE)

    # 3. Neutral Body White: (840, 1680, 1100, 2000)
    draw.rectangle([840, 1680, 1100, 2000], fill=BODY_WHITE, outline=BODY_SHADOW, width=2)
    draw_center(draw, 970, 1830, "BODY WHITE", get_font(FONT_MONO, 20), INK_MUTED)

    # 4. Neutral Bevel Tone: (1140, 1680, 1400, 2000)
    draw.rectangle([1140, 1680, 1400, 2000], fill=BODY_BEVEL, outline=BODY_SHADOW, width=2)
    draw_center(draw, 1270, 1830, "BEVEL TONE", get_font(FONT_MONO, 20), INK_MUTED)

    # 5. Neutral Dark Slate: (1440, 1680, 1700, 2000)
    draw.rectangle([1440, 1680, 1700, 2000], fill=PLATE_DARK, outline=(55, 65, 75, 255), width=2)
    draw_center(draw, 1570, 1830, "DARK SLATE", get_font(FONT_MONO, 20), WHITE)

    # 6. Neutral Metal: (1740, 1680, 2000, 2000)
    draw.rectangle([1740, 1680, 2000, 2000], fill=(195, 204, 215, 255), outline=(130, 140, 155, 255), width=2)
    draw.ellipse([1790, 1750, 1950, 1910], fill=(160, 172, 185, 255))
    draw_center(draw, 1870, 1830, "METAL", get_font(FONT_MONO, 20), INK_DARK)

    img.save(ATLAS_PATH, "PNG")
    print(f"[OK] Ultra-High Resolution (2048x2048) Texture Atlas saved: {ATLAS_PATH}")

if __name__ == "__main__":
    generate_textures()
