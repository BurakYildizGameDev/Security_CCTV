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
    img = Image.new("RGBA", (W, H), (242, 245, 248, 255))
    draw = ImageDraw.Draw(img)

    # -------------------------------------------------------------
    # Quadrant 1: Top-Left (0..512, 0..512) -> U: 0.0..0.5, V: 0.5..1.0
    # Smoke Detector Main Body Face
    # -------------------------------------------------------------
    cx, cy = 256, 256
    # Concentric molding lines
    for r in range(240, 25, -4):
        c = 236 + int(5 * math.sin(r * 0.35))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(c, c + 1, c + 2, 255), width=2)

    # Outer twist-lock flange rim
    draw.ellipse([cx - 235, cy - 235, cx + 235, cy + 235], outline=(175, 182, 192, 255), width=4)
    draw.ellipse([cx - 220, cy - 220, cx + 220, cy + 220], outline=(205, 212, 220, 255), width=2)

    # Test / Hush Button (Embossed concentric disc - clean molded finish)
    btn_x, btn_y = cx - 90, cy + 50
    draw.ellipse([btn_x - 32, btn_y - 32, btn_x + 32, btn_y + 32], fill=(228, 232, 238, 255), outline=(170, 178, 188, 255), width=3)
    draw.ellipse([btn_x - 24, btn_y - 24, btn_x + 24, btn_y + 24], fill=(236, 239, 244, 255), outline=(195, 202, 210, 255), width=1)
    draw.ellipse([btn_x - 12, btn_y - 12, btn_x + 12, btn_y + 12], fill=(242, 245, 248, 255), outline=(210, 216, 222, 255), width=1)

    # Dual Status LEDs (Green Standby & Red Alarm)
    led_x, led_y = cx + 90, cy + 50
    # Green LED
    draw.ellipse([led_x - 20, led_y - 12, led_x - 2, led_y + 12], fill=(20, 25, 30, 255), outline=(70, 80, 92, 255), width=2)
    draw.ellipse([led_x - 17, led_y - 9, led_x - 5, led_y + 9], fill=(25, 215, 65, 255))
    # Red LED
    draw.ellipse([led_x + 2, led_y - 12, led_x + 20, led_y + 12], fill=(20, 25, 30, 255), outline=(70, 80, 92, 255), width=2)
    draw.ellipse([led_x + 5, led_y - 9, led_x + 17, led_y + 9], fill=(215, 30, 25, 255))

    # Safe buffer for plain white body
    draw.rectangle([210, 10, 300, 60], fill=(242, 245, 248, 255))

    # -------------------------------------------------------------
    # Quadrant 2: Top-Right (512..1024, 0..512) -> U: 0.5..1.0, V: 0.5..1.0
    # Vent_Ring: 360° Smoke Chamber Louver Grid & Insect Screen
    # -------------------------------------------------------------
    draw.rectangle([512, 0, 1024, 512], fill=(22, 24, 28, 255))
    for vy in range(20, 492, 14):
        draw.line([(530, vy), (1006, vy)], fill=(10, 12, 16, 255), width=7)
        draw.line([(530, vy + 4), (1006, vy + 4)], fill=(48, 54, 62, 255), width=2)
    for vx in range(540, 1000, 18):
        draw.line([(vx, 15), (vx, 495)], fill=(40, 45, 52, 255), width=2)

    # -------------------------------------------------------------
    # Quadrant 3: Bottom-Left (0..512, 512..1024) -> U: 0.0..0.5, V: 0.0..0.5
    # Lens_Insert: Covert Pinhole Bezel
    # -------------------------------------------------------------
    draw.rectangle([0, 512, 512, 1024], fill=(230, 234, 238, 255))
    pcx, pcy = 256, 768
    draw.ellipse([pcx - 140, pcy - 140, pcx + 140, pcy + 140], fill=(24, 28, 34, 255), outline=(70, 80, 92, 255), width=4)
    draw.ellipse([pcx - 90, pcy - 90, pcx + 90, pcy + 90], fill=(14, 16, 20, 255), outline=(45, 55, 65, 255), width=3)
    draw.ellipse([pcx - 45, pcy - 45, pcx + 45, pcy + 45], fill=(6, 8, 10, 255))

    # -------------------------------------------------------------
    # Quadrant 4: Bottom-Right (512..1024, 512..1024) -> U: 0.5..1.0, V: 0.0..0.5
    # Lens_Glass: Miniature Pinhole Camera Optical Glass
    # -------------------------------------------------------------
    draw.rectangle([512, 512, 1024, 1024], fill=(6, 8, 12, 255))
    gcx, gcy = 768, 768
    lens_rings = [
        (220, (14, 26, 42, 255)),
        (165, (18, 38, 34, 255)),
        (115, (36, 18, 44, 255)),
        (70,  (12, 48, 62, 255)),
        (30,  (6, 10, 18, 255))
    ]
    for rad, col in lens_rings:
        draw.ellipse([gcx - rad, gcy - rad, gcx + rad, gcy + rad], fill=col, outline=(38, 60, 85, 255), width=3)

    img.save(atlas_path, "PNG")
    print(f"[OK] Re-generated Texture Atlas for Asset 32: {atlas_path}")

if __name__ == "__main__":
    generate_textures()
