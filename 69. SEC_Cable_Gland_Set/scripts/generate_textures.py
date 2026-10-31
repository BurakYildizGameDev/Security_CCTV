import math
import numpy as np
from PIL import Image, ImageDraw

def create_pure_metal_gland_texture(output_path):
    WIDTH, HEIGHT = 2048, 2048
    np.random.seed(6969)
    
    # 1. Base Nickel-Plated Brass / Stainless Steel Surface (RGB ~ 220, 224, 228)
    base_metal = np.array([220, 224, 228], dtype=np.float32)
    noise_fine = np.random.normal(0, 3.0, (HEIGHT, WIDTH))
    
    rgb_data = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    for c in range(3):
        channel = base_metal[c] + noise_fine * 0.5
        # Fine horizontal lathe brushing grain
        brush = np.sin(np.linspace(0, 500 * math.pi, HEIGHT))[:, None] * 1.8
        channel += brush
        rgb_data[:, :, c] = np.clip(channel, 0, 255).astype(np.uint8)

    # 100% Solid Opaque texture - NO ALPHA, NO TEXT!
    alpha_data = np.full((HEIGHT, WIDTH), 255, dtype=np.uint8)
    rgba = np.dstack([rgb_data, alpha_data])
    img = Image.fromarray(rgba, mode='RGBA')
    draw = ImageDraw.Draw(img)

    # -------------------------------------------------------------
    # REGION 0: PURE BRUSHED NICKEL METAL (X: 0..1024, Y: 0..1024)
    # Flawless seamless brushed metal with subtle anisotropic specular
    # -------------------------------------------------------------

    # -------------------------------------------------------------
    # REGION 1: PURE EPDM BLACK RUBBER (X: 1024..2048, Y: 0..1024)
    # Clean matte dark rubber for O-rings, grommets, cables
    # -------------------------------------------------------------
    draw.rectangle([1024, 0, 2048, 1024], fill=(22, 24, 26, 255))
    for _ in range(1200):
        rx = np.random.randint(1024, 2048)
        ry = np.random.randint(0, 1024)
        draw.point((rx, ry), fill=(32, 35, 38, 255))

    # -------------------------------------------------------------
    # REGION 2: PRECISION THREAD GROOVES (X: 0..1024, Y: 1024..2048)
    # Machined thread crest/root specular shading
    # -------------------------------------------------------------
    draw.rectangle([0, 1024, 1024, 2048], fill=(205, 210, 215, 255))
    for ty in range(1024, 2048, 16):
        draw.line([0, ty, 1024, ty], fill=(55, 60, 65, 255), width=3)
        draw.line([0, ty + 2, 1024, ty + 2], fill=(250, 252, 255, 255), width=3)
        draw.line([0, ty + 7, 1024, ty + 7], fill=(160, 165, 170, 255), width=3)

    # -------------------------------------------------------------
    # REGION 3: SATIN POLISHED NICKEL DOME (X: 1024..2048, Y: 1024..2048)
    # Ultra-smooth satin finish
    # -------------------------------------------------------------
    draw.rectangle([1024, 1024, 2048, 2048], fill=(224, 228, 232, 255))
    for dy in range(1024, 2048, 24):
        draw.line([1024, dy, 2048, dy], fill=(210, 215, 220, 255), width=2)
        draw.line([1024, dy + 2, 2048, dy + 2], fill=(240, 244, 248, 255), width=1)

    # ZERO TEXT, ZERO WRITING as explicitly requested!
    img.save(output_path, "PNG")
    print(f"Pure Metal Cable Gland texture (NO TEXT) saved to: {output_path}")

if __name__ == "__main__":
    import os
    target_path = os.path.join(r"C:\Users\Burak\Desktop\Security_CCTV\69. SEC_Cable_Gland_Set\exports\T_Security_Atlas.png")
    create_pure_metal_gland_texture(target_path)
