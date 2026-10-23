import os
import math
from PIL import Image, ImageDraw, ImageFont

def generate_thermal_textures():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)

    atlas_path = os.path.join(exports_dir, "T_Security_Atlas.png")

    W, H = 1024, 1024
    # Base industrial warm grey/powder coat white
    img = Image.new("RGBA", (W, H), (232, 235, 238, 255))
    draw = ImageDraw.Draw(img)

    # 1. Subtle metal surface noise / brushed lines
    for y in range(0, H, 3):
        noise = int(5 * math.sin(y * 0.2))
        c = max(220, min(242, 232 + noise))
        draw.line([(0, y), (W, y)], fill=(c, c + 1, c + 3, 255), width=2)

    # 2. Quadrant 1: Thermal Camera Body Details (U: 0.0..0.5, V: 0.5..1.0 -> X: 0..512, Y: 0..512)
    # Dark identification placard
    px0, py0, px1, py1 = 30, 40, 480, 230
    draw.rectangle([px0, py0, px1, py1], fill=(22, 26, 32, 255), outline=(55, 65, 75, 255), width=3)
    draw.text((px0 + 15, py0 + 15), "SEC-THERM LWIR 640 PRO", fill=(255, 255, 255, 255))
    draw.text((px0 + 15, py0 + 45), "UNCOOLED VOx MICROBOLOMETER 17um", fill=(240, 180, 60, 255)) # Thermal amber
    draw.text((px0 + 15, py0 + 72), "NETD <40mK  f=35mm F/1.0 RADIOMETRIC", fill=(160, 205, 240, 255))
    draw.text((px0 + 15, py0 + 98), "SPECTRAL RANGE: 8-14um LWIR  IP67", fill=(140, 155, 170, 255))
    draw.text((px0 + 15, py0 + 125), "SN: TH640-2026-9814-X  POE+ 802.3at", fill=(225, 220, 85, 255))

    # Barcode
    bx0, by0 = px0 + 290, py0 + 85
    for b in range(24):
        bw = 2 if (b % 3 == 0) else (4 if b % 5 == 0 else 1)
        bx = bx0 + b * 6
        draw.rectangle([bx, by0, bx + bw, by0 + 40], fill=(235, 240, 245, 255))

    # Regulatory and safety stamps
    draw.rectangle([30, 250, 230, 315], fill=(215, 222, 228, 255), outline=(130, 140, 150, 255), width=2)
    draw.text((45, 262), "CE  FC  RoHS  UL", fill=(45, 55, 65, 255))
    draw.text((45, 285), "THERMAL IMAGING SYS", fill=(80, 90, 100, 255))

    # Cooling fin grooves on body side (X: 0..512, Y: 340..490)
    for k in range(5):
        fy = 345 + k * 28
        draw.rectangle([20, fy, 492, fy + 16], fill=(40, 45, 52, 255), outline=(75, 85, 95, 255), width=2)
        draw.line([(22, fy + 3), (490, fy + 3)], fill=(90, 100, 110, 255), width=2)

    # 3. Quadrant 2: Front Bezel & Lens Barrel (U: 0.5..1.0, V: 0.5..1.0 -> X: 512..1024, Y: 0..512)
    draw.rectangle([512, 0, 1024, 512], fill=(28, 32, 38, 255))
    bcx, bcy = 768, 256
    draw.ellipse([bcx - 220, bcy - 220, bcx + 220, bcy + 220], fill=(20, 24, 30, 255), outline=(65, 75, 88, 255), width=6)
    draw.ellipse([bcx - 170, bcy - 170, bcx + 170, bcy + 170], fill=(15, 18, 22, 255), outline=(90, 105, 120, 255), width=3)
    # Lens specifications circular text
    draw.text((bcx - 140, bcy - 195), "GERMANIUM LWIR OPTICS 35MM F/1.0", fill=(170, 185, 200, 255))
    draw.text((bcx - 110, bcy + 175), "SEALED N2 PURGED HOUSING", fill=(130, 145, 160, 255))
    # Nitrogen purge sealed valve indicator
    draw.ellipse([bcx + 140, bcy - 20, bcx + 165, bcy + 5], fill=(200, 160, 40, 255), outline=(50, 40, 10, 255), width=2)

    # 4. Quadrant 3: Mount Bracket & Angle Scale (U: 0.0..0.5, V: 0.0..0.5 -> X: 0..512, Y: 512..1024)
    draw.rectangle([0, 512, 512, 1024], fill=(215, 220, 226, 255))
    mcx, mcy = 256, 768
    # 4 bolt holes
    for bx, by in [(-180, -180), (180, -180), (180, 180), (-180, 180)]:
        draw.ellipse([mcx + bx - 22, mcy + by - 22, mcx + bx + 22, mcy + by + 22], fill=(45, 50, 56, 255), outline=(120, 130, 140, 255), width=3)
        draw.ellipse([mcx + bx - 14, mcy + by - 14, mcx + bx + 14, mcy + by + 14], fill=(185, 192, 200, 255))
    # Degree angle indicator arc
    draw.arc([mcx - 140, mcy - 140, mcx + 140, mcy + 140], start=150, end=390, fill=(40, 45, 50, 255), width=4)
    for deg in range(-30, 31, 10):
        rad = math.radians(deg + 270)
        p1 = (mcx + 130 * math.cos(rad), mcy + 130 * math.sin(rad))
        p2 = (mcx + 150 * math.cos(rad), mcy + 150 * math.sin(rad))
        draw.line([p1, p2], fill=(60, 70, 80, 255), width=2)
    draw.text((mcx - 50, mcy + 90), "TILT SCALE ±30°", fill=(80, 90, 100, 255))

    # 5. Quadrant 4: Germanium Optical Window & Rear Panel (U: 0.5..1.0, V: 0.0..0.5 -> X: 512..1024, Y: 512..1024)
    # Germanium LWIR optical interference coatings (amber, gold, dark ruby, metallic deep purple)
    draw.rectangle([512, 512, 1024, 1024], fill=(18, 14, 12, 255))
    gcx, gcy = 768, 768
    germanium_rings = [
        (220, (35, 25, 15, 255)),
        (180, (65, 45, 20, 255)),
        (140, (110, 75, 25, 255)),
        (100, (160, 110, 35, 255)), # Warm golden germanium anti-reflection
        (60,  (90, 50, 20, 255)),
        (25,  (40, 20, 15, 255))
    ]
    for grad, gcol in germanium_rings:
        draw.ellipse([gcx - grad, gcy - grad, gcx + grad, gcy + grad], fill=gcol, outline=(50, 35, 18, 255), width=3)
    draw.text((gcx - 110, gcy - 8), "GERMANIUM LWIR WINDOW", fill=(240, 190, 70, 255))

    img.save(atlas_path, "PNG")
    print(f"[OK] Generated 1024x1024 Texture Atlas for Asset 28: {atlas_path}")

if __name__ == "__main__":
    generate_thermal_textures()
