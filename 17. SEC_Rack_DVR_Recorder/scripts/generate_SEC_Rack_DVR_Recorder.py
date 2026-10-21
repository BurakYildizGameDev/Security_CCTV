"""
SEC_Rack_DVR_Recorder Generator Script (Revision 4 - Ultra-High Resolution 2048x2048 Textures & Razor-Sharp Typography)
Industrial Low-Poly Security & CCTV Asset Pack
Upper Budget Limit: 500 triangles

Hierarchy:
SEC_Rack_DVR_Recorder (Root Empty at 0, 0, 0, bottom-front-center of chassis)
 └── Chassis (Mesh, child of Root)
      ├── Rack_Ears (Mesh, child of Chassis)
      └── Front_Panel (Mesh, child of Chassis)
           ├── Status_Display (Mesh, child of Front_Panel, M_Screen)
           ├── Power_Button (Mesh, child of Front_Panel, M_Security_Atlas)
           └── Status_LED_Array (Mesh, child of Front_Panel, M_Emission)

Materials:
    Slot 0: M_Security_Atlas (2048x2048 Ultra-Sharp Atlas)
    Slot 1: M_Screen (1024x512 VFD Alphanumeric Display)
    Slot 2: M_Emission
    Slot 3: M_Metal
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


def get_fonts_2048():
    """High-resolution bold fonts for 2048x2048 atlas and 1024x512 screen."""
    try:
        font_xl = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 52)
        font_lg = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 40)
        font_md = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 30)
        font_sm = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 24)
        font_xs = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 20)
        title_xl = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 56)
        title_lg = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 42)
        title_md = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 32)
        title_sm = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 24)
        title_xs = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 20)
    except Exception:
        font_xl = font_lg = font_md = font_sm = font_xs = ImageFont.load_default()
        title_xl = title_lg = title_md = title_sm = title_xs = ImageFont.load_default()
    return font_xl, font_lg, font_md, font_sm, font_xs, title_xl, title_lg, title_md, title_sm, title_xs


def generate_screen_texture():
    """Generate 1024x512 Ultra-Sharp VFD Display Texture (T_Screen.png)."""
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    out_path = os.path.join(EXPORTS_DIR, "T_Screen.png")
    if not HAS_PIL:
        return out_path

    w, h = 1024, 512
    img = Image.new("RGBA", (w, h), (6, 14, 18, 255))
    draw = ImageDraw.Draw(img)
    f_xl, f_lg, f_md, f_sm, f_xs, t_xl, t_lg, t_md, t_sm, t_xs = get_fonts_2048()

    # VFD phosphorescent scanline pattern
    for y in range(0, h, 4):
        draw.line([(0, y), (w, y)], fill=(4, 10, 14, 255))

    # Outer display border
    draw.rectangle([12, 12, w - 12, h - 12], outline=(20, 80, 95, 255), width=3)
    draw.rectangle([20, 20, w - 20, h - 20], outline=(12, 50, 60, 255), width=2)

    # Line 1: Header & Live indicator
    draw.text((44, 48), "SEC-DVR 1600 PRO   [LIVE]", fill=(60, 245, 255, 255), font=t_lg)

    # Line 2: Channels & Realtime recording status
    draw.text((44, 140), "CH 01-16: 1080P/25FPS ● REC", fill=(45, 255, 170, 255), font=f_lg)

    # Line 3: Storage health telemetry
    draw.text((44, 230), "HDD: 4x4TB RAID5 [HEALTHY]", fill=(50, 235, 255, 255), font=f_lg)

    # Line 4: Network telemetry
    draw.text((44, 320), "NET: 192.168.1.100 [ONLINE]", fill=(60, 245, 255, 255), font=f_lg)

    # Bottom status badges
    badges = ["H.265", "4K-OUT", "RAID-5", "GBE", "UTC+3"]
    for i, b in enumerate(badges):
        bx = 44 + i * 190
        draw.rectangle([bx, 416, bx + 170, 472], fill=(12, 38, 46, 255), outline=(35, 120, 140, 255), width=2)
        draw.text((bx + 26, 428), b, fill=(90, 240, 255, 255), font=t_sm)

    img.save(out_path, format="PNG")
    print(f"[INFO] Generated 1024x512 T_Screen.png: {out_path}")
    return out_path


def generate_security_atlas_texture():
    """Generate 2048x2048 Ultra-Sharp Texture Atlas (T_Security_Atlas.png)."""
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    out_path = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")
    if not HAS_PIL:
        return out_path

    w, h = 2048, 2048
    img = Image.new("RGBA", (w, h), (26, 28, 32, 255))
    draw = ImageDraw.Draw(img)
    f_xl, f_lg, f_md, f_sm, f_xs, t_xl, t_lg, t_md, t_sm, t_xs = get_fonts_2048()

    # Base noise/brushing across top casing
    for y in range(0, 960, 4):
        for x in range(0, 2048, 8):
            if (x + y) % 9 == 0:
                draw.point((x, y), fill=(32, 35, 40, 255))

    # =========================================================================
    # ZONE 1: FRONT FASCIA PLATE (X: 0..2048, Y: 960..1360, Height: 400px)
    # =========================================================================
    for y in range(960, 1360):
        shade = int(22 + ((y - 960) / 400.0) * 12)
        draw.line([(0, y), (2048, y)], fill=(shade, shade + 1, shade + 3, 255))
    draw.line([(0, 960), (2048, 960)], fill=(75, 82, 95, 255), width=3)
    draw.line([(0, 1356), (2048, 1356)], fill=(12, 13, 15, 255), width=3)

    # Left Section (Screen Left): Brand Title & Subtitle (X: 80..760)
    draw.text((80, 984), "SEC-DVR 1600 PRO", fill=(255, 255, 255, 255), font=t_xl)
    draw.text((84, 1052), "16-CHANNEL REALTIME H.265 EMBEDDED DIGITAL VIDEO RECORDER", fill=(195, 205, 225, 255), font=t_sm)

    # 4 HDD Caddy Bays with high-contrast text and push latches
    for d in range(4):
        dx = 80 + d * 160
        dy = 1104
        draw.rectangle([dx, dy, dx + 148, dy + 230], fill=(20, 22, 25, 255), outline=(65, 72, 85, 255), width=2)
        # Handle latch
        draw.rectangle([dx + 16, dy + 20, dx + 132, dy + 56], fill=(35, 40, 48, 255), outline=(85, 95, 110, 255), width=2)
        draw.text((dx + 28, dy + 24), f"HDD {d+1}", fill=(240, 245, 255, 255), font=t_sm)
        # Release button & key lock
        draw.rectangle([dx + 22, dy + 76, dx + 80, dy + 104], fill=(28, 32, 38, 255), outline=(70, 80, 95, 255), width=1)
        draw.text((dx + 30, dy + 80), "PUSH", fill=(170, 180, 195, 255), font=f_xs)
        draw.ellipse([dx + 100, dy + 82, dx + 120, dy + 102], fill=(50, 55, 65, 255), outline=(100, 115, 130, 255), width=1)
        # Ventilation slits on caddy
        for sy in range(dy + 124, dy + 210, 16):
            draw.rectangle([dx + 18, sy, dx + 128, sy + 6], fill=(12, 13, 15, 255))

    # Center-Right Section: LED Indicator Labels (X: 1290..1530, Y: 1040..1320)
    # Row 1: PWR, NET, HDD, LNK (Labels at Y = 1148)
    # Row 2: REC, ALM, ERR, ACT  (Labels at Y = 1272)
    led_row1 = ["PWR", "NET", "HDD", "LNK"]
    for i, lbl in enumerate(led_row1):
        lx = 1296 + i * 58
        draw.ellipse([lx + 2, 1088, lx + 34, 1120], outline=(65, 75, 90, 255), width=2)
        draw.text((lx + 2, 1136), lbl, fill=(240, 248, 255, 255), font=f_sm)

    led_row2 = ["REC", "ALM", "ERR", "ACT"]
    for i, lbl in enumerate(led_row2):
        lx = 1296 + i * 58
        draw.ellipse([lx + 2, 1212, lx + 34, 1244], outline=(65, 75, 90, 255), width=2)
        draw.text((lx + 2, 1260), lbl, fill=(240, 248, 255, 255), font=f_sm)

    # Right Section: Jog-Shuttle Dial & Navigation Cluster (X: 1550..1810)
    draw.ellipse([1560, 1064, 1720, 1224], fill=(28, 30, 36, 255), outline=(85, 95, 110, 255), width=3)
    for ang in range(0, 360, 20):
        rad = math.radians(ang)
        x1 = 1640 + int(72 * math.cos(rad))
        y1 = 1144 + int(72 * math.sin(rad))
        x2 = 1640 + int(80 * math.cos(rad))
        y2 = 1144 + int(80 * math.sin(rad))
        draw.line([(x1, y1), (x2, y2)], fill=(120, 130, 145, 255), width=3)
    draw.ellipse([1590, 1094, 1690, 1194], fill=(20, 22, 26, 255), outline=(65, 75, 88, 255), width=2)
    draw.text((1624, 1132), "OK", fill=(255, 255, 255, 255), font=t_md)

    nav_btns = [("MENU", 1736, 1064), ("ESC", 1736, 1124), ("PTZ", 1736, 1184), ("PLAY", 1736, 1244)]
    for n_txt, nx, ny in nav_btns:
        draw.rectangle([nx, ny, nx + 76, ny + 48], fill=(32, 36, 44, 255), outline=(75, 85, 100, 255), width=2)
        draw.text((nx + 8, ny + 10), n_txt, fill=(240, 248, 255, 255), font=f_sm)

    # Far Right Section (Screen Right): Front Dual USB & Standby Button (X: 1830..1960)
    draw.rectangle([1834, 1064, 1930, 1116], fill=(16, 17, 19, 255), outline=(85, 95, 110, 255), width=2)
    draw.text((1846, 1076), "USB 1", fill=(240, 248, 255, 255), font=f_sm)
    draw.rectangle([1834, 1136, 1930, 1188], fill=(16, 17, 19, 255), outline=(85, 95, 110, 255), width=2)
    draw.text((1846, 1148), "USB 2", fill=(240, 248, 255, 255), font=f_sm)

    # Standby power symbol area (Power_Button texture cap)
    draw.ellipse([1838, 1224, 1922, 1308], fill=(26, 28, 32, 255), outline=(95, 105, 120, 255), width=3)
    draw.text((1866, 1244), "⏻", fill=(255, 255, 255, 255), font=t_lg)

    # =========================================================================
    # ZONE 2: REAR RECESSED I/O PANEL (X: 0..1340, Y: 1370..1830, Height: 460px)
    # =========================================================================
    draw.rectangle([0, 1370, 1340, 1830], fill=(20, 22, 25, 255))
    draw.rectangle([16, 1384, 1324, 1816], fill=(26, 29, 33, 255), outline=(65, 72, 85, 255), width=3)
    draw.text((40, 1396), "REAR I/O CONNECTIONS - 16-CH BNC VIDEO MATRIX & RS-485", fill=(255, 255, 255, 255), font=f_lg)

    # 16 BNC Video Inputs (2 rows of 8)
    for row in range(2):
        for col in range(8):
            ch_num = row * 8 + col + 1
            bx = 48 + col * 88
            by = 1452 + row * 88
            draw.ellipse([bx, by, bx + 68, by + 68], fill=(70, 75, 82, 255), outline=(150, 160, 175, 255), width=3)
            draw.ellipse([bx + 18, by + 18, bx + 50, by + 50], fill=(28, 30, 34, 255), outline=(200, 210, 225, 255), width=2)
            draw.ellipse([bx + 28, by + 28, bx + 40, by + 40], fill=(235, 205, 85, 255))
            draw.text((bx + 10, by + 52), f"{ch_num}", fill=(255, 255, 255, 255), font=f_sm)

    # Digital & Communication Ports (Right of BNCs)
    draw.rectangle([780, 1456, 910, 1512], fill=(32, 35, 42, 255), outline=(105, 115, 130, 255), width=3)
    draw.text((796, 1470), "HDMI 4K", fill=(255, 255, 255, 255), font=f_sm)

    draw.rectangle([780, 1540, 910, 1596], fill=(28, 55, 110, 255), outline=(75, 115, 210, 255), width=3)
    draw.text((808, 1552), "VGA OUT", fill=(255, 255, 255, 255), font=f_sm)

    # LAN & RS485 Terminal block
    draw.rectangle([950, 1456, 1070, 1520], fill=(18, 22, 26, 255), outline=(95, 105, 120, 255), width=3)
    draw.text((968, 1472), "LAN GBE", fill=(240, 248, 255, 255), font=f_sm)

    draw.rectangle([950, 1540, 1070, 1596], fill=(18, 85, 42, 255), outline=(45, 155, 75, 255), width=3)
    draw.text((964, 1552), "RS-485", fill=(240, 255, 245, 255), font=f_sm)

    # AC Inlet Socket Shroud & Rocker Switch
    draw.rectangle([1110, 1452, 1290, 1608], fill=(15, 16, 18, 255), outline=(80, 88, 98, 255), width=3)
    draw.rectangle([1140, 1480, 1160, 1520], fill=(200, 205, 215, 255))
    draw.rectangle([1210, 1480, 1230, 1520], fill=(200, 205, 215, 255))
    draw.rectangle([1176, 1540, 1196, 1580], fill=(200, 205, 215, 255))
    draw.text((1120, 1624), "100-240V AC 150W", fill=(220, 230, 240, 255), font=f_sm)
    draw.text((1260, 1624), "⏚", fill=(235, 215, 80, 255), font=t_lg)

    # =========================================================================
    # ZONE 3: FACTORY SPECIFICATION RATING PLATE (X: 1360..2030, Y: 1370..1830)
    # Ultra-Sharp, 100% Legible Industrial Rating Plate
    # =========================================================================
    draw.rectangle([1360, 1370, 2030, 1830], fill=(20, 22, 25, 255))
    draw.rectangle([1390, 1390, 2000, 1810], fill=(242, 245, 248, 255), outline=(100, 110, 120, 255), width=3)
    draw.rectangle([1400, 1400, 1990, 1800], outline=(160, 170, 180, 255), width=2)

    draw.text((1424, 1416), "19\" RACK DVR RECORDER", fill=(10, 15, 20, 255), font=t_md)
    draw.text((1424, 1472), "MODEL: SEC-DVR16-PRO   16-CH EMBEDDED H.265", fill=(15, 20, 25, 255), font=f_sm)
    draw.text((1424, 1508), "POWER: 100-240V ~ 50/60Hz 1.5A 150W MAX", fill=(15, 20, 25, 255), font=f_sm)
    draw.text((1424, 1544), "SERIAL: DVR-2026-99412-B", fill=(15, 20, 25, 255), font=f_sm)
    draw.text((1424, 1580), "MAC: 00:1B:44:F2:78:A1", fill=(15, 20, 25, 255), font=f_sm)

    # Crisp Thick Barcode
    for bx in range(1424, 1750, 6):
        if (bx * 7) % 11 < 6:
            draw.line([(bx, 1628), (bx, 1712)], fill=(5, 10, 15, 255), width=4)
    draw.text((1470, 1724), "*DVR202699412B*", fill=(10, 15, 20, 255), font=f_sm)

    cert_labels = ["CE", "FCC", "RoHS", "WEEE", "UL"]
    for i, c in enumerate(cert_labels):
        cx = 1810
        cy = 1612 + i * 34
        draw.text((cx, cy), f"[{c}]", fill=(10, 15, 20, 255), font=f_sm)

    # =========================================================================
    # ZONE 4: LOUVERS & EXHAUST FAN GRILL (X: 0..900, Y: 1840..2048)
    # =========================================================================
    for ly in range(1852, 2036, 18):
        draw.rectangle([30, ly, 880, ly + 8], fill=(10, 12, 14, 255), outline=(40, 45, 52, 255), width=2)

    # =========================================================================
    # ZONE 5: DARK ANODIZED RACK METAL (X: 920..1440, Y: 1840..2048)
    # =========================================================================
    for y in range(1840, 2048):
        shade = int(42 + ((y - 1840) / 208.0) * 14)
        draw.line([(920, y), (1440, y)], fill=(shade, shade + 2, shade + 4, 255))
    draw.rectangle([924, 1844, 1436, 2044], outline=(75, 82, 92, 255), width=3)

    # =========================================================================
    # ZONE 6: EIA-310 RACK EAR SLOTS & M6 SCREWS (X: 1460..1900, Y: 1840..2048)
    # =========================================================================
    draw.rectangle([1460, 1840, 1900, 2048], fill=(28, 30, 34, 255), outline=(65, 72, 80, 255), width=3)
    m6_screws = [(1540, 1944), (1680, 1944), (1820, 1944)]
    for vx, vy in m6_screws:
        draw.rounded_rectangle([vx - 28, vy - 48, vx + 28, vy + 48], radius=12, fill=(15, 16, 18, 255), outline=(60, 66, 75, 255), width=2)
        draw.ellipse([vx - 22, vy - 22, vx + 22, vy + 22], fill=(160, 168, 178, 255), outline=(85, 90, 98, 255), width=3)
        draw.line([(vx, vy - 16), (vx, vy + 16)], fill=(35, 40, 45, 255), width=3)
        draw.line([(vx - 16, vy), (vx + 16, vy)], fill=(35, 40, 45, 255), width=3)

    # =========================================================================
    # ZONE 7: NEUTRAL BUFFER (X: 1920..2048, Y: 1920..2048)
    # =========================================================================
    draw.rectangle([1920, 1920, 2048, 2048], fill=(26, 28, 32, 255))

    img.save(out_path, format="PNG")
    print(f"[INFO] Generated 2048x2048 T_Security_Atlas.png: {out_path}")
    return out_path


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
    Slot 3: M_Metal
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
    bsdf0.inputs['Metallic'].default_value = 0.20
    mat_atlas.diffuse_color = (0.16, 0.17, 0.20, 1.0)
    materials["M_Security_Atlas"] = mat_atlas

    # Slot 1: M_Screen (Emissive VFD Alphanumeric Display)
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

    bsdf1.inputs['Emission Strength'].default_value = 1.70
    bsdf1.inputs['Roughness'].default_value = 0.05
    bsdf1.inputs['Metallic'].default_value = 0.02
    mat_screen.diffuse_color = (0.10, 0.45, 0.50, 1.0)
    materials["M_Screen"] = mat_screen

    # Slot 2: M_Emission (Front status LED jewel array)
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

    # Slot 3: M_Metal (Dark anodized rack metal & chrome M6 screws)
    mat_metal = bpy.data.materials.get("M_Metal")
    if not mat_metal:
        mat_metal = bpy.data.materials.new(name="M_Metal")
    mat_metal.use_nodes = True
    nodes3 = mat_metal.node_tree.nodes
    links3 = mat_metal.node_tree.links
    nodes3.clear()

    out3 = nodes3.new(type='ShaderNodeOutputMaterial')
    out3.location = (300, 0)
    bsdf3 = nodes3.new(type='ShaderNodeBsdfPrincipled')
    bsdf3.location = (0, 0)
    links3.new(bsdf3.outputs['BSDF'], out3.inputs['Surface'])

    tex3 = nodes3.new(type='ShaderNodeTexImage')
    tex3.location = (-300, 0)
    tex3.image = atlas_img
    tex3.interpolation = 'Linear'
    links3.new(tex3.outputs['Color'], bsdf3.inputs['Base Color'])

    bsdf3.inputs['Roughness'].default_value = 0.25
    bsdf3.inputs['Metallic'].default_value = 0.85
    mat_metal.diffuse_color = (0.35, 0.38, 0.42, 1.0)
    materials["M_Metal"] = mat_metal

    return materials


def attach_standard_materials(mesh, materials):
    """Ensure materials are present in the exact order specified."""
    mesh.materials.clear()
    mesh.materials.append(materials["M_Security_Atlas"])  # Slot 0
    mesh.materials.append(materials["M_Screen"])          # Slot 1
    mesh.materials.append(materials["M_Emission"])        # Slot 2
    mesh.materials.append(materials["M_Metal"])           # Slot 3


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


def apply_continuous_front_uv(bm, face, uv_rect, x_bounds, z_bounds):
    """
    Apply continuous, non-repeating front planar UV mapping.
    Maps 3D local coordinate (x, z) to (u, v) seamlessly across multiple faces.
    Viewer looking from front (+Y to -Y):
    Screen Left is +X (maps to u0, left of texture image).
    Screen Right is -X (maps to u1, right of texture image).
    """
    face.normal_update()
    u0, v0, u1, v1 = uv_rect
    xmin, xmax = x_bounds
    zmin, zmax = z_bounds
    x_span = xmax - xmin if xmax > xmin else 1.0
    z_span = zmax - zmin if zmax > zmin else 1.0
    uv_lay = bm.loops.layers.uv.verify()

    for loop in face.loops:
        x = loop.vert.co.x
        z = loop.vert.co.z
        fu = (xmax - x) / x_span
        fv = (z - zmin) / z_span
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
# In normalized UV space (0.0 to 1.0)
UV_CASING_METAL     = (0.010, 0.540, 0.460, 0.990)
UV_FRONT_FASCIA     = (0.000, 0.336, 1.000, 0.531) # Y: 960..1360
UV_REAR_IO_BAY      = (0.000, 0.106, 0.654, 0.331) # X: 0..1340, Y: 1370..1830
UV_RATING_LABEL     = (0.664, 0.106, 0.991, 0.331) # X: 1360..2030, Y: 1370..1830
UV_LOUVERS          = (0.015, 0.005, 0.440, 0.101) # Y: 1840..2048
UV_DARK_METAL       = (0.450, 0.005, 0.705, 0.101) # Y: 1840..2048
UV_RACK_SLOTS       = (0.713, 0.005, 0.928, 0.101) # Y: 1840..2048
UV_POWER_BTN        = (0.910, 0.363, 0.955, 0.402) # Standby icon
UV_NEUTRAL_BUFFER   = (0.940, 0.005, 0.990, 0.055)


# -------------------------------------------------------------
# High-Density Low-Poly Mesh Builders
# -------------------------------------------------------------

def build_chassis_mesh(mesh, materials):
    """
    Build Chassis:
    19-inch 2U rack enclosure (Width 440mm, Height 88mm, Depth 380mm).
    Root pivot at (0, 0, 0) bottom front center.
    - Top, bottom, left and right side walls with ventilation louvers.
    - 4 molded bottom rubber feet.
    - Recessed rear I/O connection bay (15mm deep) facing -Y.
    - Rear AC power socket area and fully framed specification rating plate.
    Tris count: ~90 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    x_hw = 0.220       # 440mm chassis width
    z_h  = 0.088       # 88mm 2U height
    y_f  = 0.000       # Front chassis face
    y_r  = -0.380      # Rear chassis panel

    # 1. Main outer casing shell
    v_f_bl = bm.verts.new(Vector((-x_hw, y_f, 0.000)))
    v_f_br = bm.verts.new(Vector(( x_hw, y_f, 0.000)))
    v_f_tr = bm.verts.new(Vector(( x_hw, y_f, z_h)))
    v_f_tl = bm.verts.new(Vector((-x_hw, y_f, z_h)))

    v_r_bl = bm.verts.new(Vector((-x_hw, y_r, 0.000)))
    v_r_br = bm.verts.new(Vector(( x_hw, y_r, 0.000)))
    v_r_tr = bm.verts.new(Vector(( x_hw, y_r, z_h)))
    v_r_tl = bm.verts.new(Vector((-x_hw, y_r, z_h)))

    # Bottom face
    f_bot = bm.faces.new([v_f_bl, v_r_bl, v_r_br, v_f_br])
    f_bot.material_index = 0; set_face_uv_rect(bm, f_bot, UV_NEUTRAL_BUFFER)

    # Top face
    f_top = bm.faces.new([v_f_tl, v_f_tr, v_r_tr, v_r_tl])
    f_top.material_index = 0; set_face_uv_rect(bm, f_top, UV_CASING_METAL)

    # Left side (X = -x_hw) with louvers
    f_l = bm.faces.new([v_f_bl, v_f_tl, v_r_tl, v_r_bl])
    f_l.material_index = 0; set_face_uv_rect(bm, f_l, UV_LOUVERS)

    # Right side (X = +x_hw) with louvers
    f_r = bm.faces.new([v_f_br, v_r_br, v_r_tr, v_f_tr])
    f_r.material_index = 0; set_face_uv_rect(bm, f_r, UV_LOUVERS)

    # 2. 4 Molded bottom rubber feet pads at Z=0.000m
    feet_coords = [(-0.180, -0.050), (0.180, -0.050), (-0.180, -0.330), (0.180, -0.330)]
    for fx, fy in feet_coords:
        v_ft = [
            bm.verts.new(Vector((fx - 0.015, fy - 0.015, 0.000))),
            bm.verts.new(Vector((fx + 0.015, fy - 0.015, 0.000))),
            bm.verts.new(Vector((fx + 0.015, fy + 0.015, 0.000))),
            bm.verts.new(Vector((fx - 0.015, fy + 0.015, 0.000)))
        ]
        f_foot = bm.faces.new(v_ft)
        f_foot.material_index = 0; set_face_uv_rect(bm, f_foot, UV_NEUTRAL_BUFFER)

    # 3. Rear Panel: Recessed I/O Bay (recessed 15mm into Y = -0.365m)
    y_io_recess = -0.365
    x_io_l = -0.205
    x_io_r =  0.065
    z_io_b =  0.010
    z_io_t =  0.078

    v_io_f = [
        bm.verts.new(Vector((x_io_l, y_io_recess, z_io_b))),
        bm.verts.new(Vector((x_io_r, y_io_recess, z_io_b))),
        bm.verts.new(Vector((x_io_r, y_io_recess, z_io_t))),
        bm.verts.new(Vector((x_io_l, y_io_recess, z_io_t)))
    ]
    f_io = bm.faces.new(list(reversed(v_io_f)))
    f_io.material_index = 0
    set_face_uv_rect(bm, f_io, UV_REAR_IO_BAY, flip_u=False)

    # Rear outer surround rim
    v_io_rim = [
        bm.verts.new(Vector((x_io_l, y_r, z_io_b))),
        bm.verts.new(Vector((x_io_r, y_r, z_io_b))),
        bm.verts.new(Vector((x_io_r, y_r, z_io_t))),
        bm.verts.new(Vector((x_io_l, y_r, z_io_t)))
    ]
    for i in range(4):
        i_n = (i + 1) % 4
        f_rw = bm.faces.new([v_io_rim[i], v_io_rim[i_n], v_io_f[i_n], v_io_f[i]])
        f_rw.material_index = 0; set_face_uv_rect(bm, f_rw, UV_CASING_METAL)

    # Split rear right into specification rating plate rectangle:
    x_rp_l = 0.075
    x_rp_r = 0.210
    z_rp_b = 0.008
    z_rp_t = 0.080

    v_rp = [
        bm.verts.new(Vector((x_rp_l, y_r, z_rp_b))),
        bm.verts.new(Vector((x_rp_r, y_r, z_rp_b))),
        bm.verts.new(Vector((x_rp_r, y_r, z_rp_t))),
        bm.verts.new(Vector((x_rp_l, y_r, z_rp_t)))
    ]
    f_rating = bm.faces.new(list(reversed(v_rp)))
    f_rating.material_index = 0
    set_face_uv_rect(bm, f_rating, UV_RATING_LABEL, flip_u=False)

    # Rear surrounding faces connecting outer shell to I/O rim and rating plate
    f_rt = bm.faces.new([v_r_tl, v_io_rim[3], v_io_rim[2], v_rp[2], v_r_tr])
    f_rt.material_index = 0; set_face_uv_rect(bm, f_rt, UV_CASING_METAL)

    f_rb = bm.faces.new([v_r_bl, v_r_br, v_rp[1], v_rp[0], v_io_rim[1], v_io_rim[0]])
    f_rb.material_index = 0; set_face_uv_rect(bm, f_rb, UV_CASING_METAL)

    f_rl = bm.faces.new([v_r_bl, v_io_rim[0], v_io_rim[3], v_r_tl])
    f_rl.material_index = 0; set_face_uv_rect(bm, f_rl, UV_CASING_METAL)

    f_rmid = bm.faces.new([v_io_rim[1], v_rp[0], v_rp[3], v_io_rim[2]])
    f_rmid.material_index = 0; set_face_uv_rect(bm, f_rmid, UV_CASING_METAL)

    f_rr = bm.faces.new([v_rp[1], v_r_br, v_r_tr, v_rp[2]])
    f_rr.material_index = 0; set_face_uv_rect(bm, f_rr, UV_CASING_METAL)

    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


