"""
Security CCTV Asset Production Suite - Asset 62
Asset Name: SEC_Alarm_Keypad_Touch (Capacitive Touchscreen Keypad)
Ultra-Premium High-Resolution Texture Atlas Generator (2048x2048)
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
FONT_SANS_REG = r"C:\Windows\Fonts\arial.ttf"

ATLAS_W, ATLAS_H = 2048, 2048

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
    # Base dark graphite
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), (20, 23, 28, 255))
    draw = ImageDraw.Draw(img)

    # Subtle horizontal brushed micro-grain
    for y in range(0, ATLAS_H, 2):
        grain = ((y * 13) % 7) - 3
        draw.line([(0, y), (ATLAS_W, y)], fill=(20 + grain, 23 + grain, 28 + grain, 255), width=1)

    # =========================================================================
    # 1. 7-INCH CAPACITIVE TOUCHSCREEN UI (50, 50) to (1450, 950) -> 1400 x 900 px
    # Ultra-Modern Obsidian Glass UI (16:10 aspect ratio)
    # =========================================================================
    sx0, sy0, sx1, sy1 = 50, 50, 1450, 950
    # Deep obsidian glass body with subtle gradient
    for y in range(sy0, sy1):
        t = (y - sy0) / (sy1 - sy0)
        c = int(10 + t * 6)
        draw.line([(sx0, y), (sx1, y)], fill=(c, c + 2, c + 6, 255))
    # Beveled inner glass frame
    draw.rectangle([sx0, sy0, sx1, sy1], outline=(55, 68, 85, 255), width=3)
    draw.rectangle([sx0 + 3, sy0 + 3, sx1 - 3, sy1 - 3], outline=(25, 32, 42, 255), width=2)

    # --- TOP STATUS BAR (sy0 to sy0 + 85) ---
    bar_y1 = sy0 + 85
    for y in range(sy0 + 3, bar_y1):
        t = (y - sy0) / 85.0
        val = int(24 - t * 8)
        draw.line([(sx0 + 3, y), (sx1 - 3, y)], fill=(val, val + 4, val + 10, 255))
    draw.line([(sx0 + 3, bar_y1), (sx1 - 3, bar_y1)], fill=(50, 65, 85, 255), width=2)

    # Brand Title
    draw.text((sx0 + 35, sy0 + 26), "SEC-VISION", fill=(255, 255, 255, 255), font=load_font(FONT_SANS, 24))
    draw.text((sx0 + 210, sy0 + 30), "TOUCH 7 PRO", fill=(45, 195, 245, 255), font=load_font(FONT_MONO, 18))

    # Center System Status Pill Badge
    pill_w = 260
    pill_h = 42
    pill_cx = (sx0 + sx1) // 2
    pill_cy = sy0 + 42
    draw.rounded_rectangle([pill_cx - pill_w//2, pill_cy - pill_h//2, pill_cx + pill_w//2, pill_cy + pill_h//2],
                           radius=21, fill=(12, 45, 28, 255), outline=(40, 195, 95, 255), width=2)
    draw.ellipse([pill_cx - pill_w//2 + 18, pill_cy - 7, pill_cx - pill_w//2 + 32, pill_cy + 7], fill=(50, 240, 120, 255))
    draw.text((pill_cx - pill_w//2 + 42, pill_cy - 10), "READY TO ARM", fill=(225, 255, 235, 255), font=load_font(FONT_SANS, 18))

    # Right Telemetry: Time, WiFi, 5G, Battery
    time_str = "12:45 PM"
    draw.text((sx1 - 380, sy0 + 28), time_str, fill=(245, 248, 255, 255), font=load_font(FONT_SANS, 22))
    draw.text((sx1 - 265, sy0 + 32), "OCT 31", fill=(170, 185, 205, 255), font=load_font(FONT_MONO, 16))

    # WiFi Signal Arcs (vector style)
    w_cx = sx1 - 130
    w_cy = sy0 + 50
    draw.arc([w_cx - 16, w_cy - 16, w_cx + 16, w_cy + 16], start=215, end=325, fill=(45, 195, 245, 255), width=3)
    draw.arc([w_cx - 10, w_cy - 10, w_cx + 10, w_cy + 10], start=215, end=325, fill=(45, 195, 245, 255), width=3)
    draw.ellipse([w_cx - 3, w_cy + 2, w_cx + 3, w_cy + 8], fill=(45, 195, 245, 255))

    # Battery Icon
    b_x = sx1 - 70
    b_y = sy0 + 34
    draw.rounded_rectangle([b_x, b_y, b_x + 38, b_y + 20], radius=4, outline=(180, 195, 215, 255), width=2)
    draw.rectangle([b_x + 38, b_y + 6, b_x + 42, b_y + 14], fill=(180, 195, 215, 255))
    draw.rounded_rectangle([b_x + 3, b_y + 3, b_x + 35, b_y + 17], radius=2, fill=(50, 220, 110, 255))

    # --- LEFT PANEL: 4 INTERACTIVE ARM TILES ---
    tiles = [
        ("ARM STAY", "Interior Bypassed", (18, 55, 120), (35, 110, 220), (45, 160, 255), "STAY"),
        ("ARM AWAY", "All Zones Armed", (140, 45, 15), (220, 80, 30), (255, 120, 50), "AWAY"),
        ("ARM NIGHT", "Perimeter & Doors", (90, 25, 130), (160, 50, 210), (195, 80, 255), "NIGHT"),
        ("DISARM", "System Disarmed", (20, 95, 45), (35, 165, 80), (60, 220, 110), "DISARM")
    ]
    tile_w = 280
    tile_h = 160
    t_start_x = sx0 + 40
    t_start_y = sy0 + 115
    for i, (t_title, t_sub, c_dark, c_mid, c_glow, mode) in enumerate(tiles):
        col = i % 2
        row = i // 2
        tx0 = t_start_x + col * (tile_w + 25)
        ty0 = t_start_y + row * (tile_h + 25)
        tx1 = tx0 + tile_w
        ty1 = ty0 + tile_h

        # Tile glass gradient
        for y in range(ty0, ty1):
            f = (y - ty0) / float(tile_h)
            cr = int(c_dark[0] + (c_mid[0] - c_dark[0]) * (1.0 - f))
            cg = int(c_dark[1] + (c_mid[1] - c_dark[1]) * (1.0 - f))
            cb = int(c_dark[2] + (c_mid[2] - c_dark[2]) * (1.0 - f))
            draw.line([(tx0, y), (tx1, y)], fill=(cr, cg, cb, 255))
        draw.rounded_rectangle([tx0, ty0, tx1, ty1], radius=18, outline=c_glow, width=3)
        draw.line([(tx0 + 12, ty0 + 6), (tx1 - 12, ty0 + 6)], fill=(255, 255, 255, 120), width=2)

        # Mode Icon Badge
        ic_x = tx0 + 40
        ic_y = ty0 + 52
        if mode in ["STAY", "AWAY"]:
            # House silhouette
            draw.polygon([(ic_x, ic_y - 18), (ic_x + 18, ic_y - 2), (ic_x - 18, ic_y - 2)], fill=(255, 255, 255, 240))
            draw.rectangle([ic_x - 13, ic_y - 2, ic_x + 13, ic_y + 16], fill=(255, 255, 255, 240))
            draw.rectangle([ic_x - 4, ic_y + 4, ic_x + 4, ic_y + 16], fill=(c_dark[0], c_dark[1], c_dark[2], 255))
        elif mode == "NIGHT":
            # Moon & Star
            draw.ellipse([ic_x - 16, ic_y - 16, ic_x + 16, ic_y + 16], fill=(255, 255, 255, 240))
            draw.ellipse([ic_x - 8, ic_y - 18, ic_x + 20, ic_y + 10], fill=(c_dark[0], c_dark[1], c_dark[2], 255))
        else:
            # Shield
            draw.polygon([(ic_x - 16, ic_y - 16), (ic_x + 16, ic_y - 16), (ic_x + 16, ic_y + 4),
                          (ic_x, ic_y + 18), (ic_x - 16, ic_y + 4)], fill=(255, 255, 255, 240))
            draw.polygon([(ic_x - 11, ic_y - 12), (ic_x + 11, ic_y - 12), (ic_x + 11, ic_y + 2),
                          (ic_x, ic_y + 13), (ic_x - 11, ic_y + 2)], fill=(c_dark[0], c_dark[1], c_dark[2], 255))

        # Title & Subtitle
        draw.text((tx0 + 75, ty0 + 32), t_title, fill=(255, 255, 255, 255), font=load_font(FONT_SANS, 22))
        draw.text((tx0 + 75, ty0 + 64), t_sub, fill=(215, 230, 255, 255), font=load_font(FONT_SANS_REG, 15))

        # Bottom Action Bar
        draw.rounded_rectangle([tx0 + 20, ty1 - 55, tx1 - 20, ty1 - 18], radius=10, fill=(0, 0, 0, 110), outline=c_glow, width=1)
        draw_center_text(draw, (tx0 + tx1)//2, ty1 - 36, "TAP TO SELECT", load_font(FONT_MONO, 13), (255, 255, 255, 255))

    # --- RIGHT PANEL: HIGH-SECURITY CAPACITIVE PIN KEYPAD ---
    kx0 = sx0 + 670
    kx1 = sx1 - 40
    ky0 = sy0 + 115
    ky1 = sy1 - 85
    # Recessed frosted acrylic panel
    draw.rounded_rectangle([kx0, ky0, kx1, ky1], radius=20, fill=(16, 20, 27, 255), outline=(45, 58, 76, 255), width=2)

    # PIN Input Screen Box
    box_y0 = ky0 + 20
    box_y1 = ky0 + 95
    draw.rounded_rectangle([kx0 + 35, box_y0, kx1 - 35, box_y1], radius=12, fill=(8, 11, 16, 255), outline=(60, 78, 102, 255), width=2)
    draw.text((kx0 + 55, box_y0 + 25), "ENTER PIN:", fill=(160, 180, 205, 255), font=load_font(FONT_MONO, 18))
    # 4 Glowing Masked Dots
    for d in range(4):
        cx_dot = kx0 + 240 + d * 60
        cy_dot = (box_y0 + box_y1) // 2
        draw.ellipse([cx_dot - 12, cy_dot - 12, cx_dot + 12, cy_dot + 12], fill=(45, 220, 120, 255), outline=(180, 255, 210, 255), width=2)
        draw.ellipse([cx_dot - 4, cy_dot - 4, cx_dot + 4, cy_dot + 4], fill=(255, 255, 255, 255))

    # 12 Glass Round Tactile Buttons
    btn_matrix = [
        [("1", ""), ("2", "ABC"), ("3", "DEF")],
        [("4", "GHI"), ("5", "JKL"), ("6", "MNO")],
        [("7", "PQRS"), ("8", "TUV"), ("9", "WXYZ")],
        [("CLR", "CLEAR"), ("0", "+"), ("ENT", "ENTER")]
    ]
    for r in range(4):
        for c in range(3):
            num, sub = btn_matrix[r][c]
            bcx = kx0 + 105 + c * 185
            bcy = ky0 + 160 + r * 105
            r_btn = 42

            fill_c = (26, 33, 44, 255)
            rim_c = (70, 88, 115, 255)
            if num == "CLR":
                fill_c = (110, 25, 30, 255)
                rim_c = (220, 55, 65, 255)
            elif num == "ENT":
                fill_c = (20, 105, 55, 255)
                rim_c = (45, 215, 115, 255)

            # Button circle with gradient & bevel
            draw.ellipse([bcx - r_btn, bcy - r_btn, bcx + r_btn, bcy + r_btn], fill=fill_c, outline=rim_c, width=3)
            draw.arc([bcx - r_btn + 2, bcy - r_btn + 2, bcx + r_btn - 2, bcy + r_btn - 2], start=200, end=340, fill=(255, 255, 255, 100), width=2)

            if sub:
                draw_center_text(draw, bcx, bcy - 7, num, load_font(FONT_SANS, 24 if len(num) <= 2 else 16), (255, 255, 255, 255))
                draw_center_text(draw, bcx, bcy + 18, sub, load_font(FONT_MONO, 10), (180, 198, 220, 255))
            else:
                draw_center_text(draw, bcx, bcy, num, load_font(FONT_SANS, 26), (255, 255, 255, 255))

    # --- BOTTOM STATUS FOOTER BAR ---
    bot_y0 = sy1 - 65
    for y in range(bot_y0, sy1 - 3):
        draw.line([(sx0 + 3, y), (sx1 - 3, y)], fill=(18, 22, 28, 255))
    draw.line([(sx0 + 3, bot_y0), (sx1 - 3, bot_y0)], fill=(45, 58, 75, 255), width=2)
    telemetry = "SYSTEM NORMAL  •  ALL 16 ZONES SECURED  •  AC POWER: 13.8V FLOAT  •  21.5°C"
    draw_center_text(draw, (sx0 + sx1) // 2, (bot_y0 + sy1) // 2, telemetry, load_font(FONT_MONO, 15), (70, 225, 135, 255))

    # =========================================================================
    # 2. FRONT BEZEL / HOUSING (1500, 50) to (2000, 950) -> 500 x 900 px
    # Matte Brushed Graphite Console Bezel with Pre-compensated Circular Sensors
    # =========================================================================
    fx0, fy0, fx1, fy1 = 1500, 50, 2000, 950
    draw.rectangle([fx0, fy0, fx1, fy1], fill=(26, 30, 36, 255), outline=(45, 52, 64, 255), width=4)
    # Fine horizontal brushed grain on bezel
    for y in range(fy0 + 4, fy1 - 4, 3):
        bg = ((y * 7) % 5) - 2
        draw.line([(fx0 + 4, y), (fx1 - 4, y)], fill=(26 + bg, 30 + bg, 36 + bg, 255), width=1)
    # Beveled highlight lines
    draw.line([(fx0 + 6, fy0 + 6), (fx1 - 6, fy0 + 6)], fill=(55, 65, 80, 255), width=2)
    draw.line([(fx0 + 6, fy1 - 6), (fx1 - 6, fy1 - 6)], fill=(12, 14, 18, 255), width=2)

    # Pre-compensated Microphone pinhole (Aspect ratio compensation: rx=2.5, ry=6.5)
    mx = fx0 + 140
    my = fy0 + 45
    draw.ellipse([mx - 2, my - 6, mx + 2, my + 6], fill=(8, 10, 12, 255), outline=(65, 75, 90, 255), width=1)

    # Pre-compensated Ambient Light Sensor (rx=3.5, ry=9)
    ax = fx1 - 140
    ay = fy0 + 45
    draw.ellipse([ax - 4, ay - 9, ax + 4, ay + 9], fill=(12, 16, 22, 255), outline=(80, 95, 115, 255), width=1)
    draw.ellipse([ax - 2, ay - 4, ax + 2, ay + 4], fill=(25, 45, 65, 255))

    # =========================================================================
    # 3. REAR MOUNTING PLATE & WIRING DIAGRAM (50, 1020) to (1450, 1650) -> 1400 x 630 px
    # Realistic Commercial Alarm Backplate: 8-Pin Terminal Block, RJ45 PoE Port,
    # Gang Box Mounting Pattern, Wall Tamper Switch, Stamped Certification Plate
    # =========================================================================
    rx0, ry0, rx1, ry1 = 50, 1020, 1450, 1650
    draw.rectangle([rx0, ry0, rx1, ry1], fill=(22, 25, 30, 255), outline=(60, 72, 88, 255), width=4)

    # Molded outer bevel and stiffening ribs
    draw.line([(rx0 + 8, ry0 + 8), (rx1 - 8, ry0 + 8)], fill=(45, 55, 70, 255), width=3)
    draw.line([(rx0 + 8, ry1 - 8), (rx1 - 8, ry1 - 8)], fill=(12, 15, 20, 255), width=3)
    draw.line([(rx0 + 8, ry0 + 8), (rx0 + 8, ry1 - 8)], fill=(45, 55, 70, 255), width=3)
    draw.line([(rx1 - 8, ry0 + 8), (rx1 - 8, ry1 - 8)], fill=(12, 15, 20, 255), width=3)

    # Header Bar
    draw.rectangle([rx0 + 15, ry0 + 15, rx1 - 15, ry0 + 65], fill=(14, 17, 22, 255), outline=(40, 50, 65, 255), width=2)
    draw.text((rx0 + 35, ry0 + 26), "SEC-VISION ENTERPRISE CONSOLE  •  WALL MOUNTING BACKPLATE", fill=(255, 255, 255, 255), font=load_font(FONT_SANS, 18))
    draw.text((rx1 - 380, ry0 + 28), "▲  THIS SIDE UP / CEILING  ▲", fill=(245, 195, 35, 255), font=load_font(FONT_MONO, 15))

    # Corner Keyhole Mounting Slots with Metal Screw Collars
    for kx in [rx0 + 85, rx1 - 85]:
        for ky in [ry0 + 130, ry1 - 120]:
            draw.ellipse([kx - 26, ky - 35, kx + 26, ky + 17], fill=(12, 15, 20, 255), outline=(130, 145, 165, 255), width=3)
            draw.rounded_rectangle([kx - 12, ky + 2, kx + 12, ky + 48], radius=6, fill=(12, 15, 20, 255), outline=(130, 145, 165, 255), width=2)
            draw.ellipse([kx - 12, ky - 21, kx + 12, ky + 3], fill=(200, 210, 225, 255))

    # Single-Gang / Double-Gang Box Mounting Slots (Top & Bottom Center)
    mcx = (rx0 + rx1) // 2
    for gy in [ry0 + 95, ry1 - 85]:
        draw.rounded_rectangle([mcx - 110, gy - 12, mcx + 110, gy + 12], radius=10, fill=(12, 15, 20, 255), outline=(85, 98, 115, 255), width=2)
        draw.ellipse([mcx - 90, gy - 8, mcx - 74, gy + 8], fill=(180, 190, 205, 255))
        draw.ellipse([mcx + 74, gy - 8, mcx + 90, gy + 8], fill=(180, 190, 205, 255))
    draw_center_text(draw, mcx, ry0 + 120, "STANDARD ELECTRICAL GANG-BOX PATTERN (83.5mm C-C)", load_font(FONT_MONO, 12), (160, 175, 195, 255))

    # --- LEFT SECTION: WIRING TERMINAL BLOCK DIAGRAM (rx0 + 140 to rx0 + 640) ---
    tx0 = rx0 + 140
    ty0 = ry0 + 150
    tx1 = rx0 + 640
    ty1 = ry1 - 120
    draw.rounded_rectangle([tx0, ty0, tx1, ty1], radius=12, fill=(16, 20, 26, 255), outline=(50, 62, 78, 255), width=2)
    draw.rectangle([tx0, ty0, tx1, ty0 + 38], fill=(25, 32, 42, 255), outline=(50, 62, 78, 255), width=1)
    draw.text((tx0 + 20, ty0 + 10), "FIELD WIRING TERMINAL ASSIGNMENT", fill=(45, 195, 245, 255), font=load_font(FONT_SANS, 14))

    terminals = [
        ("1", "+12V DC", "MAIN DC POWER (+)", (235, 45, 45, 255)),
        ("2", "GND", "POWER COMMON (0V)", (180, 190, 205, 255)),
        ("3", "RS485 A+", "DATA BUS DATA (+)", (245, 205, 35, 255)),
        ("4", "RS485 B-", "DATA BUS DATA (-)", (45, 215, 115, 255)),
        ("5", "WIEG D0", "CARD READER DATA 0", (220, 235, 255, 255)),
        ("6", "WIEG D1", "CARD READER DATA 1", (75, 150, 245, 255)),
        ("7", "TAMPER", "WALL TAMPER LOOP", (245, 130, 35, 255)),
        ("8", "ALM OUT", "AUX RELAY N.C.", (215, 75, 180, 255)),
    ]
    term_h = (ty1 - ty0 - 45) // 8
    for idx, (p_num, p_name, p_desc, p_color) in enumerate(terminals):
        py = ty0 + 44 + idx * term_h
        # Screw circle
        draw.ellipse([tx0 + 18, py + 3, tx0 + 38, py + 23], fill=(40, 48, 60, 255), outline=(130, 145, 165, 255), width=2)
        draw.line([(tx0 + 22, py + 13), (tx0 + 34, py + 13)], fill=(180, 195, 215, 255), width=2)
        # Pin Number Badge
        draw.rounded_rectangle([tx0 + 46, py + 2, tx0 + 68, py + 24], radius=4, fill=(25, 30, 40, 255), outline=(70, 85, 105, 255), width=1)
        draw_center_text(draw, tx0 + 57, py + 13, p_num, load_font(FONT_MONO, 12), (255, 255, 255, 255))
        # Pin Name
        draw.text((tx0 + 78, py + 4), p_name, fill=p_color, font=load_font(FONT_SANS, 13))
        # Pin Description
        draw.text((tx0 + 175, py + 5), p_desc, fill=(160, 175, 195, 255), font=load_font(FONT_MONO, 11))

    # --- CENTER RECESSED CABLE BAY & RJ45 ETHERNET PORT (rx0 + 660 to rx0 + 820) ---
    bx0_c = rx0 + 665
    by0_c = ry0 + 150
    bx1_c = rx0 + 815
    by1_c = ry1 - 120
    draw.rounded_rectangle([bx0_c, by0_c, bx1_c, by1_c], radius=10, fill=(10, 13, 18, 255), outline=(65, 80, 100, 255), width=3)
    draw_center_text(draw, (bx0_c + bx1_c)//2, by0_c + 20, "CABLE PASS-THROUGH", load_font(FONT_MONO, 11), (200, 215, 235, 255))

    # RJ45 Jack Outline
    rj_y0 = by0_c + 45
    rj_y1 = rj_y0 + 85
    draw.rectangle([bx0_c + 20, rj_y0, bx1_c - 20, rj_y1], fill=(22, 28, 38, 255), outline=(100, 120, 145, 255), width=2)
    # Bottom key tab
    draw.rectangle([bx0_c + 45, rj_y1 - 18, bx1_c - 45, rj_y1 + 8], fill=(14, 18, 24, 255), outline=(100, 120, 145, 255), width=2)
    # 8 Gold pins inside RJ45
    for p in range(8):
        px = bx0_c + 32 + p * 11
        draw.line([(px, rj_y0 + 10), (px, rj_y0 + 35)], fill=(235, 195, 45, 255), width=2)
    draw_center_text(draw, (bx0_c + bx1_c)//2, rj_y1 + 22, "10/100 PoE 802.3af", load_font(FONT_MONO, 10), (45, 195, 245, 255))

    # Wall Tamper Microswitch Plunger
    tamp_y = by1_c - 55
    draw.ellipse([(bx0_c + bx1_c)//2 - 20, tamp_y - 20, (bx0_c + bx1_c)//2 + 20, tamp_y + 20], fill=(28, 34, 45, 255), outline=(225, 45, 55, 255), width=2)
    draw.ellipse([(bx0_c + bx1_c)//2 - 10, tamp_y - 10, (bx0_c + bx1_c)//2 + 10, tamp_y + 10], fill=(225, 45, 55, 255))
    draw_center_text(draw, (bx0_c + bx1_c)//2, tamp_y + 32, "TAMPER SWITCH", load_font(FONT_MONO, 10), (255, 120, 120, 255))

    # --- RIGHT SECTION: COMPLIANCE SPECIFICATION PLATE (rx0 + 840 to rx1 - 140) ---
    px0 = rx0 + 840
    py0 = ry0 + 150
    px1 = rx1 - 140
    py1 = ry1 - 120
    draw.rounded_rectangle([px0, py0, px1, py1], radius=12, fill=(16, 20, 26, 255), outline=(50, 62, 78, 255), width=2)
    draw.rectangle([px0, py0, px1, py0 + 38], fill=(25, 32, 42, 255), outline=(50, 62, 78, 255), width=1)
    draw.text((px0 + 20, py0 + 10), "SPECIFICATIONS & CERTIFICATIONS", fill=(245, 195, 35, 255), font=load_font(FONT_SANS, 14))

    specs_list = [
        ("MODEL", "SEC-TS70-HD (7-INCH CAPACITIVE TOUCH)", (255, 255, 255, 255)),
        ("POWER", "12V-24V DC 1.5A / PoE IEEE 802.3af (6.5W)", (200, 215, 235, 255)),
        ("COMM", "100BASE-TX ETHERNET / RS-485 / WIEGAND", (200, 215, 235, 255)),
        ("SECURITY", "EN 50131-1 GRADE 3 / EN 50131-3 CLASS II", (245, 195, 35, 255)),
        ("FIRE/UL", "UL 1023 / UL 985 LISTED • FCC PART 15B", (200, 215, 235, 255)),
        ("MAC ADDR", "70:B3:D5:8C:4A:21  |  IP20 INDOOR", (200, 215, 235, 255)),
        ("SERIAL NO", "*SEC-TS70-202688921-C*", (255, 255, 255, 255)),
    ]
    for idx, (k_lbl, v_val, v_col) in enumerate(specs_list):
        sy_line = py0 + 48 + idx * 26
        draw.text((px0 + 20, sy_line), f"{k_lbl}:", fill=(130, 145, 165, 255), font=load_font(FONT_MONO, 12))
        draw.text((px0 + 105, sy_line), v_val, fill=v_col, font=load_font(FONT_MONO, 12))

    # Realistic Compact Barcode & Certification Badges
    b_y0 = py0 + 235
    for bc in range(px0 + 20, px0 + 195, 4):
        w = 1 if (bc % 8 == 0) else 3
        draw.rectangle([bc, b_y0, bc + w, b_y0 + 38], fill=(235, 240, 250, 255))
    draw.text((px0 + 20, b_y0 + 42), "*TS70HD-202688921*", fill=(160, 175, 195, 255), font=load_font(FONT_MONO, 11))

    # Regulatory Badges (CE, FCC, RoHS) - neatly fitted inside box with 32px right padding
    b_start = px0 + 210
    draw.rounded_rectangle([b_start, b_y0, b_start + 48, b_y0 + 35], radius=6, outline=(180, 195, 215, 255), width=2)
    draw_center_text(draw, b_start + 24, b_y0 + 17, "CE", load_font(FONT_SANS, 15), (255, 255, 255, 255))

    draw.rounded_rectangle([b_start + 56, b_y0, b_start + 110, b_y0 + 35], radius=6, outline=(180, 195, 215, 255), width=2)
    draw_center_text(draw, b_start + 83, b_y0 + 17, "FCC", load_font(FONT_SANS, 14), (255, 255, 255, 255))

    draw.rounded_rectangle([b_start + 118, b_y0, b_start + 178, b_y0 + 35], radius=6, outline=(180, 195, 215, 255), width=2)
    draw_center_text(draw, b_start + 148, b_y0 + 17, "RoHS", load_font(FONT_SANS, 14), (45, 215, 115, 255))

    # Bottom Console Lock / Release Latches
    draw_center_text(draw, mcx, ry1 - 35, "◄  PRESS DUAL BOTTOM TABS TO RELEASE CONSOLE FROM MOUNTING PLATE  ►", load_font(FONT_MONO, 13), (245, 195, 35, 255))

    # =========================================================================
    # 4. BOTTOM STATUS LED GLOW BLADE (1500, 1020) to (2000, 1200)
    # Gorgeous diffused emerald cyan acrylic light pipe with realistic glow falloff
    # =========================================================================
    lx0, ly0, lx1, ly1 = 1500, 1020, 2000, 1200
    draw.rectangle([lx0, ly0, lx1, ly1], fill=(12, 16, 20, 255), outline=(40, 50, 65, 255), width=2)

    # Frosted acrylic bar with multi-layer gaussian-like glow
    bar_y0 = ly0 + 45
    bar_y1 = ly1 - 45
    mid_y = (bar_y0 + bar_y1) / 2.0
    for y in range(bar_y0, bar_y1):
        dy = abs(y - mid_y) / (bar_y1 - bar_y0) * 2.0
        v_alpha = math.cos(dy * math.pi / 2.0)
        for x in range(lx0 + 25, lx1 - 25):
            dx = abs(x - (lx0 + lx1)/2.0) / ((lx1 - lx0)/2.0 - 25)
            h_falloff = math.cos(dx * math.pi / 2.5) if dx < 1.0 else 0.0
            intensity = max(0.0, min(1.0, v_alpha * h_falloff))
            r = int(25 + 35 * intensity)
            g = int(80 + 175 * intensity)
            b = int(60 + 140 * intensity)
            draw.point((x, y), fill=(r, g, b, 255))
    draw.rounded_rectangle([lx0 + 25, bar_y0, lx1 - 25, bar_y1], radius=8, outline=(150, 255, 210, 200), width=2)
    draw_center_text(draw, (lx0 + lx1) // 2, (bar_y0 + bar_y1) // 2, "SEC-STATUS LED GLOW BLADE", load_font(FONT_MONO, 13), (255, 255, 255, 240))

    # =========================================================================
    # 5. MATERIAL SWATCHES (1500..2000, 1250..2020)
    # =========================================================================
    draw.rectangle([1500, 1250, 1720, 1550], fill=(32, 36, 44, 255)) # Frame Grey
    draw.rectangle([1750, 1250, 2000, 1550], fill=(18, 22, 28, 255)) # Mount Dark
    draw.rectangle([1500, 1600, 1720, 1950], fill=(10, 12, 16, 255)) # Glass Obsidian
    draw.rectangle([1750, 1600, 2000, 1950], fill=(45, 220, 120, 255)) # Green Status

    img.save(ATLAS_PATH, "PNG")
    print(f"[Atlas] Generated: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

if __name__ == "__main__":
    generate_atlas()
