"""
SEC_Console_Camera_Joystick Generator Script (Enhanced Keycaps & Precision Rear UV)
Industrial Low-Poly Security & CCTV Asset Pack
Upper Budget Limit: 600 triangles

Hierarchy:
SEC_Console_Camera_Joystick (Root Empty at 0, 0, 0, bottom desk center)
 └── Console_Housing (Mesh, child of Root)
      ├── Display (Mesh, child of Console_Housing, M_Screen)
      ├── Button_Array (Mesh, child of Console_Housing, M_Security_Atlas)
      ├── Joystick_Base (Mesh, child of Console_Housing, M_Security_Atlas)
      └── Joystick_Pivot (Empty, child of Console_Housing, -30°..+30° on local X/Z)
           └── Joystick_Lever (Mesh, child of Joystick_Pivot, M_Security_Atlas)
                └── Joystick_Grip (Mesh, child of Joystick_Lever, M_Security_Atlas)

Materials:
    Slot 0: M_Security_Atlas (2048x2048 Ultra-Sharp Atlas)
    Slot 1: M_Screen (1024x512 LCD Telemetry Display)
    Slot 2: M_Emission (Status LEDs)
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
    """High-resolution bold fonts for 2048x2048 atlas and 1024x512 screen."""
    try:
        font_xl = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 54)
        font_lg = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 40)
        font_md = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 30)
        font_sm = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 24)
        font_xs = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 19)
        title_xl = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 56)
        title_lg = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 42)
        title_md = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 32)
        title_sm = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 24)
        title_xs = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 19)
    except Exception:
        font_xl = font_lg = font_md = font_sm = font_xs = ImageFont.load_default()
        title_xl = title_lg = title_md = title_sm = title_xs = ImageFont.load_default()
    return font_xl, font_lg, font_md, font_sm, font_xs, title_xl, title_lg, title_md, title_sm, title_xs


def generate_screen_texture():
    """Generate 1024x512 Ultra-Sharp PTZ Telemetry LCD Texture (T_Screen.png)."""
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    out_path = os.path.join(EXPORTS_DIR, "T_Screen.png")
    if not HAS_PIL:
        return out_path

    w, h = 1024, 512
    img = Image.new("RGBA", (w, h), (10, 20, 28, 255))
    draw = ImageDraw.Draw(img)
    f_xl, f_lg, f_md, f_sm, f_xs, t_xl, t_lg, t_md, t_sm, t_xs = get_fonts()

    # LCD matrix pixel grid lines
    for y in range(0, h, 4):
        draw.line([(0, y), (w, y)], fill=(6, 14, 22, 255))

    # Outer display bezel frame
    draw.rectangle([10, 10, w - 10, h - 10], outline=(30, 90, 120, 255), width=3)
    draw.rectangle([18, 18, w - 18, h - 18], outline=(18, 55, 75, 255), width=2)

    # Line 1: Camera title & PTZ Mode
    draw.text((40, 42), "CAM 01: [MAIN GATE DOME]  PTZ", fill=(70, 245, 255, 255), font=t_lg)

    # Line 2: Pan & Tilt angles
    draw.text((40, 125), "PAN: 142.5° CW     TILT: -15.0°", fill=(240, 250, 255, 255), font=f_lg)

    # Line 3: Optical Zoom level & Focus
    draw.text((40, 205), "ZOOM: 12.0x OPTICAL    FOCUS: AUTO", fill=(50, 255, 170, 255), font=f_lg)

    # Line 4: Active Preset & Protocol
    draw.text((40, 285), "PRESET: [04 NORTH BARRIER]", fill=(240, 250, 255, 255), font=f_lg)

    # Line 5: Comm telemetry & Link status
    draw.text((40, 365), "PELCO-D  9600-8-N-1  ADDR: 01", fill=(80, 230, 255, 255), font=f_md)

    # Bottom status banner
    badges = ["AUTO-IRIS", "SPEED: HIGH", "PATROL: ON", "LINK: OK"]
    for i, b in enumerate(badges):
        bx = 40 + i * 235
        draw.rectangle([bx, 430, bx + 215, 482], fill=(14, 42, 58, 255), outline=(40, 140, 175, 255), width=2)
        draw.text((bx + 20, 442), b, fill=(100, 245, 255, 255), font=t_sm)

    img.save(out_path, format="PNG")
    print(f"[INFO] Generated 1024x512 T_Screen.png: {out_path}")
    return out_path


# Define Keycap matrix for 3D buttons (4 rows x 5 columns)
KEYCAP_MATRIX = [
    [("1", 40), ("2", 40), ("3", 40), ("CAM", 30), ("MON", 30)],
    [("4", 40), ("5", 40), ("6", 40), ("PRESET", 24), ("SHOT", 28)],
    [("7", 40), ("8", 40), ("9", 40), ("IRIS +", 24), ("IRIS -", 24)],
    [("CLR", 30), ("0", 40), ("ENT", 30), ("FOCUS+", 22), ("FOCUS-", 22)]
]


def generate_security_atlas_texture():
    """Generate 2048x2048 Ultra-Sharp Texture Atlas (T_Security_Atlas.png)."""
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    out_path = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")
    if not HAS_PIL:
        return out_path

    w, h = 2048, 2048
    img = Image.new("RGBA", (w, h), (26, 28, 32, 255))
    draw = ImageDraw.Draw(img)
    f_xl, f_lg, f_md, f_sm, f_xs, t_xl, t_lg, t_md, t_sm, t_xs = get_fonts()

    # Base noise/texture across top casing
    for y in range(0, 1200, 4):
        for x in range(0, 2048, 8):
            if (x + y) % 9 == 0:
                draw.point((x, y), fill=(32, 35, 40, 255))

    # Coordinate converter for Zone 1 (inclined top panel)
    def x_to_px(x_val):
        return int(round(2048.0 * (x_val + 0.160) / 0.320))

    def y_to_py(y_val):
        fv = (y_val + 0.110) / 0.220
        return int(round(1200.0 * (1.0 - fv)))

    # =========================================================================
    # ZONE 1: CONSOLE TOP INCLINED PANEL (X: 0..2048, Y: 0..1200)
    # =========================================================================
    for y in range(0, 1200):
        shade = int(24 + (y / 1200.0) * 10)
        draw.line([(0, y), (2048, y)], fill=(shade, shade + 1, shade + 3, 255))
    draw.line([(0, 0), (2048, 0)], fill=(75, 82, 95, 255), width=3)
    draw.line([(0, 1196), (2048, 1196)], fill=(15, 17, 20, 255), width=3)

    # 1.1 Brand & Product Header (Top-Left: X: 128..900, Y: 30..110)
    draw.text((128, 30), "SEC-PTZ CONTROLLER PRO", fill=(255, 255, 255, 255), font=t_lg)
    draw.text((128, 85), "3-AXIS INDUSTRIAL CCTV SURVEILLANCE KEYBOARD & JOYSTICK", fill=(160, 180, 205, 255), font=f_sm)

    # Top-Right System Info
    draw.text((1250, 35), "PROTOCOL: PELCO-D / PELCO-P / VISCA", fill=(140, 160, 190, 255), font=f_sm)
    draw.text((1250, 75), "SYSTEM STATUS: OPTIMAL  |  BUS: RS-485 / RS-422 SERIAL", fill=(100, 120, 150, 255), font=f_xs)

    # 1.2 Display Bezel Surround Frame (Matching 3D cavity X: [-0.140, -0.020] -> [128, 896], Y: [0.025, 0.085] -> [136, 464])
    # Bezel outer outline around cavity
    draw.rectangle([118, 126, 906, 474], fill=(16, 18, 22, 255), outline=(65, 75, 90, 255), width=3)
    # Inside cavity socket (clean dark background where 3D Display sits)
    draw.rectangle([126, 134, 898, 466], fill=(10, 12, 14, 255), outline=(35, 42, 52, 255), width=2)
    # Sub-label directly above the display bezel
    draw.text((130, 108), "[ TELEMETRY LCD MONITOR ]", fill=(120, 140, 170, 255), font=f_xs)

    # Status LED indicators directly below display bezel (Y = 495)
    led_labels = [("PWR", (40, 220, 80, 255)), ("TX", (245, 190, 30, 255)), ("RX", (40, 210, 245, 255)), ("ALARM", (245, 45, 45, 255))]
    for i, (lbl, lcol) in enumerate(led_labels):
        lx = 170 + i * 190
        # LED socket housing
        draw.ellipse([lx, 492, lx + 22, 514], fill=(18, 20, 24, 255), outline=(60, 70, 85, 255), width=2)
        # LED lit lens center
        draw.ellipse([lx + 4, 496, lx + 18, 510], fill=lcol)
        draw.text((lx + 30, 494), lbl, fill=(225, 235, 250, 255), font=f_sm)

    # 1.3 Keypad Section (Matching 3D button locations pixel-for-pixel!)
    # Recessed tray plate behind buttons
    draw.rectangle([118, 555, 960, 1140], fill=(20, 22, 27, 255), outline=(48, 56, 68, 255), width=2)
    draw.text((220, 575), "[ NUMERIC SELECT ]", fill=(130, 150, 180, 255), font=f_sm)
    draw.text((680, 575), "[ CAM / PRESET ]", fill=(130, 150, 180, 255), font=f_sm)

    x_cols = [-0.130, -0.105, -0.080, -0.050, -0.024]
    widths = [0.016, 0.016, 0.016, 0.022, 0.022]
    y_rows = [-0.020, -0.042, -0.064, -0.086]
    kh = 0.016

    # Draw pixel-perfect recessed well sockets under each 3D button
    for r in range(4):
        ky = y_rows[r]
        py_min = y_to_py(ky + kh * 0.5)
        py_max = y_to_py(ky - kh * 0.5)
        for c in range(5):
            kx = x_cols[c]
            kw = widths[c]
            px_min = x_to_px(kx - kw * 0.5)
            px_max = x_to_px(kx + kw * 0.5)
            # Socket border slightly larger than button (+4px)
            draw.rectangle([px_min - 4, py_min - 4, px_max + 4, py_max + 4], fill=(14, 16, 20, 255), outline=(40, 48, 60, 255), width=2)

    # 1.4 Joystick Base Well & PTZ Compass Rose (Center: X=0.080 -> 1536, Y=-0.010 -> 655)
    cx = x_to_px(0.080)
    cy = y_to_py(-0.010)

    # Outer protective dial rings
    draw.ellipse([cx - 310, cy - 310, cx + 310, cy + 310], outline=(55, 65, 80, 255), width=2)
    draw.ellipse([cx - 280, cy - 280, cx + 280, cy + 280], outline=(75, 90, 110, 255), width=2)
    draw.ellipse([cx - 260, cy - 260, cx + 260, cy + 260], fill=(18, 20, 24, 255), outline=(45, 52, 62, 255), width=2)

    # Compass degree ticks
    for deg in range(0, 360, 15):
        rad = math.radians(deg)
        r1 = 280
        r2 = 305 if deg % 45 == 0 else 296
        x1 = cx + int(r1 * math.cos(rad))
        y1 = cy + int(r1 * math.sin(rad))
        x2 = cx + int(r2 * math.cos(rad))
        y2 = cy + int(r2 * math.sin(rad))
        draw.line([(x1, y1), (x2, y2)], fill=(120, 135, 155, 255), width=3 if deg % 45 == 0 else 2)

    # Cardinal Direction Labels (Safe inside bounds, zero cutoffs!)
    draw.text((cx - 60, cy - 355), "▲ TILT UP", fill=(255, 255, 255, 255), font=t_md)
    draw.text((cx - 80, cy + 325), "▼ TILT DOWN", fill=(255, 255, 255, 255), font=t_md)
    draw.text((cx - 440, cy - 14), "◀ PAN LEFT", fill=(255, 255, 255, 255), font=t_md)
    draw.text((cx + 325, cy - 14), "PAN RIGHT ▶", fill=(255, 255, 255, 255), font=t_md)

    # Diagonal Zoom Labels (Outside the joystick boot)
    draw.text((cx - 250, cy - 250), "↺ ZOOM -", fill=(80, 220, 255, 255), font=t_sm)
    draw.text((cx + 140, cy - 250), "ZOOM + ↻", fill=(80, 220, 255, 255), font=t_sm)

    # Quick Buttons centered below the joystick zone (Y = 1045..1135)
    q_labels = ["AUTO TOUR", "SPEED HI/LO", "LOCK"]
    q_w = 200
    q_gap = 25
    q_start_x = cx - int((3 * q_w + 2 * q_gap) / 2)
    for i, qlbl in enumerate(q_labels):
        qx = q_start_x + i * (q_w + q_gap)
        qy = 1045
        draw.rectangle([qx, qy, qx + q_w, qy + 85], fill=(24, 27, 33, 255), outline=(65, 75, 90, 255), width=2)
        try:
            bbox = t_sm.getbbox(qlbl)
            tw = bbox[2] - bbox[0]
            tx = qx + (q_w - tw) // 2
        except Exception:
            tx = qx + 20
        draw.text((tx, qy + 26), qlbl, fill=(230, 240, 255, 255), font=t_sm)

    # =========================================================================
    # ZONE 2: REAR I/O CONNECTIONS PANEL (X: 0..1350, Y: 1220..1650, Height: 430px)
    # =========================================================================
    draw.rectangle([0, 1220, 1350, 1650], fill=(20, 22, 25, 255))
    draw.rectangle([15, 1235, 1335, 1635], fill=(26, 29, 34, 255), outline=(65, 75, 90, 255), width=3)
    draw.text((40, 1250), "REAR INTERFACE: RS-485 / RS-422 SERIAL BUS & DC 12V", fill=(255, 255, 255, 255), font=f_lg)

    # RS-485 Terminal Block (Green)
    draw.rectangle([50, 1320, 360, 1480], fill=(18, 75, 38, 255), outline=(40, 150, 70, 255), width=3)
    draw.text((70, 1335), "RS-485 CONTROL", fill=(240, 255, 245, 255), font=f_md)
    term_pins_485 = ["A (+)", "B (-)", "GND", "+12V"]
    for i, tp in enumerate(term_pins_485):
        px = 70 + i * 70
        draw.ellipse([px + 10, 1380, px + 40, 1410], fill=(210, 215, 225, 255), outline=(50, 55, 65, 255), width=2)
        draw.text((px, 1430), tp, fill=(220, 245, 225, 255), font=f_xs)

    # RS-422 Terminal Block (Blue)
    draw.rectangle([400, 1320, 750, 1480], fill=(22, 45, 95, 255), outline=(50, 95, 190, 255), width=3)
    draw.text((420, 1335), "RS-422 FULL DUPLEX", fill=(235, 245, 255, 255), font=f_md)
    term_pins_422 = ["TX+", "TX-", "RX+", "RX-"]
    for i, tp in enumerate(term_pins_422):
        px = 420 + i * 80
        draw.ellipse([px + 10, 1380, px + 40, 1410], fill=(210, 215, 225, 255), outline=(50, 55, 65, 255), width=2)
        draw.text((px + 5, 1430), tp, fill=(210, 230, 255, 255), font=f_xs)

    # RJ-45 Ethernet Network Port
    draw.rectangle([800, 1320, 980, 1480], fill=(16, 18, 22, 255), outline=(90, 100, 115, 255), width=3)
    draw.text((825, 1335), "ETHERNET", fill=(220, 230, 245, 255), font=f_md)
    draw.rectangle([840, 1385, 940, 1455], fill=(30, 34, 40, 255), outline=(130, 140, 155, 255), width=2)
    draw.text((865, 1410), "LAN", fill=(70, 220, 255, 255), font=f_sm)

    # DC 12V Coaxial Power Jack & Rocker Switch
    draw.rectangle([1030, 1320, 1310, 1480], fill=(16, 18, 22, 255), outline=(80, 90, 105, 255), width=3)
    draw.ellipse([1060, 1370, 1120, 1430], fill=(45, 50, 60, 255), outline=(140, 150, 165, 255), width=3)
    draw.ellipse([1080, 1390, 1100, 1410], fill=(210, 180, 80, 255))
    draw.text((1050, 1445), "DC 12V 1A", fill=(210, 220, 235, 255), font=f_xs)

    # Power switch
    draw.rectangle([1170, 1365, 1270, 1435], fill=(180, 30, 30, 255), outline=(90, 100, 115, 255), width=2)
    draw.text((1205, 1385), "I / O", fill=(255, 255, 255, 255), font=f_md)

    # =========================================================================
    # ZONE 3: SPECIFICATION RATING PLATE (X: 1370..2048, Y: 1220..1650)
    # =========================================================================
    draw.rectangle([1370, 1220, 2048, 1650], fill=(20, 22, 25, 255))
    draw.rectangle([1390, 1235, 2025, 1635], fill=(242, 245, 248, 255), outline=(95, 105, 115, 255), width=3)
    draw.rectangle([1400, 1245, 2015, 1625], outline=(160, 170, 180, 255), width=2)

    draw.text((1420, 1260), "PTZ CAMERA CONTROLLER", fill=(10, 15, 20, 255), font=t_md)
    draw.text((1420, 1315), "MODEL: SEC-KBD-300   3-AXIS PTZ KEYBOARD", fill=(15, 20, 25, 255), font=f_sm)
    draw.text((1420, 1350), "POWER: DC 12V 1.0A 12W MAX", fill=(15, 20, 25, 255), font=f_sm)
    draw.text((1420, 1385), "SERIAL: KBD-2026-88194-C", fill=(15, 20, 25, 255), font=f_sm)
    draw.text((1420, 1420), "BAUD: 2400 / 4800 / 9600 / 19200 BPS", fill=(15, 20, 25, 255), font=f_sm)

    for bx in range(1420, 1760, 6):
        if (bx * 7) % 11 < 6:
            draw.line([(bx, 1465), (bx, 1545)], fill=(5, 10, 15, 255), width=4)
    draw.text((1465, 1555), "*KBD202688194C*", fill=(10, 15, 20, 255), font=f_sm)

    cert_labels = ["CE", "FCC", "RoHS", "WEEE", "UL"]
    for i, c in enumerate(cert_labels):
        cx = 1830
        cy = 1450 + i * 32
        draw.text((cx, cy), f"[{c}]", fill=(10, 15, 20, 255), font=f_sm)

    # =========================================================================
    # ZONE 4: DARK RUBBER BOOT & GRIP TEXTURE (X: 0..800, Y: 1670..2048)
    # =========================================================================
    for y in range(1670, 2048):
        shade = int(25 + ((y - 1670) / 378.0) * 12)
        draw.line([(0, y), (800, y)], fill=(shade, shade, shade + 2, 255))
    for gy in range(1680, 2040, 16):
        draw.line([(10, gy), (790, gy)], fill=(15, 15, 18, 255), width=3)
    draw.rectangle([5, 1675, 795, 2043], outline=(55, 60, 70, 255), width=2)

    # =========================================================================
    # ZONE 5: CHROME SHAFT METAL (X: 820..1350, Y: 1670..2048)
    # =========================================================================
    for y in range(1670, 2048):
        shade = int(140 + ((y - 1670) / 378.0) * 55)
        draw.line([(820, y), (1350, y)], fill=(shade, shade + 2, shade + 5, 255))
    draw.rectangle([824, 1674, 1346, 2044], outline=(85, 95, 110, 255), width=3)

    # =========================================================================
    # ZONE 6: 20 TACTILE 3D KEYCAP TEXTURES (X: 1360..2030, Y: 1670..2030)
    # 4 rows x 5 columns = 20 individual keycaps with razor-sharp typography!
    # =========================================================================
    draw.rectangle([1360, 1670, 2030, 2030], fill=(22, 24, 28, 255))
    for r in range(4):
        for c in range(5):
            lbl, font_sz = KEYCAP_MATRIX[r][c]
            kx = 1365 + c * 132
            ky = 1675 + r * 88
            kw, kh = 124, 80
            draw.rectangle([kx, ky, kx + kw, ky + kh], fill=(36, 40, 48, 255), outline=(75, 85, 100, 255), width=2)
            draw.rectangle([kx + 4, ky + 4, kx + kw - 4, ky + kh - 4], fill=(28, 31, 38, 255), outline=(55, 62, 75, 255), width=1)
            # Choose font
            if font_sz == 40:
                f_cur = t_lg
            elif font_sz == 30:
                f_cur = t_md
            elif font_sz == 28:
                f_cur = t_sm
            elif font_sz == 24:
                f_cur = f_sm
            else:
                f_cur = f_xs

            # Center text in keycap
            try:
                bbox = f_cur.getbbox(lbl)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
                tx = kx + (kw - tw) // 2
                ty = ky + (kh - th) // 2 - 2
            except Exception:
                tx = kx + 20
                ty = ky + 25
            draw.text((tx, ty), lbl, fill=(255, 255, 255, 255), font=f_cur)

    # =========================================================================
    # ZONE 7: NEUTRAL DARK BUFFER (X: 1980..2048, Y: 0..68)
    # Guaranteed 100% clean solid dark polymer/metal - zero text bleed!
    # =========================================================================
    draw.rectangle([1980, 0, 2048, 68], fill=(26, 28, 32, 255))

    img.save(out_path, format="PNG")
    print(f"[INFO] Generated 2048x2048 T_Security_Atlas.png: {out_path}")
    return out_path


def get_keycap_uv(r, c):
    """Return normalized [u0, v0, u1, v1] for keycap at row r, column c."""
    kx = 1365 + c * 132
    ky = 1675 + r * 88
    kw, kh = 124, 80
    u0 = kx / 2048.0
    u1 = (kx + kw) / 2048.0
    v0 = (2048.0 - (ky + kh)) / 2048.0
    v1 = (2048.0 - ky) / 2048.0
    return (u0, v0, u1, v1)


def load_or_create_textures():
    """Ensure textures exist and load them into Blender data."""
    atlas_path = generate_security_atlas_texture()
    screen_path = generate_screen_texture()

    if os.path.exists(atlas_path):
        atlas_img = bpy.data.images.load(atlas_path, check_existing=True)
        atlas_img.reload()
    else:
        atlas_img = bpy.data.images.new("T_Security_Atlas", width=2048, height=2048, alpha=True)

    if os.path.exists(screen_path):
        screen_img = bpy.data.images.load(screen_path, check_existing=True)
        screen_img.reload()
    else:
        screen_img = bpy.data.images.new("T_Screen", width=1024, height=512, alpha=True)

    return atlas_img, screen_img


def create_materials(atlas_img, screen_img):
    """
    Slot 0: M_Security_Atlas
    Slot 1: M_Screen
    Slot 2: M_Emission
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
    tex0.interpolation = 'Linear'
    links0.new(tex0.outputs['Color'], bsdf0.inputs['Base Color'])

    bsdf0.inputs['Roughness'].default_value = 0.40
    bsdf0.inputs['Metallic'].default_value = 0.15
    mat_atlas.diffuse_color = (0.16, 0.17, 0.20, 1.0)
    materials["M_Security_Atlas"] = mat_atlas

    # Slot 1: M_Screen (PTZ Telemetry LCD)
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
    tex1.interpolation = 'Linear'
    links1.new(tex1.outputs['Color'], bsdf1.inputs['Base Color'])
    links1.new(tex1.outputs['Color'], bsdf1.inputs['Emission Color'])

    bsdf1.inputs['Emission Strength'].default_value = 1.60
    bsdf1.inputs['Roughness'].default_value = 0.08
    bsdf1.inputs['Metallic'].default_value = 0.02
    mat_screen.diffuse_color = (0.10, 0.45, 0.50, 1.0)
    materials["M_Screen"] = mat_screen

    # Slot 2: M_Emission (Status LEDs)
    mat_emission = bpy.data.materials.get("M_Emission")
    if not mat_emission:
        mat_emission = bpy.data.materials.new(name="M_Emission")
    mat_emission.use_nodes = True
    nodes2 = mat_emission.node_tree.nodes
    links2 = mat_emission.node_tree.links
    nodes2.clear()

    out2 = nodes2.new(type='ShaderNodeOutputMaterial')
    out2.location = (300, 0)
    bsdf2 = nodes2.new(type='ShaderNodeBsdfPrincipled')
    bsdf2.location = (0, 0)
    links2.new(bsdf2.outputs['BSDF'], out2.inputs['Surface'])

    bsdf2.inputs['Base Color'].default_value = (0.2, 1.0, 0.4, 1.0)
    bsdf2.inputs['Emission Color'].default_value = (0.2, 1.0, 0.4, 1.0)
    bsdf2.inputs['Emission Strength'].default_value = 5.0
    bsdf2.inputs['Roughness'].default_value = 0.15
    mat_emission.diffuse_color = (0.2, 1.0, 0.4, 1.0)
    materials["M_Emission"] = mat_emission

    return materials


