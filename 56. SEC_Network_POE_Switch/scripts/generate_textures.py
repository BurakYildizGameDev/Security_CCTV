"""
=============================================================================
Security CCTV Asset Production Suite - Asset 56
Asset Name: SEC_Network_POE_Switch (PoE Ag Anahtari)
Texture Atlas Generator (2048x2048) - 1:1 Aspect-Locked Precision Texture
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
CHASSIS_BLACK   = (20, 22, 26, 255)
FRONT_FASCIA    = (28, 33, 42, 255)
BEZEL_EDGE      = (48, 56, 70, 255)
STEEL_METAL     = (165, 175, 190, 255)
GOLD_PIN        = (225, 185, 45, 255)
RJ45_DARK       = (12, 14, 18, 255)
RJ45_INNER      = (18, 21, 26, 255)
LED_GREEN       = (40, 235, 85, 255)
LED_AMBER       = (245, 175, 25, 255)
LED_BLUE        = (40, 150, 250, 255)
WHITE           = (255, 255, 255, 255)
INK_TEXT        = (225, 232, 242, 255)
INK_SOFT        = (145, 155, 170, 255)
INK_CYAN        = (45, 195, 245, 255)
PORT_DIVIDER    = (40, 48, 62, 255)

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
    # 1. FRONT 1U SWITCH FASCIA (74..1974, 30..220)
    # Physical: 440mm x 44mm (Exact 10.0:1 Ratio, 1900 x 190 px, 0.00% Stretch)
    # =========================================================================
    fx0, fy0, fx1, fy1 = 74, 30, 1974, 220
    draw.rectangle([fx0, fy0, fx1, fy1], fill=FRONT_FASCIA, outline=BEZEL_EDGE, width=2)
    # Top and bottom bevel highlights
    draw.line([(fx0 + 2, fy0 + 2), (fx1 - 2, fy0 + 2)], fill=(65, 75, 92, 255), width=2)
    draw.line([(fx0 + 2, fy1 - 2), (fx1 - 2, fy1 - 2)], fill=(14, 16, 20, 255), width=2)

    # Rack mount ear indicator lines (outer 92 px on each end)
    draw.line([(fx0 + 92, fy0), (fx0 + 92, fy1)], fill=(45, 52, 65, 255), width=2)
    draw.line([(fx1 - 92, fy0), (fx1 - 92, fy1)], fill=(45, 52, 65, 255), width=2)
    for rx in [fx0 + 46, fx1 - 46]:
        draw.rounded_rectangle([rx - 10, fy0 + 35, rx + 10, fy1 - 35], radius=5, fill=(12, 14, 16, 255), outline=STEEL_METAL, width=2)

    # --- Left Section: Corporate Branding & Spec ---
    draw.text((fx0 + 115, fy0 + 22), "SEC-VISION", fill=WHITE, font=load_font(FONT_SANS, 22))
    draw.text((fx0 + 115, fy0 + 54), "24-PORT GIGABIT PoE+ MANAGED SWITCH", fill=INK_CYAN, font=load_font(FONT_MONO, 12))
    draw.text((fx0 + 115, fy0 + 78), "IEEE 802.3at/af 370W POE BUDGET | SW-2400P", fill=INK_SOFT, font=load_font(FONT_MONO, 11))
    draw.text((fx0 + 115, fy0 + 100), "LAYER 2+ CCTV ENTERPRISE INFRASTRUCTURE", fill=(105, 115, 130, 255), font=load_font(FONT_MONO, 10))

    # --- System Status Cluster (PWR, SYS, PoE MAX) ---
    st_y = fy0 + 138
    # PWR LED
    draw.ellipse([fx0 + 115, st_y, fx0 + 129, st_y + 14], fill=LED_GREEN)
    draw.text((fx0 + 136, st_y), "PWR", fill=WHITE, font=load_font(FONT_MONO, 11))
    # SYS LED
    draw.ellipse([fx0 + 185, st_y, fx0 + 199, st_y + 14], fill=LED_GREEN)
    draw.text((fx0 + 206, st_y), "SYS", fill=WHITE, font=load_font(FONT_MONO, 11))
    # PoE MAX LED
    draw.ellipse([fx0 + 255, st_y, fx0 + 269, st_y + 14], fill=LED_AMBER)
    draw.text((fx0 + 276, st_y), "PoE MAX", fill=WHITE, font=load_font(FONT_MONO, 11))

    # Reset Button Pinhole
    draw.ellipse([fx0 + 355, st_y + 2, fx0 + 365, st_y + 12], fill=(8, 10, 12, 255), outline=STEEL_METAL, width=1)
    draw.text((fx0 + 372, st_y), "RESET", fill=INK_SOFT, font=load_font(FONT_MONO, 10))

    # --- Console RJ45 Port (X: ~750..815) ---
    con_x0, con_y0 = fx0 + 690, fy0 + 45
    con_x1, con_y1 = con_x0 + 60, con_y0 + 75
    draw.rectangle([con_x0, con_y0, con_x1, con_y1], fill=RJ45_DARK, outline=(40, 110, 200, 255), width=2)
    draw_center_text(draw, (con_x0 + con_x1) // 2, (con_y0 + con_y1) // 2, "CONSOLE", load_font(FONT_MONO, 10), (80, 170, 255, 255))
    draw.text((con_x0 + 2, con_y1 + 8), "RS-232 / RJ45", fill=INK_SOFT, font=load_font(FONT_MONO, 9))

    # --- Center Section: 24 RJ-45 PoE+ Ports (12 Columns x 2 Rows) ---
    # Front Panel X: -0.220 to +0.220 (Width 0.440m = 1900 px, so 4318.18 px/m)
    # Top Row center: z = +0.0068m -> y = 30 + (0.022 - 0.0068)/0.044 * 190 = 96 px
    # Bot Row center: z = -0.0068m -> y = 30 + (0.022 - (-0.0068))/0.044 * 190 = 154 px
    # Port width: 0.0135m -> 58.3 px (w_px = 58)
    # Port height: 0.0115m -> 49.7 px (h_px = 50)
    # Top LED center: z = +0.0165m -> y = 54 px
    # Bot LED center: z = -0.0165m -> y = 196 px

    port_bed_x0 = 890
    port_bed_x1 = 1780
    draw.rounded_rectangle([port_bed_x0, fy0 + 10, port_bed_x1, fy1 - 10], radius=5, fill=(14, 16, 21, 255), outline=PORT_DIVIDER, width=2)
    draw.text((port_bed_x0 + 16, fy0 + 14), "10/100/1000M POE+ PORTS [1 - 24]", fill=INK_TEXT, font=load_font(FONT_MONO, 10))

    # 12 Columns matching 3D coordinates exactly:
    # x_c(c) = -0.01275 + c * 0.0160 m
    for col in range(12):
        x_c_m = -0.01275 + col * 0.0160
        cx_px = int(round(74 + ((x_c_m - (-0.220)) / 0.440) * 1900))
        
        # --- Top Port (Odd: 1, 3, 5, ..., 23) ---
        port_num_top = col * 2 + 1
        cy_top = 96
        # Port socket frame on texture
        pw2, ph2 = 29, 25
        draw.rectangle([cx_px - pw2, cy_top - ph2, cx_px + pw2, cy_top + ph2], fill=RJ45_INNER, outline=BEZEL_EDGE, width=1)
        # Gold pin traces inside socket
        for p in range(6):
            px_pin = cx_px - 15 + p * 6
            draw.line([(px_pin, cy_top - 18), (px_pin, cy_top - 8)], fill=GOLD_PIN, width=2)
        # Top LED indicator bead (y = 54)
        draw.rounded_rectangle([cx_px - 8, 54 - 4, cx_px + 8, 54 + 4], radius=2, fill=LED_GREEN, outline=(30, 160, 60, 255), width=1)
        # Port number label between LED and socket (y = 66)
        draw_center_text(draw, cx_px, 66, str(port_num_top), load_font(FONT_MONO, 10), WHITE)

        # --- Bottom Port (Even: 2, 4, 6, ..., 24) ---
        port_num_bot = col * 2 + 2
        cy_bot = 154
        # Port socket frame on texture
        draw.rectangle([cx_px - pw2, cy_bot - ph2, cx_px + pw2, cy_bot + ph2], fill=RJ45_INNER, outline=BEZEL_EDGE, width=1)
        # Gold pin traces inside socket
        for p in range(6):
            px_pin = cx_px - 15 + p * 6
            draw.line([(px_pin, cy_bot + 8), (px_pin, cy_bot + 18)], fill=GOLD_PIN, width=2)
        # Port number label between socket and LED (y = 184)
        draw_center_text(draw, cx_px, 184, str(port_num_bot), load_font(FONT_MONO, 10), WHITE)
        # Bottom LED indicator bead (y = 196)
        draw.rounded_rectangle([cx_px - 8, 196 - 4, cx_px + 8, 196 + 4], radius=2, fill=LED_GREEN, outline=(30, 160, 60, 255), width=1)

    # --- Right Section: 2x 10G SFP+ Uplink Slots (Ports 25 & 26) ---
    sfp_x0 = 1805
    sfp_x1 = 1875
    draw.rounded_rectangle([sfp_x0, fy0 + 15, sfp_x1, fy1 - 15], radius=4, fill=(16, 19, 24, 255), outline=STEEL_METAL, width=2)
    draw.text((sfp_x0 + 4, fy0 + 20), "10G SFP+", fill=WHITE, font=load_font(FONT_MONO, 10))
    # SFP+ Port 25
    draw.rectangle([sfp_x0 + 8, fy0 + 42, sfp_x0 + 32, fy0 + 98], fill=(10, 12, 15, 255), outline=STEEL_METAL, width=1)
    draw_center_text(draw, sfp_x0 + 20, fy0 + 70, "25", load_font(FONT_MONO, 10), INK_CYAN)
    # SFP+ Port 26
    draw.rectangle([sfp_x0 + 38, fy0 + 42, sfp_x0 + 62, fy0 + 98], fill=(10, 12, 15, 255), outline=STEEL_METAL, width=1)
    draw_center_text(draw, sfp_x0 + 50, fy0 + 70, "26", load_font(FONT_MONO, 10), INK_CYAN)
    draw_center_text(draw, (sfp_x0 + sfp_x1) // 2, fy0 + 115, "UPLINK", load_font(FONT_MONO, 9), INK_SOFT)

    # =========================================================================
    # 2. RJ45 PORT SOCKET INNER SURFACES & PINS (74..1974, 250..450)
    # =========================================================================
    draw.rectangle([74, 250, 1974, 450], fill=(16, 18, 23, 255), outline=BEZEL_EDGE, width=2)
    draw.text((90, 260), "RJ-45 SHIELDED JACK CAVITY TEXTURE / INTERNAL PINS & CONTACTS", fill=INK_SOFT, font=load_font(FONT_MONO, 11))
    # 8 individual gold pin strips
    for p in range(8):
        px = 120 + p * 38
        draw.rectangle([px, 300, px + 24, 430], fill=RJ45_DARK, outline=(35, 42, 54, 255), width=1)
        draw.line([(px + 12, 310), (px + 12, 420)], fill=GOLD_PIN, width=4)

    # =========================================================================
    # 3. REAR 1U POWER & FAN PANEL (74..1974, 480..670)
    # Physical: 440mm x 44mm (Exact 10.0:1 Ratio, 1900 x 190 px, 0.00% Stretch)
    # =========================================================================
    rx0, ry0, rx1, ry1 = 74, 480, 1974, 670
    draw.rectangle([rx0, ry0, rx1, ry1], fill=(22, 25, 30, 255), outline=BEZEL_EDGE, width=2)

    # Dual Cooling Exhaust Fans
    for idx, fx in enumerate([rx0 + 200, rx0 + 440]):
        # Outer fan vent circle
        draw.ellipse([fx, ry0 + 25, fx + 140, ry0 + 165], fill=(14, 16, 20, 255), outline=STEEL_METAL, width=2)
        # Concentric wire guard rings
        draw.ellipse([fx + 20, ry0 + 45, fx + 120, ry0 + 145], outline=(55, 65, 80, 255), width=2)
        draw.ellipse([fx + 45, ry0 + 70, fx + 95, ry0 + 120], fill=(25, 30, 38, 255), outline=STEEL_METAL, width=1)
        draw_center_text(draw, fx + 70, ry0 + 95, f"FAN {idx+1}", load_font(FONT_MONO, 11), INK_SOFT)
        # 8 radial wire spoke lines
        for deg in range(0, 360, 45):
            rad = math.radians(deg)
            ex = fx + 70 + int(55 * math.cos(rad))
            ey = ry0 + 95 + int(55 * math.sin(rad))
            draw.line([(fx + 70, ry0 + 95), (ex, ey)], fill=(50, 60, 75, 255), width=2)

    # Industrial Grounding Lug
    draw.ellipse([rx0 + 640, ry0 + 80, rx0 + 670, ry0 + 110], fill=(160, 130, 40, 255), outline=WHITE, width=2)
    draw_center_text(draw, rx0 + 655, ry0 + 95, "⏚", load_font(FONT_MONO, 16), WHITE)
    draw.text((rx0 + 635, ry0 + 122), "GND TERMINAL", fill=INK_SOFT, font=load_font(FONT_MONO, 10))

    # Center Spec Plate
    sp_x0, sp_y0 = rx0 + 740, ry0 + 30
    draw.rectangle([sp_x0, sp_y0, sp_x0 + 680, sp_y0 + 130], fill=(14, 16, 20, 255), outline=(55, 65, 80, 255), width=1)
    draw.text((sp_x0 + 20, sp_y0 + 15), "SEC-VISION 24-PORT POE+ MANAGED SWITCH", fill=WHITE, font=load_font(FONT_MONO, 12))
    draw.text((sp_x0 + 20, sp_y0 + 38), "MODEL: SW-2400P | INPUT: 100-240V ~ 50/60Hz 5A MAX", fill=INK_CYAN, font=load_font(FONT_MONO, 11))
    draw.text((sp_x0 + 20, sp_y0 + 60), "TOTAL POWER CONSUMPTION: 420W (POE BUDGET: 370W)", fill=INK_SOFT, font=load_font(FONT_MONO, 10))
    draw.text((sp_x0 + 20, sp_y0 + 82), "CERTIFIED: [CE]  [FCC CLASS A]  [RoHS]  [UL 60950-1]  [IP20]", fill=(175, 185, 200, 255), font=load_font(FONT_MONO, 10))
    draw.text((sp_x0 + 20, sp_y0 + 104), "SERIAL: *SW24P20268841B* | MADE IN INDUSTRIAL SURVEILLANCE ZONE", fill=INK_SOFT, font=load_font(FONT_MONO, 9))

    # AC Power Section (Right End)
    ac_x0 = rx1 - 380
    draw.rectangle([ac_x0, ry0 + 25, rx1 - 30, ry0 + 165], fill=(14, 16, 20, 255), outline=(55, 65, 80, 255), width=2)
    draw.text((ac_x0 + 15, ry0 + 35), "100-240V AC INLET", fill=WHITE, font=load_font(FONT_MONO, 11))

    # IEC C14 3-pin AC power inlet socket
    iec_cx, iec_cy = ac_x0 + 110, ry0 + 105
    # Hexagonal / beveled IEC housing
    draw.polygon([
        (iec_cx - 45, iec_cy - 30),
        (iec_cx + 45, iec_cy - 30),
        (iec_cx + 55, iec_cy),
        (iec_cx + 45, iec_cy + 30),
        (iec_cx - 45, iec_cy + 30),
        (iec_cx - 55, iec_cy)
    ], fill=(8, 10, 12, 255), outline=STEEL_METAL)
    # 3 Brass pins
    draw.rectangle([iec_cx - 30, iec_cy - 12, iec_cx - 24, iec_cy + 12], fill=GOLD_PIN)
    draw.rectangle([iec_cx + 24, iec_cy - 12, iec_cx + 30, iec_cy + 12], fill=GOLD_PIN)
    draw.rectangle([iec_cx - 3, iec_cy - 20, iec_cx + 3, iec_cy - 6], fill=GOLD_PIN)

    # I/O Rocker Power Switch
    sw_x0 = ac_x0 + 240
    draw.rectangle([sw_x0, ry0 + 60, sw_x0 + 50, ry0 + 140], fill=(12, 14, 18, 255), outline=WHITE, width=2)
    draw.rectangle([sw_x0 + 4, ry0 + 64, sw_x0 + 46, ry0 + 100], fill=(30, 35, 45, 255))
    draw_center_text(draw, sw_x0 + 25, ry0 + 82, "I", load_font(FONT_MONO, 14), WHITE)
    draw.rectangle([sw_x0 + 4, ry0 + 100, sw_x0 + 46, ry0 + 136], fill=(18, 22, 28, 255))
    draw_center_text(draw, sw_x0 + 25, ry0 + 118, "O", load_font(FONT_MONO, 14), INK_SOFT)

    # =========================================================================
    # 4. FLAT CLEAN COLOR AND MATERIAL SWATCHES (74..1974, 700..2000)
    # =========================================================================
    # Dedicated clean areas without text for 3D faces:
    draw.rectangle([50, 1500, 450, 1900], fill=CHASSIS_BLACK)       # Flat chassis paint
    draw.rectangle([550, 1500, 950, 1900], fill=(12, 14, 18, 255))  # Deep socket black
    draw.rectangle([1050, 1500, 1450, 1900], fill=STEEL_METAL)      # Metal ear finish

    # Labeled swatches for visual reference and QA inspection:
    swatches = [
        ((74, 720, 520, 1020), CHASSIS_BLACK, "CHASSIS_BLACK"),
        ((560, 720, 1000, 1020), FRONT_FASCIA, "FRONT_FASCIA"),
        ((1040, 720, 1480, 1020), STEEL_METAL, "STEEL_METAL"),
        ((1520, 720, 1960, 1020), (12, 14, 18, 255), "INNER_RECESS"),
        ((74, 1060, 520, 1360), LED_GREEN, "EMIT_GREEN"),
        ((560, 1060, 1000, 1360), GOLD_PIN, "GOLD_TERMINAL"),
        ((1040, 1060, 1480, 1360), (60, 68, 80, 255), "RACK_EAR_METAL"),
        ((1520, 1060, 1960, 1360), RJ45_DARK, "RJ45_DARK")
    ]
    for box, col, name in swatches:
        draw.rectangle(box, fill=col)
        draw.text((box[0] + 20, box[1] + 20), name, fill=WHITE, font=load_font(FONT_MONO, 16))

    img.save(ATLAS_PATH, "PNG")
    print(f"[Atlas] Generated: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")

if __name__ == "__main__":
    generate_atlas()
