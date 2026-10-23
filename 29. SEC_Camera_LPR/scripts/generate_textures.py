import os
import math
from PIL import Image, ImageDraw

def generate_lpr_textures():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)

    atlas_path = os.path.join(exports_dir, "T_Security_Atlas.png")

    W, H = 1024, 1024
    img = Image.new("RGBA", (W, H), (234, 238, 242, 255))
    draw = ImageDraw.Draw(img)

    # 1. Subtle metal surface noise / brushed lines
    for y in range(0, H, 3):
        noise = int(5 * math.sin(y * 0.22))
        c = max(222, min(244, 234 + noise))
        draw.line([(0, y), (W, y)], fill=(c, c + 1, c + 3, 255), width=2)

    # 2. Quadrant 1: LPR Camera Body Details (U: 0.0..0.5, V: 0.5..1.0 -> X: 0..512, Y: 0..512)
    px0, py0, px1, py1 = 30, 40, 480, 230
    draw.rectangle([px0, py0, px1, py1], fill=(20, 24, 30, 255), outline=(50, 60, 72, 255), width=3)
    draw.text((px0 + 15, py0 + 15), "SEC-LPR ANPR ULTRA 4K", fill=(255, 255, 255, 255))
    draw.text((px0 + 15, py0 + 45), "GLOBAL SHUTTER 60FPS / TRAFFIC ENFORCEMENT", fill=(100, 220, 255, 255))
    draw.text((px0 + 15, py0 + 72), "PLATE CAPTURE RANGE: 15-50M  UP TO 250 KM/H", fill=(240, 200, 70, 255))
    draw.text((px0 + 15, py0 + 98), "MOTORIZED f=12-40mm F/1.4 AUTO-IRIS  IP68", fill=(160, 180, 200, 255))
    draw.text((px0 + 15, py0 + 125), "SN: LPR4K-2026-7731-X  POE+ / 24V AC", fill=(225, 220, 85, 255))

    # Barcode
    bx0, by0 = px0 + 290, py0 + 85
    for b in range(24):
        bw = 2 if (b % 3 == 0) else (4 if b % 5 == 0 else 1)
        bx = bx0 + b * 6
        draw.rectangle([bx, by0, bx + bw, by0 + 40], fill=(235, 240, 245, 255))

    # Regulatory stamps
    draw.rectangle([30, 250, 230, 315], fill=(215, 222, 228, 255), outline=(130, 140, 150, 255), width=2)
    draw.text((45, 262), "CE  FC  RoHS  UL", fill=(45, 55, 65, 255))
    draw.text((45, 285), "ANPR / LPR SYSTEM", fill=(80, 90, 100, 255))

    # Dual mounting slide rails
    draw.rectangle([20, 360, 492, 385], fill=(45, 50, 58, 255), outline=(100, 110, 120, 255), width=2)
    draw.rectangle([20, 420, 492, 445], fill=(45, 50, 58, 255), outline=(100, 110, 120, 255), width=2)
    draw.text((40, 395), "ADJUSTABLE DUAL BRACKET RAIL", fill=(90, 105, 120, 255))

    # 3. Quadrant 2: Sunshield Hood & Lens Bezel (U: 0.5..1.0, V: 0.5..1.0 -> X: 512..1024, Y: 0..512)
    draw.rectangle([512, 0, 1024, 512], fill=(236, 240, 245, 255))
    # Top ridge strip
    draw.rectangle([512, 20, 1024, 75], fill=(205, 212, 220, 255), outline=(160, 170, 180, 255), width=2)
    draw.text((540, 38), "EXTENDED ALL-WEATHER SUNSHIELD VISOR", fill=(85, 95, 105, 255))
    # Anti-glare matte coating (interior)
    draw.rectangle([512, 140, 1024, 320], fill=(18, 20, 24, 255))
    draw.text((560, 220), "ANTI-REFLECTIVE MATTE FINISH", fill=(80, 85, 95, 255))
    # Telephoto lens bezel
    bcx, bcy = 768, 420
    draw.ellipse([bcx - 85, bcy - 85, bcx + 85, bcy + 85], fill=(24, 28, 34, 255), outline=(70, 80, 92, 255), width=4)
    draw.ellipse([bcx - 65, bcy - 65, bcx + 65, bcy + 65], fill=(12, 14, 18, 255), outline=(45, 55, 65, 255), width=2)
    draw.text((bcx - 60, bcy - 8), "12-40mm F/1.4", fill=(140, 160, 180, 255))

    # 4. Quadrant 3: Wall Mount Plate (U: 0.0..0.5, V: 0.0..0.5 -> X: 0..512, Y: 512..1024)
    draw.rectangle([0, 512, 512, 1024], fill=(218, 224, 230, 255))
    mcx, mcy = 256, 768
    # 4 heavy-duty mounting anchors
    for bx, by in [(-170, -170), (170, -170), (170, 170), (-170, 170)]:
        draw.ellipse([mcx + bx - 22, mcy + by - 22, mcx + bx + 22, mcy + by + 22], fill=(45, 50, 56, 255), outline=(120, 130, 140, 255), width=3)
        draw.ellipse([mcx + bx - 14, mcy + by - 14, mcx + bx + 14, mcy + by + 14], fill=(185, 192, 200, 255))
    # Pan/Tilt degree scale
    draw.arc([mcx - 130, mcy - 130, mcx + 130, mcy + 130], start=160, end=380, fill=(40, 45, 50, 255), width=4)
    draw.text((mcx - 85, mcy + 80), "PAN ±40° / TILT ±25°", fill=(80, 90, 100, 255))

    # 5. Quadrant 4: High-Power Pulsed IR LED Illuminator Array (U: 0.5..1.0, V: 0.0..0.5 -> X: 512..1024, Y: 512..1024)
    # Deep dark acrylic faceplate
    draw.rectangle([512, 512, 1024, 1024], fill=(12, 14, 18, 255))
    # Matrix of 4x4 = 16 high-power IR LED emitters
    # Centered at (768, 768)
    icx, icy = 768, 768
    step_x = 90
    step_y = 90
    for row in range(4):
        for col in range(4):
            lx = int(icx - 135 + col * step_x)
            ly = int(icy - 135 + row * step_y)
            # Outer reflector cup
            draw.ellipse([lx - 34, ly - 34, lx + 34, ly + 34], fill=(28, 32, 38, 255), outline=(60, 68, 78, 255), width=2)
            # Fresnel lens ring
            draw.ellipse([lx - 24, ly - 24, lx + 24, ly + 24], fill=(38, 42, 50, 255), outline=(80, 90, 105, 255), width=1)
            # Glowing 850nm IR diode core (bright red + hotspot)
            draw.ellipse([lx - 14, ly - 14, lx + 14, ly + 14], fill=(210, 30, 25, 255))
            draw.ellipse([lx - 6, ly - 6, lx + 6, ly + 6], fill=(255, 190, 180, 255))

    # Header label on illuminator face
    draw.rectangle([540, 525, 996, 565], fill=(20, 24, 30, 255), outline=(70, 80, 90, 255), width=2)
    draw.text((570, 538), "HIGH-POWER PULSED IR STROBE 850NM / 80M", fill=(240, 210, 80, 255))

    img.save(atlas_path, "PNG")
    print(f"[OK] Generated 1024x1024 Texture Atlas for Asset 29: {atlas_path}")

if __name__ == "__main__":
    generate_lpr_textures()
