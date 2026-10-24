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
    img = Image.new("RGBA", (W, H), (234, 238, 242, 255))
    draw = ImageDraw.Draw(img)

    # -------------------------------------------------------------
    # Quadrant 1: Top-Left (0..512, 0..512) -> U: 0.0..0.5, V: 0.5..1.0
    # Mount Base, Knuckle Fork & Heavy Cast Armor Powder-Coat
    # -------------------------------------------------------------
    draw.rectangle([0, 0, 512, 512], fill=(232, 236, 240, 255))
    draw.rectangle([15, 15, 497, 497], outline=(205, 212, 220, 255), width=2)

    # Safe Powder-Coat Neutral Buffer (U: 0.10..0.40, V: 0.60..0.90 -> Y: 50..450)
    draw.rectangle([50, 50, 460, 460], fill=(234, 238, 242, 255))

    # Heavy Anchor Bolt & Washer Graphics
    bolt_coords = [(110, 110), (402, 110), (110, 402), (402, 402)]
    for bx, by in bolt_coords:
        draw.ellipse([bx - 32, by - 32, bx + 32, by + 32], fill=(160, 168, 178, 255), outline=(110, 118, 128, 255), width=3)
        draw.ellipse([bx - 20, by - 20, bx + 20, by + 20], fill=(60, 65, 72, 255))
        hex_pts = []
        for h in range(6):
            hang = h * (2.0 * math.pi / 6.0)
            hex_pts.append((bx + int(16 * math.cos(hang)), by + int(16 * math.sin(hang))))
        draw.polygon(hex_pts, fill=(200, 206, 214, 255), outline=(80, 85, 92, 255))

    # Ground Lug Symbol
    draw.ellipse([256 - 22, 110 - 22, 256 + 22, 110 + 22], fill=(185, 150, 40, 255), outline=(140, 110, 25, 255), width=2)
    draw.text((248, 102), "⏚", fill=(255, 255, 255, 255))

    # -------------------------------------------------------------
    # Quadrant 2: Top-Right (512..1024, 0..512) -> U: 0.5..1.0, V: 0.5..1.0
    # Armored Camera Flank Branding, Specification & Barcode
    # -------------------------------------------------------------
    draw.rectangle([512, 0, 1024, 512], fill=(232, 236, 240, 255))

    # Side Placard Box (U: 0.52..0.99, V: 0.80..0.96 -> Y: 40..205)
    draw.rectangle([530, 40, 1010, 205], fill=(16, 18, 22, 255), outline=(85, 95, 105, 255), width=2)
    draw.rectangle([535, 45, 1005, 200], outline=(45, 52, 62, 255), width=1)

    pcx = 770
    placard_lines = [
        (54,  "SEC-CAM  |  ARMORED IK10+", (255, 255, 255, 255)),
        (78,  "HEAVY VANDAL-PROOF INDUSTRIAL SURVEILLANCE", (195, 215, 235, 255)),
        (98,  "EX-PROOF ENCLOSURE  •  NEMA 4X / IP68", (245, 195, 45, 255)),
        (180, "MODEL: SEC-ARM-4000  •  4K 60FPS  •  CE RoHS", (145, 158, 172, 255))
    ]
    for y_pos, t_str, t_col in placard_lines:
        t_w = draw.textlength(t_str)
        draw.text((pcx - t_w / 2, y_pos), t_str, fill=t_col)

    # Centered Barcode
    bar_w = 360
    hbx = int(pcx - bar_w / 2)
    hby = 122
    for b in range(72):
        thick = 3 if (b % 4 == 0 or b % 9 == 0) else (2 if b % 2 == 0 else 1)
        b_col = (255, 255, 255, 255) if (b % 3 == 0 or b % 5 == 0) else (16, 18, 22, 255)
        draw.line([(hbx + b * 5, hby), (hbx + b * 5, hby + 48)], fill=b_col, width=thick)

    # Angle degree scale for Aim_Pivot (Y: 240..340)
    draw.rectangle([540, 240, 996, 340], fill=(36, 40, 48, 255), outline=(95, 105, 115, 255), width=2)
    t_angle = "TILT AIM SCALE: -25°  -15°   0°  +15°  +25°"
    draw.text((pcx - draw.textlength(t_angle) / 2, 255), t_angle, fill=(210, 222, 234, 255))
    for t in range(21):
        tx = 580 + t * 19
        h_len = 16 if (t % 5 == 0) else 8
        draw.line([(tx, 290), (tx, 290 + h_len)], fill=(255, 255, 255, 255) if t % 5 == 0 else (160, 170, 180, 255), width=2 if t % 5 == 0 else 1)
    t_lock = "▲ TORQUE SPEC: 15 Nm M8 HIGH-TENSILE CLAMP"
    draw.text((pcx - draw.textlength(t_lock) / 2, 316), t_lock, fill=(245, 195, 45, 255))

    # Dark graphite zone for Knuckle Joint & Rear Cable Gland (Y: 370..490)
    draw.rectangle([540, 370, 996, 490], fill=(40, 44, 50, 255), outline=(75, 82, 92, 255), width=2)
    t_gland = "PG-16 EXPLOSION-PROOF ARMORED CABLE CONDUIT"
    draw.text((pcx - draw.textlength(t_gland) / 2, 415), t_gland, fill=(160, 172, 185, 255))

    # -------------------------------------------------------------
    # Quadrant 3: Bottom-Left (0..512, 512..1024) -> U: 0.0..0.5, V: 0.0..0.5
    # Lens Guard Steel Bezel & Smart IR LED Array
    # -------------------------------------------------------------
    draw.rectangle([0, 512, 512, 1024], fill=(22, 24, 28, 255))
    cx, cy = 256, 768
    draw.ellipse([cx - 210, cy - 210, cx + 210, cy + 210], fill=(30, 34, 40, 255), outline=(90, 100, 112, 255), width=4)
    draw.ellipse([cx - 165, cy - 165, cx + 165, cy + 165], fill=(16, 18, 22, 255), outline=(55, 62, 72, 255), width=3)
    draw.text((cx - 90, cy - 130), "BALLISTIC OPTICS", fill=(175, 190, 205, 255))
    draw.text((cx - 80, cy + 110), "IK10+ ARMORED", fill=(245, 195, 45, 255))

    # 8 High-Power Smart IR Illuminators
    for a_idx in range(8):
        ang = a_idx * (2.0 * math.pi / 8.0)
        lx = int(cx + 120 * math.cos(ang))
        ly = int(cy + 120 * math.sin(ang))
        draw.ellipse([lx - 16, ly - 16, lx + 16, ly + 16], fill=(38, 42, 50, 255), outline=(78, 88, 98, 255), width=2)
        draw.ellipse([lx - 9, ly - 9, lx + 9, ly + 9], fill=(210, 30, 25, 255))

    # 4 Torx Security Bolt Heads on Guard Bezel
    for b_idx in range(4):
        ang = (math.pi / 4.0) + b_idx * (math.pi / 2.0)
        bx = int(cx + 185 * math.cos(ang))
        by = int(cy + 185 * math.sin(ang))
        draw.ellipse([bx - 14, by - 14, bx + 14, by + 14], fill=(180, 188, 196, 255), outline=(100, 108, 116, 255), width=2)
        draw.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=(45, 50, 58, 255))

    # -------------------------------------------------------------
    # Quadrant 4: Bottom-Right (512..1024, 512..1024) -> U: 0.5..1.0, V: 0.0..0.5
    # High-Transmission Ballistic Optic Lens Glass
    # -------------------------------------------------------------
    draw.rectangle([512, 512, 1024, 1024], fill=(8, 10, 14, 255))
    lcx, lcy = 768, 768
    lens_layers = [
        (225, (14, 24, 40, 255)),
        (180, (18, 40, 34, 255)),
        (135, (36, 18, 46, 255)),
        (85,  (12, 50, 62, 255)),
        (40,  (8, 14, 22, 255))
    ]
    for rad, col in lens_layers:
        draw.ellipse([lcx - rad, lcy - rad, lcx + rad, lcy + rad], fill=col, outline=(42, 68, 92, 255), width=3)

    img.save(atlas_path, "PNG")
    print(f"[OK] Generated Texture Atlas for Asset 33: {atlas_path}")

if __name__ == "__main__":
    generate_textures()
