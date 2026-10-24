import os
import math
from PIL import Image, ImageDraw

def generate_textures():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)

    atlas_path = os.path.join(exports_dir, "T_Security_Atlas.png")

    W, H = 1024, 1024
    img = Image.new("RGBA", (W, H), (236, 240, 244, 255))
    draw = ImageDraw.Draw(img)

    # -------------------------------------------------------------
    # Quadrant 1: Top-Left (0..512, 0..512) -> U: 0.0..0.5, V: 0.5..1.0
    # Corner Bracket: Clean Industrial Powder-Coat Off-White Finish
    # -------------------------------------------------------------
    draw.rectangle([0, 0, 512, 512], fill=(236, 240, 244, 255))
    draw.rectangle([15, 15, 497, 497], outline=(210, 218, 226, 255), width=2)

    # Clean Powder-Coat Zone (U: 0.05..0.45, V: 0.55..0.95 -> Y: 50..460)
    draw.rectangle([50, 50, 460, 460], fill=(238, 241, 245, 255))

    # 4 Anchor Bolt graphics
    bolt_coords = [(100, 280), (410, 280), (100, 400), (410, 400)]
    for bx, by in bolt_coords:
        draw.ellipse([bx - 28, by - 28, bx + 28, by + 28], fill=(165, 172, 180, 255), outline=(115, 122, 130, 255), width=2)
        draw.ellipse([bx - 18, by - 18, bx + 18, by + 18], fill=(65, 70, 78, 255))
        hex_pts = []
        for h in range(6):
            hang = h * (2.0 * math.pi / 6.0)
            hex_pts.append((bx + int(14 * math.cos(hang)), by + int(14 * math.sin(hang))))
        draw.polygon(hex_pts, fill=(205, 210, 216, 255), outline=(85, 90, 98, 255))

    # -------------------------------------------------------------
    # Quadrant 2: Top-Right (512..1024, 0..512) -> U: 0.5..1.0, V: 0.5..1.0
    # Camera Flank Branding, Knuckle & Angle Scale
    # -------------------------------------------------------------
    draw.rectangle([512, 0, 1024, 512], fill=(236, 239, 243, 255))
    # Side Placard (U: 0.52..0.99, V: 0.80..0.95 -> Y: 45..205)
    draw.rectangle([530, 45, 1010, 205], fill=(18, 20, 25, 255), outline=(75, 85, 95, 255), width=2)
    draw.rectangle([535, 50, 1005, 200], outline=(40, 48, 58, 255), width=1)

    pcx = 770
    placard_lines = [
        (58,  "SEC-CAM  |  4K ULTRA HD", (255, 255, 255, 255)),
        (82,  "3.6mm F/1.6 FIXED IRIS  •  120° FOV OPTICS", (195, 215, 235, 255)),
        (104, "SMART IR 50M  •  IP66 / IK10 VANDAL-PROOF", (245, 195, 45, 255)),
        (178, "SN: CN4K-2026-98214-X  •  CE FCC RoHS", (145, 158, 172, 255))
    ]
    for y_pos, t_str, t_col in placard_lines:
        t_w = draw.textlength(t_str)
        draw.text((pcx - t_w / 2, y_pos), t_str, fill=t_col)

    # Centered Barcode
    bar_w = 340
    hbx = int(pcx - bar_w / 2)
    hby = 126
    for b in range(68):
        thick = 3 if (b % 5 == 0 or b % 11 == 0) else (2 if b % 2 == 0 else 1)
        b_col = (255, 255, 255, 255) if (b % 3 == 0 or b % 7 == 0) else (18, 20, 25, 255)
        draw.line([(hbx + b * 5, hby), (hbx + b * 5, hby + 42)], fill=b_col, width=thick)

    # Angle degree scale for Swivel Aim_Pivot (Y: 240..340)
    draw.rectangle([540, 240, 996, 340], fill=(38, 42, 50, 255), outline=(100, 110, 120, 255), width=2)
    draw.text((560, 255), "SWIVEL AIM ANGLE: -30°  -15°   0°  +15°  +30°", fill=(210, 220, 230, 255))
    for t in range(21):
        tx = 560 + t * 20
        h_len = 16 if (t % 5 == 0) else 8
        draw.line([(tx, 290), (tx, 290 + h_len)], fill=(255, 255, 255, 255) if t % 5 == 0 else (160, 170, 180, 255), width=2 if t % 5 == 0 else 1)
    draw.text((560, 315), "▲ LOCK TIGHTEN M6 HEX BOLT", fill=(240, 190, 50, 255))

    # Dark graphite zone for Knuckle Joint & Rear Cable Gland (Y: 370..490)
    draw.rectangle([540, 370, 996, 490], fill=(42, 45, 52, 255), outline=(75, 80, 90, 255), width=2)
    draw.text((560, 390), "HEAVY CAST ALUMINUM SWIVEL KNUCKLE", fill=(170, 180, 190, 255))
    draw.text((560, 420), "PG-11 COMPRESSION GLAND / RJ45 PASSTHROUGH", fill=(130, 140, 150, 255))

    # -------------------------------------------------------------
    # Quadrant 3: Bottom-Left (0..512, 512..1024) -> U: 0.0..0.5, V: 0.0..0.5
    # Visor, Front Bezel & IR LEDs
    # -------------------------------------------------------------
    draw.rectangle([0, 512, 512, 1024], fill=(20, 22, 26, 255))
    cx, cy = 256, 768
    draw.ellipse([cx - 200, cy - 200, cx + 200, cy + 200], fill=(26, 29, 35, 255), outline=(85, 95, 110, 255), width=4)
    draw.ellipse([cx - 150, cy - 150, cx + 150, cy + 150], fill=(14, 16, 20, 255), outline=(50, 60, 70, 255), width=3)
    draw.text((cx - 95, cy - 120), "4K WIDE-ANGLE IRIS", fill=(160, 175, 195, 255))
    draw.text((cx - 80, cy + 100), "SMART IR LED ARRAY", fill=(130, 145, 165, 255))

    for a_idx in range(6):
        ang = a_idx * (2.0 * math.pi / 6.0)
        lx = int(cx + 105 * math.cos(ang))
        ly = int(cy + 105 * math.sin(ang))
        draw.ellipse([lx - 15, ly - 15, lx + 15, ly + 15], fill=(36, 40, 48, 255), outline=(75, 85, 95, 255), width=2)
        draw.ellipse([lx - 8, ly - 8, lx + 8, ly + 8], fill=(195, 30, 25, 255))

    # -------------------------------------------------------------
    # Quadrant 4: Bottom-Right (512..1024, 512..1024) -> U: 0.5..1.0, V: 0.0..0.5
    # Multi-Coated Optical Lens Glass
    # -------------------------------------------------------------
    draw.rectangle([512, 512, 1024, 1024], fill=(8, 10, 15, 255))
    lcx, lcy = 768, 768
    lens_layers = [
        (225, (15, 25, 42, 255)),
        (180, (20, 42, 36, 255)),
        (135, (38, 20, 48, 255)),
        (85,  (14, 52, 65, 255)),
        (40,  (8, 14, 24, 255))
    ]
    for rad, col in lens_layers:
        draw.ellipse([lcx - rad, lcy - rad, lcx + rad, lcy + rad], fill=col, outline=(45, 70, 95, 255), width=3)
    draw.text((lcx - 85, lcy - 10), "MULTI-COATED 4K", fill=(110, 150, 195, 255))

    img.save(atlas_path, "PNG")
    print(f"[OK] Re-generated Texture Atlas for Asset 31: {atlas_path}")

if __name__ == "__main__":
    generate_textures()
