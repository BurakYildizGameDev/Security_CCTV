"""
SEC_Monitor_CCTV_Quad_LCD Generator Script (Master Quality Revision 2 - High Fidelity & Sealed Cavities)
Industrial Low-Poly Security & CCTV Asset Pack
Upper Budget Limit: 500 triangles

Hierarchy:
SEC_Monitor_CCTV_Quad_LCD (Root Empty at 0, 0, 0 on desk)
 ├── Stand_Base (Mesh, child of Root)
 ├── Stand_Neck (Mesh, child of Root)
 └── Display_Tilt_Pivot (Empty at hinge, child of Root, local X: -10°..+10°)
      └── Display_Housing (Mesh, child of Display_Tilt_Pivot)
           ├── Screen_Top_Left (Mesh, child of Display_Housing, M_Screen)
           ├── Screen_Top_Right (Mesh, child of Display_Housing, M_Screen)
           ├── Screen_Bottom_Left (Mesh, child of Display_Housing, M_Screen)
           └── Screen_Bottom_Right (Mesh, child of Display_Housing, M_Screen)

Materials:
    Slot 0: M_Security_Atlas
    Slot 1: M_Screen
    Slot 2: M_Metal
"""

import os
import sys
import math
import json
import site
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler

# Ensure Pillow from user-site is available
if site.getusersitepackages() not in sys.path:
    sys.path.append(site.getusersitepackages())
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except Exception as e:
    HAS_PIL = False
    print(f"[WARN] PIL not available directly: {e}")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(PROJECT_DIR, "exports")