def attach_standard_materials(mesh, materials):
    """Ensure materials are present in the exact order specified: Slot 0 Atlas, Slot 1 Screen, Slot 2 Emission."""
    mesh.materials.clear()
    mesh.materials.append(materials["M_Security_Atlas"])  # Slot 0
    mesh.materials.append(materials["M_Screen"])          # Slot 1
    mesh.materials.append(materials["M_Emission"])        # Slot 2


def set_face_uv_rect(bm, face, uv_rect, flip_u=False, flip_v=False):
    """Map face planar projections to a rectangular UV sub-region [u0, v0, u1, v1]."""
    face.normal_update()
    u0, v0, u1, v1 = uv_rect
    uv_lay = bm.loops.layers.uv.verify()

    coords_2d = []
    normal = face.normal
    nx, ny, nz = abs(normal.x), abs(normal.y), abs(normal.z)

    if (nz >= nx and nz >= ny) or (nx < 1e-4 and ny < 1e-4 and nz < 1e-4):
        for loop in face.loops:
            coords_2d.append((loop.vert.co.x, loop.vert.co.y))
    elif nx >= ny and nx >= nz:
        for loop in face.loops:
            coords_2d.append((loop.vert.co.y, loop.vert.co.z))
    else:
        for loop in face.loops:
            coords_2d.append((loop.vert.co.x, loop.vert.co.z))

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