def build_rack_ears_mesh(mesh, materials):
    """
    Build Rack_Ears:
    Standard 19-inch 2U rack ears (Width 21.3mm, Height 88mm, Flange 3mm).
    - Authentic U-shaped grab handles with open clearance.
    - EIA-310 slotted mounting holes and 4x M6 chrome rack screws with washers.
    - Dark anodized rack metal (M_Metal / Slot 3).
    Tris count: ~104 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    z_h = 0.088
    flange_thick = 0.003

    ear_configs = [
        (-0.220, -0.2413, True),
        ( 0.220,  0.2413, False)
    ]

    for xi, xo, is_left in ear_configs:
        x_min = min(xi, xo)
        x_max = max(xi, xo)

        # 1. Front Flange Box (3mm thick along +Y)
        v_fl_b = [
            bm.verts.new(Vector((x_min, 0.000, 0.000))),
            bm.verts.new(Vector((x_max, 0.000, 0.000))),
            bm.verts.new(Vector((x_max, 0.000, z_h))),
            bm.verts.new(Vector((x_min, 0.000, z_h)))
        ]
        v_fl_f = [
            bm.verts.new(Vector((x_min, flange_thick, 0.000))),
            bm.verts.new(Vector((x_max, flange_thick, 0.000))),
            bm.verts.new(Vector((x_max, flange_thick, z_h))),
            bm.verts.new(Vector((x_min, flange_thick, z_h)))
        ]

        f_fl_front = bm.faces.new([v_fl_f[0], v_fl_f[1], v_fl_f[2], v_fl_f[3]] if not is_left else [v_fl_f[3], v_fl_f[2], v_fl_f[1], v_fl_f[0]])
        f_fl_front.material_index = 0
        set_face_uv_rect(bm, f_fl_front, UV_RACK_SLOTS)

        f_fl_out = bm.faces.new([v_fl_b[1], v_fl_b[2], v_fl_f[2], v_fl_f[1]] if not is_left else [v_fl_b[0], v_fl_f[0], v_fl_f[3], v_fl_b[3]])
        f_fl_out.material_index = 3; set_face_uv_rect(bm, f_fl_out, UV_DARK_METAL)

        f_fl_top = bm.faces.new([v_fl_b[3], v_fl_b[2], v_fl_f[2], v_fl_f[3]] if not is_left else [v_fl_b[2], v_fl_b[3], v_fl_f[3], v_fl_f[2]])
        f_fl_top.material_index = 3; set_face_uv_rect(bm, f_fl_top, UV_DARK_METAL)

        f_fl_bot = bm.faces.new([v_fl_b[0], v_fl_f[0], v_fl_f[1], v_fl_b[1]] if not is_left else [v_fl_b[1], v_fl_f[1], v_fl_f[0], v_fl_b[0]])
        f_fl_bot.material_index = 3; set_face_uv_rect(bm, f_fl_bot, UV_DARK_METAL)

        # 2. Side mounting wing along chassis side (Y: 0.000 to -0.035m)
        v_sw_b = [
            bm.verts.new(Vector((xi, 0.000, 0.000))),
            bm.verts.new(Vector((xi, -0.035, 0.000))),
            bm.verts.new(Vector((xi, -0.035, z_h))),
            bm.verts.new(Vector((xi, 0.000, z_h)))
        ]
        f_sw = bm.faces.new(list(reversed(v_sw_b)) if is_left else v_sw_b)
        f_sw.material_index = 3; set_face_uv_rect(bm, f_sw, UV_DARK_METAL)

        # 3. Authentic U-Shaped Grab Handle Bar with real opening clearance
        hx = (xi + xo) * 0.5
        h_w = 0.003
        h_reach = 0.024

        v_sb = [
            bm.verts.new(Vector((hx - h_w, flange_thick, 0.016))),
            bm.verts.new(Vector((hx + h_w, flange_thick, 0.016))),
            bm.verts.new(Vector((hx + h_w, h_reach, 0.016))),
            bm.verts.new(Vector((hx - h_w, h_reach, 0.016))),
            bm.verts.new(Vector((hx - h_w, flange_thick, 0.026))),
            bm.verts.new(Vector((hx + h_w, flange_thick, 0.026))),
            bm.verts.new(Vector((hx + h_w, h_reach, 0.026))),
            bm.verts.new(Vector((hx - h_w, h_reach, 0.026)))
        ]
        v_st = [
            bm.verts.new(Vector((hx - h_w, flange_thick, 0.062))),
            bm.verts.new(Vector((hx + h_w, flange_thick, 0.062))),
            bm.verts.new(Vector((hx + h_w, h_reach, 0.062))),
            bm.verts.new(Vector((hx - h_w, h_reach, 0.062))),
            bm.verts.new(Vector((hx - h_w, flange_thick, 0.072))),
            bm.verts.new(Vector((hx + h_w, flange_thick, 0.072))),
            bm.verts.new(Vector((hx + h_w, h_reach, 0.072))),
            bm.verts.new(Vector((hx - h_w, h_reach, 0.072)))
        ]
        f_grip_f = bm.faces.new([v_sb[3], v_sb[2], v_st[6], v_st[7]])
        f_grip_f.material_index = 3; set_face_uv_rect(bm, f_grip_f, UV_DARK_METAL)

        f_grip_b = bm.faces.new([v_st[3], v_st[2], v_sb[6], v_sb[7]])
        f_grip_b.material_index = 3; set_face_uv_rect(bm, f_grip_b, UV_DARK_METAL)

        f_grip_o = bm.faces.new([v_sb[2], v_sb[1], v_st[5], v_st[6]]) if not is_left else bm.faces.new([v_sb[0], v_sb[3], v_st[7], v_st[4]])
        f_grip_o.material_index = 3; set_face_uv_rect(bm, f_grip_o, UV_DARK_METAL)

        f_grip_i = bm.faces.new([v_sb[0], v_sb[3], v_st[7], v_st[4]]) if not is_left else bm.faces.new([v_sb[2], v_sb[1], v_st[5], v_st[6]])
        f_grip_i.material_index = 3; set_face_uv_rect(bm, f_grip_i, UV_DARK_METAL)

        f_sb_b = bm.faces.new([v_sb[0], v_sb[1], v_sb[2], v_sb[3]])
        f_sb_b.material_index = 3; set_face_uv_rect(bm, f_sb_b, UV_DARK_METAL)

        f_st_t = bm.faces.new([v_st[7], v_st[6], v_st[5], v_st[4]])
        f_st_t.material_index = 3; set_face_uv_rect(bm, f_st_t, UV_DARK_METAL)

        # 4. Two M6 Chrome Rack Screws with Cup Washers per ear
        for sz in [0.014, 0.074]:
            v_sc = []
            for a in range(6):
                ang = 2.0 * math.pi * a / 6.0
                sc_x = hx + 0.005 * math.cos(ang)
                sc_z = sz + 0.005 * math.sin(ang)
                v_sc.append(bm.verts.new(Vector((sc_x, flange_thick + 0.002, sc_z))))
            f_sc = bm.faces.new(list(reversed(v_sc)) if is_left else v_sc)
            f_sc.material_index = 3; set_face_uv_rect(bm, f_sc, UV_CASING_METAL)

    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


def build_front_panel_mesh(mesh, materials):
    """
    Build Front_Panel:
    Extruded front fascia plate (8mm thick, Y = +0.008m).
    - Outer 4-edge chamfers.
    - Centered cutout opening for Status_Display (X: -0.050 to +0.050, Z: 0.026 to 0.062).
    - Continuous, non-repeating front planar UV mapping (Zero texture repetition!).
    - Tactile 3D Jog-Shuttle dial on front right (X = -0.130).
    - Recessed dual USB backup ports (X = -0.185).
    Tris count: ~130 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    x_hw = 0.220
    z_h  = 0.088
    y_b  = 0.000       # Seam against chassis
    y_f  = 0.008       # Front face of fascia

    # Front face boundary coordinates:
    x_bounds = (-x_hw + 0.003, x_hw - 0.003)
    z_bounds = (0.003, z_h - 0.003)

    # Display Cutout Coordinates (Window for Status_Display):
    dx0, dx1 = -0.050, 0.050
    dz0, dz1 =  0.026, 0.062
    y_bed    =  0.003
    y_lip    =  0.008

    # 1. Outer Chassis Seam Vertices (at Y = 0.000)
    v_b_bl = bm.verts.new(Vector((-x_hw, y_b, 0.000)))
    v_b_br = bm.verts.new(Vector(( x_hw, y_b, 0.000)))
    v_b_tr = bm.verts.new(Vector(( x_hw, y_b, z_h)))
    v_b_tl = bm.verts.new(Vector((-x_hw, y_b, z_h)))

    # Outer Front Chamfer Vertices (at Y = 0.008)
    v_f_br = bm.verts.new(Vector(( x_hw - 0.003, y_f, 0.003)))       # Screen Left (+X)
    v_f_bl = bm.verts.new(Vector((-x_hw + 0.003, y_f, 0.003)))       # Screen Right (-X)
    v_f_tl = bm.verts.new(Vector((-x_hw + 0.003, y_f, z_h - 0.003))) # Screen Right (-X)
    v_f_tr = bm.verts.new(Vector(( x_hw - 0.003, y_f, z_h - 0.003))) # Screen Left (+X)

    # Perimeter Chamfers
    f_ch_b = bm.faces.new([v_b_bl, v_b_br, v_f_br, v_f_bl]); f_ch_b.material_index = 0; set_face_uv_rect(bm, f_ch_b, UV_CASING_METAL)
    f_ch_t = bm.faces.new([v_b_tr, v_b_tl, v_f_tl, v_f_tr]); f_ch_t.material_index = 0; set_face_uv_rect(bm, f_ch_t, UV_CASING_METAL)
    f_ch_l = bm.faces.new([v_b_tl, v_b_bl, v_f_bl, v_f_tl]); f_ch_l.material_index = 0; set_face_uv_rect(bm, f_ch_l, UV_CASING_METAL)
    f_ch_r = bm.faces.new([v_b_br, v_b_tr, v_f_tr, v_f_br]); f_ch_r.material_index = 0; set_face_uv_rect(bm, f_ch_r, UV_CASING_METAL)

    # 2. Cutout Window Perimeter Lip (at Y = 0.008)
    v_win_br = bm.verts.new(Vector((dx1, y_lip, dz0))) # +X
    v_win_bl = bm.verts.new(Vector((dx0, y_lip, dz0))) # -X
    v_win_tl = bm.verts.new(Vector((dx0, y_lip, dz1))) # -X
    v_win_tr = bm.verts.new(Vector((dx1, y_lip, dz1))) # +X

    # 3. Cutout Window Recessed Bed (at Y = 0.003)
    v_bed_br = bm.verts.new(Vector((dx1 - 0.002, y_bed, dz0 + 0.002)))
    v_bed_bl = bm.verts.new(Vector((dx0 + 0.002, y_bed, dz0 + 0.002)))
    v_bed_tl = bm.verts.new(Vector((dx0 + 0.002, y_bed, dz1 - 0.002)))
    v_bed_tr = bm.verts.new(Vector((dx1 - 0.002, y_bed, dz1 - 0.002)))

    # Beveled Frame Walls of the Window (Zero see-through gap!)
    f_ww_b = bm.faces.new([v_win_bl, v_win_br, v_bed_br, v_bed_bl]); f_ww_b.material_index = 0; set_face_uv_rect(bm, f_ww_b, UV_CASING_METAL)
    f_ww_r = bm.faces.new([v_win_br, v_win_tr, v_bed_tr, v_bed_br]); f_ww_r.material_index = 0; set_face_uv_rect(bm, f_ww_r, UV_CASING_METAL)
    f_ww_t = bm.faces.new([v_win_tr, v_win_tl, v_bed_tl, v_bed_tr]); f_ww_t.material_index = 0; set_face_uv_rect(bm, f_ww_t, UV_CASING_METAL)
    f_ww_l = bm.faces.new([v_win_tl, v_win_bl, v_bed_bl, v_bed_tl]); f_ww_l.material_index = 0; set_face_uv_rect(bm, f_ww_l, UV_CASING_METAL)

    # Solid backing floor behind display screen
    f_bed = bm.faces.new([v_bed_bl, v_bed_br, v_bed_tr, v_bed_tl])
    f_bed.material_index = 0; set_face_uv_rect(bm, f_bed, UV_NEUTRAL_BUFFER)

    # 4. Front Panel Face around the Window: 4 surrounding quads with CONTINUOUS UV!
    f_face_l = bm.faces.new([v_f_br, v_win_br, v_win_tr, v_f_tr])
    f_face_l.material_index = 0
    apply_continuous_front_uv(bm, f_face_l, UV_FRONT_FASCIA, x_bounds, z_bounds)

    f_face_r = bm.faces.new([v_win_bl, v_f_bl, v_f_tl, v_win_tl])
    f_face_r.material_index = 0
    apply_continuous_front_uv(bm, f_face_r, UV_FRONT_FASCIA, x_bounds, z_bounds)

    f_face_b = bm.faces.new([v_f_br, v_f_bl, v_win_bl, v_win_br])
    f_face_b.material_index = 0
    apply_continuous_front_uv(bm, f_face_b, UV_FRONT_FASCIA, x_bounds, z_bounds)

    f_face_t = bm.faces.new([v_win_tr, v_win_tl, v_f_tl, v_f_tr])
    f_face_t.material_index = 0
    apply_continuous_front_uv(bm, f_face_t, UV_FRONT_FASCIA, x_bounds, z_bounds)

    # 5. Tactile 3D Jog-Shuttle Dial on Screen Right (12-sided beveled cylinder)
    dial_x = -0.130
    dial_z =  0.044
    dial_r =  0.015
    y_dial =  0.013

    v_dial_b = []
    v_dial_f = []
    for a in range(12):
        ang = 2.0 * math.pi * a / 12.0
        bx = dial_x + dial_r * math.cos(ang)
        bz = dial_z + dial_r * math.sin(ang)
        v_dial_b.append(bm.verts.new(Vector((bx, y_f, bz))))
        v_dial_f.append(bm.verts.new(Vector((bx, y_dial, bz))))

    for a in range(12):
        a_n = (a + 1) % 12
        f_ds = bm.faces.new([v_dial_b[a], v_dial_b[a_n], v_dial_f[a_n], v_dial_f[a]])
        f_ds.material_index = 0; set_face_uv_rect(bm, f_ds, UV_CASING_METAL)

    f_dial_cap = bm.faces.new(list(reversed(v_dial_f)))
    f_dial_cap.material_index = 0; set_face_uv_rect(bm, f_dial_cap, UV_CASING_METAL)

    # 6. Recessed Dual Front USB Ports (Screen Right: X: [-0.196, -0.174], Z: [0.018, 0.038])
    usb_x0, usb_x1 = -0.196, -0.174
    usb_z0, usb_z1 =  0.018,  0.038
    v_usb_lip = [
        bm.verts.new(Vector((usb_x0, y_f, usb_z0))),
        bm.verts.new(Vector((usb_x1, y_f, usb_z0))),
        bm.verts.new(Vector((usb_x1, y_f, usb_z1))),
        bm.verts.new(Vector((usb_x0, y_f, usb_z1)))
    ]
    v_usb_bed = [
        bm.verts.new(Vector((usb_x0, 0.003, usb_z0))),
        bm.verts.new(Vector((usb_x1, 0.003, usb_z0))),
        bm.verts.new(Vector((usb_x1, 0.003, usb_z1))),
        bm.verts.new(Vector((usb_x0, 0.003, usb_z1)))
    ]
    for i in range(4):
        i_n = (i + 1) % 4
        f_uw = bm.faces.new([v_usb_lip[i], v_usb_lip[i_n], v_usb_bed[i_n], v_usb_bed[i]])
        f_uw.material_index = 0; set_face_uv_rect(bm, f_uw, UV_CASING_METAL)
    f_ubed = bm.faces.new(v_usb_bed); f_ubed.material_index = 0; set_face_uv_rect(bm, f_ubed, UV_NEUTRAL_BUFFER)

    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


