"""
=============================================================================
Security CCTV Asset Production Suite - Asset 52
Asset Name: SEC_Monitor_Keyboard (CCTV Operator Klavyesi)
Texture Atlas Generator (2048x2048)
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

FONT_MONO = r"C:\Windows\Fonts\consolab.ttf"
FONT_SANS = r"C:\Windows\Fonts\arialbd.ttf"
FONT_SEGOE = r"C:\Windows\Fonts\segoeuib.ttf"

ATLAS_W, ATLAS_H = 2048, 2048

# Color Palette
CHASSIS_DARK = (24, 27, 32, 255)
CHASSIS_BEVEL = (38, 43, 51, 255)
KEY_TOP_DARK = (32, 36, 44, 255)
KEY_TOP_ACCENT = (42, 48, 58, 255)
KEY_CCTV_SPECIAL = (28, 55, 80, 255)
KEY_REC_RED = (95, 25, 25, 255)
RUBBER_BLACK = (16, 17, 19, 255)
WHITE = (255, 255, 255, 255)
INK_TEXT = (225, 232, 242, 255)
INK_CYAN = (45, 195, 245, 255)
INK_AMBER = (245, 175, 25, 255)
INK_GREEN = (45, 225, 85, 255)
INK_RED = (245, 55, 45, 255)

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

def draw_key_cap(draw, x0, y0, x1, y1, label, sub_label=None, fill=KEY_TOP_DARK, text_col=WHITE, sub_col=INK_CYAN):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=fill, outline=(55, 62, 75, 255), width=2)
    # Bevel highlight on top
    draw.line([(x0 + 4, y0 + 3), (x1 - 4, y0 + 3)], fill=(80, 90, 110, 255), width=1)
    
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    
    if sub_label:
        f_main = load_font(FONT_MONO, 16)
        f_sub = load_font(FONT_MONO, 12)
        draw_center_text(draw, cx, cy - 8, label, f_main, text_col)
        draw_center_text(draw, cx, cy + 10, sub_label, f_sub, sub_col)
    else:
        f_main = load_font(FONT_MONO, 18)
        draw_center_text(draw, cx, cy, label, f_main, text_col)

def main():
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), CHASSIS_DARK)
    draw = ImageDraw.Draw(img)

    # =========================================================================
    # 1. KEYBOARD TOP CHASSIS (0..1440, 0..600)
    # =========================================================================
    cx0, cy0, cx1, cy1 = 20, 20, 1420, 580
    draw.rounded_rectangle([cx0, cy0, cx1, cy1], radius=16, fill=(28, 31, 38, 255), outline=(50, 56, 68, 255), width=3)
    
    # Outer chamfer border
    draw.line([(cx0 + 8, cy0 + 8), (cx1 - 8, cy0 + 8)], fill=(65, 75, 90, 255), width=2)
    draw.line([(cx0 + 8, cy1 - 8), (cx1 - 8, cy1 - 8)], fill=(18, 20, 24, 255), width=2)

    # Top Branding Header & Status LEDs
    f_brand = load_font(FONT_SANS, 22)
    f_model = load_font(FONT_MONO, 14)
    draw.text((cx0 + 30, cy0 + 20), "SEC-VISION", fill=WHITE, font=f_brand)
    draw.text((cx0 + 175, cy0 + 26), "CCTV OPERATOR CONSOLE KEYBOARD  |  MODEL KB-884-PRO", fill=(160, 175, 195, 255), font=f_model)

    # Status LEDs top right: NUM, CAPS, CCTV, REC
    leds = [
        ("NUM", INK_GREEN, cx1 - 320),
        ("CAPS", INK_GREEN, cx1 - 240),
        ("CCTV", INK_CYAN, cx1 - 160),
        ("REC", INK_RED, cx1 - 80)
    ]
    f_led = load_font(FONT_MONO, 12)
    for name, col, lx in leds:
        draw.ellipse([lx, cy0 + 24, lx + 12, cy0 + 36], fill=col)
        draw.text((lx + 18, cy0 + 23), name, fill=WHITE, font=f_led)

    # Recessed Key Well (Where keys sit)
    kx0, ky0, kx1, ky1 = cx0 + 20, cy0 + 60, cx1 - 20, cy1 - 25
    draw.rounded_rectangle([kx0, ky0, kx1, ky1], radius=8, fill=(18, 20, 25, 255), outline=(42, 48, 58, 255), width=2)

    # =========================================================================
    # 2. INDIVIDUAL KEY ROWS (Mapped to Key_Row_01 .. Key_Row_05)
    # Each row is 1360 x 140 px on the atlas
    # =========================================================================

    # --- ROW 01 (Function & CCTV Navigation): Y = 620 .. 760 ---
    ry0 = 620
    draw.rectangle([20, ry0, 1420, ry0 + 140], fill=(22, 25, 30, 255), outline=(45, 52, 64, 255), width=1)
    row1_keys = [
        ("ESC", None, KEY_TOP_DARK, WHITE, INK_CYAN, 70),
        ("F1", "CAM 1", KEY_CCTV_SPECIAL, WHITE, INK_CYAN, 75),
        ("F2", "CAM 2", KEY_CCTV_SPECIAL, WHITE, INK_CYAN, 75),
        ("F3", "CAM 3", KEY_CCTV_SPECIAL, WHITE, INK_CYAN, 75),
        ("F4", "CAM 4", KEY_CCTV_SPECIAL, WHITE, INK_CYAN, 75),
        ("F5", "QUAD", KEY_CCTV_SPECIAL, WHITE, INK_AMBER, 75),
        ("F6", "SEQ", KEY_CCTV_SPECIAL, WHITE, INK_AMBER, 75),
        ("F7", "FREEZE", KEY_CCTV_SPECIAL, WHITE, INK_AMBER, 80),
        ("F8", "MUX", KEY_CCTV_SPECIAL, WHITE, INK_CYAN, 75),
        ("F9", "PTZ", KEY_TOP_ACCENT, WHITE, INK_GREEN, 75),
        ("F10", "IRIS+", KEY_TOP_ACCENT, WHITE, INK_CYAN, 75),
        ("F11", "IRIS-", KEY_TOP_ACCENT, WHITE, INK_CYAN, 75),
        ("F12", "LOCK", KEY_TOP_ACCENT, WHITE, INK_RED, 75),
        ("PRINT", "LOG", KEY_TOP_DARK, WHITE, INK_CYAN, 80),
        ("PAUSE", "ALM", KEY_REC_RED, WHITE, WHITE, 85)
    ]
    cur_x = 35
    for lbl, sub, fill, tc, sc, kw in row1_keys:
        draw_key_cap(draw, cur_x, ry0 + 20, cur_x + kw, ry0 + 120, lbl, sub, fill, tc, sc)
        cur_x += kw + 14

    # --- ROW 02 (Numbers & Presets): Y = 780 .. 920 ---
    ry1 = 780
    draw.rectangle([20, ry1, 1420, ry1 + 140], fill=(22, 25, 30, 255), outline=(45, 52, 64, 255), width=1)
    row2_keys = [
        ("~", "`", KEY_TOP_DARK, WHITE, INK_CYAN, 65),
        ("1", "PRE 1", KEY_TOP_DARK, WHITE, INK_CYAN, 70),
        ("2", "PRE 2", KEY_TOP_DARK, WHITE, INK_CYAN, 70),
        ("3", "PRE 3", KEY_TOP_DARK, WHITE, INK_CYAN, 70),
        ("4", "PRE 4", KEY_TOP_DARK, WHITE, INK_CYAN, 70),
        ("5", "PRE 5", KEY_TOP_DARK, WHITE, INK_CYAN, 70),
        ("6", "PRE 6", KEY_TOP_DARK, WHITE, INK_CYAN, 70),
        ("7", "PRE 7", KEY_TOP_DARK, WHITE, INK_CYAN, 70),
        ("8", "PRE 8", KEY_TOP_DARK, WHITE, INK_CYAN, 70),
        ("9", "PRE 9", KEY_TOP_DARK, WHITE, INK_CYAN, 70),
        ("0", "TOUR", KEY_TOP_DARK, WHITE, INK_AMBER, 70),
        ("-", "_", KEY_TOP_DARK, WHITE, INK_CYAN, 65),
        ("+", "=", KEY_TOP_DARK, WHITE, INK_CYAN, 65),
        ("BACKSPACE", "CLR", KEY_TOP_ACCENT, WHITE, INK_RED, 120),
        ("HOME", "RESET", KEY_TOP_DARK, WHITE, INK_GREEN, 85)
    ]
    cur_x = 35
    for lbl, sub, fill, tc, sc, kw in row2_keys:
        draw_key_cap(draw, cur_x, ry1 + 20, cur_x + kw, ry1 + 120, lbl, sub, fill, tc, sc)
        cur_x += kw + 14

    # --- ROW 03 (QWERTY & Zoom Controls): Y = 940 .. 1080 ---
    ry2 = 940
    draw.rectangle([20, ry2, 1420, ry2 + 140], fill=(22, 25, 30, 255), outline=(45, 52, 64, 255), width=1)
    row3_keys = [
        ("TAB", "CCTV", KEY_TOP_ACCENT, WHITE, INK_CYAN, 95),
        ("Q", None, KEY_TOP_DARK, WHITE, INK_CYAN, 68),
        ("W", "TILT▲", KEY_TOP_ACCENT, WHITE, INK_GREEN, 68),
        ("E", None, KEY_TOP_DARK, WHITE, INK_CYAN, 68),
        ("R", "REC", KEY_REC_RED, WHITE, WHITE, 68),
        ("T", None, KEY_TOP_DARK, WHITE, INK_CYAN, 68),
        ("Y", None, KEY_TOP_DARK, WHITE, INK_CYAN, 68),
        ("U", None, KEY_TOP_DARK, WHITE, INK_CYAN, 68),
        ("I", None, KEY_TOP_DARK, WHITE, INK_CYAN, 68),
        ("O", None, KEY_TOP_DARK, WHITE, INK_CYAN, 68),
        ("P", "PLAY", KEY_TOP_DARK, WHITE, INK_GREEN, 68),
        ("[", "ZOOM-", KEY_CCTV_SPECIAL, WHITE, INK_CYAN, 75),
        ("]", "ZOOM+", KEY_CCTV_SPECIAL, WHITE, INK_CYAN, 75),
        ("DEL", "ACK", KEY_REC_RED, WHITE, WHITE, 90),
        ("END", "PARK", KEY_TOP_DARK, WHITE, INK_AMBER, 85)
    ]
    cur_x = 35
    for lbl, sub, fill, tc, sc, kw in row3_keys:
        draw_key_cap(draw, cur_x, ry2 + 20, cur_x + kw, ry2 + 120, lbl, sub, fill, tc, sc)
        cur_x += kw + 14

    # --- ROW 04 (Home row ASDF & Iris/Pan Controls): Y = 1100 .. 1240 ---
    ry3 = 1100
    draw.rectangle([20, ry3, 1420, ry3 + 140], fill=(22, 25, 30, 255), outline=(45, 52, 64, 255), width=1)
    row4_keys = [
        ("CAPS", "LOCK", KEY_TOP_ACCENT, WHITE, INK_CYAN, 105),
        ("A", "PAN◀", KEY_TOP_ACCENT, WHITE, INK_GREEN, 68),
        ("S", "TILT▼", KEY_TOP_ACCENT, WHITE, INK_GREEN, 68),
        ("D", "PAN▶", KEY_TOP_ACCENT, WHITE, INK_GREEN, 68),
        ("F", "FOCUS+", KEY_CCTV_SPECIAL, WHITE, INK_CYAN, 68),
        ("G", "FOCUS-", KEY_CCTV_SPECIAL, WHITE, INK_CYAN, 68),
        ("H", None, KEY_TOP_DARK, WHITE, INK_CYAN, 68),
        ("J", None, KEY_TOP_DARK, WHITE, INK_CYAN, 68),
        ("K", None, KEY_TOP_DARK, WHITE, INK_CYAN, 68),
        ("L", None, KEY_TOP_DARK, WHITE, INK_CYAN, 68),
        (";", ":", KEY_TOP_DARK, WHITE, INK_CYAN, 65),
        ("'", "\"", KEY_TOP_DARK, WHITE, INK_CYAN, 65),
        ("ENTER", "ACK ALARM", KEY_CCTV_SPECIAL, WHITE, INK_AMBER, 145),
        ("PGUP", "SPEED+", KEY_TOP_DARK, WHITE, INK_CYAN, 85)
    ]
    cur_x = 35
    for lbl, sub, fill, tc, sc, kw in row4_keys:
        draw_key_cap(draw, cur_x, ry3 + 20, cur_x + kw, ry3 + 120, lbl, sub, fill, tc, sc)
        cur_x += kw + 14

    # --- ROW 05 (Shift, Space, Arrow Navigation & PTZ): Y = 1260 .. 1400 ---
    ry4 = 1260
    draw.rectangle([20, ry4, 1420, ry4 + 140], fill=(22, 25, 30, 255), outline=(45, 52, 64, 255), width=1)
    row5_keys = [
        ("SHIFT", None, KEY_TOP_ACCENT, WHITE, INK_CYAN, 120),
        ("CTRL", "CCTV", KEY_TOP_ACCENT, WHITE, INK_CYAN, 80),
        ("ALT", None, KEY_TOP_ACCENT, WHITE, INK_CYAN, 75),
        ("SPACEBAR", "MANUAL EVENT MARK [REC]", KEY_TOP_DARK, WHITE, INK_GREEN, 380),
        ("ALT", None, KEY_TOP_ACCENT, WHITE, INK_CYAN, 75),
        ("CTRL", None, KEY_TOP_ACCENT, WHITE, INK_CYAN, 80),
        ("◀", "PAN L", KEY_CCTV_SPECIAL, WHITE, INK_CYAN, 65),
        ("▲", "TILT U", KEY_CCTV_SPECIAL, WHITE, INK_CYAN, 65),
        ("▼", "TILT D", KEY_CCTV_SPECIAL, WHITE, INK_CYAN, 65),
        ("▶", "PAN R", KEY_CCTV_SPECIAL, WHITE, INK_CYAN, 65),
        ("PGDN", "SPEED-", KEY_TOP_DARK, WHITE, INK_CYAN, 85)
    ]
    cur_x = 35
    for lbl, sub, fill, tc, sc, kw in row5_keys:
        draw_key_cap(draw, cur_x, ry4 + 20, cur_x + kw, ry4 + 120, lbl, sub, fill, tc, sc)
        cur_x += kw + 14

    # =========================================================================
    # 3. KEYBOARD REAR & BOTTOM BASE (0..1440, 1420..1980)
    # =========================================================================
    bx0, by0, bx1, by1 = 20, 1440, 1420, 1980
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=14, fill=(20, 22, 26, 255), outline=(45, 50, 60, 255), width=2)
    
    # Specification Plate in center bottom
    px0, py0, px1, py1 = bx0 + 120, by0 + 80, bx1 - 120, by1 - 80
    draw.rectangle([px0, py0, px1, py1], fill=(14, 16, 20, 255), outline=(55, 62, 74, 255), width=2)
    
    draw.text((px0 + 30, py0 + 20), "SEC-VISION SECURITY KEYBOARD CONTROLLER", fill=WHITE, font=load_font(FONT_MONO, 18))
    draw.line([(px0 + 30, py0 + 48), (px1 - 30, py0 + 48)], fill=(55, 62, 74, 255), width=1)
    
    specs = [
        "MODEL NUMBER  : SEC-KB-884-PRO (CCTV OPERATOR TERMINAL)",
        "RATED VOLTAGE : 5V DC --- 250mA (USB 2.0 / RS-485)",
        "SWITCH TYPE   : INDUSTRIAL MEMBRANE SCISSOR (10M CYCLES)",
        "KEY PROTOCOL  : PELCO-D / PELCO-P / STANDARD HID KEYBOARD",
        "SERIAL NUMBER : SN-KB884-2026-904128",
        "COMPLIANCE    : [CE]  [FCC CLASS B]  [RoHS]  [IP42 RUGGED]"
    ]
    for i, s in enumerate(specs):
        draw.text((px0 + 30, py0 + 60 + i * 26), s, fill=INK_TEXT, font=load_font(FONT_MONO, 14))

    # Barcode
    bar_x = px1 - 320
    bar_y = py0 + 65
    for b in range(0, 280, 5):
        w = 2 if (b % 15 == 0 or b % 25 == 0) else 1
        draw.line([(bar_x + b, bar_y), (bar_x + b, bar_y + 90)], fill=WHITE, width=w)
    draw.text((bar_x + 35, bar_y + 100), "*SN-KB884-2026-904128*", fill=INK_TEXT, font=load_font(FONT_MONO, 12))

    # Four Corner Rubber Feet outlines on bottom plate
    draw.rounded_rectangle([bx0 + 40, by0 + 30, bx0 + 100, by0 + 70], radius=4, fill=RUBBER_BLACK, outline=(35, 40, 50, 255), width=1)
    draw.rounded_rectangle([bx1 - 100, by0 + 30, bx1 - 40, by0 + 70], radius=4, fill=RUBBER_BLACK, outline=(35, 40, 50, 255), width=1)
    draw.rounded_rectangle([bx0 + 40, by1 - 70, bx0 + 100, by1 - 30], radius=4, fill=RUBBER_BLACK, outline=(35, 40, 50, 255), width=1)
    draw.rounded_rectangle([bx1 - 100, by1 - 70, bx1 - 40, by1 - 30], radius=4, fill=RUBBER_BLACK, outline=(35, 40, 50, 255), width=1)

    # =========================================================================
    # 4. FLAT COLOR & MATERIAL SWATCHES (1500..2048, 0..2048)
    # =========================================================================
    swatches = [
        ((1500, 40, 2000, 240), CHASSIS_DARK, "CHASSIS_DARK"),
        ((1500, 260, 2000, 460), CHASSIS_BEVEL, "CHASSIS_BEVEL"),
        ((1500, 480, 2000, 680), KEY_TOP_DARK, "KEY_TOP_DARK"),
        ((1500, 700, 2000, 900), KEY_TOP_ACCENT, "KEY_TOP_ACCENT"),
        ((1500, 920, 2000, 1120), KEY_CCTV_SPECIAL, "KEY_CCTV_SPECIAL"),
        ((1500, 1140, 2000, 1340), RUBBER_BLACK, "M_RUBBER"),
        ((1500, 1360, 2000, 1560), (140, 148, 160, 255), "STEEL_LOGO"),
        ((1500, 1580, 2000, 1780), (10, 12, 15, 255), "INNER_SHADOW"),
        ((1500, 1800, 2000, 2000), (45, 52, 65, 255), "KEY_SIDES")
    ]
    for box, col, name in swatches:
        draw.rectangle(box, fill=col)
        draw.text((box[0] + 20, box[1] + 20), name, fill=WHITE, font=load_font(FONT_MONO, 16))

    img.save(ATLAS_PATH, "PNG")
    print(f"[Atlas] Generated: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

if __name__ == "__main__":
    main()