def apply_continuous_top_uv(bm, face, uv_rect, x_bounds, y_bounds):
    """
    Continuous planar projection across the inclined top surface of the console.
    """
    face.normal_update()
    u0, v0, u1, v1 = uv_rect
    xmin, xmax = x_bounds
    ymin, ymax = y_bounds
    x_span = xmax - xmin if xmax > xmin else 1.0
    y_span = ymax - ymin if ymax > ymin else 1.0
    uv_lay = bm.loops.layers.uv.verify()

    for loop in face.loops:
        x = loop.vert.co.x
        y = loop.vert.co.y
        fu = (x - xmin) / x_span
        fv = (y - ymin) / y_span
        u = u0 + fu * (u1 - u0)
        v = v0 + fv * (v1 - v0)
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
UV_CONSOLE_TOP      = (0.000, 0.414, 1.000, 1.000) # Y: 0..1200
UV_REAR_IO          = (0.000, 0.194, 0.659, 0.404) # X: 0..1350, Y: 1220..1650
UV_RATING_LABEL     = (0.669, 0.194, 0.992, 0.404) # X: 1370..2048, Y: 1220..1650
UV_RUBBER_BOOT      = (0.000, 0.000, 0.391, 0.185) # Y: 1670..2048
UV_CHROME_SHAFT     = (0.401, 0.000, 0.659, 0.185) # Y: 1670..2048
UV_BUTTON_CAP       = (0.664, 0.000, 0.991, 0.185) # Y: 1670..2048
UV_NEUTRAL_BUFFER   = (0.967, 0.967, 1.000, 1.000) # Guaranteed clean solid dark buffer (Zone 7)


