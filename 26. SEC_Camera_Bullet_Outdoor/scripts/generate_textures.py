import os
import math
from PIL import Image, ImageDraw

def generate_bullet_textures():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)

    atlas_path = os.path.join(exports_dir, "T_Security_Atlas.png")

    W, H = 1024, 1024
    img = Image.new("RGBA", (W, H), (232, 236, 240, 255))
    draw = ImageDraw.Draw(img)

    # 1. Base Powder-Coated Metal Texture
    for y in range(0, H, 3):
        noise = int(6 * math.sin(y * 0.25))
        c_val = max(220, min(242, 230 + noise))
        draw.line([(0, y), (W, y)], fill=(c_val, c_val + 2, c_val + 4, 255), width=2)

    # 2. Zone 1: Camera Body Details (U: 0.0 - 0.5, V: 0.5 - 1.0 -> X: 0..512, Y: 0..512)
    # Brand and Model Plate
    px0, py0, px1, py1 = 30, 40, 480, 210
    draw.rectangle([px0, py0, px1, py1], fill=(22, 25, 30, 255), outline=(50, 60, 70, 255), width=3)
    draw.text((px0 + 15, py0 + 15), "SEC-CAM BULLET 4K PRO", fill=(255, 255, 255, 255))
    draw.text((px0 + 15, py0 + 45), "ULTRA HD IP67 / IK10 CCTV", fill=(160, 200, 235, 255))
    draw.text((px0 + 15, py0 + 75), "POE+ 802.3at / 12V DC  IR 60M  f=3.6mm", fill=(140, 155, 170, 255))
    draw.text((px0 + 15, py0 + 105), "SN: BC4K-2026-94827-X", fill=(225, 220, 85, 255))

    # Barcode
    bx0, by0 = px0 + 290, py0 + 70
    for b in range(24):
        bw = 2 if (b % 3 == 0) else (4 if b % 5 == 0 else 1)
        bx = bx0 + b * 6
        draw.rectangle([bx, by0, bx + bw, by0 + 45], fill=(235, 240, 245, 255))

    # Regulatory stamps
    draw.rectangle([30, 230, 220, 295], fill=(215, 222, 228, 255), outline=(130, 140, 150, 255), width=2)
    draw.text((45, 245), "CE  FC  RoHS  UL", fill=(45, 55, 65, 255))
    draw.text((45, 268), "INDUSTRIAL SURVEILLANCE", fill=(80, 90, 100, 255))

    # Body seam panel lines
    draw.line([(0, 380), (512, 380)], fill=(110, 120, 130, 255), width=3)
    draw.line([(0, 383), (512, 383)], fill=(250, 255, 255, 255), width=2)

    # 3. Zone 2: Sunshield Hood (U: 0.5 - 1.0, V: 0.5 - 1.0 -> X: 512..1024, Y: 0..512)
    draw.rectangle([512, 0, 1024, 512], fill=(236, 240, 245, 255))
    # Top ridge strip
    draw.rectangle([512, 20, 1024, 75], fill=(205, 212, 220, 255), outline=(160, 170, 180, 255), width=2)
    draw.text((540, 36), "IMPACT RESISTANT POLYCARBONATE HOOD", fill=(90, 105, 115, 255))
    # Slide slot
    draw.rectangle([700, 30, 920, 65], fill=(45, 50, 60, 255), outline=(110, 120, 130, 255), width=2)
    draw.ellipse([790, 34, 825, 61], fill=(175, 180, 190, 255), outline=(60, 65, 75, 255), width=2) # thumbscrew
    # Anti-glare matte coating (interior)
    draw.rectangle([512, 220, 1024, 430], fill=(18, 20, 24, 255))
    draw.text((560, 310), "ANTI-GLARE MATTE COATING", fill=(75, 80, 90, 255))
    # Rubber bumper edge
    draw.rectangle([512, 440, 1024, 512], fill=(26, 30, 34, 255))
    draw.line([(512, 440), (1024, 440)], fill=(60, 65, 75, 255), width=4)

    # 4. Zone 3: Wall Mount Plate & Bracket (U: 0.0 - 0.5, V: 0.0 - 0.5 -> X: 0..512, Y: 512..1024)
    draw.rectangle([0, 512, 512, 1024], fill=(218, 224, 230, 255))
    # Circular flange border preview (centered at 256, 768)
    fcx, fcy = 256, 768
    draw.ellipse([fcx - 220, fcy - 220, fcx + 220, fcy + 220], outline=(140, 150, 160, 255), width=5)
    draw.ellipse([fcx - 170, fcy - 170, fcx + 170, fcy + 170], fill=(200, 208, 215, 255), outline=(120, 130, 140, 255), width=3)
    # 3 Countersunk screws
    for ang_deg in [0, 120, 240]:
        rad = math.radians(ang_deg)
        scx = int(fcx + 130 * math.cos(rad))
        scy = int(fcy + 130 * math.sin(rad))
        draw.ellipse([scx - 18, scy - 18, scx + 18, scy + 18], fill=(45, 50, 55, 255), outline=(110, 120, 130, 255), width=2)
        draw.ellipse([scx - 10, scy - 10, scx + 10, scy + 10], fill=(185, 192, 200, 255))
        draw.line([(scx - 8, scy), (scx + 8, scy)], fill=(35, 40, 45, 255), width=3)
    # Center cable entry
    draw.ellipse([fcx - 45, fcy - 45, fcx + 45, fcy + 45], fill=(24, 26, 30, 255), outline=(70, 80, 90, 255), width=4)

    # 5. Zone 4: IR Faceplate (U: 0.5 - 1.0, V: 0.0 - 0.5 -> X: 512..1024, Y: 512..1024)
    # Centered at (768, 768) in 1024x1024 -> UV center is (0.75, 0.25)
    icx, icy = 768, 768
    ir_radius = 230
    draw.rectangle([512, 512, 1024, 1024], fill=(14, 16, 20, 255))
    draw.ellipse([icx - ir_radius, icy - ir_radius, icx + ir_radius, icy + ir_radius],
                 fill=(22, 24, 28, 255), outline=(55, 62, 72, 255), width=5)

    # Concentric IR LED array dots (18 LEDs in outer ring, 12 in inner ring)
    for r_ring, count in [(170, 18), (115, 12)]:
        for k in range(count):
            ang = k * (2.0 * math.pi / count)
            lx = int(icx + r_ring * math.cos(ang))
            ly = int(icy + r_ring * math.sin(ang))
            draw.ellipse([lx - 13, ly - 13, lx + 13, ly + 13], fill=(36, 40, 46, 255), outline=(65, 72, 82, 255), width=2)
            draw.ellipse([lx - 7, ly - 7, lx + 7, ly + 7], fill=(180, 25, 20, 255)) # Glowing diode
            draw.ellipse([lx - 3, ly - 3, lx + 3, ly + 3], fill=(255, 180, 170, 255)) # Hotspot

    # Center optical aperture
    draw.ellipse([icx - 65, icy - 65, icx + 65, icy + 65],
                 fill=(6, 8, 12, 255), outline=(45, 75, 105, 255), width=4)

    # Status LED & CDS Sensor
    draw.ellipse([icx - 16, icy + 185, icx + 16, icy + 217], fill=(20, 220, 50, 255), outline=(140, 255, 160, 255), width=2)
    draw.ellipse([icx - 16, icy - 217, icx + 16, icy - 185], fill=(16, 18, 22, 255), outline=(70, 78, 88, 255), width=2)

    img.save(atlas_path, "PNG")
    print(f"[OK] Generated 1024x1024 Texture Atlas: {atlas_path}")

if __name__ == "__main__":
    generate_bullet_textures()