def setup_clean_scene():
    """Reset scene to a clean metric environment."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'


def get_fonts():
    try:
        font_main_lg = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 26)
        font_main_md = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 17)
        font_main_sm = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 13)
        font_title_lg = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 28)
        font_title_md = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 18)
        font_title_sm = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 12)
    except Exception:
        font_main_lg = font_main_md = font_main_sm = ImageFont.load_default()
        font_title_lg = font_title_md = font_title_sm = ImageFont.load_default()
    return font_main_lg, font_main_md, font_main_sm, font_title_lg, font_title_md, font_title_sm


def generate_screen_texture():
    """Generate 1024x1024 4-Quadrant CCTV Display Texture (T_Screen.png) with enhanced contrast."""
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    out_path = os.path.join(EXPORTS_DIR, "T_Screen.png")
    if not HAS_PIL:
        return out_path

    w, h = 1024, 1024
    img = Image.new("RGBA", (w, h), (20, 24, 28, 255))
    draw = ImageDraw.Draw(img)
    f_lg, f_md, f_sm, t_lg, t_md, t_sm = get_fonts()

    # --- QUADRANT 1: CAM 01 - MAIN ENTRANCE GATE (Top-Left: X 0..512, Y 0..512) ---
    for y in range(0, 512):
        shade = int(22 + (y / 512.0) * 18)
        draw.line([(0, y), (512, y)], fill=(shade - 3, shade + 5, shade, 255))

    draw.line([(0, 220), (512, 220)], fill=(45, 65, 50, 255), width=2)
    draw.rectangle([20, 150, 120, 220], fill=(32, 45, 36, 255))
    draw.rectangle([130, 130, 210, 220], fill=(26, 38, 30, 255))
    draw.rectangle([340, 160, 460, 220], fill=(28, 40, 32, 255))

    road_pts = [(210, 220), (280, 220), (450, 512), (50, 512)]
    draw.polygon(road_pts, fill=(38, 42, 45, 255))
    for i in range(5):
        y0 = 230 + i * 55
        y1 = y0 + 32
        x0 = 245 + int((i / 5.0) * 5)
        draw.line([(x0, y0), (x0, y1)], fill=(220, 190, 50, 255), width=3)

    draw.rectangle([40, 230, 140, 360], fill=(55, 65, 75, 255), outline=(90, 105, 120, 255), width=2)
    draw.rectangle([55, 250, 125, 290], fill=(100, 150, 165, 255), outline=(130, 180, 195, 255))
    draw.rectangle([35, 220, 145, 230], fill=(75, 88, 100, 255))
    draw.text((45, 305), "GATE 01", fill=(230, 240, 250, 255), font=t_sm)

    draw.rectangle([140, 320, 170, 380], fill=(220, 80, 35, 255), outline=(255, 105, 60, 255))
    for b in range(12):
        bx0 = 170 + b * 20
        bx1 = bx0 + 20
        col = (240, 200, 30, 255) if b % 2 == 0 else (25, 25, 25, 255)
        draw.polygon([(bx0, 335), (bx1, 335), (bx1 + 8, 345), (bx0 + 8, 345)], fill=col)

    for fx in range(320, 512, 25):
        draw.line([(fx, 220), (fx, 360)], fill=(75, 95, 80, 255), width=2)
    draw.line([(320, 240), (512, 240)], fill=(75, 95, 80, 255), width=2)
    draw.line([(320, 300), (512, 300)], fill=(75, 95, 80, 255), width=2)

    draw.rectangle([210, 320, 380, 440], outline=(50, 255, 150, 255), width=2)
    draw.rectangle([210, 300, 380, 320], fill=(50, 255, 150, 220))
    draw.text((215, 303), "VEHICLE DETECTED [99%]", fill=(10, 30, 15, 255), font=f_sm)

    draw.rectangle([8, 8, 504, 38], fill=(12, 18, 15, 220))
    draw.ellipse([18, 17, 30, 29], fill=(240, 30, 30, 255))
    draw.text((36, 15), "REC", fill=(255, 60, 60, 255), font=f_md)
    draw.text((80, 15), "CAM 01 - MAIN GATE", fill=(250, 255, 250, 255), font=f_md)
    draw.text((310, 15), "2026-10-25 13:15:22", fill=(230, 240, 230, 255), font=f_md)
    draw.text((12, 485), "1080P 30FPS | 4.2 Mbps | H.265 | WDR ON", fill=(180, 210, 195, 255), font=f_sm)
    draw.line([(256, 246), (256, 266)], fill=(140, 230, 170, 220), width=1)
    draw.line([(246, 256), (266, 256)], fill=(140, 230, 170, 220), width=1)

    # --- QUADRANT 2: CAM 02 - PERIMETER NORTH (Top-Right: X 512..1024, Y 0..512) ---
    for y in range(0, 512):
        shade = int(18 + (y / 512.0) * 22)
        draw.line([(512, y), (1024, y)], fill=(shade - 4, shade + 8, shade - 2, 255))

    draw.line([(512, 230), (1024, 230)], fill=(30, 55, 35, 255), width=2)
    for fx in range(540, 1010, 20):
        draw.line([(fx, 190), (fx, 400)], fill=(65, 105, 75, 255), width=2)
    draw.line([(520, 210), (1024, 210)], fill=(85, 135, 95, 255), width=2)
    draw.line([(520, 260), (1024, 260)], fill=(85, 135, 95, 255), width=2)
    draw.line([(520, 330), (1024, 330)], fill=(85, 135, 95, 255), width=2)
    for cx in range(530, 1010, 16):
        draw.ellipse([cx, 185, cx + 18, 210], outline=(110, 160, 120, 255), width=2)

    draw.line([(930, 140), (910, 380)], fill=(100, 130, 110, 255), width=3)
    draw.line([(950, 140), (970, 380)], fill=(100, 130, 110, 255), width=3)
    draw.polygon([(940, 140), (700, 420), (980, 420)], fill=(50, 85, 60, 120))

    draw.rectangle([680, 270, 790, 360], outline=(255, 235, 50, 255), width=2)
    draw.rectangle([680, 250, 790, 270], fill=(255, 235, 50, 220))
    draw.text((685, 253), "MOTION ZONE 2B", fill=(20, 20, 10, 255), font=f_sm)

    draw.rectangle([520, 8, 1016, 38], fill=(12, 18, 15, 220))
    draw.ellipse([530, 17, 542, 29], fill=(240, 30, 30, 255))
    draw.text((548, 15), "REC", fill=(255, 60, 60, 255), font=f_md)
    draw.text((592, 15), "CAM 02 - PERIMETER NORTH", fill=(250, 255, 250, 255), font=f_md)
    draw.text((822, 15), "2026-10-25 13:15:22", fill=(230, 240, 230, 255), font=f_md)
    draw.text((524, 485), "IR 850nm ILLUMINATION: ON | B/W MODE | SENS: HIGH", fill=(160, 210, 175, 255), font=f_sm)
    draw.line([(768, 246), (768, 266)], fill=(140, 230, 170, 220), width=1)
    draw.line([(758, 256), (778, 256)], fill=(140, 230, 170, 220), width=1)

    # --- QUADRANT 3: CAM 03 - DATA CENTER B2 (Bottom-Left: X 0..512, Y 512..1024) ---
    for y in range(512, 1024):
        shade = int(20 + ((y - 512) / 512.0) * 18)
        draw.line([(0, y), (512, y)], fill=(shade - 3, shade, shade + 12, 255))

    for gy in range(700, 1024, 35):
        draw.line([(0, gy), (512, gy)], fill=(40, 52, 70, 255), width=2)
    for gx in range(50, 480, 55):
        draw.line([(256, 680), (gx, 1024)], fill=(40, 52, 70, 255), width=2)

    draw.rectangle([40, 620, 110, 880], fill=(32, 38, 48, 255), outline=(70, 85, 105, 255), width=2)
    draw.rectangle([120, 640, 180, 850], fill=(28, 34, 44, 255), outline=(65, 80, 100, 255), width=2)
    draw.rectangle([400, 620, 470, 880], fill=(32, 38, 48, 255), outline=(70, 85, 105, 255), width=2)
    draw.rectangle([330, 640, 390, 850], fill=(28, 34, 44, 255), outline=(65, 80, 100, 255), width=2)

    for ry in range(635, 870, 12):
        draw.rectangle([45, ry, 105, ry + 4], fill=(45, 55, 68, 255))
        draw.ellipse([48, ry + 1, 52, ry + 3], fill=(50, 200, 255, 255))
        draw.ellipse([58, ry + 1, 62, ry + 3], fill=(60, 255, 100, 255))
        draw.ellipse([68, ry + 1, 72, ry + 3], fill=(255, 190, 40, 255))

        draw.rectangle([405, ry, 465, ry + 4], fill=(45, 55, 68, 255))
        draw.ellipse([408, ry + 1, 412, ry + 3], fill=(60, 255, 100, 255))
        draw.ellipse([418, ry + 1, 422, ry + 3], fill=(50, 200, 255, 255))

    draw.rectangle([180, 570, 330, 600], fill=(230, 190, 35, 255), outline=(150, 125, 25, 255))
    draw.text((195, 578), "CABLE TRAY - MAIN FIBER", fill=(20, 20, 20, 255), font=t_sm)

    draw.rectangle([8, 520, 504, 550], fill=(12, 18, 26, 220))
    draw.ellipse([18, 529, 30, 541], fill=(240, 30, 30, 255))
    draw.text((36, 527), "REC", fill=(255, 60, 60, 255), font=f_md)
    draw.text((80, 527), "CAM 03 - DATA CENTER B2", fill=(250, 255, 255, 255), font=f_md)
    draw.text((310, 527), "2026-10-25 13:15:22", fill=(230, 240, 250, 255), font=f_md)
    draw.text((12, 997), "TEMP: 19.4°C | HUMID: 41% | HALON GAS: ARMED | LEVEL 4 RESTRICTED", fill=(160, 205, 245, 255), font=f_sm)
    draw.line([(256, 758), (256, 778)], fill=(120, 205, 255, 220), width=1)
    draw.line([(246, 768), (266, 768)], fill=(120, 205, 255, 220), width=1)

    # --- QUADRANT 4: CAM 04 - LOADING DOCK (Bottom-Right: X 512..1024, Y 512..1024) ---
    for y in range(512, 1024):
        shade = int(22 + ((y - 512) / 512.0) * 18)
        draw.line([(512, y), (1024, y)], fill=(shade + 6, shade + 3, shade - 3, 255))

    draw.rectangle([600, 580, 940, 740], fill=(60, 64, 68, 255), outline=(95, 100, 105, 255), width=2)
    for sy in range(590, 740, 14):
        draw.line([(600, sy), (940, sy)], fill=(40, 44, 48, 255), width=2)
    draw.rectangle([600, 740, 940, 850], fill=(145, 155, 168, 255))
    draw.text((710, 780), "[ BAY 03 - OPEN ]", fill=(25, 30, 35, 255), font=f_md)

    for hx in range(540, 1000, 30):
        col = (245, 200, 35, 255) if (hx // 30) % 2 == 0 else (30, 30, 30, 255)
        draw.polygon([(hx, 880), (hx + 20, 880), (hx + 35, 915), (hx + 15, 915)], fill=col)

    draw.rectangle([540, 810, 620, 870], fill=(160, 115, 70, 255), outline=(120, 85, 50, 255))
    draw.rectangle([550, 760, 610, 810], fill=(185, 140, 85, 255), outline=(135, 100, 60, 255))
    draw.text((555, 780), "CARGO", fill=(45, 35, 25, 255), font=t_sm)

    draw.rectangle([910, 810, 990, 880], fill=(245, 155, 25, 255), outline=(190, 115, 20, 255))
    draw.rectangle([890, 840, 910, 875], fill=(35, 35, 35, 255))
    draw.ellipse([920, 865, 945, 890], fill=(25, 25, 25, 255))
    draw.ellipse([965, 865, 990, 890], fill=(25, 25, 25, 255))

    draw.rectangle([520, 520, 1016, 550], fill=(18, 18, 15, 220))
    draw.ellipse([530, 529, 542, 541], fill=(240, 30, 30, 255))
    draw.text((548, 527), "REC", fill=(255, 60, 60, 255), font=f_md)
    draw.text((592, 527), "CAM 04 - LOADING DOCK 03", fill=(255, 255, 250, 255), font=f_md)
    draw.text((822, 527), "2026-10-25 13:15:22", fill=(240, 240, 230, 255), font=f_md)
    draw.text((524, 997), "BAY SENSOR: ACTIVE | DOCK LEVELER: REST | MOTION: IDLE", fill=(225, 215, 185, 255), font=f_sm)
    draw.line([(768, 758), (768, 778)], fill=(230, 210, 140, 220), width=1)
    draw.line([(758, 768), (778, 768)], fill=(230, 210, 140, 220), width=1)

    draw.line([(510, 0), (510, 1024)], fill=(15, 18, 20, 255), width=4)
    draw.line([(0, 510), (1024, 510)], fill=(15, 18, 20, 255), width=4)

    for y in range(0, 1024, 4):
        draw.line([(0, y), (1024, y)], fill=(0, 0, 0, 20))

    img.save(out_path, format="PNG")
    print(f"[INFO] Generated T_Screen.png: {out_path}")
    return out_path


def generate_security_atlas_texture():
    """Generate 1024x1024 Texture Atlas (T_Security_Atlas.png)"""
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    out_path = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")
    if not HAS_PIL:
        return out_path

    w, h = 1024, 1024
    img = Image.new("RGBA", (w, h), (26, 28, 32, 255))
    draw = ImageDraw.Draw(img)
    f_lg, f_md, f_sm, t_lg, t_md, t_sm = get_fonts()

    # Base casing micro-texture
    for y in range(0, 512, 4):
        for x in range(0, 512, 4):
            if (x + y) % 8 == 0:
                draw.point((x, y), fill=(30, 32, 36, 255))
            elif (x * y) % 7 == 0:
                draw.point((x, y), fill=(22, 24, 28, 255))

    # --- ZONE 1: FRONT BEZEL CHIN & BRAND STRIP (X: 0..1024, Y: 512..640) ---
    for y in range(512, 640):
        shade = int(22 + ((y - 512) / 128.0) * 8)
        draw.line([(0, y), (1024, y)], fill=(shade, shade + 2, shade + 4, 255))
    draw.line([(0, 512), (1024, 512)], fill=(65, 72, 82, 255), width=2)
    draw.line([(0, 638), (1024, 638)], fill=(10, 11, 13, 255), width=2)

    draw.text((25, 538), "SEC-QUAD 24L", fill=(245, 250, 255, 255), font=t_lg)
    draw.text((28, 585), "PROFESSIONAL 4-CHANNEL CCTV SURVEILLANCE LCD MONITOR", fill=(185, 195, 210, 255), font=t_sm)

    btn_labels = ["CH 1", "CH 2", "CH 3", "CH 4", "QUAD", "AUTO"]
    for i, lbl in enumerate(btn_labels):
        bx = 420 + i * 58
        by = 548
        draw.rectangle([bx, by, bx + 50, by + 34], fill=(36, 40, 48, 255), outline=(90, 100, 115, 255), width=1)
        draw.text((bx + 8, by + 8), lbl, fill=(220, 230, 240, 255), font=f_sm)
        led_col = (40, 255, 90, 255) if lbl == "QUAD" else (20, 60, 30, 255)
        draw.ellipse([bx + 20, by + 40, bx + 28, by + 48], fill=led_col, outline=(70, 80, 90, 255))

    osd_keys = ["MENU", "▲", "▼", "ENTER"]
    for i, k in enumerate(osd_keys):
        kx = 785 + i * 42
        ky = 548
        draw.rectangle([kx, ky, kx + 36, ky + 34], fill=(34, 38, 44, 255), outline=(80, 90, 105, 255), width=1)
        draw.text((kx + 6, ky + 10), k, fill=(210, 220, 230, 255), font=f_sm)

    # Power button & LED
    draw.ellipse([960, 545, 1005, 590], fill=(28, 30, 34, 255), outline=(90, 100, 115, 255), width=2)
    draw.text((975, 555), "⏻", fill=(240, 245, 255, 255), font=t_md)
    draw.ellipse([977, 602, 989, 614], fill=(40, 255, 90, 255), outline=(160, 255, 190, 255), width=2)

    # --- ZONE 2: REAR RECESSED I/O BAY (X: 0..512, Y: 640..896) ---
    draw.rectangle([0, 640, 512, 896], fill=(22, 24, 27, 255))
    draw.rectangle([10, 650, 502, 886], fill=(28, 31, 35, 255), outline=(60, 68, 78, 255), width=2)
    draw.text((25, 660), "REAR I/O CONNECTIONS - 75 OHM BNC / DIGITAL", fill=(220, 230, 240, 255), font=f_md)

    for b in range(4):
        bx = 35 + b * 65
        by = 705
        draw.ellipse([bx, by, bx + 42, by + 42], fill=(70, 75, 82, 255), outline=(140, 150, 160, 255), width=2)
        draw.ellipse([bx + 12, by + 12, bx + 30, by + 30], fill=(30, 32, 36, 255), outline=(190, 200, 210, 255), width=1)
        draw.ellipse([bx + 18, by + 18, bx + 24, by + 24], fill=(230, 200, 85, 255))
        draw.text((bx + 2, by + 48), f"IN {b+1}", fill=(210, 220, 230, 255), font=f_sm)

    for b in range(4):
        bx = 35 + b * 65
        by = 785
        draw.ellipse([bx, by, bx + 42, by + 42], fill=(70, 75, 82, 255), outline=(140, 150, 160, 255), width=2)
        draw.ellipse([bx + 12, by + 12, bx + 30, by + 30], fill=(30, 32, 36, 255), outline=(190, 200, 210, 255), width=1)
        draw.ellipse([bx + 18, by + 18, bx + 24, by + 24], fill=(230, 200, 85, 255))
        draw.text((bx, by + 48), f"OUT {b+1}", fill=(190, 200, 210, 255), font=f_sm)

    draw.rectangle([310, 705, 380, 735], fill=(35, 38, 44, 255), outline=(100, 110, 125, 255), width=2)
    draw.text((322, 712), "HDMI IN", fill=(220, 230, 240, 255), font=f_sm)

    draw.rectangle([310, 755, 380, 785], fill=(30, 60, 120, 255), outline=(70, 105, 200, 255), width=2)
    draw.text((324, 762), "VGA IN", fill=(230, 240, 255, 255), font=f_sm)

    draw.rectangle([410, 720, 485, 800], fill=(16, 17, 19, 255), outline=(75, 82, 92, 255), width=2)
    draw.rectangle([425, 740, 435, 755], fill=(190, 195, 205, 255))
    draw.rectangle([460, 740, 470, 755], fill=(190, 195, 205, 255))
    draw.rectangle([442, 765, 452, 780], fill=(190, 195, 205, 255))
    draw.text((412, 810), "100-240V AC", fill=(180, 190, 200, 255), font=f_sm)

    # --- ZONE 3: FACTORY SPECIFICATION RATING PLATE (X: 512..1024, Y: 640..896) ---
    draw.rectangle([512, 640, 1024, 896], fill=(22, 24, 27, 255))
    draw.rectangle([530, 655, 1005, 880], fill=(230, 235, 240, 255), outline=(100, 110, 120, 255), width=2)
    draw.rectangle([535, 660, 1000, 875], outline=(150, 160, 170, 255), width=1)

    draw.text((550, 670), "INDUSTRIAL CCTV MONITOR", fill=(15, 20, 25, 255), font=t_lg)
    draw.text((550, 705), "MODEL: SEC-24Q-LCD   TYPE: QUAD-VIEW SURVEILLANCE DISPLAY", fill=(20, 25, 30, 255), font=f_sm)
    draw.text((550, 725), "INPUT RATING: 100-240V ~ 50/60Hz 1.2A 45W MAX", fill=(20, 25, 30, 255), font=f_sm)
    draw.text((550, 745), "SERIAL NO: SQ-2026-98104-REV B   MAC: 00:1B:44:A2:89:C4", fill=(20, 25, 30, 255), font=f_sm)

    for bx in range(550, 820, 4):
        if (bx * 7) % 11 < 6:
            draw.line([(bx, 775), (bx, 825)], fill=(10, 15, 20, 255), width=2)
    draw.text((590, 832), "*SQ202698104B*", fill=(10, 15, 20, 255), font=f_sm)

    cert_labels = ["CE", "FCC", "RoHS", "WEEE", "UL LISTED"]
    for i, c in enumerate(cert_labels):
        cx = 840 + (i % 2) * 75
        cy = 765 + (i // 2) * 35
        draw.rectangle([cx, cy, cx + 65, cy + 28], fill=(210, 215, 222, 255), outline=(60, 70, 80, 255), width=1)
        draw.text((cx + 10, cy + 6), c, fill=(20, 25, 30, 255), font=f_sm)

    # --- ZONE 4: LOUVERS (X: 0..480, Y: 896..1024) ---
    for ly in range(908, 1015, 12):
        draw.rectangle([20, ly, 460, ly + 6], fill=(12, 13, 15, 255), outline=(35, 38, 44, 255), width=1)

    # --- ZONE 5: PURE BRUSHED METAL FOR STAND BASE (X: 490..700, Y: 896..1024) ---
    for y in range(896, 1024):
        shade = int(50 + ((y - 896) / 128.0) * 14)
        draw.line([(490, y), (700, y)], fill=(shade, shade + 3, shade + 6, 255))
    draw.rectangle([492, 898, 698, 1022], outline=(80, 88, 98, 255), width=2)

    # --- ZONE 6: VESA 100x100 MOUNTING PLATE (X: 710..950, Y: 896..1024) ---
    draw.rectangle([710, 896, 950, 1024], fill=(28, 30, 34, 255), outline=(60, 66, 75, 255), width=2)
    draw.text((750, 955), "VESA 100x100", fill=(140, 150, 160, 255), font=f_sm)
    vesa_screws = [(730, 915), (930, 915), (730, 1005), (930, 1005)]
    for vx, vy in vesa_screws:
        draw.ellipse([vx - 10, vy - 10, vx + 10, vy + 10], fill=(150, 158, 168, 255), outline=(75, 80, 88, 255), width=2)
        draw.line([(vx, vy - 7), (vx, vy + 7)], fill=(40, 44, 50, 255), width=2)
        draw.line([(vx - 7, vy), (vx + 7, vy)], fill=(40, 44, 50, 255), width=2)

    # --- ZONE 7: NEUTRAL BUFFER FOR BEVELS (X: 960..1024, Y: 960..1024) ---
    draw.rectangle([960, 960, 1024, 1024], fill=(28, 30, 34, 255))

    img.save(out_path, format="PNG")
    print(f"[INFO] Generated T_Security_Atlas.png: {out_path}")
    return out_path


def load_or_create_textures():
    """Ensure textures exist and load them into Blender data."""
    atlas_path = generate_security_atlas_texture()
    screen_path = generate_screen_texture()

    if os.path.exists(atlas_path):
        atlas_img = bpy.data.images.load(atlas_path, check_existing=True)
    else:
        atlas_img = bpy.data.images.new("T_Security_Atlas", width=512, height=512, alpha=True)

    if os.path.exists(screen_path):
        screen_img = bpy.data.images.load(screen_path, check_existing=True)
    else:
        screen_img = bpy.data.images.new("T_Screen", width=512, height=512, alpha=True)

    return atlas_img, screen_img


def create_materials(atlas_img, screen_img):
    """
    Slot 0: M_Security_Atlas
    Slot 1: M_Screen
    Slot 2: M_Metal
    """
    materials = {}

    # Slot 0: M_Security_Atlas
    mat_atlas = bpy.data.materials.get("M_Security_Atlas")
    if not mat_atlas:
        mat_atlas = bpy.data.materials.new(name="M_Security_Atlas")
    mat_atlas.use_nodes = True
    nodes0 = mat_atlas.node_tree.nodes
    links0 = mat_atlas.node_tree.links
    nodes0.clear()

    out0 = nodes0.new(type='ShaderNodeOutputMaterial')
    out0.location = (300, 0)
    bsdf0 = nodes0.new(type='ShaderNodeBsdfPrincipled')
    bsdf0.location = (0, 0)
    links0.new(bsdf0.outputs['BSDF'], out0.inputs['Surface'])

    tex0 = nodes0.new(type='ShaderNodeTexImage')
    tex0.location = (-300, 0)
    tex0.image = atlas_img
    links0.new(tex0.outputs['Color'], bsdf0.inputs['Base Color'])

    bsdf0.inputs['Roughness'].default_value = 0.45
    bsdf0.inputs['Metallic'].default_value = 0.05
    mat_atlas.diffuse_color = (0.16, 0.17, 0.20, 1.0)
    materials["M_Security_Atlas"] = mat_atlas

    # Slot 1: M_Screen (Vibrant emissive 4-feed surveillance display)
    mat_screen = bpy.data.materials.get("M_Screen")
    if not mat_screen:
        mat_screen = bpy.data.materials.new(name="M_Screen")
    mat_screen.use_nodes = True
    nodes1 = mat_screen.node_tree.nodes
    links1 = mat_screen.node_tree.links
    nodes1.clear()

    out1 = nodes1.new(type='ShaderNodeOutputMaterial')
    out1.location = (300, 0)
    bsdf1 = nodes1.new(type='ShaderNodeBsdfPrincipled')
    bsdf1.location = (0, 0)
    links1.new(bsdf1.outputs['BSDF'], out1.inputs['Surface'])

    tex1 = nodes1.new(type='ShaderNodeTexImage')
    tex1.location = (-300, 0)
    tex1.image = screen_img
    links1.new(tex1.outputs['Color'], bsdf1.inputs['Base Color'])
    links1.new(tex1.outputs['Color'], bsdf1.inputs['Emission Color'])

    bsdf1.inputs['Emission Strength'].default_value = 1.40
    bsdf1.inputs['Roughness'].default_value = 0.08
    bsdf1.inputs['Metallic'].default_value = 0.02
    mat_screen.diffuse_color = (0.20, 0.35, 0.28, 1.0)
    materials["M_Screen"] = mat_screen

    # Slot 2: M_Metal (Brushed chrome/aluminum hinge pin, stand accents, BNC barrels)
    mat_metal = bpy.data.materials.get("M_Metal")
    if not mat_metal:
        mat_metal = bpy.data.materials.new(name="M_Metal")
    mat_metal.use_nodes = True
    nodes2 = mat_metal.node_tree.nodes
    links2 = mat_metal.node_tree.links
    nodes2.clear()

    out2 = nodes2.new(type='ShaderNodeOutputMaterial')
    out2.location = (300, 0)
    bsdf2 = nodes2.new(type='ShaderNodeBsdfPrincipled')
    bsdf2.location = (0, 0)
    links2.new(bsdf2.outputs['BSDF'], out2.inputs['Surface'])

    tex2 = nodes2.new(type='ShaderNodeTexImage')
    tex2.location = (-300, 0)
    tex2.image = atlas_img
    links2.new(tex2.outputs['Color'], bsdf2.inputs['Base Color'])

    bsdf2.inputs['Roughness'].default_value = 0.20
    bsdf2.inputs['Metallic'].default_value = 0.95
    mat_metal.diffuse_color = (0.75, 0.78, 0.82, 1.0)
    materials["M_Metal"] = mat_metal

    return materials


def attach_standard_materials(mesh, materials):
    """Ensure materials are present in the exact order specified."""
    mesh.materials.clear()
    mesh.materials.append(materials["M_Security_Atlas"])  # Slot 0
    mesh.materials.append(materials["M_Screen"])          # Slot 1
    mesh.materials.append(materials["M_Metal"])           # Slot 2


def set_face_uv_rect(bm, face, uv_rect, flip_u=False, flip_v=False):
    """Map face planar projections to a rectangular UV sub-region [u0, v0, u1, v1]."""
    face.normal_update()
    u0, v0, u1, v1 = uv_rect
    uv_lay = bm.loops.layers.uv.verify()

    coords_2d = []
    normal = face.normal
    nx, ny, nz = abs(normal.x), abs(normal.y), abs(normal.z)

    if (ny >= nx and ny >= nz) or (nx < 1e-4 and ny < 1e-4 and nz < 1e-4):
        for loop in face.loops:
            coords_2d.append((loop.vert.co.x, loop.vert.co.z))
    elif nx >= ny and nx >= nz:
        for loop in face.loops:
            coords_2d.append((loop.vert.co.y, loop.vert.co.z))
    else:
        for loop in face.loops:
            coords_2d.append((loop.vert.co.x, loop.vert.co.y))

    min_x = min(c[0] for c in coords_2d)
    max_x = max(c[0] for c in coords_2d)
    min_y = min(c[1] for c in coords_2d)
    max_y = max(c[1] for c in coords_2d)
    span_x = max_x - min_x if max_x > min_x else 1.0
    span_y = max_y - min_y if max_y > min_y else 1.0

    for i, loop in enumerate(face.loops):
        cx, cy = coords_2d[i]
        factor_u = (cx - min_x) / span_x
        factor_v = (cy - min_y) / span_y
        if flip_u:
            factor_u = 1.0 - factor_u
        if flip_v:
            factor_v = 1.0 - factor_v
        u = u0 + factor_u * (u1 - u0)
        v = v0 + factor_v * (v1 - v0)
        loop[uv_lay].uv = (u, v)


def mark_sharp_edges_by_angle(bm, threshold_deg=35.0):
    """Mark edges sharp if face angle exceeds threshold for clean hard-surface normals."""
    rad = math.radians(threshold_deg)
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            try:
                angle = edge.calc_face_angle()
                if angle > rad:
                    edge.smooth = False
                else:
                    edge.smooth = True
            except Exception:
                edge.smooth = False
        else:
            edge.smooth = False


# Constant UV Atlas coordinates (u0, v0, u1, v1)
UV_CASING_PLASTIC   = (0.010, 0.540, 0.460, 0.990)
UV_CHIN_PANEL       = (0.000, 0.375, 1.000, 0.500)
UV_REAR_IO_BAY      = (0.000, 0.125, 0.500, 0.375)
UV_RATING_LABEL     = (0.500, 0.125, 1.000, 0.375)
UV_LOUVERS          = (0.010, 0.005, 0.460, 0.120)
UV_STAND_METAL      = (0.485, 0.005, 0.690, 0.120)
UV_VESA_PLATE       = (0.700, 0.005, 0.940, 0.120)
UV_NEUTRAL_BUFFER   = (0.940, 0.005, 0.990, 0.055)


# -------------------------------------------------------------
# High-Fidelity Low-Poly Mesh Builders
# -------------------------------------------------------------

def build_stand_base_mesh(mesh, materials):
    """
    Build Stand_Base:
    12-sided beveled heavy base plate with dual chamfered tier,
    recessed neck collar and 4 molded bottom rubber feet pads.
    Tris count: ~86 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    n_sides = 12
    r_x = 0.110
    r_y = 0.085
    z_bot = 0.000
    z_mid = 0.007
    z_top = 0.012

    v_bot = []
    v_mid = []
    v_top = []
    for i in range(n_sides):
        ang = 2.0 * math.pi * i / n_sides
        bx = r_x * math.cos(ang)
        by = r_y * math.sin(ang) - 0.015
        v_bot.append(bm.verts.new(Vector((bx, by, z_bot))))
        v_mid.append(bm.verts.new(Vector((bx, by, z_mid))))
        v_top.append(bm.verts.new(Vector((bx * 0.93, by * 0.93, z_top))))

    f_b = bm.faces.new(list(reversed(v_bot)))
    f_b.material_index = 0; set_face_uv_rect(bm, f_b, UV_NEUTRAL_BUFFER)

    for i in range(n_sides):
        i_n = (i + 1) % n_sides
        f_sw = bm.faces.new([v_bot[i], v_bot[i_n], v_mid[i_n], v_mid[i]])
        f_sw.material_index = 0; set_face_uv_rect(bm, f_sw, UV_CASING_PLASTIC)

        f_ch = bm.faces.new([v_mid[i], v_mid[i_n], v_top[i_n], v_top[i]])
        f_ch.material_index = 0; set_face_uv_rect(bm, f_ch, UV_CASING_PLASTIC)

    # Top accent plate (Brushed Gunmetal)
    f_t = bm.faces.new(v_top)
    f_t.material_index = 2; set_face_uv_rect(bm, f_t, UV_STAND_METAL)

    # 4 Molded rubber feet pads underneath at Z=0.000m
    feet_pos = [(-0.075, -0.065), (0.075, -0.065), (-0.075, 0.035), (0.075, 0.035)]
    for fx, fy in feet_pos:
        v_f = [
            bm.verts.new(Vector((fx - 0.014, fy - 0.010, z_bot))),
            bm.verts.new(Vector((fx + 0.014, fy - 0.010, z_bot))),
            bm.verts.new(Vector((fx + 0.014, fy + 0.010, z_bot))),
            bm.verts.new(Vector((fx - 0.014, fy + 0.010, z_bot)))
        ]
        f_pad = bm.faces.new(v_f)
        f_pad.material_index = 0; set_face_uv_rect(bm, f_pad, UV_NEUTRAL_BUFFER)

    # Neck collar boss
    sx, sy = 0.025, 0.020
    y_c = -0.020
    v_col_b = [
        bm.verts.new(Vector((-sx, y_c - sy, z_top))),
        bm.verts.new(Vector(( sx, y_c - sy, z_top))),
        bm.verts.new(Vector(( sx, y_c + sy, z_top))),
        bm.verts.new(Vector((-sx, y_c + sy, z_top)))
    ]
    v_col_t = [
        bm.verts.new(Vector((-sx, y_c - sy, 0.018))),
        bm.verts.new(Vector(( sx, y_c - sy, 0.018))),
        bm.verts.new(Vector(( sx, y_c + sy, 0.018))),
        bm.verts.new(Vector((-sx, y_c + sy, 0.018)))
    ]
    for i in range(4):
        i_n = (i + 1) % 4
        f_c = bm.faces.new([v_col_b[i], v_col_b[i_n], v_col_t[i_n], v_col_t[i]])
        f_c.material_index = 0; set_face_uv_rect(bm, f_c, UV_CASING_PLASTIC)
    f_ct = bm.faces.new(v_col_t); f_ct.material_index = 0; set_face_uv_rect(bm, f_ct, UV_CASING_PLASTIC)

    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


