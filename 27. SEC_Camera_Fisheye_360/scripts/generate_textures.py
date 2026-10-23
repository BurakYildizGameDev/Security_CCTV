import os
import math
from PIL import Image, ImageDraw, ImageFont

def generate_fisheye_textures():
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
        c_shade = 230 + int(8 * math.sin(r * 0.25))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(c_shade, c_shade + 1, c_shade + 3, 255), width=2)

    # 2. Quadrant 1: Main Ceiling Housing Disc Graphics (U: 0.0..0.5, V: 0.5..1.0 -> X: 0..512, Y: 0..512)
    # Outer mounting trim border
    draw.ellipse([cx - 230, cy - 230, cx + 230, cy + 230], outline=(175, 184, 192, 255), width=4)
    draw.ellipse([cx - 220, cy - 220, cx + 220, cy + 220], outline=(205, 212, 220, 255), width=2)

    # 3 Torx Tamper-Proof Security Screws at 120 degrees
    for s_idx in range(3):
        sang = s_idx * (2.0 * math.pi / 3.0) + math.pi / 6.0
        scx = int(cx + 200 * math.cos(sang))
        scy = int(cy + 200 * math.sin(sang))
        draw.ellipse([scx - 12, scy - 12, scx + 12, scy + 12], fill=(50, 55, 62, 255), outline=(130, 140, 150, 255), width=2)
        draw.ellipse([scx - 8, scy - 8, scx + 8, scy + 8], fill=(195, 202, 210, 255))
        # Torx 6-point star
        for p in range(6):
            pa = p * (2.0 * math.pi / 6.0)
            draw.line([(scx, scy), (int(scx + 5 * math.cos(pa)), int(scy + 5 * math.sin(pa)))], fill=(30, 35, 40, 255), width=2)

    # Circular text around perimeter
    draw.text((cx - 150, cy - 180), "360° FISHEYE PANORAMIC 12MP UHD", fill=(45, 52, 60, 255))
    draw.text((cx - 120, cy - 165), "INDUSTRIAL SURVEILLANCE", fill=(100, 110, 120, 255))

    # Bottom perimeter info
    draw.text((cx - 90, cy + 165), "IP66 / IK10 VANDAL-PROOF", fill=(80, 90, 100, 255))
    draw.text((cx - 110, cy + 180), "SN: FE360-12MP-98432  POE+", fill=(110, 120, 130, 255))

    # Dual microphone pinhole arrays (left and right)
    for sign in [-1, 1]:
        mx = cx + sign * 170
        my = cy
        draw.ellipse([mx - 14, my - 14, mx + 14, my + 14], fill=(215, 222, 228, 255), outline=(150, 160, 170, 255), width=1)
        for p_ang in range(6):
            pa = p_ang * (2.0 * math.pi / 6.0)
            px = int(mx + 6 * math.cos(pa))
            py = int(my + 6 * math.sin(pa))
            draw.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(30, 35, 40, 255))
        draw.ellipse([mx - 2, my - 2, mx + 2, my + 2], fill=(25, 28, 32, 255))
        draw.text((mx - 10, my + 16), "MIC", fill=(100, 110, 120, 255))

    # Status LED cluster (top right)
    led_x = cx + 120
    led_y = cy - 120
    draw.ellipse([led_x - 10, led_y - 10, led_x + 10, led_y + 10], fill=(35, 40, 48, 255), outline=(90, 100, 110, 255), width=2)
    draw.ellipse([led_x - 5, led_y - 5, led_x + 5, led_y + 5], fill=(25, 190, 65, 255), outline=(120, 255, 150, 255), width=1) # Green power
    draw.text((led_x - 14, led_y + 12), "STATUS", fill=(95, 105, 115, 255))

    # Central lens well aperture (dark recess)
    draw.ellipse([cx - 120, cy - 120, cx + 120, cy + 120], fill=(18, 20, 24, 255), outline=(45, 50, 58, 255), width=3)
    draw.ellipse([cx - 90, cy - 90, cx + 90, cy + 90], fill=(10, 12, 15, 255), outline=(30, 35, 42, 255), width=2)
    draw.text((cx - 60, cy - 65), "F=1.05mm 1:2.0 360°", fill=(120, 135, 150, 255))
    draw.text((cx - 50, cy + 50), "PANOMORPH", fill=(90, 105, 120, 255))

    # 3. Quadrant 2: Trim Ring Metallic Finish (U: 0.5..1.0, V: 0.5..1.0 -> X: 512..1024, Y: 0..512)
    draw.rectangle([512, 0, 1024, 512], fill=(36, 40, 46, 255))
    # Beveled highlight bands & knurling
    draw.line([(512, 40), (1024, 40)], fill=(85, 95, 105, 255), width=4)
    draw.line([(512, 120), (1024, 120)], fill=(24, 26, 30, 255), width=6)
    draw.line([(512, 220), (1024, 220)], fill=(70, 78, 88, 255), width=3)
    draw.text((540, 160), "ANODIZED HARDENED ALUMINUM BEZEL", fill=(130, 140, 155, 255))

    # 4. Quadrant 3: Ceiling Plate Base Metal (U: 0.0..0.5, V: 0.0..0.5 -> X: 0..512, Y: 512..1024)
    draw.rectangle([0, 512, 512, 1024], fill=(225, 230, 236, 255))
    draw.rectangle([40, 552, 472, 984], fill=(218, 224, 230, 255), outline=(170, 180, 190, 255), width=3)
    draw.text((60, 580), "CEILING RECESSED MOUNTING ADAPTER", fill=(90, 100, 110, 255))
    draw.text((60, 610), "COMPATIBLE WITH STANDARD 4\" JUNCTION BOX", fill=(120, 130, 140, 255))

    # 5. Quadrant 4: Optical Multi-Coated Lens Base (U: 0.5..1.0, V: 0.0..0.5 -> X: 512..1024, Y: 512..1024)
    draw.rectangle([512, 512, 1024, 1024], fill=(8, 10, 14, 255))
    ocx, ocy = 768, 768
    # Multi-spectral optical iris reflections (emerald green, violet, cobalt blue)
    rings_spec = [
        (220, (14, 26, 42, 255)),
        (175, (22, 38, 32, 255)),
        (130, (32, 18, 38, 255)),
        (85,  (12, 45, 55, 255)),
        (45,  (6, 12, 18, 255))
    ]
    for orad, ocolor in rings_spec:
        draw.ellipse([ocx - orad, ocy - orad, ocx + orad, ocy + orad], fill=ocolor, outline=(45, 65, 90, 255), width=3)
    draw.text((ocx - 90, ocy - 8), "MULTI-ELEMENT OPTICS", fill=(100, 135, 170, 255))

    img.save(atlas_path, "PNG")
    print(f"[OK] Generated 1024x1024 Texture Atlas: {atlas_path}")

if __name__ == "__main__":
    generate_fisheye_textures()