def build_status_display_mesh(mesh, materials):
    """
    Build Status_Display:
    Alphanumeric VFD display sitting flush inside the front panel cutout window.
    Origin at its geometric center (X: 0.000, Y: +0.0055m, Z: 0.044m).
    Width: 96mm, Height: 32mm.
    Material: M_Screen (Slot 1).
    Tris count: 2 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    hw = 0.048
    hh = 0.016

    v_br = bm.verts.new(Vector(( hw, 0.0, -hh))) # Screen Left (+X)
    v_bl = bm.verts.new(Vector((-hw, 0.0, -hh))) # Screen Right (-X)
    v_tl = bm.verts.new(Vector((-hw, 0.0,  hh)))
    v_tr = bm.verts.new(Vector(( hw, 0.0,  hh)))

    f = bm.faces.new([v_br, v_bl, v_tl, v_tr])
    f.material_index = 1 # M_Screen

    uv_lay = bm.loops.layers.uv.verify()
    f.loops[0][uv_lay].uv = (0.0, 0.0) # v_br
    f.loops[1][uv_lay].uv = (1.0, 0.0) # v_bl
    f.loops[2][uv_lay].uv = (1.0, 1.0) # v_tl
    f.loops[3][uv_lay].uv = (0.0, 1.0) # v_tr

    bm.to_mesh(mesh)
    bm.free()


def build_power_button_mesh(mesh, materials):
    """
    Build Power_Button:
    Tactile 8-sided cylindrical button protruding from front panel.
    Origin at X: -0.185, Y: +0.008, Z: 0.054 (Screen Right).
    Material: Slot 0 M_Security_Atlas (with standby ⏻ logo).
    Tris count: 18 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    r = 0.007
    v_b = []
    v_f = []
    for a in range(8):
        ang = 2.0 * math.pi * a / 8.0
        bx = r * math.cos(ang)
        bz = r * math.sin(ang)
        v_b.append(bm.verts.new(Vector((bx, 0.000, bz))))
        v_f.append(bm.verts.new(Vector((bx, 0.0035, bz))))

    for a in range(8):
        a_n = (a + 1) % 8
        f_s = bm.faces.new([v_b[a], v_b[a_n], v_f[a_n], v_f[a]])
        f_s.material_index = 0; set_face_uv_rect(bm, f_s, UV_CASING_METAL)

    f_front = bm.faces.new(list(reversed(v_f)))
    f_front.material_index = 0
    set_face_uv_rect(bm, f_front, UV_POWER_BTN)

    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