# -------------------------------------------------------------
# High-Density Low-Poly Mesh Builders
# -------------------------------------------------------------

def build_console_housing_mesh(mesh, materials):
    """
    Build Console_Housing:
    Ergonomic desktop PTZ console chassis (Width 320mm, Depth 220mm).
    Root pivot at (0, 0, 0) bottom center on desk.
    - Front low edge (Z = 0.025m), rear high edge (Z = 0.075m).
    - Recessed display window cavity on left side (Width 120mm, Height 60mm, Depth 4mm).
    - Rear vertical I/O panel with serial terminals and specification sticker (100% un-mirrored!).
    Tris count: ~130 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    x_hw = 0.160       # 320mm console width
    y_front = -0.110   # Front edge (near user)
    y_rear  =  0.110   # Rear edge (away from user)
    z_f = 0.025        # Front height 25mm
    z_r = 0.075        # Rear height 75mm

    x_bounds = (-x_hw, x_hw)
    y_bounds = (y_front, y_rear)

    # 1. Outer Chassis Vertices
    v_b_fl = bm.verts.new(Vector((-x_hw, y_front, 0.000)))
    v_b_fr = bm.verts.new(Vector(( x_hw, y_front, 0.000)))
    v_b_rr = bm.verts.new(Vector(( x_hw, y_rear,  0.000)))
    v_b_rl = bm.verts.new(Vector((-x_hw, y_rear,  0.000)))

    v_t_fl = bm.verts.new(Vector((-x_hw, y_front, z_f)))
    v_t_fr = bm.verts.new(Vector(( x_hw, y_front, z_f)))
    v_t_rr = bm.verts.new(Vector(( x_hw, y_rear,  z_r)))
    v_t_rl = bm.verts.new(Vector((-x_hw, y_rear,  z_r)))

    # Bottom desk face
    f_bot = bm.faces.new([v_b_fl, v_b_rl, v_b_rr, v_b_fr])
    f_bot.material_index = 0; set_face_uv_rect(bm, f_bot, UV_NEUTRAL_BUFFER)

    # Front vertical face (near user)
    f_front = bm.faces.new([v_b_fl, v_b_fr, v_t_fr, v_t_fl])
    f_front.material_index = 0; set_face_uv_rect(bm, f_front, UV_NEUTRAL_BUFFER)

    # Left side wall
    f_left = bm.faces.new([v_b_rl, v_b_fl, v_t_fl, v_t_rl])
    f_left.material_index = 0; set_face_uv_rect(bm, f_left, UV_NEUTRAL_BUFFER)

    # Right side wall
    f_right = bm.faces.new([v_b_fr, v_b_rr, v_t_rr, v_t_fr])
    f_right.material_index = 0; set_face_uv_rect(bm, f_right, UV_NEUTRAL_BUFFER)

    # Rear vertical panel split:
    # Viewed from behind (+Y looking -Y): Screen Left is +X, Screen Right is -X
    # We place I/O section at X: [+0.160 down to -0.020] (width 180mm)
    # We place Rating plate at X: [-0.020 down to -0.160] (width 140mm)
    v_r_mid_b = bm.verts.new(Vector((-0.020, y_rear, 0.000)))
    v_r_mid_t = bm.verts.new(Vector((-0.020, y_rear, z_r)))

    # Left I/O Panel (Screen Left from behind, X: -0.020 to +0.160)
    # With flip_u=True, it reads naturally from left to right!
    f_rear_io = bm.faces.new([v_r_mid_b, v_b_rr, v_t_rr, v_r_mid_t])
    f_rear_io.material_index = 0
    set_face_uv_rect(bm, f_rear_io, UV_REAR_IO, flip_u=True)

    # Right Rating Plate (Screen Right from behind, X: -0.160 to -0.020)
    # With flip_u=True, it reads naturally from left to right!
    f_rear_rp = bm.faces.new([v_b_rl, v_r_mid_b, v_r_mid_t, v_t_rl])
    f_rear_rp.material_index = 0
    set_face_uv_rect(bm, f_rear_rp, UV_RATING_LABEL, flip_u=True)

    # 2. Recessed Display Window Cavity on Left Side of Inclined Top:
    # X: [-0.140, -0.020] (Width 120mm)
    # Y: [+0.025, +0.085] (Depth 60mm)
    def plane_z(y):
        return z_f + (y - y_front) / (y_rear - y_front) * (z_r - z_f)

    wx0, wx1 = -0.140, -0.020
    wy0, wy1 =  0.025,  0.085
    wz0, wz1 = plane_z(wy0), plane_z(wy1)

    v_w_fl = bm.verts.new(Vector((wx0, wy0, wz0)))
    v_w_fr = bm.verts.new(Vector((wx1, wy0, wz0)))
    v_w_rr = bm.verts.new(Vector((wx1, wy1, wz1)))
    v_w_rl = bm.verts.new(Vector((wx0, wy1, wz1)))

    recess_d = 0.004
    v_wb_fl = bm.verts.new(Vector((wx0 + 0.002, wy0 + 0.002, wz0 - recess_d)))
    v_wb_fr = bm.verts.new(Vector((wx1 - 0.002, wy0 + 0.002, wz0 - recess_d)))
    v_wb_rr = bm.verts.new(Vector((wx1 - 0.002, wy1 - 0.002, wz1 - recess_d)))
    v_wb_rl = bm.verts.new(Vector((wx0 + 0.002, wy1 - 0.002, wz1 - recess_d)))

    f_ww_f = bm.faces.new([v_w_fl, v_w_fr, v_wb_fr, v_wb_fl]); f_ww_f.material_index = 0; set_face_uv_rect(bm, f_ww_f, UV_NEUTRAL_BUFFER)
    f_ww_r = bm.faces.new([v_w_fr, v_w_rr, v_wb_rr, v_wb_fr]); f_ww_r.material_index = 0; set_face_uv_rect(bm, f_ww_r, UV_NEUTRAL_BUFFER)
    f_ww_b = bm.faces.new([v_w_rr, v_w_rl, v_wb_rl, v_wb_rr]); f_ww_b.material_index = 0; set_face_uv_rect(bm, f_ww_b, UV_NEUTRAL_BUFFER)
    f_ww_l = bm.faces.new([v_w_rl, v_w_fl, v_wb_fl, v_wb_rl]); f_ww_l.material_index = 0; set_face_uv_rect(bm, f_ww_l, UV_NEUTRAL_BUFFER)

    f_w_bed = bm.faces.new([v_wb_fl, v_wb_fr, v_wb_rr, v_wb_rl])
    f_w_bed.material_index = 0; set_face_uv_rect(bm, f_w_bed, UV_NEUTRAL_BUFFER)

    # 3. Top Inclined Panel Surface surrounding the Window (Continuous UV mapping)
    f_top_front = bm.faces.new([v_t_fl, v_t_fr, v_w_fr, v_w_fl])
    f_top_front.material_index = 0
    apply_continuous_top_uv(bm, f_top_front, UV_CONSOLE_TOP, x_bounds, y_bounds)

    f_top_rear = bm.faces.new([v_w_rl, v_w_rr, v_t_rr, v_t_rl])
    f_top_rear.material_index = 0
    apply_continuous_top_uv(bm, f_top_rear, UV_CONSOLE_TOP, x_bounds, y_bounds)

    f_top_left = bm.faces.new([v_t_fl, v_w_fl, v_w_rl, v_t_rl])
    f_top_left.material_index = 0
    apply_continuous_top_uv(bm, f_top_left, UV_CONSOLE_TOP, x_bounds, y_bounds)

    f_top_right = bm.faces.new([v_w_fr, v_t_fr, v_t_rr, v_w_rr])
    f_top_right.material_index = 0
    apply_continuous_top_uv(bm, f_top_right, UV_CONSOLE_TOP, x_bounds, y_bounds)

    # 4. Four molded bottom rubber feet
    feet_coords = [(-0.135, -0.085), (0.135, -0.085), (-0.135, 0.085), (0.135, 0.085)]
    for fx, fy in feet_coords:
        v_ft = [
            bm.verts.new(Vector((fx - 0.012, fy - 0.012, 0.000))),
            bm.verts.new(Vector((fx + 0.012, fy - 0.012, 0.000))),
            bm.verts.new(Vector((fx + 0.012, fy + 0.012, 0.000))),
            bm.verts.new(Vector((fx - 0.012, fy + 0.012, 0.000)))
        ]
        f_ft = bm.faces.new(v_ft)
        f_ft.material_index = 0; set_face_uv_rect(bm, f_ft, UV_NEUTRAL_BUFFER)

    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


def build_display_mesh(mesh, materials):
    """
    Build Display:
    Alphanumeric LCD status telemetry display sitting flush inside the recessed cavity.
    Origin at its geometric center (X: -0.080, Y: +0.055, Z: 0.062).
    Width: 116mm, Height: 56mm. Tilted to match console slope.
    Material: M_Screen (Slot 1).
    Tris count: 2 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    hw = 0.058
    hh = 0.028

    v_fl = bm.verts.new(Vector((-hw, -hh, 0.0)))
    v_fr = bm.verts.new(Vector(( hw, -hh, 0.0)))
    v_rr = bm.verts.new(Vector(( hw,  hh, 0.0)))
    v_rl = bm.verts.new(Vector((-hw,  hh, 0.0)))

    f = bm.faces.new([v_fl, v_fr, v_rr, v_rl])
    f.material_index = 1 # M_Screen

    uv_lay = bm.loops.layers.uv.verify()
    f.loops[0][uv_lay].uv = (0.0, 0.0)
    f.loops[1][uv_lay].uv = (1.0, 0.0)
    f.loops[2][uv_lay].uv = (1.0, 1.0)
    f.loops[3][uv_lay].uv = (0.0, 1.0)

    bm.to_mesh(mesh)
    bm.free()


