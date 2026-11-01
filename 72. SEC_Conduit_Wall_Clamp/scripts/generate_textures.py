import math
import numpy as np
from PIL import Image, ImageDraw

def create_pure_clamp_texture(output_path):
    WIDTH, HEIGHT = 2048, 2048
    np.random.seed(7272)
    
    # 1. Base Hot-Dip Galvanized (HDG) Steel (218, 222, 226)
    base_color = np.array([218, 222, 226], dtype=np.float32)
    noise_fine = np.random.normal(0, 3.5, (HEIGHT, WIDTH))
    
    # Galvanized zinc spangle crystalline pattern
    spangle = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    for _ in range(160):
        cx = np.random.randint(0, WIDTH)
        cy = np.random.randint(0, HEIGHT)
        radius = np.random.randint(30, 180)
        shade = np.random.uniform(-14, 14)
        y, x = np.ogrid[-cy:HEIGHT-cy, -cx:WIDTH-cx]
        mask = x*x + y*y <= radius*radius
        spangle[mask] += shade * 0.35
        
    rgb_data = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    for c in range(3):
        channel = base_color[c] + noise_fine + spangle
        rgb_data[:, :, c] = np.clip(channel, 0, 255).astype(np.uint8)
        
    # 100% Solid Opaque texture - NO ALPHA, NO TEXT, NO BARCODE
    alpha_data = np.full((HEIGHT, WIDTH), 255, dtype=np.uint8)
    rgba = np.dstack([rgb_data, alpha_data])
    img = Image.fromarray(rgba, mode='RGBA')
    draw = ImageDraw.Draw(img)
    
    # -------------------------------------------------------------
    # REGION 0: CLEAN HDG SHEET STEEL (0..1024, 0..1024)
    # Natural zinc spangles, zero text, pure industrial galvanized finish
    # -------------------------------------------------------------
    
    # -------------------------------------------------------------
    # REGION 1: DARKENED ZINC / HARDWARE BOLT STEEL (1024..2048, 0..1024)
    # -------------------------------------------------------------
    draw.rectangle([1024, 0, 2048, 1024], fill=(138, 144, 150, 255))
    for _ in range(3500):
        rx = np.random.randint(1024, 2048)
        ry = np.random.randint(0, 1024)
        draw.point((rx, ry), fill=(118, 124, 130, 255))
    for _ in range(2000):
        rx = np.random.randint(1024, 2048)
        ry = np.random.randint(0, 1024)
        draw.point((rx, ry), fill=(160, 166, 172, 255))
        
    # -------------------------------------------------------------
    # REGION 2: POLISHED ZINC PLATE (0..2048, 1024..1400) - NO TEXT / NO BARCODE
    # -------------------------------------------------------------
    draw.rectangle([0, 1024, 2048, 1400], fill=(212, 216, 220, 255))
    for _ in range(2000):
        rx = np.random.randint(0, 2048)
        ry = np.random.randint(1024, 1400)
        draw.point((rx, ry), fill=(190, 195, 200, 255))
        
    # -------------------------------------------------------------
    # REGION 3: THREAD & HARDWARE ACCENTS (0..1024, 1400..2048)
    # -------------------------------------------------------------
    draw.rectangle([0, 1400, 1024, 2048], fill=(155, 160, 166, 255))
    for ty in range(1400, 2048, 20):
        draw.line([0, ty, 1024, ty + 6], fill=(110, 115, 120, 255), width=3)
        draw.line([0, ty + 6, 1024, ty + 12], fill=(195, 200, 205, 255), width=2)
        
    img.save(output_path, "PNG")
    print(f"Clean Text-Free / Barcode-Free Clamp Texture saved to: {output_path}")

if __name__ == "__main__":
    import os
    target = os.path.join(r"C:\Users\Burak\Desktop\Security_CCTV\72. SEC_Conduit_Wall_Clamp\exports\T_Security_Atlas.png")
    create_pure_clamp_texture(target)
