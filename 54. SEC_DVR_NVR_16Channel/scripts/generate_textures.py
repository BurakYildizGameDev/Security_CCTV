"""
=============================================================================
Security CCTV Asset Production Suite - Asset 54
Asset Name: SEC_DVR_NVR_16Channel (16 Kanalli NVR Kayit Cihazi)
Texture Atlas & VFD Screen Generator
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

# Color Palette
CHASSIS_BLACK = (20, 22, 26, 255)
FRONT_FASCIA = (28, 32, 40, 255)
STEEL_METAL = (160, 170, 182, 255)
LED_GREEN = (40, 230, 80, 255)
LED_RED = (235, 45, 35, 255)
LED_AMBER = (245, 175, 20, 255)
LED_BLUE = (35, 145, 245, 255)
WHITE = (255, 255, 255, 255)
INK_TEXT = (220, 228, 238, 255)
INK_SOFT = (145, 155, 170, 255)

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

def draw_center_text(draw, cx, cy, text, font, fill):
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = cx - w // 2 - bbox[0]
    y = cy - h // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=fill)

def generate_atlas():
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), CHASSIS_BLACK)
    draw = ImageDraw.Draw(img)

    # =========================================================================
    # 1. FRONT 2U FASCIA PANEL (20..1960, 20..380)
    # Dimensions match 482.6mm x 88.0mm (approx 5.5 : 1)
    # =========================================================================
    fx0, fy0, fx1, fy1 = 20, 20, 1960, 360
    draw.rectangle([fx0, fy0, fx1, fy1], fill=FRONT_FASCIA, outline=(55, 62, 75, 255), width=2)
    draw.line([(fx0 + 4, fy0 + 4), (fx1 - 4, fy0 + 4)], fill=(75, 85, 100, 255), width=2)
    draw.line([(fx0 + 4, fy1 - 4), (fx1 - 4, fy1 - 4)], fill=(15, 18, 22, 255), width=2)

    # Rack Mount Ears: Left & Right with mounting screw slots
    for rx in [fx0 + 40, fx1 - 40]:
        draw.rounded_rectangle([rx - 15, fy0 + 30, rx + 15, fy0 + 80], radius=8, fill=(12, 14, 16, 255), outline=STEEL_METAL, width=2)
        draw.rounded_rectangle([rx - 15, fy1 - 80, rx + 15, fy1 - 30], radius=8, fill=(12, 14, 16, 255), outline=STEEL_METAL, width=2)

    # Left Section: Brand Logo & Model Info
    draw.text((fx0 + 110, fy0 + 40), "SEC-VISION", fill=WHITE, font=load_font(FONT_SANS, 26))
    draw.text((fx0 + 110, fy0 + 78), "16-CHANNEL 4K NETWORK VIDEO RECORDER  |  MODEL NVR-1600-PRO", fill=INK_SOFT, font=load_font(FONT_MONO, 14))
    draw.text((fx0 + 110, fy0 + 102), "H.265+ AI SURVEILLANCE  •  RAID 5 / HOT SWAP DUAL GBE", fill=(45, 190, 240, 255), font=load_font(FONT_MONO, 12))

    # Power & System Status Cluster (Near Power Button)
    draw.ellipse([fx0 + 115, fy0 + 160, fx0 + 130, fy0 + 175], fill=LED_GREEN)
    draw.text((fx0 + 140, fy0 + 158), "PWR", fill=WHITE, font=load_font(FONT_MONO, 13))

    draw.ellipse([fx0 + 200, fy0 + 160, fx0 + 215, fy0 + 175], fill=LED_BLUE)
    draw.text((fx0 + 225, fy0 + 158), "NET", fill=WHITE, font=load_font(FONT_MONO, 13))

    draw.ellipse([fx0 + 285, fy0 + 160, fx0 + 300, fy0 + 175], fill=LED_GREEN)
    draw.text((fx0 + 310, fy0 + 158), "HDD", fill=WHITE, font=load_font(FONT_MONO, 13))

    draw.ellipse([fx0 + 370, fy0 + 160, fx0 + 385, fy0 + 175], fill=LED_AMBER)
    draw.text((fx0 + 395, fy0 + 158), "ALM", fill=WHITE, font=load_font(FONT_MONO, 13))

    # Center Screen Bezel Cutout (Inner Pure Black Cavity where 3D Display sits)
    # Screen opening matches X: -0.060..0.060 (W=0.120m), Z: -0.015..0.015 (H=0.030m)
    # On texture: sx0 = 760, sx1 = 1220, sy0 = 80, sy1 = 260
    draw.rounded_rectangle([760, 80, 1220, 260], radius=6, fill=(8, 10, 14, 255), outline=(50, 58, 70, 255), width=2)

    # 16 Channel LED Status Array Recess (Right of Screen)
    # 2 rows of 8 channels: CH 1..8 and CH 9..16
    draw.rounded_rectangle([1260, 60, 1720, 280], radius=8, fill=(16, 18, 22, 255), outline=(45, 52, 65, 255), width=1)
    draw.text((1280, 75), "CHANNEL STATUS [1 - 16]:", fill=INK_TEXT, font=load_font(FONT_MONO, 13))
    
    for row in range(2):
        for col in range(8):
            ch_num = row * 8 + col + 1
            lx = 1285 + col * 52
            ly = 110 + row * 65
            # LED diode
            draw.ellipse([lx, ly, lx + 16, ly + 16], fill=LED_GREEN)
            draw_center_text(draw, lx + 8, ly + 32, f"{ch_num:02d}", load_font(FONT_MONO, 11), INK_SOFT)

    # Front USB Ports & Backup Slot (Bottom Right)
    draw.rounded_rectangle([1750, 90, 1900, 270], radius=6, fill=(14, 16, 20, 255), outline=(48, 55, 68, 255), width=1)
    draw.text((1765, 105), "USB 3.0", fill=WHITE, font=load_font(FONT_MONO, 12))
    draw.rectangle([1775, 135, 1875, 165], fill=(22, 26, 32, 255), outline=STEEL_METAL, width=2)
    draw.text((1765, 185), "BACKUP", fill=WHITE, font=load_font(FONT_MONO, 12))
    draw.rectangle([1775, 215, 1875, 245], fill=(22, 26, 32, 255), outline=STEEL_METAL, width=2)

    # =========================================================================
    # 2. POWER BUTTON CAP TEXTURE (120..280, 420..540)
    # =========================================================================
    draw.rounded_rectangle([120, 420, 280, 540], radius=12, fill=(35, 40, 50, 255), outline=(75, 88, 110, 255), width=3)
    # Standby Power Symbol
    draw.ellipse([175, 450, 225, 500], outline=WHITE, width=4)
    draw.rectangle([197, 442, 203, 475], fill=(35, 40, 50, 255))
    draw.line([(200, 440), (200, 470)], fill=WHITE, width=4)

    # =========================================================================
    # 3. REAR CHASSIS I/O PANEL (20..1960, 600..1020)
    # BNC Ports (16x), HDMI, VGA, LAN1/2, Audio, RS-485, AC Power Inlet
    # =========================================================================
    rx0, ry0, rx1, ry1 = 20, 600, 1960, 1000
    draw.rectangle([rx0, ry0, rx1, ry1], fill=(24, 27, 32, 255), outline=(50, 56, 68, 255), width=2)
    
    # 16x BNC Video Input Connectors (2 rows of 8)
    draw.text((rx0 + 40, ry0 + 30), "VIDEO IN (1 - 16 CH COMPOSITE / HD-TVI / AHD / CVI)", fill=WHITE, font=load_font(FONT_MONO, 14))
    for r in range(2):
        for c in range(8):
            bx = rx0 + 50 + c * 85
            by = ry0 + 70 + r * 80
            draw.ellipse([bx, by, bx + 55, by + 55], fill=(38, 42, 50, 255), outline=STEEL_METAL, width=3)
            draw.ellipse([bx + 18, by + 18, bx + 37, by + 37], fill=(12, 14, 16, 255), outline=(220, 180, 50, 255), width=2)
            draw.ellipse([bx + 25, by + 25, bx + 30, by + 30], fill=WHITE)

    # Network, Video Out, Audio, Alarm Terminal
    draw.text((rx0 + 780, ry0 + 30), "HDMI / VGA OUT  |  AUDIO IN/OUT  |  DUAL GIGABIT LAN", fill=WHITE, font=load_font(FONT_MONO, 14))
    draw.rectangle([rx0 + 780, ry0 + 70, rx0 + 860, ry0 + 130], fill=(15, 18, 22, 255), outline=STEEL_METAL, width=2)
    draw_center_text(draw, rx0 + 820, ry0 + 100, "HDMI", load_font(FONT_MONO, 12), INK_TEXT)
    
    draw.rectangle([rx0 + 880, ry0 + 70, rx0 + 960, ry0 + 130], fill=(20, 35, 75, 255), outline=STEEL_METAL, width=2)
    draw_center_text(draw, rx0 + 920, ry0 + 100, "VGA", load_font(FONT_MONO, 12), INK_TEXT)

    draw.rectangle([rx0 + 990, ry0 + 70, rx0 + 1070, ry0 + 130], fill=(15, 18, 22, 255), outline=STEEL_METAL, width=2)
    draw_center_text(draw, rx0 + 1030, ry0 + 100, "LAN 1", load_font(FONT_MONO, 12), INK_TEXT)

    draw.rectangle([rx0 + 1090, ry0 + 70, rx0 + 1170, ry0 + 130], fill=(15, 18, 22, 255), outline=STEEL_METAL, width=2)
    draw_center_text(draw, rx0 + 1130, ry0 + 100, "LAN 2", load_font(FONT_MONO, 12), INK_TEXT)

    # Power Inlet 100-240V AC
    px0 = rx1 - 320
    draw.rectangle([px0, ry0 + 60, rx1 - 40, ry0 + 200], fill=(12, 14, 18, 255), outline=(55, 62, 75, 255), width=2)
    draw.text((px0 + 20, ry0 + 75), "POWER INLET: 100-240V AC 50/60Hz 150W", fill=WHITE, font=load_font(FONT_MONO, 11))
    draw.ellipse([px0 + 60, ry0 + 120, px0 + 100, ry0 + 160], outline=STEEL_METAL, width=3)
    draw.ellipse([px0 + 120, ry0 + 120, px0 + 160, ry0 + 160], outline=STEEL_METAL, width=3)
    draw.ellipse([px0 + 180, ry0 + 120, px0 + 220, ry0 + 160], outline=STEEL_METAL, width=3)

    # =========================================================================
    # 4. FLAT COLOR & MATERIAL SWATCHES (20..2000, 1060..2020)
    # =========================================================================
    swatches = [
        ((20, 1060, 480, 1300), CHASSIS_BLACK, "CHASSIS_BLACK"),
        ((520, 1060, 980, 1300), FRONT_FASCIA, "FRONT_FASCIA"),
        ((1020, 1060, 1480, 1300), STEEL_METAL, "STEEL_METAL"),
        ((1520, 1060, 1980, 1300), (12, 14, 18, 255), "INNER_RECESS")
    ]
    for box, col, name in swatches:
        draw.rectangle(box, fill=col)
        draw.text((box[0] + 20, box[1] + 20), name, fill=WHITE, font=load_font(FONT_MONO, 16))

    img.save(ATLAS_PATH, "PNG")
    print(f"[Atlas] Generated: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

def generate_screen():
    SW, SH = 1024, 256
    img = Image.new("RGBA", (SW, SH), (6, 12, 10, 255))
    draw = ImageDraw.Draw(img)

    # Green VFD / Vacuum Fluorescent Display aesthetic
    VFD_GREEN = (45, 235, 115, 255)
    VFD_DIM   = (20, 95, 45, 255)

    # Display border frame
    draw.rectangle([4, 4, SW - 5, SH - 5], outline=VFD_DIM, width=2)
    
    # Header Line
    draw.text((25, 20), "SEC-VISION  16CH  NETWORK  VIDEO  RECORDER", fill=VFD_GREEN, font=load_font(FONT_MONO, 24))
    draw.line([(25, 58), (SW - 25, 58)], fill=VFD_GREEN, width=2)

    # Status telemetry lines
    draw.text((25, 75),  "REC STATUS: [ALL 16 CHANNELS RECORDING OK]", fill=VFD_GREEN, font=load_font(FONT_MONO, 20))
    draw.text((25, 115), "RAID-5 POOL: 4x 4TB ENTERPRISE [ONLINE HEALTHY]", fill=VFD_GREEN, font=load_font(FONT_MONO, 18))
    draw.text((25, 155), "STORAGE CAP: 14.2 TB / 16.0 TB  (88.7% FREE)", fill=VFD_GREEN, font=load_font(FONT_MONO, 18))
    draw.text((25, 195), "IP: 192.168.1.200  |  THROUGHPUT: 160 Mbps  |  FAN: OK", fill=VFD_GREEN, font=load_font(FONT_MONO, 17))

    img.save(SCREEN_PATH, "PNG")
    print(f"[Screen] Generated: {SCREEN_PATH} ({SW}x{SH})")

def main():
    generate_atlas()
    generate_screen()

if __name__ == "__main__":
    main()