def build_status_led_array_mesh(mesh, materials):
    """
    Build Status_LED_Array:
    8 discrete indicator jewel domes (PWR, NET, HDD, LNK, REC, ALM, ERR, ACT).
    Positioned cleanly ABOVE their printed labels on the front panel!
    Material: M_Emission (Slot 2).
    Tris count: ~48 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    # Offsets relative to obj_leds origin (centered at X: -0.080, Z: 0.044)
    # Row 1 (Z: +0.012): PWR (+0.018), NET (+0.006), HDD (-0.006), LNK (-0.018)
    # Row 2 (Z: -0.012): REC (+0.018), ALM (+0.006), ERR (-0.006), ACT (-0.018)
    led_offsets = [
        ( 0.018,  0.012), # PWR
        ( 0.006,  0.012), # NET
        (-0.006,  0.012), # HDD
        (-0.018,  0.012), # LNK
        ( 0.018, -0.012), # REC
        ( 0.006, -0.012), # ALM
        (-0.006, -0.012), # ERR
        (-0.018, -0.012)  # ACT
    ]

    r_led = 0.0025
    for lx, lz in led_offsets:
        v_dome = []
        for a in range(6):
            ang = 2.0 * math.pi * a / 6.0
            vx = lx + r_led * math.cos(ang)
            vz = lz + r_led * math.sin(ang)
            v_dome.append(bm.verts.new(Vector((vx, 0.002, vz))))
        f_led = bm.faces.new(v_dome)
        f_led.material_index = 2 # M_Emission
        set_face_uv_rect(bm, f_led, UV_NEUTRAL_BUFFER)

    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
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

    # 1. Root Empty: SEC_Rack_DVR_Recorder at (0, 0, 0)
    root_empty = bpy.data.objects.new("SEC_Rack_DVR_Recorder", None)
    root_empty.empty_display_type = 'PLAIN_AXES'
    root_empty.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root_empty)

    # 2. Chassis (child of Root)
    mesh_chassis = bpy.data.meshes.new("Chassis")
    obj_chassis = bpy.data.objects.new("Chassis", mesh_chassis)
    build_chassis_mesh(mesh_chassis, materials)
    bpy.context.collection.objects.link(obj_chassis)
    obj_chassis.parent = root_empty

    # 3. Rack_Ears (child of Chassis)
    mesh_ears = bpy.data.meshes.new("Rack_Ears")
    obj_ears = bpy.data.objects.new("Rack_Ears", mesh_ears)
    build_rack_ears_mesh(mesh_ears, materials)
    bpy.context.collection.objects.link(obj_ears)
    obj_ears.parent = obj_chassis

    # 4. Front_Panel (child of Chassis)
    mesh_front = bpy.data.meshes.new("Front_Panel")
    obj_front = bpy.data.objects.new("Front_Panel", mesh_front)
    build_front_panel_mesh(mesh_front, materials)
    bpy.context.collection.objects.link(obj_front)
    obj_front.parent = obj_chassis

    # 5. Status_Display (child of Front_Panel)
    mesh_display = bpy.data.meshes.new("Status_Display")
    obj_display = bpy.data.objects.new("Status_Display", mesh_display)
    build_status_display_mesh(mesh_display, materials)
    bpy.context.collection.objects.link(obj_display)
    obj_display.location = Vector((0.000, 0.0055, 0.044))
    obj_display.parent = obj_front

    # 6. Power_Button (child of Front_Panel)
    mesh_power = bpy.data.meshes.new("Power_Button")
    obj_power = bpy.data.objects.new("Power_Button", mesh_power)
    build_power_button_mesh(mesh_power, materials)
    bpy.context.collection.objects.link(obj_power)
    obj_power.location = Vector((-0.180, 0.008, 0.054))
    obj_power.parent = obj_front
    obj_power["press_axis"] = "Y"
    obj_power["travel_m"] = 0.002
    obj_power["action"] = "POWER_TOGGLE"

    # 7. Status_LED_Array (child of Front_Panel)
    mesh_leds = bpy.data.meshes.new("Status_LED_Array")
    obj_leds = bpy.data.objects.new("Status_LED_Array", mesh_leds)
    build_status_led_array_mesh(mesh_leds, materials)
    bpy.context.collection.objects.link(obj_leds)
    obj_leds.location = Vector((-0.080, 0.008, 0.044))
    obj_leds.parent = obj_front

    bpy.context.view_layer.update()

    # Save Blend file
    blend_path = os.path.join(EXPORTS_DIR, "SEC_Rack_DVR_Recorder.blend")
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
    obj_chassis.select_set(True)
    obj_ears.select_set(True)
    obj_front.select_set(True)
    obj_display.select_set(True)
    obj_power.select_set(True)
    obj_leds.select_set(True)

    fbx_path = os.path.join(EXPORTS_DIR, "SEC_Rack_DVR_Recorder.fbx")
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
    root = bpy.data.objects.get("SEC_Rack_DVR_Recorder")
    assert root is not None, "[QA ERROR] Root object 'SEC_Rack_DVR_Recorder' not found!"
    assert root.type == 'EMPTY', f"[QA ERROR] Root should be EMPTY, got {root.type}"

    # Calculate triangulated polygon count
    total_tris = 0
    mesh_count = 0
    for obj in imported_objs:
        if obj.type == 'MESH':
            mesh_count += 1
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            tris = len(bm.faces)
            total_tris += tris
            bm.free()

    print(f"[QA] TOTAL TRIANGLES: {total_tris} (Budget limit: 500)")
    assert total_tris <= 500, f"[QA ERROR] Triangles {total_tris} exceeds budget 500!"

    expected_materials = ["M_Security_Atlas", "M_Screen", "M_Emission", "M_Metal"]
    imported_mat_names = [m.name for m in bpy.data.materials]
    for em in expected_materials:
        assert any(em in im for im in imported_mat_names), f"[QA ERROR] Material {em} missing from imported scene!"

    # Write manifest
    manifest_path = os.path.join(EXPORTS_DIR, "manifest.json")
    manifest_data = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_Rack_DVR_Recorder"] = {
        "asset_name": "SEC_Rack_DVR_Recorder",
        "fbx_path": "exports/SEC_Rack_DVR_Recorder.fbx",
        "blend_path": "exports/SEC_Rack_DVR_Recorder.blend",
        "tris_count": total_tris,
        "mesh_count": mesh_count,
        "empty_count": 1,
        "materials": expected_materials,
        "status": "SUCCESS"
    }

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=2)

    print(f"[QA] Manifest written to {manifest_path}")
    print("[QA] ALL CHECKS PASSED SUCCESSFULLY!\n")


if __name__ == "__main__":
    assemble_and_export()
