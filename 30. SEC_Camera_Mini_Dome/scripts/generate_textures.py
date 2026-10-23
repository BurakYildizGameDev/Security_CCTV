import os
import math
from PIL import Image, ImageDraw

def generate_mini_dome_textures():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)

    atlas_path = os.path.join(exports_dir, "T_Security_Atlas.png")

    W, H = 1024, 1024
    img = Image.new("RGBA", (W, H), (236, 240, 244, 255))
    draw = ImageDraw.Draw(img)

    # 1. Subtle radial brushed texture on base
    cx, cy = 256, 256
    for r in range(240, 20, -3):
        c = 232 + int(6 * math.sin(r * 0.25))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(c, c + 1, c + 3, 255), width=2)

    # 2. Quadrant 1: Ceiling Mount Base Disc (U: 0.0..0.5, V: 0.5..1.0 -> X: 0..512, Y: 0..512)
    # Outer mounting trim border
    draw.ellipse([cx - 230, cy - 230, cx + 230, cy + 230], outline=(175, 184, 192, 255), width=4)
    draw.ellipse([cx - 220, cy - 220, cx + 220, cy + 220], outline=(205, 212, 220, 255), width=2)

    # 3 Torx Tamper-Proof Screws at 120°
    for s_idx in range(3):
        sang = s_idx * (2.0 * math.pi / 3.0) + math.pi / 6.0
        scx = int(cx + 195 * math.cos(sang))
        scy = int(cy + 195 * math.sin(sang))
        draw.ellipse([scx - 12, scy - 12, scx + 12, scy + 12], fill=(48, 52, 60, 255), outline=(130, 140, 150, 255), width=2)
        draw.ellipse([scx - 8, scy - 8, scx + 8, scy + 8], fill=(195, 202, 210, 255))
        for p in range(6):
            pa = p * (2.0 * math.pi / 6.0)
            draw.line([(scx, scy), (int(scx + 5 * math.cos(pa)), int(scy + 5 * math.sin(pa)))], fill=(30, 35, 40, 255), width=2)

    # Perimeter technical typography
    draw.text((cx - 145, cy - 175), "SEC-CAM MINI DOME 4K COMPACT", fill=(45, 52, 60, 255))
    draw.text((cx - 115, cy - 160), "PROFESSIONAL INDOOR/OUTDOOR", fill=(100, 110, 120, 255))
    draw.text((cx - 90, cy + 160), "POE 802.3af  IP66 / IK08", fill=(80, 90, 100, 255))
    draw.text((cx - 105, cy + 175), "SN: MD4K-2026-6184-C", fill=(110, 120, 130, 255))

    # Status LED & microphone
    led_x, led_y = cx + 120, cy - 120
    draw.ellipse([led_x - 9, led_y - 9, led_x + 9, led_y + 9], fill=(35, 40, 48, 255), outline=(90, 100, 110, 255), width=2)
    draw.ellipse([led_x - 5, led_y - 5, led_x + 5, led_y + 5], fill=(25, 200, 60, 255), outline=(120, 255, 150, 255), width=1)
    draw.text((led_x - 14, led_y + 11), "PWR", fill=(90, 100, 110, 255))

    # Inner dome seating bezel
    draw.ellipse([cx - 130, cy - 130, cx + 130, cy + 130], outline=(140, 150, 160, 255), width=3)
    draw.ellipse([cx - 110, cy - 110, cx + 110, cy + 110], fill=(25, 28, 34, 255), outline=(60, 70, 80, 255), width=2)

    # 3. Quadrant 2: Internal Gimbal Eyeball Sphere (U: 0.5..1.0, V: 0.5..1.0 -> X: 512..1024, Y: 0..512)
    draw.rectangle([512, 0, 1024, 512], fill=(22, 25, 30, 255))
    gcx, gcy = 768, 256
    draw.ellipse([gcx - 210, gcy - 210, gcx + 210, gcy + 210], fill=(28, 32, 38, 255), outline=(65, 75, 88, 255), width=4)
    draw.ellipse([gcx - 140, gcy - 140, gcx + 140, gcy + 140], fill=(14, 16, 20, 255), outline=(45, 55, 65, 255), width=3)
    draw.text((gcx - 85, gcy - 115), "f=2.8mm F/2.0 105°", fill=(140, 160, 180, 255))
    draw.text((gcx - 70, gcy + 95), "WIDE ANGLE IRIS", fill=(100, 115, 130, 255))

    # 2 Micro IR LEDs inside eyeball
    for sign in [-1, 1]:
        lx = gcx + sign * 90
        ly = gcy
        draw.ellipse([lx - 12, ly - 12, lx + 12, ly + 12], fill=(40, 45, 52, 255), outline=(70, 80, 90, 255), width=2)
        draw.ellipse([lx - 6, ly - 6, lx + 6, ly + 6], fill=(190, 30, 25, 255))

    # 4. Quadrant 3: Ceiling Template & Regulatory (U: 0.0..0.5, V: 0.0..0.5 -> X: 0..512, Y: 512..1024)
    draw.rectangle([0, 512, 512, 1024], fill=(222, 226, 232, 255))
    draw.rectangle([30, 542, 482, 994], fill=(215, 220, 226, 255), outline=(160, 170, 180, 255), width=2)
    draw.text((50, 570), "CEILING QUICK-MOUNT BRACKET", fill=(80, 90, 100, 255))
    draw.text((50, 600), "CE  FC  RoHS  UKCA  UL LISTED", fill=(60, 70, 80, 255))
    draw.text((50, 630), "IK08 IMPACT RESISTANT POLYCARBONATE", fill=(100, 110, 120, 255))

    # 5. Quadrant 4: Optical Multi-Coated Lens Base (U: 0.5..1.0, V: 0.0..0.5 -> X: 512..1024, Y: 512..1024)
    draw.rectangle([512, 512, 1024, 1024], fill=(8, 10, 14, 255))
    ocx, ocy = 768, 768
    lens_rings = [
        (220, (14, 28, 45, 255)),
        (170, (20, 40, 35, 255)),
        (120, (35, 18, 42, 255)),
        (75,  (12, 50, 60, 255)),
        (35,  (6, 12, 20, 255))
    ]
    for lrad, lcol in lens_rings:
        draw.ellipse([ocx - lrad, ocy - lrad, ocx + lrad, ocy + lrad], fill=lcol, outline=(40, 65, 90, 255), width=3)
    draw.text((ocx - 80, ocy - 8), "MULTI-COATED OPTICS", fill=(100, 140, 180, 255))

    img.save(atlas_path, "PNG")
    print(f"[OK] Generated 1024x1024 Texture Atlas for Asset 30: {atlas_path}")

if __name__ == "__main__":
    generate_mini_dome_textures()