def build_stand_neck_mesh(mesh, materials):
    """
    Build Stand_Neck:
    Curved sculpted neck with octagonal cross-section,
    beveled cable pass-through portal, dual clevis knuckles,
    cylindrical pivot axle and side tension adjustment knob.
    Tris count: ~100 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    def make_oct_ring(bm, rx, ry, cx, cy, z):
        verts = []
        for i in range(8):
            ang = 2.0 * math.pi * i / 8.0 + (math.pi / 8.0)
            verts.append(bm.verts.new(Vector((cx + rx * math.cos(ang), cy + ry * math.sin(ang), z))))
        return verts

    r0 = make_oct_ring(bm, 0.022, 0.018, 0, -0.020, 0.012)
    r1 = make_oct_ring(bm, 0.021, 0.017, 0, -0.020, 0.070)
    r2 = make_oct_ring(bm, 0.020, 0.016, 0, -0.020, 0.130)
    r3 = make_oct_ring(bm, 0.019, 0.015, 0, -0.020, 0.220)

    for i in range(8):
        i_n = (i + 1) % 8
        f_lo = bm.faces.new([r0[i], r0[i_n], r1[i_n], r1[i]])
        f_lo.material_index = 0; set_face_uv_rect(bm, f_lo, UV_CASING_PLASTIC)

        f_hi = bm.faces.new([r2[i], r2[i_n], r3[i_n], r3[i]])
        f_hi.material_index = 0; set_face_uv_rect(bm, f_hi, UV_CASING_PLASTIC)

    # Middle section: side walls around the cable pass-through slot
    for i in [1, 2, 5, 6]:
        i_n = (i + 1) % 8
        f_m = bm.faces.new([r1[i], r1[i_n], r2[i_n], r2[i]])
        f_m.material_index = 0; set_face_uv_rect(bm, f_m, UV_CASING_PLASTIC)

    # Dual tilt clevis hinge knuckles at top (Z: 0.240m, Y: -0.020m)
    for x_side in [-0.018, 0.018]:
        v_k_l = []
        v_k_r = []
        for a in range(6):
            ang = 2.0 * math.pi * a / 6.0
            ky = -0.020 + 0.012 * math.cos(ang)
            kz =  0.240 + 0.012 * math.sin(ang)
            v_k_l.append(bm.verts.new(Vector((x_side - 0.005, ky, kz))))
            v_k_r.append(bm.verts.new(Vector((x_side + 0.005, ky, kz))))
        for a in range(6):
            a_n = (a + 1) % 6
            f_k = bm.faces.new([v_k_l[a], v_k_l[a_n], v_k_r[a_n], v_k_r[a]])
            f_k.material_index = 0; set_face_uv_rect(bm, f_k, UV_CASING_PLASTIC)
        f_kl = bm.faces.new(list(reversed(v_k_l))); f_kl.material_index = 0; set_face_uv_rect(bm, f_kl, UV_CASING_PLASTIC)
        f_kr = bm.faces.new(v_k_r); f_kr.material_index = 0; set_face_uv_rect(bm, f_kr, UV_CASING_PLASTIC)

    # Cylindrical metal pivot axle pin & side adjustment knob
    v_ax_l = []
    v_ax_r = []
    for a in range(6):
        ang = 2.0 * math.pi * a / 6.0
        ay = -0.020 + 0.007 * math.cos(ang)
        az =  0.240 + 0.007 * math.sin(ang)
        v_ax_l.append(bm.verts.new(Vector((-0.026, ay, az))))
        v_ax_r.append(bm.verts.new(Vector(( 0.030, ay, az))))
    for a in range(6):
        a_n = (a + 1) % 6
        f_ax = bm.faces.new([v_ax_l[a], v_ax_l[a_n], v_ax_r[a_n], v_ax_r[a]])
        f_ax.material_index = 2; set_face_uv_rect(bm, f_ax, UV_STAND_METAL)
    f_al = bm.faces.new(list(reversed(v_ax_l))); f_al.material_index = 2; set_face_uv_rect(bm, f_al, UV_STAND_METAL)
    f_ar = bm.faces.new(v_ax_r); f_ar.material_index = 2; set_face_uv_rect(bm, f_ar, UV_STAND_METAL)

    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


def build_display_housing_mesh(mesh, materials):
    """
    Build Display_Housing:
    - 100% physically sealed screen cavities with solid recessed backing beds.
    - Zero see-through gaps from any viewing angle.
    - Beveled crosshair divider bars, stepped inner bezel frame.
    - 3D tactile buttons on front chin panel (Power button, status LED, OSD buttons).
    - Rear electronics pack with VESA 100x100 screw bosses, louvers,
      rating sticker and recessed I/O bay with 3D BNC barrels.
    Tris count: ~234 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    x_w = 0.265
    z_h = 0.155
    y_front = 0.020
    y_bevel = 0.016
    y_back  = -0.010
    x_bev = x_w - 0.005
    z_bev = z_h - 0.005

    # 1. Front Outer Bezel Loop
    v_fb = [
        bm.verts.new(Vector((-x_bev, y_front, -z_bev))),
        bm.verts.new(Vector(( x_bev, y_front, -z_bev))),
        bm.verts.new(Vector(( x_bev, y_front,  z_bev))),
        bm.verts.new(Vector((-x_bev, y_front,  z_bev)))
    ]

    v_ob = [
        bm.verts.new(Vector((-x_w, y_bevel, -z_h))),
        bm.verts.new(Vector(( x_w, y_bevel, -z_h))),
        bm.verts.new(Vector(( x_w, y_bevel,  z_h))),
        bm.verts.new(Vector((-x_w, y_bevel,  z_h)))
    ]

    v_rb = [
        bm.verts.new(Vector((-x_w, y_back, -z_h))),
        bm.verts.new(Vector(( x_w, y_back, -z_h))),
        bm.verts.new(Vector(( x_w, y_back,  z_h))),
        bm.verts.new(Vector((-x_w, y_back,  z_h)))
    ]

    for i in range(4):
        i_n = (i + 1) % 4
        f_ch = bm.faces.new([v_ob[i], v_ob[i_n], v_fb[i_n], v_fb[i]])
        f_ch.material_index = 0; set_face_uv_rect(bm, f_ch, UV_CASING_PLASTIC)

        f_sw = bm.faces.new([v_rb[i], v_rb[i_n], v_ob[i_n], v_ob[i]])
        f_sw.material_index = 0; set_face_uv_rect(bm, f_sw, UV_CASING_PLASTIC)

    # 2. Front Bezel Faces
    z_chin_top = -0.133
    z_scr_top  =  0.147
    x_scr_edge =  0.258

    # Chin face
    v_chin = [
        bm.verts.new(Vector((-x_bev, y_front, -z_bev))),
        bm.verts.new(Vector(( x_bev, y_front, -z_bev))),
        bm.verts.new(Vector(( x_bev, y_front, z_chin_top))),
        bm.verts.new(Vector((-x_bev, y_front, z_chin_top)))
    ]
    f_chin = bm.faces.new(v_chin)
    f_chin.material_index = 0
    set_face_uv_rect(bm, f_chin, UV_CHIN_PANEL, flip_u=True)

    # Top Bezel strip
    v_top_strip = [
        bm.verts.new(Vector((-x_bev, y_front, z_scr_top))),
        bm.verts.new(Vector(( x_bev, y_front, z_scr_top))),
        bm.verts.new(Vector(( x_bev, y_front, z_bev))),
        bm.verts.new(Vector((-x_bev, y_front, z_bev)))
    ]
    f_ts = bm.faces.new(v_top_strip)
    f_ts.material_index = 0; set_face_uv_rect(bm, f_ts, UV_CASING_PLASTIC)

    # Left & Right Bezel strips
    v_left_strip = [
        bm.verts.new(Vector((x_scr_edge, y_front, z_chin_top))),
        bm.verts.new(Vector((x_bev,      y_front, z_chin_top))),
        bm.verts.new(Vector((x_bev,      y_front, z_scr_top))),
        bm.verts.new(Vector((x_scr_edge, y_front, z_scr_top)))
    ]
    f_ls = bm.faces.new(v_left_strip)
    f_ls.material_index = 0; set_face_uv_rect(bm, f_ls, UV_CASING_PLASTIC)

    v_right_strip = [
        bm.verts.new(Vector((-x_bev,      y_front, z_chin_top))),
        bm.verts.new(Vector((-x_scr_edge, y_front, z_chin_top))),
        bm.verts.new(Vector((-x_scr_edge, y_front, z_scr_top))),
        bm.verts.new(Vector((-x_bev,      y_front, z_scr_top)))
    ]
    f_rs = bm.faces.new(v_right_strip)
    f_rs.material_index = 0; set_face_uv_rect(bm, f_rs, UV_CASING_PLASTIC)

    # 3. 3D Beveled Central Crosshair Divider Bars
    dx_bar = 0.003
    dz_bar = 0.003
    y_bar  = 0.0205 # Protrudes 0.5mm in front of bezel face

    # Vertical bar (top and bottom sections)
    v_vbt = [
        bm.verts.new(Vector((-dx_bar, y_bar, dz_bar))),
        bm.verts.new(Vector(( dx_bar, y_bar, dz_bar))),
        bm.verts.new(Vector(( dx_bar, y_bar, z_scr_top))),
        bm.verts.new(Vector((-dx_bar, y_bar, z_scr_top)))
    ]
    f_vbt = bm.faces.new(v_vbt); f_vbt.material_index = 0; set_face_uv_rect(bm, f_vbt, UV_CASING_PLASTIC)

    v_vbb = [
        bm.verts.new(Vector((-dx_bar, y_bar, z_chin_top))),
        bm.verts.new(Vector(( dx_bar, y_bar, z_chin_top))),
        bm.verts.new(Vector(( dx_bar, y_bar, -dz_bar))),
        bm.verts.new(Vector((-dx_bar, y_bar, -dz_bar)))
    ]
    f_vbb = bm.faces.new(v_vbb); f_vbb.material_index = 0; set_face_uv_rect(bm, f_vbb, UV_CASING_PLASTIC)

    # Horizontal bar (left and right sections)
    v_hbl = [
        bm.verts.new(Vector((dx_bar,     y_bar, -dz_bar))),
        bm.verts.new(Vector((x_scr_edge, y_bar, -dz_bar))),
        bm.verts.new(Vector((x_scr_edge, y_bar,  dz_bar))),
        bm.verts.new(Vector((dx_bar,     y_bar,  dz_bar)))
    ]
    f_hbl = bm.faces.new(v_hbl); f_hbl.material_index = 0; set_face_uv_rect(bm, f_hbl, UV_CASING_PLASTIC)

    v_hbr = [
        bm.verts.new(Vector((-x_scr_edge, y_bar, -dz_bar))),
        bm.verts.new(Vector((-dx_bar,     y_bar, -dz_bar))),
        bm.verts.new(Vector((-dx_bar,     y_bar,  dz_bar))),
        bm.verts.new(Vector((-x_scr_edge, y_bar,  dz_bar)))
    ]
    f_hbr = bm.faces.new(v_hbr); f_hbr.material_index = 0; set_face_uv_rect(bm, f_hbr, UV_CASING_PLASTIC)

    # Center junction cap
    v_cap = [
        bm.verts.new(Vector((-dx_bar, y_bar, -dz_bar))),
        bm.verts.new(Vector(( dx_bar, y_bar, -dz_bar))),
        bm.verts.new(Vector(( dx_bar, y_bar,  dz_bar))),
        bm.verts.new(Vector((-dx_bar, y_bar,  dz_bar)))
    ]
    f_cap = bm.faces.new(v_cap); f_cap.material_index = 0; set_face_uv_rect(bm, f_cap, UV_CASING_PLASTIC)

    # 4. SEALED SCREEN BAYS & SOLID RECESSED BED FLOORS
    # For each of the 4 quadrants:
    # Model 4 sloped inner bezel walls + 1 solid bed floor at Y = +0.0160m
    # Front opening at Y = +0.0190m, Bed floor at Y = +0.0160m (3mm recessed cavity)
    y_lip = 0.0190
    y_bed = 0.0160

    bay_configs = [
        # (x_min, x_max, z_min, z_max) front opening
        ( dx_bar,      x_scr_edge,  dz_bar,     z_scr_top), # Top-Left
        (-x_scr_edge, -dx_bar,      dz_bar,     z_scr_top), # Top-Right
        ( dx_bar,      x_scr_edge,  z_chin_top, -dz_bar),   # Bottom-Left
        (-x_scr_edge, -dx_bar,      z_chin_top, -dz_bar)    # Bottom-Right
    ]

    for bx0, bx1, bz0, bz1 in bay_configs:
        # Front lip opening (Y = y_lip)
        v_lip = [
            bm.verts.new(Vector((bx0, y_lip, bz0))),
            bm.verts.new(Vector((bx1, y_lip, bz0))),
            bm.verts.new(Vector((bx1, y_lip, bz1))),
            bm.verts.new(Vector((bx0, y_lip, bz1)))
        ]
        # Bed floor (Y = y_bed, slightly expanded by 1.5mm so screen tucks cleanly under lip)
        dbx = 0.0015 if bx0 > 0 else -0.0015
        f_x0 = bx0 - dbx
        f_x1 = bx1 + dbx
        f_z0 = bz0 - 0.0015
        f_z1 = bz1 + 0.0015

        v_bed = [
            bm.verts.new(Vector((f_x0, y_bed, f_z0))),
            bm.verts.new(Vector((f_x1, y_bed, f_z0))),
            bm.verts.new(Vector((f_x1, y_bed, f_z1))),
            bm.verts.new(Vector((f_x0, y_bed, f_z1)))
        ]

        # 4 sloped inner bezel walls
        for i in range(4):
            i_n = (i + 1) % 4
            f_wall = bm.faces.new([v_lip[i], v_lip[i_n], v_bed[i_n], v_bed[i]])
            f_wall.material_index = 0; set_face_uv_rect(bm, f_wall, UV_CASING_PLASTIC)

        # Solid bed floor behind the screen
        f_floor = bm.faces.new(v_bed)
        f_floor.material_index = 0; set_face_uv_rect(bm, f_floor, UV_NEUTRAL_BUFFER)

    # 5. Tactile 3D Buttons on Chin Panel
    # Circular Power Button (extrudes 2.5mm forward to Y=+0.0225m)
    pwr_x = -0.215
    pwr_z = -0.143
    pwr_r = 0.006
    v_pwr_b = []
    v_pwr_f = []
    for a in range(6):
        ang = 2.0 * math.pi * a / 6.0
        px = pwr_x + pwr_r * math.cos(ang)
        pz = pwr_z + pwr_r * math.sin(ang)
        v_pwr_b.append(bm.verts.new(Vector((px, y_front, pz))))
        v_pwr_f.append(bm.verts.new(Vector((px, 0.0225, pz))))
    for a in range(6):
        a_n = (a + 1) % 6
        f_ps = bm.faces.new([v_pwr_b[a], v_pwr_b[a_n], v_pwr_f[a_n], v_pwr_f[a]])
        f_ps.material_index = 0; set_face_uv_rect(bm, f_ps, UV_CASING_PLASTIC)
    f_pcap = bm.faces.new(v_pwr_f); f_pcap.material_index = 0; set_face_uv_rect(bm, f_pcap, (0.930, 0.400, 0.990, 0.470))

    # Glowing Green Power Status LED Jewel Dome
    led_x = -0.235
    v_led = []
    for a in range(6):
        ang = 2.0 * math.pi * a / 6.0
        lx = led_x + 0.0035 * math.cos(ang)
        lz = pwr_z + 0.0035 * math.sin(ang)
        v_led.append(bm.verts.new(Vector((lx, 0.0215, lz))))
    f_led = bm.faces.new(v_led); f_led.material_index = 0; set_face_uv_rect(bm, f_led, (0.940, 0.380, 0.980, 0.420))

    # 4 Tactile OSD Buttons (MENU, ▲, ▼, AUTO)
    osd_xs = [-0.130, -0.095, -0.060, -0.025]
    for ox in osd_xs:
        v_ob = [
            bm.verts.new(Vector((ox - 0.008, y_front, -0.147))),
            bm.verts.new(Vector((ox + 0.008, y_front, -0.147))),
            bm.verts.new(Vector((ox + 0.008, y_front, -0.139))),
            bm.verts.new(Vector((ox - 0.008, y_front, -0.139)))
        ]
        v_of = [
            bm.verts.new(Vector((ox - 0.008, 0.0215, -0.147))),
            bm.verts.new(Vector((ox + 0.008, 0.0215, -0.147))),
            bm.verts.new(Vector((ox + 0.008, 0.0215, -0.139))),
            bm.verts.new(Vector((ox - 0.008, 0.0215, -0.139)))
        ]
        for i in range(4):
            i_n = (i + 1) % 4
            f_os = bm.faces.new([v_ob[i], v_ob[i_n], v_of[i_n], v_of[i]])
            f_os.material_index = 0; set_face_uv_rect(bm, f_os, UV_CASING_PLASTIC)
        f_of = bm.faces.new(v_of); f_of.material_index = 0; set_face_uv_rect(bm, f_of, (0.750, 0.400, 0.920, 0.460))

    # 6. Rear Main Housing & VESA Electronics Pack
    rx_w = 0.090
    rz_h = 0.090
    y_rear_pack = -0.034

    v_pack_b = [
        bm.verts.new(Vector((-rx_w, y_back, -rz_h))),
        bm.verts.new(Vector(( rx_w, y_back, -rz_h))),
        bm.verts.new(Vector(( rx_w, y_back,  rz_h))),
        bm.verts.new(Vector((-rx_w, y_back,  rz_h)))
    ]

    f_r_bot = bm.faces.new([v_rb[0], v_rb[1], v_pack_b[1], v_pack_b[0]])
    f_r_bot.material_index = 0; set_face_uv_rect(bm, f_r_bot, UV_CASING_PLASTIC, flip_u=False)

    f_r_top = bm.faces.new([v_pack_b[3], v_pack_b[2], v_rb[2], v_rb[3]])
    f_r_top.material_index = 0; set_face_uv_rect(bm, f_r_top, UV_CASING_PLASTIC, flip_u=False)

    f_r_r = bm.faces.new([v_pack_b[1], v_rb[1], v_rb[2], v_pack_b[2]])
    f_r_r.material_index = 0; set_face_uv_rect(bm, f_r_r, UV_CASING_PLASTIC, flip_u=False)

    f_r_l = bm.faces.new([v_rb[0], v_pack_b[0], v_pack_b[3], v_rb[3]])
    f_r_l.material_index = 0; set_face_uv_rect(bm, f_r_l, UV_CASING_PLASTIC, flip_u=False)

    # Specification Rating Sticker on left rear wing
    y_lbl = y_back - 0.0003
    v_lbl = [
        bm.verts.new(Vector((-0.210, y_lbl, -0.025))),
        bm.verts.new(Vector((-0.115, y_lbl, -0.025))),
        bm.verts.new(Vector((-0.115, y_lbl,  0.025))),
        bm.verts.new(Vector((-0.210, y_lbl,  0.025)))
    ]
    f_lbl = bm.faces.new(v_lbl); f_lbl.material_index = 0; set_face_uv_rect(bm, f_lbl, UV_RATING_LABEL, flip_u=False)

    # Rear Electronics Box Faces
    z_vesa_top =  0.040
    z_io_split  = -0.015
    y_io_recess = -0.022

    # Top Louver Face
    v_louvers = [
        bm.verts.new(Vector((-rx_w, y_rear_pack, z_vesa_top))),
        bm.verts.new(Vector(( rx_w, y_rear_pack, z_vesa_top))),
        bm.verts.new(Vector(( rx_w, y_rear_pack, rz_h))),
        bm.verts.new(Vector((-rx_w, y_rear_pack, rz_h)))
    ]
    f_louvers = bm.faces.new(v_louvers); f_louvers.material_index = 0; set_face_uv_rect(bm, f_louvers, UV_LOUVERS, flip_u=False)

    # Middle VESA 100x100 Mounting Plate Face
    v_vesa = [
        bm.verts.new(Vector((-rx_w, y_rear_pack, z_io_split))),
        bm.verts.new(Vector(( rx_w, y_rear_pack, z_io_split))),
        bm.verts.new(Vector(( rx_w, y_rear_pack, z_vesa_top))),
        bm.verts.new(Vector((-rx_w, y_rear_pack, z_vesa_top)))
    ]
    f_vesa = bm.faces.new(v_vesa); f_vesa.material_index = 0; set_face_uv_rect(bm, f_vesa, UV_VESA_PLATE, flip_u=False)

    # Bottom Recessed I/O Bay
    v_io_recess = [
        bm.verts.new(Vector((-rx_w + 0.008, y_io_recess, -rz_h + 0.008))),
        bm.verts.new(Vector(( rx_w - 0.008, y_io_recess, -rz_h + 0.008))),
        bm.verts.new(Vector(( rx_w - 0.008, y_io_recess, z_io_split - 0.008))),
        bm.verts.new(Vector((-rx_w + 0.008, y_io_recess, z_io_split - 0.008)))
    ]
    f_io = bm.faces.new(v_io_recess); f_io.material_index = 0; set_face_uv_rect(bm, f_io, UV_REAR_IO_BAY, flip_u=False)

    # Recess connecting walls
    v_io_rim = [
        bm.verts.new(Vector((-rx_w, y_rear_pack, -rz_h))),
        bm.verts.new(Vector(( rx_w, y_rear_pack, -rz_h))),
        bm.verts.new(Vector(( rx_w, y_rear_pack, z_io_split))),
        bm.verts.new(Vector((-rx_w, y_rear_pack, z_io_split)))
    ]
    for i in range(4):
        i_n = (i + 1) % 4
        f_rw = bm.faces.new([v_io_rim[i], v_io_rim[i_n], v_io_recess[i_n], v_io_recess[i]])
        f_rw.material_index = 0; set_face_uv_rect(bm, f_rw, UV_CASING_PLASTIC)

    # 4 3D BNC Metal Barrels inside the recessed I/O bay
    for b in range(4):
        bnc_x = -0.060 + b * 0.024
        bnc_z = -0.055
        v_bnc_b = []
        v_bnc_t = []
        for a in range(6):
            ang = 2.0 * math.pi * a / 6.0
            bx = bnc_x + 0.0045 * math.cos(ang)
            bz = bnc_z + 0.0045 * math.sin(ang)
            v_bnc_b.append(bm.verts.new(Vector((bx, y_io_recess, bz))))
            v_bnc_t.append(bm.verts.new(Vector((bx, y_io_recess - 0.007, bz))))
        for a in range(6):
            a_n = (a + 1) % 6
            f_bc = bm.faces.new([v_bnc_b[a], v_bnc_b[a_n], v_bnc_t[a_n], v_bnc_t[a]])
            f_bc.material_index = 2; set_face_uv_rect(bm, f_bc, UV_STAND_METAL)
        f_bcap = bm.faces.new(list(reversed(v_bnc_t))); f_bcap.material_index = 2; set_face_uv_rect(bm, f_bcap, UV_STAND_METAL)

    # Pack outer side walls
    f_ps_top = bm.faces.new([v_pack_b[3], v_pack_b[2], v_louvers[2], v_louvers[3]])
    f_ps_top.material_index = 0; set_face_uv_rect(bm, f_ps_top, UV_CASING_PLASTIC)

    f_ps_bot = bm.faces.new([v_pack_b[0], v_io_rim[0], v_io_rim[1], v_pack_b[1]])
    f_ps_bot.material_index = 0; set_face_uv_rect(bm, f_ps_bot, UV_CASING_PLASTIC)

    f_ps_l   = bm.faces.new([v_pack_b[0], v_pack_b[3], v_louvers[3], v_io_rim[0]])
    f_ps_l.material_index = 0; set_face_uv_rect(bm, f_ps_l, UV_CASING_PLASTIC)

    f_ps_r   = bm.faces.new([v_pack_b[2], v_pack_b[1], v_io_rim[1], v_louvers[2]])
    f_ps_r.material_index = 0; set_face_uv_rect(bm, f_ps_r, UV_CASING_PLASTIC)

    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


