"""
=============================================================================
Security CCTV Asset Production Suite - Asset 51
Asset Name: SEC_Monitor_Small_Status (Kucuk Durum Monitoru)
Texture Generation Script v2 (Ultra-Crisp Bezel Typography & Sharp Screen Feed)
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

ATLAS_W, ATLAS_H = 1024, 1024

# Colors
CHASSIS_DARK = (20, 22, 26, 255)
CHASSIS_MID = (34, 38, 44, 255)
CHASSIS_LIGHT = (60, 66, 76, 255)
STEEL_BRACKET = (165, 172, 182, 255)
WHITE = (255, 255, 255, 255)
INK_TEXT = (230, 236, 245, 255)
INK_SOFT = (155, 165, 178, 255)
ACCENT_BLUE = (35, 145, 245, 255)
ACCENT_GREEN = (40, 220, 80, 255)
ACCENT_RED = (235, 45, 35, 255)
ACCENT_AMBER = (245, 170, 20, 255)

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

def generate_atlas():
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), CHASSIS_DARK)
    draw = ImageDraw.Draw(img)

    # 1. FRONT BEZEL REGION (32, 32, 992, 480)
    bx0, by0, bx1, by1 = 32, 32, 992, 480
    draw.rectangle([bx0, by0, bx1, by1], fill=(26, 29, 34, 255), outline=(45, 50, 58, 255), width=3)
    
    # Outer bezel chamfer highlight lines
    draw.line([(bx0 + 6, by0 + 6), (bx1 - 6, by0 + 6)], fill=(55, 62, 72, 255), width=2)
    draw.line([(bx0 + 6, by1 - 6), (bx1 - 6, by1 - 6)], fill=(38, 42, 50, 255), width=2)
    
    # Inner screen cutout area on atlas is PURE BLACK (so no text ever sits behind screen)
    # Bezel: Top = 52px (32..84), Bottom = 86px (394..480), Sides = 107px (32..139 and 885..992)
    sx0, sy0, sx1, sy1 = bx0 + 107, by0 + 52, bx1 - 107, by1 - 86
    draw.rectangle([sx0, sy0, sx1, sy1], fill=(10, 12, 16, 255), outline=(50, 55, 65, 255), width=2)

    # Top Bezel text & status cluster
    f_title = load_font(FONT_MONO, 17)
    f_sm = load_font(FONT_MONO, 12)
    draw_left_ink(draw, bx0 + 36, by0 + 26, "SEC-MON 07S  •  INDUSTRIAL TELEMETRY DISPLAY", f_title, WHITE)
    
    # Top right LEDs: PWR (Green), NET (Blue), ALM (Amber)
    draw.ellipse([bx1 - 180, by0 + 20, bx1 - 168, by0 + 32], fill=ACCENT_GREEN)
    draw_left_ink(draw, bx1 - 164, by0 + 26, "PWR", f_sm, ACCENT_GREEN)

    draw.ellipse([bx1 - 120, by0 + 20, bx1 - 108, by0 + 32], fill=ACCENT_BLUE)
    draw_left_ink(draw, bx1 - 104, by0 + 26, "NET", f_sm, ACCENT_BLUE)

    draw.ellipse([bx1 - 60, by0 + 20, bx1 - 48, by0 + 32], fill=ACCENT_AMBER)
    draw_left_ink(draw, bx1 - 44, by0 + 26, "ALM", f_sm, ACCENT_AMBER)

    # Bottom Bezel Control Strip (Buttons & Branding)
    bot_y0 = by1 - 86 # 394
    bot_cy = (bot_y0 + by1) // 2 # 437
    draw.rectangle([bx0 + 20, bot_y0 + 8, bx1 - 20, by1 - 12], fill=(22, 24, 28, 255), outline=(40, 44, 52, 255), width=1)
    
    # Brand logo on bottom left
    f_logo = load_font(FONT_SANS, 16)
    draw_left_ink(draw, bx0 + 40, bot_cy, "SEC-TELEMETRY SYSTEMS  |  SERIES 7", f_logo, INK_TEXT)

    # Button Socket Recesses on bottom right
    # MENU Socket: x in [680, 768], y in [415, 459]
    draw.rectangle([680, 415, 768, 459], fill=(14, 16, 20, 255), outline=(48, 54, 65, 255), width=1)
    
    # ENTER Socket: x in [800, 888], y in [415, 459]
    draw.rectangle([800, 415, 888, 459], fill=(14, 16, 20, 255), outline=(48, 54, 65, 255), width=1)

    # 2. DEDICATED 3D BUTTON CAPS REGION
    # Menu Button Cap: (672, 490) to (766, 538)
    draw.rectangle([672, 490, 766, 538], fill=(38, 42, 50, 255), outline=(65, 72, 85, 255), width=2)
    draw_center_ink(draw, 719, 514, "◀ MENU", load_font(FONT_MONO, 14), WHITE)

    # Enter Button Cap: (792, 490) to (886, 538)
    draw.rectangle([792, 490, 886, 538], fill=(38, 42, 50, 255), outline=(65, 72, 85, 255), width=2)
    draw_center_ink(draw, 839, 514, "ENTER ▶", load_font(FONT_MONO, 14), WHITE)

    # 3. REAR HOUSING REGION (32, 512, 600, 992)
    rx0, ry0, rx1, ry1 = 32, 512, 600, 992
    draw.rectangle([rx0, ry0, rx1, ry1], fill=(24, 26, 30, 255), outline=(45, 50, 58, 255), width=2)

    # Ventilation Louvers
    for ly in range(ry0 + 30, ry0 + 120, 10):
        draw.line([(rx0 + 40, ly), (rx1 - 40, ly)], fill=(15, 17, 20, 255), width=4)
        draw.line([(rx0 + 40, ly + 4), (rx1 - 40, ly + 4)], fill=(45, 50, 60, 255), width=1)

    # Technical Specification Plate
    px0, py0, px1, py1 = rx0 + 40, ry0 + 140, rx1 - 40, ry0 + 340
    draw.rectangle([px0, py0, px1, py1], fill=(18, 20, 24, 255), outline=(55, 62, 72, 255), width=2)
    
    f_spec_h = load_font(FONT_MONO, 14)
    f_spec = load_font(FONT_MONO, 11)
    draw.text((px0 + 16, py0 + 14), "SEC-MONITOR 07S  •  7 INCH INDUSTRIAL DISPLAY", fill=WHITE, font=f_spec_h)
    draw.line([(px0 + 16, py0 + 34), (px1 - 16, py0 + 34)], fill=(55, 62, 72, 255), width=1)
    draw.text((px0 + 16, py0 + 42), "INPUT VOLTAGE : 12V DC  --- 1.5A MAX (18W)", fill=INK_TEXT, font=f_spec)
    draw.text((px0 + 16, py0 + 60), "RESOLUTION    : 1024 x 600 IPS COMMERCIAL", fill=INK_TEXT, font=f_spec)
    draw.text((px0 + 16, py0 + 78), "VIDEO INPUT   : BNC COMPOSITE / HDMI 1.4", fill=INK_TEXT, font=f_spec)
    draw.text((px0 + 16, py0 + 96), "OPERATING TEMP: -10°C TO +55°C  |  IP40", fill=INK_TEXT, font=f_spec)
    draw.text((px0 + 16, py0 + 114), "SERIAL NO     : SN-MON07S-202688194", fill=INK_TEXT, font=f_spec)
    draw.text((px0 + 16, py0 + 134), "[CE]  [FCC]  [RoHS COMPLIANT]  [ISO 9001]", fill=INK_SOFT, font=f_spec)

    # Rear I/O Ports
    iox0, ioy0, iox1, ioy1 = rx0 + 40, ry0 + 360, rx1 - 40, ry1 - 30
    draw.rectangle([iox0, ioy0, iox1, ioy1], fill=(14, 16, 18, 255), outline=(48, 54, 64, 255), width=1)
    f_io = load_font(FONT_MONO, 12)
    draw.text((iox0 + 20, ioy0 + 14), "VIDEO IN (BNC)", fill=INK_TEXT, font=f_io)
    draw.text((iox0 + 180, ioy0 + 14), "HDMI IN", fill=INK_TEXT, font=f_io)
    draw.text((iox0 + 300, ioy0 + 14), "DC 12V IN", fill=INK_TEXT, font=f_io)
    draw.ellipse([iox0 + 45, ioy0 + 40, iox0 + 75, ioy0 + 70], outline=STEEL_BRACKET, width=2)
    draw.rectangle([iox0 + 185, ioy0 + 45, iox0 + 235, ioy0 + 65], outline=STEEL_BRACKET, width=2)
    draw.ellipse([iox0 + 320, ioy0 + 45, iox0 + 345, ioy0 + 70], outline=STEEL_BRACKET, width=2)

    # 4. MOUNT BRACKET REGION (630, 560, 850, 992)
    mx0, my0, mx1, my1 = 630, 560, 850, 992
    draw.rectangle([mx0, my0, mx1, my1], fill=(42, 46, 52, 255), outline=(70, 76, 86, 255), width=2)
    for by in range(my0 + 20, my1 - 20, 25):
        draw.line([(mx0 + 15, by), (mx1 - 15, by)], fill=(55, 60, 70, 255), width=2)
    draw.ellipse([mx0 + 25, my0 + 35, mx0 + 55, my0 + 65], fill=(18, 20, 22, 255), outline=STEEL_BRACKET, width=2)
    draw.ellipse([mx1 - 55, my0 + 35, mx1 - 25, my0 + 65], fill=(18, 20, 22, 255), outline=STEEL_BRACKET, width=2)
    draw.ellipse([mx0 + 25, my1 - 65, mx0 + 55, my1 - 35], fill=(18, 20, 22, 255), outline=STEEL_BRACKET, width=2)
    draw.ellipse([mx1 - 55, my1 - 65, mx1 - 25, my1 - 35], fill=(18, 20, 22, 255), outline=STEEL_BRACKET, width=2)
    f_b = load_font(FONT_MONO, 12)
    draw.text((mx0 + 25, my0 + 180), "VESA 75x75 mm", fill=WHITE, font=f_b)
    draw.text((mx0 + 25, my0 + 205), "TILT ADJUSTABLE", fill=INK_SOFT, font=f_b)

    # 5. FLAT COLOR SWATCHES (880, 560, 1024, 1024)
    swatches = [
        ((880, 560, 1024, 640), CHASSIS_DARK, "CHASSIS_DARK"),
        ((880, 640, 1024, 720), CHASSIS_MID, "CHASSIS_MID"),
        ((880, 720, 1024, 800), CHASSIS_LIGHT, "CHASSIS_LIGHT"),
        ((880, 800, 1024, 880), STEEL_BRACKET, "STEEL_BRACKET"),
        ((880, 880, 1024, 960), (45, 50, 60, 255), "BUTTON_SURFACE"),
        ((880, 960, 1024, 1024), (12, 14, 18, 255), "INNER_RECESS")
    ]
    for box, col, name in swatches:
        draw.rectangle(box, fill=col)

    img.save(ATLAS_PATH, "PNG")
    print(f"[Atlas] Generated: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

def generate_screen():
    SW, SH = 1024, 640
    img = Image.new("RGBA", (SW, SH), (8, 10, 14, 255))
    draw = ImageDraw.Draw(img)

    # Top Telemetry Header
    draw.rectangle([0, 0, SW, 48], fill=(16, 20, 28, 255))
    draw.line([(0, 48), (SW, 48)], fill=(35, 140, 240, 255), width=2)
    
    f_head = load_font(FONT_MONO, 17)
    draw.text((20, 14), "SEC-STATUS TERMINAL 07S  •  SYS_ID: #884-A", fill=WHITE, font=f_head)
    
    # Live indicator right
    draw.ellipse([SW - 180, 16, SW - 166, 30], fill=ACCENT_GREEN)
    f_stat = load_font(FONT_MONO, 13)
    draw.text((SW - 158, 15), "SYSTEM: NORMAL [OK]", fill=ACCENT_GREEN, font=f_stat)

    # Left Telemetry Pane: Camera Live Preview / Mini Viewport
    cx0, cy0, cx1, cy1 = 20, 64, 530, 390
    draw.rectangle([cx0, cy0, cx1, cy1], fill=(12, 16, 22, 255), outline=(35, 55, 80, 255), width=2)
    # Scanlines inside camera feed
    for y in range(cy0 + 30, cy1 - 25, 4):
        draw.line([cx0, y, cx1, y], fill=(0, 0, 0, 40), width=1)
    
    # Camera crosshair & target reticle
    ccx = (cx0 + cx1) // 2
    ccy = (cy0 + cy1) // 2
    draw.rectangle([ccx - 60, ccy - 35, ccx + 60, ccy + 35], outline=(45, 180, 240, 180), width=2)
    draw.line([ccx - 25, ccy, ccx + 25, ccy], fill=(45, 180, 240, 220), width=2)
    draw.line([ccx, ccy - 25, ccx, ccy + 25], fill=(45, 180, 240, 220), width=2)
    
    f_cam = load_font(FONT_MONO, 13)
    draw.text((cx0 + 12, cy0 + 10), "CAM 01 [MAIN ENTRANCE GATE] • REC ●", fill=ACCENT_RED, font=f_cam)
    draw.text((cx0 + 12, cy1 - 24), "1080P/30FPS  |  H.265  |  BITRATE: 4096 kbps", fill=INK_SOFT, font=load_font(FONT_MONO, 11))

    # Right Telemetry Pane: Sensor & Subsystem Matrix
    rx0, ry0, rx1, ry1 = 550, 64, SW - 20, 390
    draw.rectangle([rx0, ry0, rx1, ry1], fill=(14, 18, 26, 255), outline=(35, 55, 80, 255), width=2)
    
    f_sub_h = load_font(FONT_MONO, 14)
    f_sub = load_font(FONT_MONO, 12)
    draw.text((rx0 + 16, ry0 + 12), "SUBSYSTEM TELEMETRY MATRIX", fill=WHITE, font=f_sub_h)
    draw.line([(rx0 + 16, ry0 + 32), (rx1 - 16, ry0 + 32)], fill=(40, 60, 85, 255), width=1)
    
    items = [
        ("PERIMETER LASER BARRIER :", "ONLINE (TX/RX SYNC)", ACCENT_GREEN),
        ("DOOR ACCESS MAGNETIC    :", "ALL 14 LOCKED [SECURE]", ACCENT_GREEN),
        ("SMOKE & FIRE DETECTORS  :", "08/08 READY (NORMAL)", ACCENT_GREEN),
        ("PIR MOTION SENSORS      :", "ARMED [NIGHT MODE]", ACCENT_AMBER),
        ("RACK UPS POWER LINE     :", "230V AC  •  BATTERY 98%", ACCENT_GREEN),
        ("DVR NVR STORAGE RAID5   :", "12.4 TB / 16 TB (HEALTHY)", ACCENT_GREEN),
        ("NETWORK SWITCH POE      :", "24 PORTS ACTIVE (180W)", ACCENT_BLUE)
    ]
    for i, (label, val, col) in enumerate(items):
        iy = ry0 + 44 + i * 26
        draw.text((rx0 + 16, iy), label, fill=INK_TEXT, font=f_sub)
        draw.text((rx0 + 240, iy), val, fill=col, font=f_sub)

    # Bottom Area: Real-Time Event Log & System Bar
    lx0, ly0, lx1, ly1 = 20, 408, SW - 20, SH - 20
    draw.rectangle([lx0, ly0, lx1, ly1], fill=(12, 15, 22, 255), outline=(30, 45, 65, 255), width=1)
    
    draw.text((lx0 + 16, ly0 + 10), "SECURITY EVENT AUDIT TRAIL [REAL-TIME]:", fill=WHITE, font=f_sub_h)
    
    logs = [
        ("04:36:12", "SEC_LOCK_49", "RACK CABINET #02 DOOR CLOSED AND SECURED", INK_TEXT),
        ("04:36:35", "SEC_CAM_01", "AI OBJECT DETECTED: PATROL PERSONNEL IN SECTOR 3", ACCENT_BLUE),
        ("04:36:50", "SEC_PDU_59", "AC POWER DISTRIBUTION LOAD BALANCED (1.42 kW)", INK_SOFT)
    ]
    for idx, (tm, src, msg, c) in enumerate(logs):
        log_y = ly0 + 34 + idx * 24
        draw.text((lx0 + 16, log_y), f"[{tm}]", fill=ACCENT_AMBER, font=f_sub)
        draw.text((lx0 + 105, log_y), f"[{src}]", fill=WHITE, font=f_sub)
        draw.text((lx0 + 225, log_y), msg, fill=c, font=f_sub)

    # Status footer bar
    draw.line([(lx0, ly1 - 28), (lx1, ly1 - 28)], fill=(25, 38, 55, 255), width=1)
    draw.text((lx0 + 16, ly1 - 20), "HOST: 192.168.1.150  |  GATEWAY: 192.168.1.1  |  LEVEL: GRADE-3  |  DATE: 2026-10-31 04:36:50 UTC", fill=INK_SOFT, font=load_font(FONT_MONO, 11))

    img.save(SCREEN_PATH, "PNG")
    print(f"[Screen] Generated: {SCREEN_PATH} ({SW}x{SH})")

if __name__ == "__main__":
    generate_atlas()
    generate_screen()