def build_button_array_mesh(mesh, materials):
    """
    Build Button_Array:
    Tactile 3D keys sitting on the inclined front-left surface of the console.
    Each key has its matching high-resolution label directly mapped to its top cap!
    Material: M_Security_Atlas (Slot 0).
    Tris count: ~180 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    y_front = -0.110
    y_rear  =  0.110
    z_f = 0.025
    z_r = 0.075
    def base_z(y):
        return z_f + (y - y_front) / (y_rear - y_front) * (z_r - z_f)

    btn_h = 0.0035

    # 4 rows x 5 columns:
    # 3 Numeric columns on Left (X: -0.130, -0.105, -0.080)
    # 2 Function columns on Right (X: -0.050, -0.024)
    x_cols = [-0.130, -0.105, -0.080, -0.050, -0.024]
    widths = [0.016, 0.016, 0.016, 0.022, 0.022]
    # Rows along Y from front to back:
    # Row 0 (top): Y = -0.020 (Keys 1, 2, 3, CAM, MON)
    # Row 1: Y = -0.042 (Keys 4, 5, 6, PRESET, SHOT)
    # Row 2: Y = -0.064 (Keys 7, 8, 9, IRIS+, IRIS-)
    # Row 3 (bottom): Y = -0.086 (Keys CLR, 0, ENT, FOCUS+, FOCUS-)
    y_rows = [-0.020, -0.042, -0.064, -0.086]

    for r in range(4):
        ky = y_rows[r]
        kh = 0.016
        hh = kh * 0.5
        bz = base_z(ky)

        for c in range(5):
            kx = x_cols[c]
            kw = widths[c]
            hw = kw * 0.5

            v_b = [
                bm.verts.new(Vector((kx - hw, ky - hh, bz))),
                bm.verts.new(Vector((kx + hw, ky - hh, bz))),
                bm.verts.new(Vector((kx + hw, ky + hh, bz + 0.003))),
                bm.verts.new(Vector((kx - hw, ky + hh, bz + 0.003)))
            ]
            v_t = [
                bm.verts.new(Vector((kx - hw + 0.001, ky - hh + 0.001, bz + btn_h))),
                bm.verts.new(Vector((kx + hw - 0.001, ky - hh + 0.001, bz + btn_h))),
                bm.verts.new(Vector((kx + hw - 0.001, ky + hh - 0.001, bz + 0.003 + btn_h))),
                bm.verts.new(Vector((kx - hw + 0.001, ky + hh - 0.001, bz + 0.003 + btn_h)))
            ]

            # Top cap of button with dedicated keycap label!
            f_top = bm.faces.new(v_t)
            f_top.material_index = 0
            uv_cap = get_keycap_uv(r, c)
            set_face_uv_rect(bm, f_top, uv_cap)

            # 4 beveled side chamfers
            for i in range(4):
                i_n = (i + 1) % 4
                f_s = bm.faces.new([v_b[i], v_b[i_n], v_t[i_n], v_t[i]])
                f_s.material_index = 0; set_face_uv_rect(bm, f_s, UV_NEUTRAL_BUFFER)

    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


def build_joystick_base_mesh(mesh, materials):
    """
    Build Joystick_Base:
    Stepped accordion rubber bellows boot and circular mounting collar flush with console slope.
    Origin at (X: +0.080, Y: -0.010, Z: surface Z), tilted by slope_angle.
    Material: M_Security_Atlas (Slot 0).
    Tris count: ~140 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    rings = [
        (0.042, 0.000),  # Mounting collar bottom sitting flush on console face
        (0.040, 0.003),  # Mounting collar top rim
        (0.035, 0.006),  # Bellows fold 1 (in)
        (0.037, 0.011),  # Bellows fold 1 (out)
        (0.026, 0.016),  # Bellows fold 2 (in)
        (0.028, 0.021),  # Bellows fold 2 (out)
        (0.014, 0.026),  # Neck collar top
    ]

    ring_verts = []
    for r, z in rings:
        v_layer = []
        for a in range(10):
            ang = 2.0 * math.pi * a / 10.0
            vx = r * math.cos(ang)
            vy = r * math.sin(ang)
            v_layer.append(bm.verts.new(Vector((vx, vy, z))))
        ring_verts.append(v_layer)

    for rg in range(len(rings) - 1):
        v1 = ring_verts[rg]
        v2 = ring_verts[rg + 1]
        uv_zone = UV_NEUTRAL_BUFFER if rg == 0 else UV_RUBBER_BOOT
        for a in range(10):
            a_n = (a + 1) % 10
            f_boot = bm.faces.new([v1[a], v1[a_n], v2[a_n], v2[a]])
            f_boot.material_index = 0
            set_face_uv_rect(bm, f_boot, uv_zone)

    # Inner collar seal around lever
    v_top = ring_verts[-1]
    v_inner = []
    for a in range(10):
        ang = 2.0 * math.pi * a / 10.0
        vx = 0.007 * math.cos(ang)
        vy = 0.007 * math.sin(ang)
        v_inner.append(bm.verts.new(Vector((vx, vy, 0.024))))
    for a in range(10):
        a_n = (a + 1) % 10
        f_rim = bm.faces.new([v_top[a], v_top[a_n], v_inner[a_n], v_inner[a]])
        f_rim.material_index = 0
        set_face_uv_rect(bm, f_rim, UV_RUBBER_BOOT)

    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


