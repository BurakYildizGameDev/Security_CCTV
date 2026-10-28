"""
=============================================================================
Security CCTV Asset Production Suite - Asset 53
Asset Name: SEC_Console_Rack_Keyboard_Drawer (1U Rack Klavye Tepsisi)
Texture Generator Script (2048x2048 Atlas)
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

ATLAS_W, ATLAS_H = 2048, 2048

# Color Palette
RACK_BLACK = (22, 24, 28, 255)
RACK_PANEL = (30, 34, 42, 255)
STEEL_GALV = (145, 155, 168, 255)
KEY_DARK = (26, 30, 38, 255)
KEY_ACCENT = (38, 48, 62, 255)
TOUCHPAD_SURF = (36, 42, 52, 255)
WHITE = (255, 255, 255, 255)
INK_TEXT = (220, 228, 238, 255)
INK_CYAN = (40, 190, 240, 255)
INK_AMBER = (245, 175, 20, 255)
INK_GREEN = (40, 220, 80, 255)
INK_RED = (235, 45, 35, 255)

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

def main():
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), RACK_BLACK)
    draw = ImageDraw.Draw(img)

    # =========================================================================
    # 1. 1U FRONT FASCIA (20..1960, 20..220)
    # Dimensions match 482.6mm x 44.45mm (approx 10.8 : 1)
    # =========================================================================
    fx0, fy0, fx1, fy1 = 20, 20, 1960, 210
    draw.rectangle([fx0, fy0, fx1, fy1], fill=RACK_PANEL, outline=(55, 62, 75, 255), width=2)
    draw.line([(fx0 + 4, fy0 + 4), (fx1 - 4, fy0 + 4)], fill=(75, 85, 100, 255), width=2)
    draw.line([(fx0 + 4, fy1 - 4), (fx1 - 4, fy1 - 4)], fill=(18, 20, 25, 255), width=2)

    # Rack Ears: Left and Right mounting holes
    for rx in [fx0 + 35, fx1 - 35]:
        draw.ellipse([rx - 14, fy0 + 20, rx + 14, fy0 + 48], fill=(12, 14, 16, 255), outline=STEEL_GALV, width=2)
        draw.ellipse([rx - 14, fy1 - 48, rx + 14, fy1 - 20], fill=(12, 14, 16, 255), outline=STEEL_GALV, width=2)

    # Front Pull Handle Recess
    hx0, hy0, hx1, hy1 = (fx0 + fx1) // 2 - 240, fy0 + 35, (fx0 + fx1) // 2 + 240, fy1 - 35
    draw.rounded_rectangle([hx0, hy0, hx1, hy1], radius=8, fill=(18, 20, 24, 255), outline=(55, 65, 80, 255), width=2)
    draw_center_text(draw, (fx0 + fx1) // 2, (fy0 + fy1) // 2, "PULL TO RELEASE  ◄►  SEC-KVM 1U DRAWER", load_font(FONT_MONO, 16), INK_CYAN)

    # Key Lock Cylinder on Left
    draw.ellipse([fx0 + 130, fy0 + 45, fx0 + 185, fy1 - 45], fill=(35, 40, 50, 255), outline=STEEL_GALV, width=2)
    draw.rectangle([fx0 + 155, fy0 + 60, fx0 + 160, fy1 - 60], fill=(12, 14, 16, 255))
    draw.text((fx0 + 200, (fy0 + fy1) // 2 - 8), "LOCK", fill=WHITE, font=load_font(FONT_MONO, 14))

    # KVM Port Selector LED Matrix on Right
    draw.text((fx1 - 340, fy0 + 30), "KVM ACTIVE PORT:", fill=INK_TEXT, font=load_font(FONT_MONO, 12))
    for p in range(8):
        lx = fx1 - 340 + p * 36
        draw.ellipse([lx, fy0 + 55, lx + 12, fy0 + 67], fill=INK_GREEN if p == 0 else (30, 45, 35, 255))
        draw_center_text(draw, lx + 6, fy0 + 85, str(p + 1), load_font(FONT_MONO, 11), WHITE)

    # =========================================================================
    # 2. KEYBOARD & TOUCHPAD SURFACE (20..1960, 240..1180)
    # Total surface fits inside tray (440mm x 260mm)
    # =========================================================================
    kx0, ky0, kx1, ky1 = 20, 240, 1960, 1180
    draw.rounded_rectangle([kx0, ky0, kx1, ky1], radius=12, fill=(20, 23, 28, 255), outline=(48, 55, 68, 255), width=2)

    # Header Strip above keyboard
    draw.rectangle([kx0 + 15, ky0 + 15, kx1 - 15, ky0 + 65], fill=(28, 32, 40, 255))
    draw.text((kx0 + 35, ky0 + 26), "SEC-VISION  |  19\" 1U RACKMOUNT CONSOLE  |  8-PORT KVM SWITCH INTERFACE", fill=WHITE, font=load_font(FONT_MONO, 16))
    draw.text((kx1 - 400, ky0 + 26), "STATUS: ONLINE  •  CASCADE: PRIMARY", fill=INK_GREEN, font=load_font(FONT_MONO, 14))

    # Left Section: 88-Key Compact Keyboard Bed (kx0 + 20 .. 1420)
    draw.rounded_rectangle([kx0 + 20, ky0 + 80, 1420, ky1 - 25], radius=8, fill=(15, 17, 21, 255), outline=(42, 48, 60, 255), width=1)
    
    # Draw key rows inside keyboard bed:
    # Row 1: ESC, F1..F12, CAM 1..4, QUAD, SEQ
    k_y0 = ky0 + 95
    row_h = 135
    row_gap = 12

    # Draw simulated crisp key rows
    f_k = load_font(FONT_MONO, 15)
    f_sub = load_font(FONT_MONO, 11)

    r1_keys = ["ESC", "F1/C1", "F2/C2", "F3/C3", "F4/C4", "F5/QD", "F6/SQ", "F7/FZ", "F8", "F9", "F10", "F11", "F12", "PRT", "PAUS"]
    cw = (1380 - len(r1_keys) * 8) // len(r1_keys)
    for i, k in enumerate(r1_keys):
        bx = kx0 + 35 + i * (cw + 8)
        col = (35, 55, 80, 255) if "C" in k or "QD" in k else KEY_DARK
        draw.rounded_rectangle([bx, k_y0, bx + cw, k_y0 + 120], radius=4, fill=col, outline=(55, 65, 80, 255), width=1)
        draw_center_text(draw, bx + cw // 2, k_y0 + 60, k, f_k, WHITE)

    # Row 2: Numbers & KVM Port Direct Select
    k_y1 = k_y0 + row_h + row_gap
    r2_keys = ["`", "1/P1", "2/P2", "3/P3", "4/P4", "5/P5", "6/P6", "7/P7", "8/P8", "9", "0", "-", "+", "BKSP", "HOME"]
    cw2 = (1380 - len(r2_keys) * 8) // len(r2_keys)
    for i, k in enumerate(r2_keys):
        bx = kx0 + 35 + i * (cw2 + 8)
        draw.rounded_rectangle([bx, k_y1, bx + cw2, k_y1 + 120], radius=4, fill=KEY_DARK, outline=(55, 65, 80, 255), width=1)
        draw_center_text(draw, bx + cw2 // 2, k_y1 + 60, k, f_k, WHITE)

    # Row 3: QWERTY & Zoom
    k_y2 = k_y1 + row_h + row_gap
    r3_keys = ["TAB", "Q", "W/▲", "E", "R/REC", "T", "Y", "U", "I", "O", "P", "[/Z-", "]/Z+", "DEL", "END"]
    for i, k in enumerate(r3_keys):
        bx = kx0 + 35 + i * (cw2 + 8)
        col = (85, 25, 25, 255) if "REC" in k else KEY_DARK
        draw.rounded_rectangle([bx, k_y2, bx + cw2, k_y2 + 120], radius=4, fill=col, outline=(55, 65, 80, 255), width=1)
        draw_center_text(draw, bx + cw2 // 2, k_y2 + 60, k, f_k, WHITE)

    # Row 4: ASDF & Pan/Tilt
    k_y3 = k_y2 + row_h + row_gap
    r4_keys = ["CAPS", "A/◄", "S/▼", "D/►", "F/F+", "G/F-", "H", "J", "K", "L", ";", "'", "ENTER [ACK]", "PGUP"]
    cw4 = (1380 - len(r4_keys) * 8) // len(r4_keys)
    for i, k in enumerate(r4_keys):
        bx = kx0 + 35 + i * (cw4 + 8)
        col = (35, 65, 95, 255) if "ENTER" in k else KEY_DARK
        draw.rounded_rectangle([bx, k_y3, bx + cw4, k_y3 + 120], radius=4, fill=col, outline=(55, 65, 80, 255), width=1)
        draw_center_text(draw, bx + cw4 // 2, k_y3 + 60, k, f_k, WHITE)

    # Row 5: Space & Arrows
    k_y4 = k_y3 + row_h + row_gap
    draw.rounded_rectangle([kx0 + 35, k_y4, kx0 + 150, k_y4 + 120], radius=4, fill=KEY_ACCENT, outline=(55, 65, 80, 255), width=1)
    draw_center_text(draw, kx0 + 92, k_y4 + 60, "SHIFT", f_k, WHITE)
    draw.rounded_rectangle([kx0 + 160, k_y4, kx0 + 260, k_y4 + 120], radius=4, fill=KEY_ACCENT, outline=(55, 65, 80, 255), width=1)
    draw_center_text(draw, kx0 + 210, k_y4 + 60, "CTRL", f_k, WHITE)
    draw.rounded_rectangle([kx0 + 270, k_y4, kx0 + 820, k_y4 + 120], radius=4, fill=KEY_DARK, outline=(55, 65, 80, 255), width=1)
    draw_center_text(draw, kx0 + 545, k_y4 + 60, "SPACEBAR  [EVENT MARK]", f_k, INK_GREEN)
    draw.rounded_rectangle([kx0 + 830, k_y4, kx0 + 930, k_y4 + 120], radius=4, fill=KEY_ACCENT, outline=(55, 65, 80, 255), width=1)
    draw_center_text(draw, kx0 + 880, k_y4 + 60, "ALT", f_k, WHITE)
    for idx, arr in enumerate(["◄", "▲", "▼", "►"]):
        abx = kx0 + 945 + idx * 85
        draw.rounded_rectangle([abx, k_y4, abx + 75, k_y4 + 120], radius=4, fill=(35, 55, 75, 255), outline=(55, 65, 80, 255), width=1)
        draw_center_text(draw, abx + 37, k_y4 + 60, arr, f_k, INK_CYAN)

    # Right Section: Touchpad & Mouse Buttons (1450 .. kx1 - 20)
    tx0, ty0, tx1, ty1 = 1455, ky0 + 80, kx1 - 25, ky1 - 25
    draw.rounded_rectangle([tx0, ty0, tx1, ty1], radius=8, fill=(18, 20, 25, 255), outline=(45, 52, 65, 255), width=1)

    # Touchpad Active Touch Area
    pad_y1 = ty1 - 130
    draw.rounded_rectangle([tx0 + 20, ty0 + 30, tx1 - 20, pad_y1], radius=6, fill=TOUCHPAD_SURF, outline=(60, 70, 88, 255), width=2)
    # Scroll bar track on right edge of touchpad
    draw.line([(tx1 - 42, ty0 + 40), (tx1 - 42, pad_y1 - 10)], fill=(75, 88, 110, 255), width=2)
    draw_center_text(draw, (tx0 + tx1 - 20) // 2, (ty0 + pad_y1) // 2, "MULTI-TOUCH PRECISION PAD", load_font(FONT_MONO, 14), (160, 175, 195, 255))

    # Physical Left and Right Mouse Buttons
    btn_w = (tx1 - tx0 - 55) // 2
    b_l_x = tx0 + 20
    b_r_x = b_l_x + btn_w + 15
    b_y0 = pad_y1 + 18
    b_y1 = ty1 - 20
    draw.rounded_rectangle([b_l_x, b_y0, b_l_x + btn_w, b_y1], radius=4, fill=(28, 32, 40, 255), outline=(55, 65, 80, 255), width=2)
    draw_center_text(draw, b_l_x + btn_w // 2, (b_y0 + b_y1) // 2, "LEFT CLICK", load_font(FONT_MONO, 14), WHITE)

    draw.rounded_rectangle([b_r_x, b_y0, b_r_x + btn_w, b_y1], radius=4, fill=(28, 32, 40, 255), outline=(55, 65, 80, 255), width=2)
    draw_center_text(draw, b_r_x + btn_w // 2, (b_y0 + b_y1) // 2, "RIGHT CLICK", load_font(FONT_MONO, 14), WHITE)

    # =========================================================================
    # 3. TELESCOPIC BALL-BEARING SLIDE RAILS (20..1100, 1220..1580)
    # Galvanized steel with ball bearing races and mounting slots
    # =========================================================================
    rx0, ry0, rx1, ry1 = 20, 1220, 1100, 1560
    draw.rectangle([rx0, ry0, rx1, ry1], fill=STEEL_GALV, outline=(180, 190, 205, 255), width=2)
    for ly in range(ry0 + 30, ry1 - 30, 24):
        draw.line([(rx0 + 20, ly), (rx1 - 20, ly)], fill=(110, 120, 132, 255), width=3)
    # Ball bearings pattern
    for bx in range(rx0 + 40, rx1 - 40, 60):
        draw.ellipse([bx, (ry0 + ry1)//2 - 12, bx + 24, (ry0 + ry1)//2 + 12], fill=(210, 220, 235, 255), outline=(90, 100, 115, 255), width=2)

    # =========================================================================
    # 4. FLAT COLOR & MATERIAL SWATCHES (1140..2048, 1220..2048)
    # =========================================================================
    swatches = [
        ((1140, 1220, 1560, 1420), RACK_BLACK, "RACK_BLACK"),
        ((1580, 1220, 2000, 1420), RACK_PANEL, "RACK_PANEL"),
        ((1140, 1440, 1560, 1640), STEEL_GALV, "M_METAL_STEEL"),
        ((1580, 1440, 2000, 1640), (16, 17, 19, 255), "M_RUBBER"),
        ((1140, 1660, 1560, 1860), KEY_DARK, "KEY_DARK"),
        ((1580, 1660, 2000, 1860), TOUCHPAD_SURF, "TOUCHPAD_SURF"),
        ((1140, 1880, 2000, 2020), (10, 12, 14, 255), "INNER_RECESS")
    ]
    for box, col, name in swatches:
        draw.rectangle(box, fill=col)
        draw.text((box[0] + 16, box[1] + 16), name, fill=WHITE, font=load_font(FONT_MONO, 14))

    img.save(ATLAS_PATH, "PNG")
    print(f"[Atlas] Generated: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

if __name__ == "__main__":
    main()