def build_single_screen_mesh(mesh, materials, quad_index):
    """
    Build a single screen quadrant mesh:
    0: Top-Left (CAM 01), 1: Top-Right (CAM 02), 2: Bottom-Left (CAM 03), 3: Bottom-Right (CAM 04)
    Flat quad with face pointing +Y, origin at its geometric center.
    Sits flush inside the recessed screen bed, overlapping the inner bezel lip.
    Material: M_Screen (Slot 1).
    Tris count: 2 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    hw = 0.1287
    hh = 0.0732 if quad_index in [0, 1] else 0.0647

    v0 = bm.verts.new(Vector((-hw, 0.0, -hh)))
    v1 = bm.verts.new(Vector(( hw, 0.0, -hh)))
    v2 = bm.verts.new(Vector(( hw, 0.0,  hh)))
    v3 = bm.verts.new(Vector((-hw, 0.0,  hh)))

    f = bm.faces.new([v0, v1, v2, v3])
    f.material_index = 1

    uv_rects = [
        (0.000, 0.500, 0.500, 1.000),
        (0.500, 0.500, 1.000, 1.000),
        (0.000, 0.000, 0.500, 0.500),
        (0.500, 0.000, 1.000, 0.500)
    ]

    set_face_uv_rect(bm, f, uv_rects[quad_index], flip_u=True, flip_v=False)

    bm.to_mesh(mesh)
    bm.free()


# -------------------------------------------------------------
# Assembly, Export and Automated QA Pipeline
# -------------------------------------------------------------

def assemble_and_export():
    """Main execution: Build hierarchy, export FBX, run automated QA, and save manifest."""
    setup_clean_scene()

    print("[INFO] Creating textures and materials...")
    atlas_img, screen_img = load_or_create_textures()
    materials = create_materials(atlas_img, screen_img)

    # 1. Root Empty: SEC_Monitor_CCTV_Quad_LCD at (0, 0, 0)
    root_empty = bpy.data.objects.new("SEC_Monitor_CCTV_Quad_LCD", None)
    root_empty.empty_display_type = 'PLAIN_AXES'
    root_empty.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root_empty)

    # 2. Stand_Base (child of Root)
    mesh_base = bpy.data.meshes.new("Stand_Base")
    obj_base = bpy.data.objects.new("Stand_Base", mesh_base)
    build_stand_base_mesh(mesh_base, materials)
    bpy.context.collection.objects.link(obj_base)
    obj_base.parent = root_empty

    # 3. Stand_Neck (child of Root)
    mesh_neck = bpy.data.meshes.new("Stand_Neck")
    obj_neck = bpy.data.objects.new("Stand_Neck", mesh_neck)
    build_stand_neck_mesh(mesh_neck, materials)
    bpy.context.collection.objects.link(obj_neck)
    obj_neck.parent = root_empty

    # 4. Display_Tilt_Pivot (Empty at hinge, child of Root)
    tilt_pivot_loc = Vector((0.000, -0.020, 0.240))
    tilt_empty = bpy.data.objects.new("Display_Tilt_Pivot", None)
    tilt_empty.empty_display_type = 'PLAIN_AXES'
    tilt_empty.location = tilt_pivot_loc
    bpy.context.collection.objects.link(tilt_empty)
    tilt_empty.parent = root_empty

    const = tilt_empty.constraints.new(type='LIMIT_ROTATION')
    const.use_limit_x = True
    const.min_x = math.radians(-10.0)
    const.max_x = math.radians(10.0)
    const.use_limit_y = True
    const.min_y = 0.0
    const.max_y = 0.0
    const.use_limit_z = True
    const.min_z = 0.0
    const.max_z = 0.0
    const.owner_space = 'LOCAL'

    tilt_empty["tilt_axis"] = "X"
    tilt_empty["min_angle_deg"] = -10.0
    tilt_empty["max_angle_deg"] = 10.0
    tilt_empty["action"] = "TILT_SCREEN"

    # 5. Display_Housing (Mesh, child of Display_Tilt_Pivot)
    mesh_housing = bpy.data.meshes.new("Display_Housing")
    obj_housing = bpy.data.objects.new("Display_Housing", mesh_housing)
    build_display_housing_mesh(mesh_housing, materials)
    bpy.context.collection.objects.link(obj_housing)
    obj_housing.location = Vector((0.0, 0.0, 0.0))
    obj_housing.parent = tilt_empty

    # 6. Four Screen Quad Meshes (children of Display_Housing)
    # Screen planes sit at Y = +0.0166m inside the recessed cavities, overlapping the lip
    screen_configs = [
        ("Screen_Top_Left",     0, Vector(( 0.1305, 0.0166,  0.0750))),
        ("Screen_Top_Right",    1, Vector((-0.1305, 0.0166,  0.0750))),
        ("Screen_Bottom_Left",  2, Vector(( 0.1305, 0.0166, -0.0665))),
        ("Screen_Bottom_Right", 3, Vector((-0.1305, 0.0166, -0.0665)))
    ]

    screen_objs = []
    for name, q_idx, loc in screen_configs:
        mesh_scr = bpy.data.meshes.new(name)
        obj_scr = bpy.data.objects.new(name, mesh_scr)
        build_single_screen_mesh(mesh_scr, materials, q_idx)
        bpy.context.collection.objects.link(obj_scr)
        obj_scr.location = loc
        obj_scr.parent = obj_housing
        screen_objs.append(obj_scr)

    bpy.context.view_layer.update()

    # Save Blend file
    blend_path = os.path.join(EXPORTS_DIR, "SEC_Monitor_CCTV_Quad_LCD.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[INFO] Saved blend file: {blend_path}")

    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        try:
            os.remove(blend1_path)
            print(f"[INFO] Removed backup file: {blend1_path}")
        except Exception:
            pass

    # Select only required objects for FBX export
    bpy.ops.object.select_all(action='DESELECT')
    root_empty.select_set(True)
    obj_base.select_set(True)
    obj_neck.select_set(True)
    tilt_empty.select_set(True)
    obj_housing.select_set(True)
    for scr in screen_objs:
        scr.select_set(True)

    fbx_path = os.path.join(EXPORTS_DIR, "SEC_Monitor_CCTV_Quad_LCD.fbx")
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        object_types={'MESH', 'EMPTY'},
        axis_forward='-Z',
        axis_up='Y',
        apply_unit_scale=True,
        bake_space_transform=False,
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        path_mode='AUTO'
    )
    print(f"[INFO] Exported FBX: {fbx_path}")

    # -------------------------------------------------------------
    # Automated Re-Import QA Test
    # -------------------------------------------------------------
    print("\n--- RUNNING AUTOMATED QA ON EXPORTED FBX ---")
    setup_clean_scene()
    bpy.ops.import_scene.fbx(filepath=fbx_path)

    qa_objects = {obj.name: obj for obj in bpy.context.scene.objects}
    print(f"[QA] Imported objects ({len(qa_objects)}): {list(qa_objects.keys())}")

    # 1. Validate Root Empty
    assert "SEC_Monitor_CCTV_Quad_LCD" in qa_objects, "Root empty missing!"
    root_qa = qa_objects["SEC_Monitor_CCTV_Quad_LCD"]
    assert root_qa.location.length < 1e-4, f"Root not at origin: {root_qa.location}"

    # 2. Validate Pivot Empty
    assert "Display_Tilt_Pivot" in qa_objects, "Display_Tilt_Pivot empty missing!"
    pivot_qa = qa_objects["Display_Tilt_Pivot"]
    assert pivot_qa.parent == root_qa, "Display_Tilt_Pivot not child of root!"

    # 3. Validate Meshes
    expected_meshes = [
        "Stand_Base",
        "Stand_Neck",
        "Display_Housing",
        "Screen_Top_Left",
        "Screen_Top_Right",
        "Screen_Bottom_Left",
        "Screen_Bottom_Right"
    ]
    total_tris = 0

    for m_name in expected_meshes:
        assert m_name in qa_objects, f"Mesh {m_name} missing from FBX!"
        m_obj = qa_objects[m_name]

        bm_qa = bmesh.new()
        bm_qa.from_mesh(m_obj.data)
        bmesh.ops.triangulate(bm_qa, faces=bm_qa.faces)
        tris = len(bm_qa.faces)
        total_tris += tris
        bm_qa.free()

        assert len(m_obj.data.uv_layers) > 0, f"Mesh {m_name} has no UV layer!"

        mat_names = [slot.name for slot in m_obj.material_slots]
        assert "M_Security_Atlas" in mat_names, f"Mesh {m_name} missing M_Security_Atlas!"
        assert "M_Screen" in mat_names, f"Mesh {m_name} missing M_Screen!"
        assert "M_Metal" in mat_names, f"Mesh {m_name} missing M_Metal!"

    # 4. Validate Hierarchy Relationships
    housing_qa = qa_objects["Display_Housing"]
    assert housing_qa.parent == pivot_qa, "Display_Housing not child of Display_Tilt_Pivot!"
    for scr_name in ["Screen_Top_Left", "Screen_Top_Right", "Screen_Bottom_Left", "Screen_Bottom_Right"]:
        assert qa_objects[scr_name].parent == housing_qa, f"{scr_name} not child of Display_Housing!"

    base_qa = qa_objects["Stand_Base"]
    assert base_qa.parent == root_qa, "Stand_Base not child of Root!"
    neck_qa = qa_objects["Stand_Neck"]
    assert neck_qa.parent == root_qa, "Stand_Neck not child of Root!"

    print(f"[QA] TOTAL TRIANGLES: {total_tris} (Budget limit: 500)")
    assert total_tris <= 500, f"Triangle budget exceeded: {total_tris} > 500!"

    manifest_data = {
        "SEC_Monitor_CCTV_Quad_LCD": {
            "asset_name": "SEC_Monitor_CCTV_Quad_LCD",
            "fbx_path": "exports/SEC_Monitor_CCTV_Quad_LCD.fbx",
            "blend_path": "exports/SEC_Monitor_CCTV_Quad_LCD.blend",
            "tris_count": total_tris,
            "mesh_count": len(expected_meshes),
            "empty_count": 2,
            "materials": ["M_Security_Atlas", "M_Screen", "M_Metal"],
            "status": "SUCCESS"
        }
    }
    manifest_path = os.path.join(EXPORTS_DIR, "manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=2)
    print(f"[QA] Manifest written to {manifest_path}")
    print("[QA] ALL CHECKS PASSED SUCCESSFULLY!\n")


if __name__ == "__main__":
    assemble_and_export()