def build_joystick_lever_mesh(mesh, materials):
    """
    Build Joystick_Lever:
    Chrome cylindrical steel shaft connecting pivot to grip.
    Origin at local (0, 0, 0) of Joystick_Pivot.
    Height: 0.035m, Radius: 0.005m (8 segments).
    Material: M_Security_Atlas (Slot 0).
    Tris count: ~16 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    r = 0.005
    h = 0.035
    v_bot = []
    v_top = []
    for a in range(8):
        ang = 2.0 * math.pi * a / 8.0
        vx = r * math.cos(ang)
        vy = r * math.sin(ang)
        v_bot.append(bm.verts.new(Vector((vx, vy, 0.000))))
        v_top.append(bm.verts.new(Vector((vx, vy, h))))

    for a in range(8):
        a_n = (a + 1) % 8
        f_cyl = bm.faces.new([v_bot[a], v_bot[a_n], v_top[a_n], v_top[a]])
        f_cyl.material_index = 0
        set_face_uv_rect(bm, f_cyl, UV_CHROME_SHAFT)

    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


def build_joystick_grip_mesh(mesh, materials):
    """
    Build Joystick_Grip:
    Ergonomic contoured 3-axis PTZ handle grip with top push button and rubber zoom twist ring.
    Origin at local (0, 0, 0) relative to lever top (Z = 0.035m).
    Height: 0.040m, Radius: 0.008m to 0.015m (10 segments).
    Material: M_Security_Atlas (Slot 0).
    Tris count: ~110 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    profile = [
        (0.008, 0.000),  # Shaft interface collar
        (0.013, 0.006),  # Lower flare
        (0.015, 0.012),  # Zoom twist ring bottom
        (0.015, 0.022),  # Zoom twist ring top (ribbed rubber traction)
        (0.013, 0.030),  # Upper grip taper
        (0.012, 0.036),  # Top bezel rim
    ]

    ring_verts = []
    for r, z in profile:
        v_layer = []
        for a in range(10):
            ang = 2.0 * math.pi * a / 10.0
            vx = r * math.cos(ang)
            vy = r * math.sin(ang)
            v_layer.append(bm.verts.new(Vector((vx, vy, z))))
        ring_verts.append(v_layer)

    for p in range(len(profile) - 1):
        v1 = ring_verts[p]
        v2 = ring_verts[p + 1]
        uv_zone = UV_RUBBER_BOOT if (p == 2) else UV_NEUTRAL_BUFFER
        for a in range(10):
            a_n = (a + 1) % 10
            f_g = bm.faces.new([v1[a], v1[a_n], v2[a_n], v2[a]])
            f_g.material_index = 0
            set_face_uv_rect(bm, f_g, uv_zone)

    # Top push-button (recessed ergonomic trigger)
    v_top_rim = ring_verts[-1]
    v_btn_center = bm.verts.new(Vector((0.0, 0.0, 0.037)))
    for a in range(10):
        a_n = (a + 1) % 10
        f_cap = bm.faces.new([v_top_rim[a], v_top_rim[a_n], v_btn_center])
        f_cap.material_index = 0
        set_face_uv_rect(bm, f_cap, UV_NEUTRAL_BUFFER)

    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


