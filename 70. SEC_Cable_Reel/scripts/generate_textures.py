import math
import numpy as np
from PIL import Image, ImageDraw

def create_pure_reel_texture(output_path):
    WIDTH, HEIGHT = 2048, 2048
    np.random.seed(7070)
    
    # 1. Base Powder-Coated Industrial Steel (Light Cool Grey: 218, 222, 226)
    base_steel = np.array([218, 222, 226], dtype=np.float32)
    noise_fine = np.random.normal(0, 3.0, (HEIGHT, WIDTH))
    
    rgb_data = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    for c in range(3):
        channel = base_steel[c] + noise_fine * 0.5
        rgb_data[:, :, c] = np.clip(channel, 0, 255).astype(np.uint8)

    # 100% Solid Opaque texture - NO ALPHA, NO GLITCH!
    alpha_data = np.full((HEIGHT, WIDTH), 255, dtype=np.uint8)
    rgba = np.dstack([rgb_data, alpha_data])
    img = Image.fromarray(rgba, mode='RGBA')
    draw = ImageDraw.Draw(img)

    # -------------------------------------------------------------
    # REGION 0: CLEAN POWDER-COATED STEEL SWATCH (X: 0..1024, Y: 0..1024)
    # Used for frame tubes, flanges, drum core - completely clean!
    # -------------------------------------------------------------

    # -------------------------------------------------------------
    # REGION 1: CLEAN MATTE BLACK RUBBER SWATCH (X: 1024..2048, Y: 0..1024)
    # Used for rubber feet, handle grip, wound cable coil
    # -------------------------------------------------------------
    draw.rectangle([1024, 0, 2048, 1024], fill=(22, 24, 26, 255))
    for _ in range(1200):
        rx = np.random.randint(1024, 2048)
        ry = np.random.randint(0, 1024)
        draw.point((rx, ry), fill=(32, 35, 38, 255))

    # -------------------------------------------------------------
    # REGION 2: DIAGONAL HAZARD CAUTION BAND (X: 0..2048, Y: 1024..1140)
    # -------------------------------------------------------------
    draw.rectangle([0, 1024, 2048, 1140], fill=(245, 195, 20, 255))
    for sx in range(-120, 2168, 48):
        pts = [(sx, 1024), (sx + 24, 1024), (sx + 24 + 116, 1140), (sx + 116, 1140)]
        draw.polygon(pts, fill=(20, 22, 25, 255))
    draw.line([0, 1024, 2048, 1024], fill=(15, 16, 18, 255), width=3)
    draw.line([0, 1140, 2048, 1140], fill=(15, 16, 18, 255), width=3)

    # -------------------------------------------------------------
    # REGION 3: RED THERMAL OVERLOAD BUTTON SWATCH (X: 0..512, Y: 1200..1600)
    # -------------------------------------------------------------
    draw.rectangle([0, 1200, 512, 1600], fill=(210, 30, 30, 255))
    draw.rectangle([20, 1220, 492, 1580], fill=(180, 20, 20, 255), outline=(245, 245, 245, 255), width=4)

    # NO UNWANTED MIDDLE TEXTURE / NO GIANT DECAL IN THE CENTER!
    img.save(output_path, "PNG")
    print(f"Clean Glitch-Free Cable Reel texture saved to: {output_path}")

if __name__ == "__main__":
    import os
    target_path = os.path.join(r"C:\Users\Burak\Desktop\Security_CCTV\70. SEC_Cable_Reel\exports\T_Security_Atlas.png")
    create_pure_reel_texture(target_path)
