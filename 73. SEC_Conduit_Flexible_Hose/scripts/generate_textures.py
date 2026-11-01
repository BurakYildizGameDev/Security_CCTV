import math
import numpy as np
from PIL import Image, ImageDraw

def create_pure_hose_texture(output_path):
    WIDTH, HEIGHT = 2048, 2048
    np.random.seed(7373)
    
    # 1. Base Metallic Steel (205, 210, 215)
    base_steel = np.array([205, 210, 215], dtype=np.float32)
    noise_fine = np.random.normal(0, 3.5, (HEIGHT, WIDTH))
    
    rgb_data = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    for c in range(3):
        channel = base_steel[c] + noise_fine
        rgb_data[:, :, c] = np.clip(channel, 0, 255).astype(np.uint8)
        
    # 100% Solid Opaque texture - ZERO TEXT, ZERO BARCODE
    alpha_data = np.full((HEIGHT, WIDTH), 255, dtype=np.uint8)
    rgba = np.dstack([rgb_data, alpha_data])
    img = Image.fromarray(rgba, mode='RGBA')
    draw = ImageDraw.Draw(img)
    
    # -------------------------------------------------------------
    # REGION 0: CORRUGATED FLEX CONDUIT RIBBING (0..1024, 0..1024)
    # -------------------------------------------------------------
    draw.rectangle([0, 0, 1024, 1024], fill=(188, 192, 198, 255))
    for ry in range(0, 1024, 16):
        # Deep groove shadow
        draw.rectangle([0, ry, 1024, ry + 4], fill=(70, 75, 80, 255))
        # Bevel highlight
        draw.rectangle([0, ry + 4, 1024, ry + 8], fill=(238, 242, 246, 255))
        # Crest face
        draw.rectangle([0, ry + 8, 1024, ry + 16], fill=(180, 185, 190, 255))
        
    for _ in range(120):
        sx = np.random.randint(0, 1024)
        sy = np.random.randint(0, 950)
        draw.line([sx, sy, sx + np.random.randint(-8, 8), sy + np.random.randint(30, 80)], fill=(130, 135, 140, 180), width=1)
        
    # -------------------------------------------------------------
    # REGION 1: POLISHED NICKEL HEX FITTING (1024..2048, 0..1024)
    # -------------------------------------------------------------
    draw.rectangle([1024, 0, 2048, 1024], fill=(220, 224, 228, 255))
    for fx in range(1024, 2048, 170):
        draw.line([fx, 0, fx, 1024], fill=(155, 160, 165, 255), width=4)
        draw.line([fx + 2, 0, fx + 2, 1024], fill=(248, 250, 252, 255), width=2)
        
    # -------------------------------------------------------------
    # REGION 2: GALVANIZED SLEEVE SWATCH (0..2048, 1024..1400) - NO TEXT / NO BARCODE
    # -------------------------------------------------------------
    draw.rectangle([0, 1024, 2048, 1400], fill=(200, 205, 210, 255))
    for _ in range(3000):
        rx = np.random.randint(0, 2048)
        ry = np.random.randint(1024, 1400)
        draw.point((rx, ry), fill=(175, 180, 185, 255))
        
    # -------------------------------------------------------------
    # REGION 3: THREADED MALE NIPPLE (0..1024, 1400..2048)
    # -------------------------------------------------------------
    draw.rectangle([0, 1400, 1024, 2048], fill=(165, 170, 175, 255))
    for ty in range(1400, 2048, 20):
        draw.line([0, ty, 1024, ty + 6], fill=(85, 90, 95, 255), width=3)
        draw.line([0, ty + 6, 1024, ty + 12], fill=(235, 240, 245, 255), width=2)
        
    img.save(output_path, "PNG")
    print(f"Clean Text-Free / Barcode-Free Flexible Hose Texture saved to: {output_path}")

if __name__ == "__main__":
    import os
    target = os.path.join(r"C:\Users\Burak\Desktop\Security_CCTV\73. SEC_Conduit_Flexible_Hose\exports\T_Security_Atlas.png")
    create_pure_hose_texture(target)