# -------------------------------------------------------------
# Assembly, Export and Automated QA Pipeline
# -------------------------------------------------------------

def assemble_and_export():
    """Build complete hierarchy, setup rotation limits, export FBX, and run verification."""
    setup_clean_scene()

    print("[INFO] Creating textures and materials...")
    atlas_img, screen_img = load_or_create_textures()
    materials = create_materials(atlas_img, screen_img)

    # 1. Root Empty: SEC_Console_Camera_Joystick at (0, 0, 0) on desk
    root_empty = bpy.data.objects.new("SEC_Console_Camera_Joystick", None)
    root_empty.empty_display_type = 'PLAIN_AXES'
    root_empty.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root_empty)

    # 2. Console_Housing (child of Root)
    mesh_housing = bpy.data.meshes.new("Console_Housing")
    obj_housing = bpy.data.objects.new("Console_Housing", mesh_housing)
    build_console_housing_mesh(mesh_housing, materials)
    bpy.context.collection.objects.link(obj_housing)
    obj_housing.parent = root_empty

    # 3. Display (child of Console_Housing)
    mesh_display = bpy.data.meshes.new("Display")
    obj_display = bpy.data.objects.new("Display", mesh_display)
    build_display_mesh(mesh_display, materials)
    bpy.context.collection.objects.link(obj_display)
    obj_display.location = Vector((-0.080, 0.055, 0.062))
    y_front = -0.110
    y_rear  =  0.110
    z_f = 0.025
    z_r = 0.075
    slope_angle = math.atan2(z_r - z_f, y_rear - y_front)
    obj_display.rotation_euler = Euler((slope_angle, 0.0, 0.0), 'XYZ')
    obj_display.parent = obj_housing

    # 4. Button_Array (child of Console_Housing)
    mesh_buttons = bpy.data.meshes.new("Button_Array")
    obj_buttons = bpy.data.objects.new("Button_Array", mesh_buttons)
    build_button_array_mesh(mesh_buttons, materials)
    bpy.context.collection.objects.link(obj_buttons)
    obj_buttons.parent = obj_housing

    # 5. Joystick_Base (child of Console_Housing)
    # Placed flush on inclined console face at X=0.080, Y=-0.010, tilted by slope_angle
    jy = -0.010
    j_surf_z = z_f + (jy - y_front) / (y_rear - y_front) * (z_r - z_f) # 0.047727
    mesh_jbase = bpy.data.meshes.new("Joystick_Base")
    obj_jbase = bpy.data.objects.new("Joystick_Base", mesh_jbase)
    build_joystick_base_mesh(mesh_jbase, materials)
    bpy.context.collection.objects.link(obj_jbase)
    obj_jbase.location = Vector((0.080, jy, j_surf_z))
    obj_jbase.rotation_euler = Euler((slope_angle, 0.0, 0.0), 'XYZ')
    obj_jbase.parent = obj_housing

    # 6. Joystick_Pivot (Empty, child of Console_Housing)
    # Pivot positioned at the neck of the boot (local Z = 0.026m along tilted normal)
    z_piv_local = 0.026
    piv_y = jy - z_piv_local * math.sin(slope_angle)
    piv_z = j_surf_z + z_piv_local * math.cos(slope_angle)
    pivot_empty = bpy.data.objects.new("Joystick_Pivot", None)
    pivot_empty.empty_display_type = 'SPHERE'
    pivot_empty.empty_display_size = 0.015
    pivot_empty.location = Vector((0.080, piv_y, piv_z))
    pivot_empty.rotation_euler = Euler((slope_angle, 0.0, 0.0), 'XYZ')
    bpy.context.collection.objects.link(pivot_empty)
    pivot_empty.parent = obj_housing

    # Add Limit Rotation Constraint on local X and Z axes (-30° to +30°)
    rot_limit = pivot_empty.constraints.new(type='LIMIT_ROTATION')
    rot_limit.use_limit_x = True
    rot_limit.min_x = math.radians(-30.0)
    rot_limit.max_x = math.radians(30.0)
    rot_limit.use_limit_z = True
    rot_limit.min_z = math.radians(-30.0)
    rot_limit.max_z = math.radians(30.0)
    rot_limit.use_limit_y = False
    rot_limit.owner_space = 'LOCAL'

    # Custom Properties for Interactive PTZ Engine
    pivot_empty["min_pitch_deg"] = -30.0
    pivot_empty["max_pitch_deg"] = 30.0
    pivot_empty["min_yaw_deg"] = -30.0
    pivot_empty["max_yaw_deg"] = 30.0
    pivot_empty["action"] = "PTZ_PAN_TILT"

    # 7. Joystick_Lever (child of Joystick_Pivot)
    mesh_lever = bpy.data.meshes.new("Joystick_Lever")
    obj_lever = bpy.data.objects.new("Joystick_Lever", mesh_lever)
    build_joystick_lever_mesh(mesh_lever, materials)
    bpy.context.collection.objects.link(obj_lever)
    obj_lever.parent = pivot_empty

    # 8. Joystick_Grip (child of Joystick_Lever)
    mesh_grip = bpy.data.meshes.new("Joystick_Grip")
    obj_grip = bpy.data.objects.new("Joystick_Grip", mesh_grip)
    build_joystick_grip_mesh(mesh_grip, materials)
    bpy.context.collection.objects.link(obj_grip)
    obj_grip.location = Vector((0.0, 0.0, 0.035))
    obj_grip.parent = obj_lever
    obj_grip["action"] = "PTZ_ZOOM_TWIST"

    bpy.context.view_layer.update()

    # Save Blend file
    blend_path = os.path.join(EXPORTS_DIR, "SEC_Console_Camera_Joystick.blend")
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
    obj_housing.select_set(True)
    obj_display.select_set(True)
    obj_buttons.select_set(True)
    obj_jbase.select_set(True)
    pivot_empty.select_set(True)
    obj_lever.select_set(True)
    obj_grip.select_set(True)

    fbx_path = os.path.join(EXPORTS_DIR, "SEC_Console_Camera_Joystick.fbx")
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

    # Run automated verification QA
    verify_fbx(fbx_path, blend_path)


