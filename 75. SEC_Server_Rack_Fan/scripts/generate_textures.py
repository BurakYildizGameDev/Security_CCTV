import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def create_rack_fan_texture(output_path):
    WIDTH, HEIGHT = 2048, 2048
    np.random.seed(7575)

    rgb_data = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    alpha_data = np.full((HEIGHT, WIDTH), 255, dtype=np.uint8)

    # -------------------------------------------------------------
    # REGION 0: Matte Black Industrial PBT Fan Frame (0..1024, 0..1024)
    # (In Blender UV: U: 0.0..0.5, V: 0.5..1.0)
    # -------------------------------------------------------------
    frame_base = np.array([32, 34, 38], dtype=np.float32)
    noise_frame = np.random.normal(0, 2.5, (1024, 1024))
    for c in range(3):
        rgb_data[0:1024, 0:1024, c] = np.clip(frame_base[c] + noise_frame, 0, 255).astype(np.uint8)

    # -------------------------------------------------------------
    # REGION 1: Nickel Plated Steel Wire Grille & Hardware (1024..2048, 0..1024)
    # (In Blender UV: U: 0.5..1.0, V: 0.5..1.0)
    # -------------------------------------------------------------
    metal_base = np.array([218, 222, 226], dtype=np.float32)
    noise_metal = np.random.normal(0, 3.5, (1024, 1024))
    for c in range(3):
        rgb_data[0:1024, 1024:2048, c] = np.clip(metal_base[c] + noise_metal, 0, 255).astype(np.uint8)

    # -------------------------------------------------------------
    # REGION 2: Center Motor Hub Specification Badge (0..1024, 1024..2048)
    # (In Blender UV: U: 0.0..0.5, V: 0.0..0.5)
    # -------------------------------------------------------------
    hub_base = np.array([24, 26, 30], dtype=np.float32)
    noise_hub = np.random.normal(0, 2.0, (1024, 1024))
    for c in range(3):
        rgb_data[1024:2048, 0:1024, c] = np.clip(hub_base[c] + noise_hub, 0, 255).astype(np.uint8)

    # -------------------------------------------------------------
    # REGION 3: Fan Blades PBT Polymer (1024..2048, 1024..2048)
    # (In Blender UV: U: 0.5..1.0, V: 0.0..0.5)
    # -------------------------------------------------------------
    blade_base = np.array([28, 30, 34], dtype=np.float32)
    noise_blade = np.random.normal(0, 2.0, (1024, 1024))
    for c in range(3):
        rgb_data[1024:2048, 1024:2048, c] = np.clip(blade_base[c] + noise_blade, 0, 255).astype(np.uint8)

    rgba = np.dstack([rgb_data, alpha_data])
    img = Image.fromarray(rgba, mode='RGBA')
    draw = ImageDraw.Draw(img)

    # 1. Subtle molding lines on frame region
    for y in range(80, 960, 160):
        draw.line([0, y, 1024, y], fill=(22, 24, 26, 255), width=2)
        draw.line([0, y + 2, 1024, y + 2], fill=(44, 46, 50, 255), width=1)

    # 2. Wire highlight stripes on metal grille region
    for x in range(1060, 2020, 60):
        draw.line([x, 0, x, 1024], fill=(160, 165, 170, 255), width=3)
        draw.line([x + 3, 0, x + 3, 1024], fill=(245, 248, 252, 255), width=2)

    # 3. Precision Motor Hub Circular Label in Region 2 (Center at X=512, Y=1536)
    hcx, hcy = 512, 1536
    hr_outer = 420
    # Outer dark blue / metallic cyan border rings
    draw.ellipse([hcx - hr_outer, hcy - hr_outer, hcx + hr_outer, hcy + hr_outer], fill=(18, 24, 32, 255), outline=(0, 160, 210, 255), width=8)
    draw.ellipse([hcx - (hr_outer - 25), hcy - (hr_outer - 25), hcx + (hr_outer - 25), hcy + (hr_outer - 25)], outline=(200, 205, 210, 255), width=4)

    # Inner disc
    hr_in = 360
    draw.ellipse([hcx - hr_in, hcy - hr_in, hcx + hr_in, hcy + hr_in], fill=(22, 25, 30, 255))

    # Font setup
    try:
        font_lg = ImageFont.truetype("arialbd.ttf", 46)
        font_md = ImageFont.truetype("arialbd.ttf", 32)
        font_sm = ImageFont.truetype("arial.ttf", 26)
    except:
        font_lg = ImageFont.load_default()
        font_md = ImageFont.load_default()
        font_sm = ImageFont.load_default()

    # Model & Specs Text
    draw.text((hcx, hcy - 180), "SEC-FAN 120 PRO", font=font_lg, fill=(255, 255, 255, 255), anchor="mm")
    draw.text((hcx, hcy - 110), "INDUSTRIAL RACK COOLING", font=font_sm, fill=(0, 190, 240, 255), anchor="mm")
    draw.text((hcx, hcy - 45), "DC 12V  0.35A  4.2W", font=font_md, fill=(230, 235, 240, 255), anchor="mm")
    draw.text((hcx, hcy + 25), "DUAL BALL BEARING  3200 RPM", font=font_sm, fill=(180, 185, 192, 255), anchor="mm")
    draw.text((hcx, hcy + 95), "AIR FLOW ──▶  ROTATION ↻", font=font_md, fill=(255, 200, 40, 255), anchor="mm")
    draw.text((hcx, hcy + 175), "CE ● FCC ● RoHS ● UL 94V-0", font=font_sm, fill=(160, 166, 174, 255), anchor="mm")

    # Direction Arrow indicator on frame flange (top of Region 0)
    draw.text((512, 120), "AIR FLOW ──▶", font=font_md, fill=(160, 166, 172, 255), anchor="mm")

    # 4. Aerodynamic streak lines on blade region
    for bx in range(1080, 2000, 80):
        draw.line([bx, 1024, bx, 2048], fill=(36, 40, 45, 255), width=2)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"[OK] High-Res Rack Fan Texture generated: {output_path}")

if __name__ == "__main__":
    out_dir = r"C:\Users\Burak\Desktop\Security_CCTV\75. SEC_Server_Rack_Fan\exports"
    target = os.path.join(out_dir, "T_Security_Atlas.png")
    create_rack_fan_texture(target)
