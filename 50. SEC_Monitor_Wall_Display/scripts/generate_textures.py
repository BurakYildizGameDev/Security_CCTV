"""
=============================================================================
Security CCTV Asset Production Suite - Asset 50
Asset Name: SEC_Monitor_Wall_Display (Duvar Tipi Buyuk Guvenlik Ekrani)
Texture Generation Script v3 (Ultra-Crisp Bezel Typography & High-Detail Screen)
=============================================================================
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")
SCREEN_PATH = os.path.join(EXPORTS_DIR, "T_Screen.png")

FONT_MONO = r"C:\Windows\Fonts\consolab.ttf"
FONT_SANS = r"C:\Windows\Fonts\arialbd.ttf"

ATLAS_W, ATLAS_H = 2048, 2048

REGION_BEZEL = (64, 64, 1984, 256)
REGION_HOUSING_REAR = (64, 340, 1280, 1180)
REGION_VESA_BRACKET = (1340, 340, 1984, 1020)
REGION_SWATCHES = (1340, 1080, 2016, 2016)

# High contrast colors
CHASSIS_DARK = (16, 18, 22, 255)
CHASSIS_MID = (30, 34, 40, 255)
CHASSIS_LIGHT = (65, 72, 82, 255)
STEEL_BRACKET = (175, 182, 192, 255)
WHITE = (255, 255, 255, 255)
INK_TEXT = (235, 240, 248, 255)
INK_SOFT = (165, 175, 190, 255)
ACCENT_BLUE = (40, 145, 245, 255)
ACCENT_GREEN = (45, 220, 85, 255)
ACCENT_RED = (240, 45, 35, 255)
ACCENT_AMBER = (255, 170, 20, 255)

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

def draw_center_ink(draw, cx, cy, text, font, fill):
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = cx - w // 2 - bbox[0]
    y = cy - h // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=fill)

def draw_left_ink(draw, x, cy, text, font, fill):
    bbox = font.getbbox(text)
    h = bbox[3] - bbox[1]
    y = cy - h // 2 - bbox[1]
    draw.text((x - bbox[0], y), text, font=font, fill=fill)

def build_atlas():
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), (14, 16, 20, 255))
    draw = ImageDraw.Draw(img)

    # 1. Swatches
    sx0, sy0, sx1, sy1 = REGION_SWATCHES
    draw.rectangle([sx0, sy0, sx1, sy1], fill=CHASSIS_DARK)
    draw.rectangle([sx0 + 20, sy0 + 20, sx1 - 20, sy0 + 200], fill=CHASSIS_MID)
    draw.rectangle([sx0 + 20, sy0 + 220, sx1 - 20, sy0 + 400], fill=CHASSIS_LIGHT)
    draw.rectangle([sx0 + 20, sy0 + 420, sx1 - 20, sy0 + 600], fill=STEEL_BRACKET)
    draw.rectangle([sx0 + 20, sy0 + 620, sx1 - 20, sy1 - 20], fill=(10, 12, 14, 255))

    # 2. FRONT BEZEL (1920 x 192) - Razor-sharp, high-contrast, industrial commercial monitor chin
    bx0, by0, bx1, by1 = REGION_BEZEL
    draw.rectangle([bx0, by0, bx1, by1], fill=(20, 23, 28, 255))
    draw.rectangle([bx0, by0, bx1, by1], outline=(10, 12, 16, 255), width=3)
    # Accent top highlight chamfer
    draw.line([(bx0, by0 + 4), (bx1, by0 + 4)], fill=(45, 52, 64, 255), width=2)
    draw.line([(bx0, by1 - 4), (bx1, by1 - 4)], fill=(30, 35, 42, 255), width=2)

    bcy = (by0 + by1) // 2
    bcx = (bx0 + bx1) // 2

    f_logo = load_font(FONT_SANS, 26)
    f_badge = load_font(FONT_MONO, 18)
    f_small = load_font(FONT_MONO, 13)
    f_btn = load_font(FONT_MONO, 14)

    # Center Brand Logo (Large, razor-sharp pure white)
    draw_center_ink(draw, bcx, bcy, "SEC-VISION 5000 PRO 4K  •  COMMERCIAL SECURITY MONITOR", f_logo, WHITE)

    # Left Model Badge Box
    draw.rectangle([bx0 + 60, bcy - 24, bx0 + 380, bcy + 24], fill=(12, 15, 18, 255), outline=(50, 58, 70, 255), width=2)
    draw_left_ink(draw, bx0 + 75, bcy - 8, "MODEL: SEC-MON50-4K", f_badge, INK_TEXT)
    draw_left_ink(draw, bx0 + 75, bcy + 12, "QUAD 4K PROCESSOR / 24/7 CCTV", f_small, (70, 180, 250, 255))

    # Right Side Controls & Status Cluster
    rx = bx1 - 480

    # Tactile OSD Buttons Silk-Screen
    btn_labels = ["MENU", "▲", "▼", "INPUT", "PWR"]
    for bi, bl in enumerate(btn_labels):
        bx_pos = rx + bi * 55
        draw.rectangle([bx_pos, bcy - 16, bx_pos + 46, bcy + 16], fill=(28, 32, 40, 255), outline=(55, 62, 75, 255), width=1)
        col_btn = ACCENT_RED if bl == "PWR" else INK_TEXT
        draw_center_ink(draw, bx_pos + 23, bcy, bl, f_btn, col_btn)

    # Status LEDs: PWR (Green), REC (Red)
    led_x = rx + len(btn_labels) * 55 + 20
    draw.ellipse([led_x, bcy - 8, led_x + 16, bcy + 8], fill=ACCENT_GREEN, outline=(10, 80, 25, 255), width=2)
    draw_left_ink(draw, led_x + 22, bcy, "PWR", f_small, ACCENT_GREEN)

    draw.ellipse([led_x + 65, bcy - 8, led_x + 81, bcy + 8], fill=ACCENT_RED, outline=(120, 20, 15, 255), width=2)
    draw_left_ink(draw, led_x + 87, bcy, "REC", f_small, ACCENT_RED)

    # IR Receiver Eye
    ir_x = led_x + 145
    draw.ellipse([ir_x, bcy - 10, ir_x + 20, bcy + 10], fill=(8, 10, 12, 255), outline=CHASSIS_LIGHT, width=2)
    draw_left_ink(draw, ir_x + 26, bcy, "IR", f_small, INK_SOFT)

    # 3. REAR HOUSING & SPECIFICATION PLATE (1216 x 840)
    hx0, hy0, hx1, hy1 = REGION_HOUSING_REAR
    draw.rectangle([hx0, hy0, hx1, hy1], fill=CHASSIS_MID)
    draw.rectangle([hx0 + 10, hy0 + 10, hx1 - 10, hy1 - 10], outline=(15, 17, 20, 255), width=4)

    lx0, ly0, lx1, ly1 = hx0 + 40, hy0 + 40, hx1 - 40, hy1 - 40
    draw.rectangle([lx0, ly0, lx1, ly1], fill=(242, 245, 250, 255), outline=(40, 45, 55, 255), width=3)

    lcx = (lx0 + lx1) // 2
    f_spec_h1 = load_font(FONT_SANS, 34)
    f_spec_h2 = load_font(FONT_MONO, 22)
    f_spec_body = load_font(FONT_MONO, 18)

    draw_center_ink(draw, lcx, ly0 + 35, "SEC-VISION INDUSTRIAL DISPLAY SYSTEMS", f_spec_h1, (20, 24, 30, 255))
    draw_center_ink(draw, lcx, ly0 + 75, "PROFESSIONAL CCTV SECURITY VIDEO MONITOR", f_spec_h2, (40, 48, 60, 255))
    draw.line([lx0 + 30, ly0 + 105, lx1 - 30, ly0 + 105], fill=(30, 35, 45, 255), width=2)

    specs = [
        "MODEL NUMBER   : SEC-MON50-4K-UHD",
        "PANEL TYPE     : 50-INCH IPS COMMERCIAL LCD (3840 x 2160 UHD)",
        "POWER INPUT    : 100 - 240 V ~ 50/60 Hz  1.8A MAX (140W)",
        "VIDEO INPUTS   : 2x HDMI 2.0, 1x DP 1.4, 2x BNC IN/OUT (AHD/TVI)",
        "CONTROL PORTS  : RS-232 IN/OUT, RS-485, RJ-45 GIGABIT LAN",
        "VESA MOUNT     : 400 x 400 mm / 200 x 200 mm M6 BOLTS",
        "COMPLIANCE     : CE, FCC CLASS-A, UL 62368-1, CB, ROHS, IP40",
        "SERIAL NUMBER  : SN-MON50-202688194-PRO"
    ]
    cur_y = ly0 + 135
    for s in specs:
        draw_left_ink(draw, lx0 + 50, cur_y, s, f_spec_body, (25, 30, 38, 255))
        cur_y += 32

    # Barcode
    draw.line([lx0 + 50, cur_y + 10, lx1 - 50, cur_y + 10], fill=(200, 205, 215, 255), width=1)
    bx_s = lx0 + 100
    for i in range(120):
        w_b = 2 if (i % 3 == 0 or i % 7 == 0) else 4
        draw.line([bx_s + i * 8, cur_y + 25, bx_s + i * 8, cur_y + 75], fill=(20, 24, 30, 255), width=w_b)
    draw_center_ink(draw, lcx, cur_y + 92, "*SEC50MON-2026-X88*", f_spec_body, (30, 35, 45, 255))

    # 4. VESA TILT BRACKET (644 x 680)
    vx0, vy0, vx1, vy1 = REGION_VESA_BRACKET
    draw.rectangle([vx0, vy0, vx1, vy1], fill=CHASSIS_MID)
    draw.rectangle([vx0 + 10, vy0 + 10, vx1 - 10, vy1 - 10], fill=(235, 238, 244, 255), outline=(50, 55, 65, 255), width=3)
    vcx = (vx0 + vx1) // 2
    draw_center_ink(draw, vcx, vy0 + 40, "HEAVY-DUTY VESA TILT MOUNT", f_badge, (20, 25, 35, 255))
    draw_center_ink(draw, vcx, vy0 + 70, "ADJUSTABLE DUAL ARM [±10° TILT]", f_small, (50, 60, 75, 255))

    img.save(ATLAS_PATH, "PNG")
    print(f"Atlas texture generated: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

def build_screen_feed():
    """Generates photorealistic, highly detailed 1920x1080 4-channel Quad CCTV screen feed."""
    sw, sh = 1920, 1080
    img = Image.new("RGBA", (sw, sh), (8, 10, 14, 255))
    draw = ImageDraw.Draw(img)

    f_cam = load_font(FONT_MONO, 26)
    f_hud = load_font(FONT_MONO, 20)
    f_tag = load_font(FONT_MONO, 16)
    f_clock = load_font(FONT_MONO, 22)

    quads = [
        ((4, 4, 956, 536), "CAM 01 - MAIN ENTRANCE / ANPR", (20, 32, 42, 255), "PLATE: [34 SEC 759] MATCHED (ALLOWED)"),
        ((964, 4, 1916, 536), "CAM 02 - PERIMETER FENCE (IR NIGHT)", (14, 26, 20, 255), "IR 850nm ACTIVE  |  FENCE SENSOR: NORMAL"),
        ((4, 544, 956, 1076), "CAM 03 - SERVER ROOM RACK AISLE", (18, 20, 32, 255), "TEMP: 19.8°C  |  HUM: 44%  |  RACK LOCK: ENGAGED"),
        ((964, 544, 1916, 1076), "CAM 04 - LOADING DOCK / CARGO", (28, 26, 22, 255), "MOTION DETECTION: SECTOR 2 ARMED (NO INTRUSION)")
    ]

    for (x0, y0, x1, y1), title, bg_col, sub_info in quads:
        draw.rectangle([x0, y0, x1, y1], fill=bg_col)
        
        # Grid scanlines
        for y in range(y0 + 50, y1 - 40, 6):
            draw.line([x0, y, x1, y], fill=(0, 0, 0, 45), width=1)
        
        # Quadrant border
        draw.rectangle([x0, y0, x1, y1], outline=(40, 55, 75, 255), width=3)

        # Header bar
        draw.rectangle([x0, y0, x1, y0 + 44], fill=(12, 15, 20, 240))
        draw_left_ink(draw, x0 + 18, y0 + 22, title, f_cam, WHITE)
        
        # LIVE & REC badge
        draw.ellipse([x1 - 130, y0 + 14, x1 - 112, y0 + 32], fill=ACCENT_RED)
        draw_left_ink(draw, x1 - 105, y0 + 22, "LIVE", f_cam, ACCENT_RED)

        # Center target reticle & detailed graphic overlays
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2

        if "CAM 01" in title:
            # Vehicle ANPR Wireframe Bounding Box
            draw.rectangle([cx - 150, cy - 80, cx + 150, cy + 80], outline=(45, 210, 100, 220), width=2)
            for c_x, c_y in [(cx-150, cy-80), (cx+150, cy-80), (cx-150, cy+80), (cx+150, cy+80)]:
                draw.rectangle([c_x-4, c_y-4, c_x+4, c_y+4], fill=(45, 210, 100, 255))
            draw_left_ink(draw, cx - 140, cy - 65, "AI DETECT: VEHICLE [SEDAN] - SPEED: 24 km/h", f_tag, (45, 210, 100, 255))
            draw_left_ink(draw, cx - 140, cy + 60, "CONFIDENCE: 98.4%  |  ACCESS: AUTHORIZED", f_tag, WHITE)
            draw.line([cx - 25, cy, cx + 25, cy], fill=(60, 180, 250, 180), width=2)
            draw.line([cx, cy - 25, cx, cy + 25], fill=(60, 180, 250, 180), width=2)

        elif "CAM 02" in title:
            # Perimeter Fence lines representation
            for fx in range(x0 + 80, x1 - 80, 90):
                draw.line([fx, y1 - 40, fx, cy - 40], fill=(30, 80, 50, 180), width=2)
            draw.line([x0 + 50, cy + 40, x1 - 50, cy + 40], fill=(40, 120, 70, 200), width=2)
            draw.line([x0 + 50, cy - 20, x1 - 50, cy - 20], fill=(40, 120, 70, 200), width=2)
            draw.arc([cx - 90, cy - 90, cx + 90, cy + 90], start=210, end=330, fill=ACCENT_GREEN, width=2)
            draw_left_ink(draw, cx - 110, cy - 60, "[NIGHT VISION THERMAL IR ON]", f_tag, ACCENT_GREEN)
            draw_left_ink(draw, cx - 110, cy + 60, "PERIMETER FENCE: NO BREACH", f_tag, INK_TEXT)

        elif "CAM 03" in title:
            # Server Room Rack outline
            for rx_offset in [-200, -60, 80, 220]:
                rcx = cx + rx_offset
                draw.rectangle([rcx - 50, cy - 100, rcx + 50, cy + 90], outline=(60, 75, 110, 200), width=2)
                for ry in range(cy - 80, cy + 80, 20):
                    draw.ellipse([rcx - 40, ry, rcx - 32, ry + 8], fill=ACCENT_GREEN)
                    draw.ellipse([rcx - 26, ry, rcx - 18, ry + 8], fill=ACCENT_BLUE)
            draw_left_ink(draw, cx - 140, cy - 115, "SERVER RACKS AISLE B2-B6", f_tag, ACCENT_BLUE)
            draw_left_ink(draw, cx - 140, cy + 105, "FIRE SUPPRESSION SYSTEM: STANDBY [OK]", f_tag, INK_TEXT)

        else: # CAM 04
            # Cargo Dock loading lines
            for lx in range(x0 + 60, x1 - 60, 40):
                draw.line([lx, y1 - 40, lx + 25, y1 - 65], fill=(220, 180, 30, 140), width=3)
            draw.rectangle([cx - 120, cy - 50, cx + 120, cy + 50], outline=(240, 180, 20, 200), width=2)
            draw_left_ink(draw, cx - 110, cy - 35, "LOADING BAY 03 [ACTIVE SECTOR]", f_tag, ACCENT_AMBER)
            draw_left_ink(draw, cx - 110, cy + 35, "CARGO FORKLIFT DETECTOR: STANDBY", f_tag, WHITE)

        # Bottom info bar
        draw.rectangle([x0, y1 - 42, x1, y1], fill=(12, 15, 20, 240))
        draw_left_ink(draw, x0 + 18, y1 - 21, "2026-10-31  04:36:50 UTC", f_clock, INK_TEXT)
        draw_left_ink(draw, x0 + 380, y1 - 21, sub_info, f_hud, ACCENT_GREEN)

    # Center Quad Split Cross Divider
    draw.line([960, 0, 960, sh], fill=(25, 30, 40, 255), width=8)
    draw.line([0, 540, sw, 540], fill=(25, 30, 40, 255), width=8)
    draw.ellipse([960 - 16, 540 - 16, 960 + 16, 540 + 16], fill=(15, 18, 25, 255), outline=ACCENT_BLUE, width=2)

    img.save(SCREEN_PATH, "PNG")
    print(f"Screen feed texture generated: {SCREEN_PATH} ({sw}x{sh})")

if __name__ == "__main__":
    build_atlas()
    build_screen_feed()