def verify_fbx(fbx_path, blend_path):
    """Import exported FBX into a fresh test scene and verify all specs."""
    print("\n--- RUNNING AUTOMATED QA ON EXPORTED FBX ---")
    setup_clean_scene()

    bpy.ops.import_scene.fbx(filepath=fbx_path)
    imported_objs = list(bpy.context.scene.objects)
    print(f"[QA] Imported objects ({len(imported_objs)}): {[o.name for o in imported_objs]}")

    # Check root object
    root = bpy.data.objects.get("SEC_Console_Camera_Joystick")
    assert root is not None, "[QA ERROR] Root object 'SEC_Console_Camera_Joystick' not found!"
    assert root.type == 'EMPTY', f"[QA ERROR] Root should be EMPTY, got {root.type}"

    # Calculate triangulated polygon count
    total_tris = 0
    mesh_count = 0
    empty_count = 0
    for obj in imported_objs:
        if obj.type == 'MESH':
            mesh_count += 1
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            tris = len(bm.faces)
            total_tris += tris
            bm.free()
        elif obj.type == 'EMPTY':
            empty_count += 1

    print(f"[QA] TOTAL TRIANGLES: {total_tris} (Budget limit: 600)")
    assert total_tris <= 600, f"[QA ERROR] Triangles {total_tris} exceeds budget 600!"

    expected_materials = ["M_Security_Atlas", "M_Screen", "M_Emission"]
    imported_mat_names = [m.name for m in bpy.data.materials]
    for em in expected_materials:
        assert any(em in im for im in imported_mat_names), f"[QA ERROR] Material {em} missing from imported scene!"

    # Verify hierarchy
    housing = bpy.data.objects.get("Console_Housing")
    assert housing is not None, "[QA ERROR] Console_Housing not found!"
    assert housing.parent == root, "[QA ERROR] Console_Housing should be child of Root!"

    jbase = bpy.data.objects.get("Joystick_Base")
    assert jbase is not None, "[QA ERROR] Joystick_Base not found!"
    assert jbase.parent == housing, "[QA ERROR] Joystick_Base should be child of Console_Housing!"

    jpivot = bpy.data.objects.get("Joystick_Pivot")
    assert jpivot is not None, "[QA ERROR] Joystick_Pivot not found!"
    assert jpivot.parent == housing, "[QA ERROR] Joystick_Pivot should be child of Console_Housing!"

    lever = bpy.data.objects.get("Joystick_Lever")
    assert lever is not None, "[QA ERROR] Joystick_Lever not found!"
    assert lever.parent == jpivot, "[QA ERROR] Joystick_Lever should be child of Joystick_Pivot!"

    grip = bpy.data.objects.get("Joystick_Grip")
    assert grip is not None, "[QA ERROR] Joystick_Grip not found!"
    assert grip.parent == lever, "[QA ERROR] Joystick_Grip should be child of Joystick_Lever!"

    # Write manifest
    manifest_path = os.path.join(EXPORTS_DIR, "manifest.json")
    manifest_data = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_Console_Camera_Joystick"] = {
        "asset_name": "SEC_Console_Camera_Joystick",
        "fbx_path": "exports/SEC_Console_Camera_Joystick.fbx",
        "blend_path": "exports/SEC_Console_Camera_Joystick.blend",
        "tris_count": total_tris,
        "mesh_count": mesh_count,
        "empty_count": empty_count,
        "materials": expected_materials,
        "status": "SUCCESS"
    }

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=2)

    print(f"[QA] Manifest written to {manifest_path}")
    print("[QA] ALL CHECKS PASSED SUCCESSFULLY!\n")


if __name__ == "__main__":
    assemble_and_export()
